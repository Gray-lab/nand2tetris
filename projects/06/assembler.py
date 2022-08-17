import sys
import code
from asmparser import ASMParser as Parser

# Location for start of symbol addresses, initialize to 16
SYMBOL_MEM_INDEX_START = 16

def main():
    # Check for proper usage
    if len(sys.argv) != 2:
        print("Incorrect number of arguments")
        sys.exit("Usage: python assembler.py file.asm")

    # Instantiate parser
    my_parser = Parser(sys.argv[1])

    # Initialize translation dictionaries
    my_code = code.Code()

    # Initialize symbol table and populate with symbols by making a first pass
    symbol_table = get_symbols(Parser(sys.argv[1]));

    # Test translation into binary
    # while my_parser.advance():
    #     if my_parser.instruction_type() == 'C':
    #         print(f"{my_parser.inst_line}  {my_parser.cur_inst}   \t| Type: {my_parser.instruction_type()} \t| Dest: {my_parser.dest()}  Comp: {my_parser.comp()}  Jump: {my_parser.jump()} \t | Translation: {translate(my_parser, my_code, symbol_table)}")
    #     else:
    #         print(f"{my_parser.inst_line}  {my_parser.cur_inst}   \t| Type: {my_parser.instruction_type()} \t| Symbol: {my_parser.symbol()} \t\t\t | Translation: {translate(my_parser, my_code, symbol_table)}")

    symbol_mem_index = SYMBOL_MEM_INDEX_START

    # Open output file for writing
    out_file_name = sys.argv[1][:-3] + 'hack'

    # Perform assembly and write out results line by line
    with open(out_file_name, 'w') as out:
        while my_parser.advance():
            # Skip any lines with loop instructions
            if my_parser.cur_inst[0] != '(':
                translate_out = translate(my_parser, my_code, symbol_table, symbol_mem_index)
                symbol_mem_index = translate_out[1]
                out.write(translate_out[0] + '\n')

def translate(parser, my_code, symbol_table, symbol_mem_index):
    """
    Translates a line into binary
    Returns:
        tuple (str, int)
        (16 digit binary string, new_symbol_mem_index)
    """
    if parser.instruction_type() == 'C':
        dest_bin = my_code.dest(parser.dest())
        comp_bin = my_code.comp(parser.comp())
        jump_bin = my_code.jump(parser.jump())
        return ("111" + comp_bin + dest_bin + jump_bin, symbol_mem_index)
    else:
        symbol = parser.symbol()
        if symbol in symbol_table:
            return ('0' + int_to_binary(int(symbol_table.get(symbol))), symbol_mem_index)
        elif symbol[0] in '0123456789':
            return ('0' + int_to_binary(int(symbol)), symbol_mem_index)
        else:
            symbol_table[symbol] = symbol_mem_index
            symbol_mem_index += 1
            return ('0' + int_to_binary(int(symbol_table.get(symbol))), symbol_mem_index)

def get_symbols(sym_parser):
    # Allocate predefined symbols
    sym_table = {
        'R0' : '0',
        'R1' : '1',
        'R2' : '2',
        'R3' : '3',
        'R4' : '4',
        'R5' : '5',
        'R5' : '5',
        'R6' : '6',
        'R7' : '7',
        'R8' : '8',
        'R9' : '9',
        'R10' : '10',
        'R11' : '11',
        'R12' : '12',
        'R13' : '13',
        'R14' : '14',
        'R15' : '15',
        'SCREEN' : '16384',
        'KBD' : '24576',
        'SP' : '0',
        'LCL' : '1',
        'ARG' : '2',
        'THIS' : '3',
        'THAT' : '4'
    }
    # Do a parser pass to get loop labels
    while sym_parser.advance():
        if sym_parser.instruction_type() != 'C':
            if sym_parser.cur_inst[0] == '(':
                symbol = sym_parser.symbol()
                if symbol not in sym_table and symbol[0] not in '0123456789':
                    # bind loop label symbols to their instruction line
                    sym_table[symbol] = sym_parser.inst_line
    return sym_table

def int_to_binary(value: (int)):
    """
    Translates a string representation of an integer into a binary string

    Returns: str
    """
    if value > 32767:
        raise ValueError("value must be <= 32767")
    elif value < 0:
        raise ValueError("value must be >= 0")

    return f"{value:015b}"

if __name__ == "__main__":
    main();
