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

    # TODO: Add handling of either a single .vm file, or a directory of .vm files
    # Make a list of filenames to drive the translation loop

    # TODO: Instantiate a parser for every .vm file 
    # - maybe this can be done one at a time in the translation loop

    # Instantiate parser using file name
    my_parser = parser.Parser(sys.argv[1])

    # Instantiate codewriter
    my_codewriter = codewriter.CodeWriter(sys.argv[1], verbose_flag=True)

    out_file_name = sys.argv[1][:-2] + "asm"
    #print(out_file_name)

    # TODO: Handle bootstrapping code, multiple file writing, and closing code
    # Translate and write .asm file
    with open(out_file_name, "w") as out:
        # TODO: Add bootstrap code (not yet implemented)
        # out.write(my_codewriter.bootstrap())
        # TODO: For each .vm file, use the relevant parser and 
        while my_parser.advance():
            out.write(my_codewriter.translate(my_parser.op, my_parser.arg1, my_parser.arg2))
            #print(my_parser.parsed_line)
            #print(my_codewriter.translate(my_parser.op, my_parser.arg1, my_parser.arg2), end="")
        out.write(my_codewriter.close())
        #print(my_codewriter.finalize(), end="")

if __name__ == '__main__':
    main()