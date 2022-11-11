import os
import sys
from typing import Tuple, List
from compilation_engine import CompilationEngine

EXIT_MESSAGE = "Usage: python jackanalyzer.py optional<file.jack or directory>"


def main():
    # Check correct usage
    if len(sys.argv) == 1:
        sys.argv[1] = os.getcwd()
    if len(sys.argv) > 2:
        print("Expected at most two arguments but received more than one")
        sys.exit(EXIT_MESSAGE)

    in_filenames, out_filenames = get_files_and_dir(sys.argv[1])
    for in_filename, out_filename in zip(in_filenames, out_filenames):
        # Making the compilation engine runs and outputs the file

        # It would be better to send the output back to this module to write it here
        CompilationEngine(in_filename, out_filename)

def get_files_and_dir(rel_path: str) -> Tuple[List[str], List[str]]:
    if os.path.isfile(rel_path) and ".jack" in rel_path:
        # If the argument is a file, we just make a list of one filename
        directory, fname = os.path.split(rel_path)
        filenames_in = [fname]
    elif os.path.isdir(rel_path):
        directory = rel_path
        # Make a list of filenames to drive the translation loop
        filenames_in = [(fname)
                        for fname in os.listdir(directory) if ".jack" in fname]
        if len(filenames_in) == 0:
            print("No .jack files were found in the target directory")
            sys.exit(EXIT_MESSAGE)
    else:
        print("Not a valid .jack file or directory path")
        sys.exit(EXIT_MESSAGE)

    filenames_out = [os.path.splitext(
        fname)[0] + ".vm" for fname in filenames_in]

    in_filenames = []
    out_filenames = []
    for file_in, file_out in zip(filenames_in, filenames_out):
        in_filenames.append(os.path.join(directory, file_in))
        out_filenames.append(os.path.join(directory, file_out))

    return in_filenames, out_filenames


if __name__ == '__main__':
    main()
