class ASMParser():
    def __init__(self, input_file):
        with open(input_file) as file:
            # Reads lines of input into a list
            lines = file.readlines()
        # TODO: refactor so that advance goes line by line without reading the whole file into memory

        # Initializes parser to line 0, with no instruction loaded
        self.input = lines
        self.next_line = 0
        self.inst_line = 0
        self.cur_inst = None


    def has_more_lines(self):
        """
        Returns true if next_line exists
        """
        if self.next_line < len(self.input):
            return True
        return False


    def advance(self):
        """
        Advances through the input line by line.
        When a non-empty non-comment line is found, loads that line into cur_inst
        after stripping any whitespace.
        Sets next_line to the line after the cur_inst.

        Returns:
            True if an instruction was found
            False otherwise
        """
        # comments are any lines that begin with //
        # whitespace before lines is ignored
        # empty lines are also ignored
        while self.has_more_lines():
            current_line = self.input[self.next_line]
            if "//" in current_line:
                current_line = current_line[0:current_line.find("//")]
            current_line = current_line.strip()
            if len(current_line) == 0:
                self.next_line += 1
            else:
                self.cur_inst = current_line
                self.next_line += 1
                # Only increment instruction line if it is not a loop label
                if self.cur_inst[0] != '(':
                    self.inst_line += 1
                return True
        # If a valid instruction was not found loads None into cur_inst
        # and returns False
        self.cur_inst = None
        return False


    def instruction_type(self):
        """
        Returns
            A if line is @xxx where xxx is either an integer number or a symbol
            L if line is (xxx) where xxx is a symbol
            C otherwise
        """
        if self.cur_inst[0] == '@':
            return 'A'
        elif self.cur_inst[0] == '(' and self.cur_inst[-1] == ')':
            return 'L'
        else:
            return 'C'


    def symbol(self):
        """
        Returns the symbol for A and L instructions
        """
        if self.instruction_type() == 'C':
            raise ValueError("Type C instruction is not a valid instruction for symbol(). Only A and L instructions contain symbols.")
        elif self.instruction_type() == 'A':
            # return the string after the @
            return self.cur_inst[1:]
        else:
            # return the string inside the ()
            return self.cur_inst[1:-1]


    def dest(self):
        """
        Returns the dest part of a C instruction
        If there is no dest, returns an empty string
        """
        if '=' in self.cur_inst:
            return self.cur_inst[0:self.cur_inst.index('=')]
        else:
            return ""


    def comp(self):
        """
        Returns the comp part of a C instruction
        If there is no comp part, raises an error
        """
        if '=' in self.cur_inst:
            eq_index = self.cur_inst.index('=') + 1
        else:
            eq_index = 0

        if ';' in self.cur_inst:
            semcol_index = self.cur_inst.index(';')
        else:
            semcol_index = len(self.cur_inst)

        comp_val = self.cur_inst[eq_index:semcol_index]

        if len(comp_val) == 0:
            raise ValueError(f"No value found for comp on line {self.inst_line}. Comp is required in a C-instruction")

        else:
            return comp_val


    def jump(self):
        """
        Returns the jump part of a C instruction
        If there is no jump, returns an empty string
        """
        if ';' in self.cur_inst:
            return self.cur_inst[self.cur_inst.index(';') + 1:]
        else:
            return ""


    def __str__(self):
        join_str = ""
        return join_str.join(self.input)