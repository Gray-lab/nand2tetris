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
    segment_list = ["sp","local","argument", "this", "that", "static", "constant", "pointer", "temp"]

    #



if __name__ == '__main__':
    main()