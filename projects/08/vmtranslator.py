import parser
import codewriter
import os

import sys
STATIC_INDEX : int = 16
STACK_INDEX : int = 256
EXIT_MESSAGE : str = "Usage: python vmtranslator.py <file.vm or directory>"
# TODO: add error checking to catch overflow of memory segments

def main():
    # Check correct usage
    if len(sys.argv) == 1:
        sys.argv[1] = os.getcwd()
    if len(sys.argv) > 2:
        print("Too many arguments arguments")
        sys.exit(EXIT_MESSAGE)

    basename : str = os.path.splitext(os.path.basename(sys.argv[1]))[0]
    is_dir = False
    if os.path.isfile(sys.argv[1]):
        # Make a list of filenames to drive the translation loop
        files = [basename]
        out_file_name = os.path.splitext(sys.argv[1])[0] + ".asm"
        # TODO: check that file is a .vm file
    elif os.path.isdir(sys.argv[1]):
        is_dir = True
        # Make a list of filenames to drive the translation loop
        files = [os.path.splitext(fname)[0] for fname in os.listdir(sys.argv[1]) if ".vm" in fname]
        # The output file when the arg is a directory is ./dirpath/.../topdirname/topdirname.asm
        if len(files) == 0:
            print("No .vm files were found in the target directory")
            sys.exit(EXIT_MESSAGE)
        out_file_name = os.path.join(sys.argv[1], basename + ".asm")
    else:
        print("Not a valid file or directory path")
        sys.exit(EXIT_MESSAGE)

    # Instantiate codewriter without a filename - will use new file method to
    # update filename before writing code
    my_codewriter = codewriter.CodeWriter(verbose_flag=True)

    # Translate and write into a .asm file
    with open(out_file_name, "w") as out:
        # TODO: Add bootstrap code (not yet implemented)
        # out.write(my_codewriter.bootstrap())
        # gor each new file instantiate a new parser and set the codewriter to the new filename
        for file in files:
            if is_dir:
                in_file = os.path.join(sys.argv[1], file + ".vm")
            else:
                in_file = os.path.join(os.path.dirname(sys.argv[1]), file + ".vm")
            my_parser = parser.Parser(in_file)
            my_codewriter.new_file(file)
            while my_parser.advance():
                out.write(my_codewriter.translate(my_parser.op, my_parser.arg1, my_parser.arg2))
                print(my_codewriter.translate(my_parser.op, my_parser.arg1, my_parser.arg2), end="")
        out.write(my_codewriter.close())
        print(my_codewriter.close(), end="")

if __name__ == '__main__':
    main()