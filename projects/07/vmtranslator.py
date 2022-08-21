import parser
import codewriter

import sys
STATIC_INDEX = 16
STACK_INDEX = 256

# TODO: add error checking to catch overflow of memory segments

def main():
    # Check correct usage
    if len(sys.argv) != 2:
        print("Incorrect number of arguments")
        sys.exit("Usage: python vmtranslator.py file.vm")

    # Instantiate parser using file name
    my_parser = parser.Parser(sys.argv[1])

    # Instantiate codewriter
    my_codewriter = codewriter.CodeWriter(sys.argv[1], verbose_flag=True)

    out_file_name = sys.argv[1][:-2] + "asm"
    print(out_file_name)

    # Translate and write .asm file
    with open(out_file_name, "w") as out:
        while my_parser.advance():
            out.write(my_codewriter.translate(my_parser.op, my_parser.arg1, my_parser.arg2))
            #print(my_parser.parsed_line)
            print(my_codewriter.translate(my_parser.op, my_parser.arg1, my_parser.arg2), end="")
        out.write(my_codewriter.finalize())
        print(my_codewriter.finalize(), end="")

if __name__ == '__main__':
    main()