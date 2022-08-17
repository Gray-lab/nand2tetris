class Code():
    def __init__(self):
        self.dest_dic = {
            ''  : '000',
            'M' : '001',
            'D' : '010',
            'DM' : '011',
            'MD' : '011',
            'A' : '100',
            'AM' : '101',
            'AD' : '110',
            'ADM' : '111'
        }

        self.jump_dic = {
            '' : '000',
            'JGT' : '001',
            'JEQ' : '010',
            'JGE' : '011',
            'JLT' : '100',
            'JNE' : '101',
            'JLE' : '110',
            'JMP' : '111'
        }

        self.comp_dict = {
            '0' : '0101010',
            '1' : '0111111',
            '-1' : '0111010',
            'D' : '0001100',
            'A' : '0110000',
            'M' : '1110000',
            '!D' : '0001101',
            '!A' : '0110001',
            '!M' : '1110001',
            '-D' : '0001111',
            '-A' : '0110011',
            '-M' : '1110011',
            'D+1' : '0011111',
            'A+1' : '0110111',
            'M+1' : '1110111',
            'D-1' : '0001110',
            'A-1' : '0110010',
            'M-1' : '1110010',
            'D+A' : '0000010',
            'D+M' : '1000010',
            'D-A' : '0010011',
            'D-M' : '1010011',
            'A-D' : '0000111',
            'M-D' : '1000111',
            'D&A' : '0000000',
            'D&M' : '1000000',
            'D|A' : '0010101',
            'D|M' : '1010101'
        }


    def dest(self, dest_val):
        """
        Returns the binary translation of dest_value
        """
        return self.dest_dic[dest_val]


    def jump(self, jump_val):
        """
        Returns the binary translation of jump_value
        """
        return self.jump_dic[jump_val]


    def comp(self, comp_val):
        """
        Returns the binary translation of comp_val
        """
        return self.comp_dict[comp_val]