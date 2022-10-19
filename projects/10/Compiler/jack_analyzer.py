# Construct a tokenizer on a file

# Tokenizer should yield a tokenized line each time it is called

import os
import sys
from typing import Tuple, List
import jack_tokenizer as jtk

EXIT_MESSAGE = "Usage: python jackanalyzer.py optional<file.jack or directory>"

def main():
  # Check correct usage
  if len(sys.argv) == 1:
      sys.argv[1] = os.getcwd()
  if len(sys.argv) > 2:
      print("Expected at most two argumnets argument but received more than one")
      sys.exit(EXIT_MESSAGE)

  in_filenames, out_filenames = get_files_and_dir(sys.argv[1])
  for in_filename, out_filename in zip(in_filenames, out_filenames):
    with open(out_filename, "w") as out:
      tokenizer = jtk.Tokenizer(in_filename)

      # write tokens into an output file
      out.write("<tokens>\n")
      for token in tokenizer.get_token():
        out.write(write_token_to_xml(token.type, token.value))
      out.write("</tokens>\n")


def write_token_to_xml(type: str, token: str) -> str:
  # Replace XML markup symbols with alternatives
  if token == '<':
    token = '&lt;'
  if token == '>':
    token = '&gt;'
  if token == '"':
    token = '&quot;'
  if token == '&':
    token = '&amp;'
  return f"\t<{ident}> {token} </{ident}>\n"


def get_files_and_dir(rel_path: str) -> Tuple[List[str], List[str]]:
  if os.path.isfile(rel_path) and ".jack" in rel_path:
      # If the argument is a file, we just make a list of one filename
      directory, fname = os.path.split(rel_path)
      filenames_in = [fname]
  elif os.path.isdir(rel_path):
      directory = rel_path
      # Make a list of filenames to drive the translation loop
      filenames_in = [(fname) for fname in os.listdir(directory) if ".jack" in fname]
      if len(filenames_in) == 0:
          print("No .jack files were found in the target directory")
          sys.exit(EXIT_MESSAGE)
  else:
      print("Not a valid .jack file or directory path")
      sys.exit(EXIT_MESSAGE)

  filenames_out = [os.path.splitext(fname)[0] + "T.xml" for fname in filenames_in]

  in_filenames = []
  out_filenames = []
  for file_in, file_out in zip(filenames_in, filenames_out):
    in_filenames.append(os.path.join(directory, file_in))
    out_filenames.append(os.path.join(directory, file_out))

  return in_filenames, out_filenames


if __name__ == '__main__':
    main()
