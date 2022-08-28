from typing import Dict

#TODO: add function for setting up new functin and filename

class CodeWriter:
    """
    Once initialized, the codewriter is used by calling the translate function with the parsed tokens.
    The translate function returns a string of hack assembly commands which are the translation of the
    vm stack machine tokens.
    """
    def __init__(self, filename:str = "", verbose_flag:bool=False, pop_pointer_temp_reg:str="R13") -> None:
        # Logical jump labels are not reset
        # (TODO: but we could make them reset by including filename in the label)
        self.eq_label : int = 0
        self.gt_label : int = 0
        self.lt_label : int = 0
        # Initialized when a function is defined
        self.return_label_id : int = None
        # filename gets initialized before translation begins
        self.filename :str = None
        # function name gets initialized when a function is definined
        self.current_function = None
        self.verbose : bool = verbose_flag
        self.pop_pointer_temp_reg : str = pop_pointer_temp_reg
        self.seg_dict : Dict[str, str]= {
            "local":"LCL",
            "argument":"ARG",
            "this":"THIS",
            "that":"THAT"
        }

    def new_file(self, filename:str) -> None:
        """
        Updates filename when starting a new file for writing
        """
        self.filename = filename

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
        return str(label)

    def close(self):
        """
        Returns assembly string to end the code with an infinite loop
        """
        return ("(END)\n"
                "@END\n"
                "0;JMP\n")

    def bootstrap(self):
        """
        Returns assembly string which bootstraps execution of the compiled code
        """
        # Set SP <- 256
        # Call Sys.init
        code = ("@256\n"
                "D=A\n"
                "@SP\n"
                "M=D\n"
                "@Sys.init\n"
                "0;JMP\n")
        return code

    def translate(self, op:str, arg1:str = "", arg2:str = "") -> str:
        """
        Parameters:
            operation
            arg1 (segment or label or function)
            arg2 (index or nVars or nArgs)
        """
        # Check that each operation has the correct number of arguments
        if ((op == "pop" or op == "push")
             and (len(arg1) == 0 or len(arg2) == 0)):
             raise ValueError("Pop and push operations require both a segment argument and an index argument.")

        if (op in ["label", "if-goto", "goto"] and len(arg1) == 0):
            raise ValueError("Label operation requires a label argument")

        # call the correct subroutine for a given operation
        if op == "pop":
            return self.write_pop(arg1, arg2)
        elif op == "push":
            return self.write_push(arg1, arg2)
        elif op in ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]:
            return self.write_arithmetic_logical(op)
        elif op == "label":
            return self.write_label(arg1)
        elif op == "goto":
            return self.write_goto(arg1)
        elif op == "if-goto":
            return self.write_if_goto(arg1)
        elif op == "call":
            return self.write_function_call(arg1, arg2)
        elif op == "function":
            return self.write_function_def(arg1, arg2)
        elif op == "return":
            return self.write_return()
        else:
            raise ValueError("Operation not found.")

    def push(self, adr:str) -> str:
        """
        Writes HACK assembly to push value at adr onto current stack at SP and increment SP
        """
        code = ""
        if self.verbose:
            code += f"\\ push {adr}\n"
        code += (f"@{adr}\n"
                 "D=M\n"
                 "@SP\n"
                 "M=M+1\n"
                 "A=M-1\n"
                 "M=D\n")
        return code

    def get_return_id(self) -> str:
        """
        Returns and increments self.return_label_id
        """
        return_id = str(self.return_label_id)
        self.return_label_id += 1
        return return_id

    def write_function_call(self, function:str, n_args:str) -> str:
        """
        Translates a VM function call into Hack assembly code
        """
        return_address : str = f"{self.current_function}$ret.{self.get_return_id()}"

        code = ""
        if self.verbose:
            code += f"// call function {function} with {n_args} args\n"

        #push return address // generate label and push it to stack
        code += self.push(return_address)
        #push LCL
        code += self.push("LCL")
        #push ARG
        code += self.push("ARG")
        #push THIS
        code += self.push("THIS")
        #push THAT
        code += self.push("THAT")
        #ARG = SP - 5- nArgs //reposition args
        code += ("@5\n"
                 "D=A\n"
                f"@{str(n_args)}\n"
                 "D=D+A\n"
                 "@SP\n"
                 "D=M-S\n"
                 "@ARG\n"
                 "M=D\n")
        #LCL = SP //reposition LCL
        code += ("@SP\n"
                 "D=M\n"
                 "@LCL\n"
                 "M=D\n")
        #goto function //transfer control to {function}
        code += (f"@{function}\n"
                  "0;JMP\n")
        #(return_adr) //inject return label
        code += f"({return_address})\n"
        return code


    def write_function_def(self, function:str, n_vars:str) -> str:
        """
        Translates a VM function definition into Hack assembly code
        """
        # Set this function as active
        self.current_function = function

        # Reset call count for return labels
        self.return_label_id = 0

        code = ""
        if self.verbose:
            code += f"// Define fuction {function} with {n_vars} variables\n"

        # Inject function entry label
        code += f"({function})\n"
        for n in range(0,n_vars):
            # Push 0 to stack for each var in n_vars
            # This could be done with a loop in assembly, but most functions will
            # have few variables, so just directly coding it should actually be
            # faster due to not having to update the counter variable
            code += ("@SP\n"
                     "M=M+1\n"
                     "A=A-1n\n"
                     "M=0\n")
        return code

    def write_return(self) -> str:
        """
        Translates a VM function return into Hack assembly code
        """
        code = ""
        if self.verbose:
            code += "// return from function\n"
        # frame = LCL // Frame is a temporary variable, say R14
        code += ("@LCL\n"
                 "D=M\n"
                 "@R15\n"
                 "M=D\n")
        # retAdr = *(frame-5) // Puts retAdr in temp variable, say R15
        code += ("@5\n"
                 "A=D-A\n"
                 "D=M\n"
                 "@R14\n"
                 "M=D\n")
        # *ARG = pop() // Repositions return value for caller
        code += ("@SP\n"
                 "AD=M\n"
                 "@ARG\n"
                 "A=M\n"
                 "M=D\n")
        # SP = ARG + 1 // Repositions SP for the caller
        code +=("@ARG\n"
                "D=M+1\n"
                "@SP\n"
                "M=D\n")
        # THAT = *(frame-1) // Restores THAT
        # THIS = *(frame-2) // Restores THIS
        # ARG = *(frame-3) // Restores ARG
        # LCL = *(frame-4) // Restores LCL
        for adr in ["THAT", "THIS", "ARG", "LCL"]:
            code += ("@R14\n"
                     "AMD=M-1\n"
                    f"@{adr}\n"
                     "M=D\n")
        # goto retAdr // jump to return adr, which is stored in R15
        code += ("@R15\n"
                 "A=M\n"
                 "0;JMP\n")
        return code

    def get_function_name(self) -> str:
        """
        returns "filename.function_name" if both self.filename and self.function_name are not empty
        if either is empty, return empty string
        """
        if self.filename == None or self.current_function == None:
            print("WARNING: File name or function name are None when calling get_function_name()")
            return ""
        else:
            return f"{self.filename}.{self.current_function()}"

    def write_label(self, label:str) -> str:
        """
        Writes assembly code jump label. Labels need to follow the symbol specification
        as definited in the vm translator spec.
        """
        # TODO: implement labeling per specification
        return f"({self.current_function}${label})\n"

    def write_goto(self, label:str) -> str:
        """
        Writes assembly code to perform an unconditional jump to (label)
        """
        code : str = ""
        if self.verbose:
            code += f"//jump to ({self.current_function}${label})\n"
        code += (f"@{self.current_function}${label}\n"
                 "0;JMP\n")
        return code

    def write_if_goto(self, label:str) -> str:
        """
        Writes assembly code which performs a conditional jump to (label)
        Condition is that top stack item != 0. If stack = 0 (false), we don't jump.
        All other values are considered true.
        """
        code :str = ""
        if self.verbose:
            code += f"//jump to ({self.current_function}${label}) if top stack item is not false (0)\n"
        code += ("@SP\n"
                "AM=M-1\n"
                "D=M\n"
                f"@{self.current_function}${label}\n"
                "D;JNE\n")
        return code

    def map_direct_seg(self, seg:str, idx:str) -> str:
        """
        Returns address call for direct segments
        static, pointer, and temp
        """
        if seg == "static":
            # get correct symbolic variable from the table
            if len(self.filename) == 0:
                raise ValueError("Filename is empty when adding a static symbol")
            return f"@{self.filename}.{idx}\n"
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

    def map_segment_push(self, seg:str, idx:str) -> str:
        """
        maps segment and index onto the correct symbolic variable or memory location
        LCL, ARG, THIS, THAT, foo.i, for push operation
        """
        if seg == "constant":
            return f"@{idx}\n"
        elif seg in ["static", "pointer", "temp"]:
            return self.map_direct_seg(seg, idx)
        elif seg in self.seg_dict:
            code = (f"@{idx}\n"
                    "D=A\n"
                    f"@{self.seg_dict.get(seg)}\n"
                    "A=D+M\n")
            return code
        else:
            raise ValueError("Invalid operation passed to map_segment")

    def write_pop(self, seg:str, idx:str) -> str:
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
                  "M=D\n")
        return code

    def write_push(self, seg:str, idx:str) -> str:
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

    def write_arithmetic_logical(self, op:str) -> str:

        if op == "add":
            code = self.pop_2()
            if self.verbose:
                code += "//add\n"
            code += "M=D+M\n"
        elif op == "sub":
            code = self.pop_2()
            if self.verbose:
                code += "//sub\n"
            code += "M=M-D\n"
        elif op == "neg":
            code = self.pop_1()
            if self.verbose:
                code += "//neg\n"
            code += "M=-M\n"
        elif op == "eq":
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
        elif op == "gt":
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
        elif op == "lt":
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
        elif op == "and":
            code = self.pop_2()
            if self.verbose:
                code += "//and\n"
            code += "M=D&M\n"
        elif op == "or":
            code = self.pop_2()
            if self.verbose:
                code += "//or\n"
            code += "M=D|M\n"
        elif op == "not":
            code = self.pop_1()
            if self.verbose:
                code += "//not\n"
            code += "M=!M\n"

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