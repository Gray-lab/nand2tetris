from typing import Dict

class CodeWriter:
    """
    Once initialized, the codewriter is used by calling the translate function with the parsed tokens.
    The translate function returns a string of hack assembly commands which are the translation of the
    vm stack machine tokens.
    """
    def __init__(self, filename:str, verbose_flag:bool=False, pop_pointer_temp_reg:str="R13") -> None:
        self.eq_label : int = 0
        self.gt_label : int = 0
        self.lt_label : int = 0
        self.static_label : int = 0
        self.filename :str = filename[0:filename.index(".")]
        self.verbose : bool = verbose_flag
        self.pop_pointer_temp_reg : str = pop_pointer_temp_reg
        self.seg_dict : Dict[str, str]= {
            "local":"LCL",
            "argument":"ARG",
            "this":"THIS",
            "that":"THAT"
        }
        self.static_var_tb : Dict[str, str] = {}

    def next_label(self, op:str) -> str:
        """
        returns and increments self.label_index for the op parameter
        """
        if op == "eq":
            label = self.eq_label
            self.eq_label += 1
        elif op == "gt":
            label = self.gt_label
            self.gt_label += 1
        elif op == "lt":
            label = self.lt_label
            self.lt_label += 1
        else:
            label = self.static_label
            self.static_label += 1
        return str(label)

    def finalize(self):
        """
        Returns assembly string to end the code with an infinite loop
        """
        return ("(END)\n"
                "@END\n"
                "0;JMP\n")

    def translate(self, op:str, seg:str = "", idx:str = "") -> str:
        """
        Parameters:
            operation
            segment
            index
        """
        # Check that each operation has the correct number of arguments
        if ((op == "pop" or op == "push")
             and (len(seg) == 0 or len(idx) == 0)):
             raise ValueError("Pop and push operations require both a segment argument and an index argument.")

        # call the correct subroutine for a given operation
        if op == "pop":
            return self.pop(seg, idx)
        elif op == "push":
            return self.push(seg, idx)
        elif op == "add":
            return self.add()
        elif op == "sub":
            return self.sub()
        elif op == "neg":
            return self.neg()
        elif op == "eq":
            return self.eq()
        elif op == "gt":
            return self.gt()
        elif op == "lt":
            return self.lt()
        elif op == "and":
            return self.t_and()
        elif op == "or":
            return self.t_or()
        elif op == "not":
            return self.t_not()
        else:
            raise ValueError("Operation not found.")

    def get_symb_static_var(self, idx:str) -> str:
        """
        Gets symbolic variable for static idx from static_var_tb.
        If no variable exists, adds new entry to static_var_tb and returns
        the new variable.
        """
        if idx in self.static_var_tb:
            return self.static_var_tb.get(idx)
        else:
            new_var : str = self.filename + "." + self.next_label('static')
            self.static_var_tb[idx] = new_var
            return new_var

    def map_segment_push(self, seg:str, idx:str) -> str:
        """
        maps segment and index onto the correct symbolic variable or memory location
        LCL, ARG, THIS, THAT, foo.i, for push operation
        """
        if seg == "constant":
            return f"@{idx}\n"
        elif seg == "static":
            return f"@{self.get_symb_static_var(idx)}\n"
        elif seg == "pointer":
            if idx == "0":
                return f"@THIS\n"
            elif idx == "1":
                return f"@THAT\n"
            else:
                raise ValueError("Pointer segment fault. Pointer segment can only have index of 0 or 1")
        elif seg == "temp":
            if int(idx) > 7:
                raise ValueError("Temp segment fault. Index must be <= 7.")
            return f"@R{str(5+int(idx))}\n"
        elif seg in self.seg_dict:
            code = (f"@{idx}\n"
                    "D=A\n"
                    f"@{self.seg_dict.get(seg)}\n"
                    "A=D+M\n")
            return code
        else:
            raise ValueError("Invalid operation passed to map_segment")

    def map_direct_seg(self, seg:str, idx:str) -> str:
        """
        Returns address call for direct segments
        static, pointer, and temp
        """
        if seg == "static":
            # get correct symbolic variable from the table
            return f"@{self.get_symb_static_var(idx)}\n"
        elif seg == "pointer":
            # pointer 0 maps to THIS, pointer 1 maps to THAT
            if idx == "0":
                return f"@THIS\n"
            elif idx == "1":
                return f"@THAT\n"
            else:
                raise ValueError("Pointer segment fault. Pointer segment can only have index of 0 or 1")
        elif seg == "temp":
            # temp uses a direct mapping on R5 through R12, or idx + 5
            if int(idx) > 7:
                raise ValueError("Temp segment fault. Index must be <= 7.")
            return f"@R{str(5+int(idx))}\n"

    def map_segment_pop(self, seg:str, idx:str) -> str:
        """
        maps segment and index onto the correct symbolic variable or memory location
        LCL, ARG, THIS, THAT, foo.i, for pop operation
        """
        if seg in ["static", "pointer", "temp"]:
            return self.map_direct_seg(seg, idx)
        elif seg in self.seg_dict:
            # calculated pointer was previously stored in temp register
            code = (f"@{self.pop_pointer_temp_reg}\n"
                     "A=M\n")
            return code
        else:
            raise ValueError("Invalid operation passed to map_segment")

    def pop(self, seg:str, idx:str) -> str:
        """
        returns hack assembly string that pops top item of stack to RAM segment[index]
        """
        code : str = ""
        if self.verbose:
            code += f"//pop {seg} {idx}\n"
        seg_map = self.map_segment_pop(seg, idx)
        # if the segment uses a base pointer, this calculates the resulting
        # address and stores it in a temporary register (R13 by default)
        if seg in ["local", "argument", "this", "that"]:
            calc_pointer = (f"@{idx}\n"
                             "D=A\n"
                            f"@{self.seg_dict.get(seg)}\n"
                             "D=D+M\n"
                            f"@{self.pop_pointer_temp_reg}\n"
                             "M=D\n")
        else:
            calc_pointer = ""
        code += (
                 f"{calc_pointer}"
                  "@SP\n"
                  "AM=M-1\n"
                  "D=M\n"
                  f"{seg_map}"
                  "M=D")
        return code

    def push(self, seg:str, idx:str) -> str:
        """
        returns hack assembly string that pushes item at RAM segment[index] to top of stack
        """
        code : str = ""
        if self.verbose:
            code += f"//push {seg} {idx}\n"

        # to push a constant, we want to access the value directly from A
        # all other operations read from M
        if seg == "constant":
            reg = "D=A\n"
        else:
            reg = "D=M\n"

        seg_map = self.map_segment_push(seg, idx)
        code += (f"{seg_map}"
                 f"{reg}"
                "@SP\n"
                "M=M+1\n"
                "A=M-1\n"
                "M=D\n")
        return code

    def add(self) -> str:
        code = self.pop_2()
        if self.verbose:
            code += "//add\n"
        code += "M=D+M\n"
        return code

    def sub(self) -> str:
        code = self.pop_2()
        if self.verbose:
            code += "//sub\n"
        code += "M=M-D\n"
        return code

    def t_and(self) -> str:
        code = self.pop_2()
        if self.verbose:
            code += "//and\n"
        code += "M=D&M\n"
        return code

    def t_or(self) -> str:
        code = self.pop_2()
        if self.verbose:
            code += "//or\n"
        code += "M=D|M\n"
        return code

    def neg(self) -> str:
        code = self.pop_1()
        if self.verbose:
            code += "//neg\n"
        code += "M=-M\n"
        return code

    def t_not(self) -> str:
        code = self.pop_1()
        if self.verbose:
            code += "//not\n"
        code += "M=!M\n"
        return code

    def eq(self) -> str:
        label = self.next_label("eq")
        code = self.pop_2()
        if self.verbose:
            code += "//eq\n"
        code += ("D=M-D\n"
                "M=-1\n"
                f"@eqTrue{label}\n"
                "D;JEQ\n"
                "@SP\n"
                "A=M-1\n"
                "M=0\n"
                f"(eqTrue{label})\n")
        return code

    def gt(self) -> str:
        label = self.next_label("gt")
        code = self.pop_2()
        if self.verbose:
            code += "//gt\n"
        code += ("D=M-D\n"
                "M=-1\n"
                f"@gtTrue{label}\n"
                "D;JGT\n"
                "@SP\n"
                "A=M-1\n"
                "M=0\n"
                f"(gtTrue{label})\n")
        return code
        return code

    def lt(self) -> str:
        label = self.next_label("lt")
        code = self.pop_2()
        if self.verbose:
            code += "//lt\n"
        code += ("D=M-D\n"
                "M=-1\n"
                f"@ltTrue{label}\n"
                "D;JLT\n"
                "@SP\n"
                "A=M-1\n"
                "M=0\n"
                f"(ltTrue{label})\n")
        return code

    def pop_2(self) -> str:
        """
        returns assembly code string that pops top two items on stack into D and A registers
        and decrements SP by 1
        """
        code : str = ""
        if self.verbose:
            code = "//pop_2\n"
        code += ("@SP\n"
                "AM=M-1\n"
                "D=M\n"
                "@SP\n"
                "A=M-1\n")
        return code

    def pop_1(self) -> str:
        """
        returns assembly code string that puts the top item on stack into the A register
        """
        code : str = ""
        if self.verbose:
            code = "//pop_1\n"
        code += (f"@SP\n"
                "A=M-1\n")
        return code
