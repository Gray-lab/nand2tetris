import re
import string
from typing import Generator, Iterator
from collections import deque

KEYWORDS = set(['class', 'constructor', 'function', 'method', 'field', 'static',
               'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null',
               'this', 'let', 'do', 'if', 'else', 'while', 'return'])
SYMBOLS = set(['{', '}', '(', ')', '[', ']', '.', ',', ';', '+',
              '-', '*', '/', '&', '|', '<', '>', '=', '~'])
DIGITS = set(list(string.digits))
IDENTIFIER_START = set(list(string.ascii_letters)).union(set(['-']))
IDENTIFIER_BODY = IDENTIFIER_START.union(DIGITS)

# Integers: Only token that begins with a digit. In the range 0 ... 32767
# String constant: any sequence of characters except /n and " enclosed in ""
# Identifier: any sequence of letters, digits and _ not starting with a digit
# Comments and whitespace are ignored.
# Line comment: //
# Block comment: /* ... */
# API documentation comment (basically same as block comment): /** ... */

class Token:
  def __init__ (self, type, value):
    self.type = type
    self.value = value

  def __eq__(self, other):
    if isinstance(other, Token):
      return self.value ==  other.value and self.type == other.type
    return False


class Tokenizer:
  def __init__ (self, in_file: str) -> None:
    self.text = self.strip_comments(in_file)


  def strip_comments(self, filename: str) -> deque:
    """
    Removes line comments, empty rows, and newlines from each row, appending them to one another
    Returns a deque of individual characters
    """
    with open(filename) as file:
      # Remove line comments and white space
      valid_rows = (row.partition("//")[0].strip() for row in file)
      # Remove empty rows
      valid_rows = (row for row in valid_rows if row)
      source=""
      for row in valid_rows:
        # Remove newline and append row
        source += row.strip('\n')
      # Remove block comments from the source string
      # Adapted from https://leetcode.com/problems/remove-comments/discuss/109195/1-liners
      clean_source = deque()
      for ch in filter(None, re.sub('/\*(.|\n)*?\*/', '', source)):
        clean_source.append(ch)
      return clean_source


  def get_token(self):
    """
    Generator which yields tokens of the form (type, token)
    while the text is not empty
    """
    text = self.text
    consume_flag = False
    ch = text.popleft()
    while text:
      # If looping from a keyword, identifier, or literal don't consume another character
      if consume_flag:
        ch = text.popleft()
      else:
        consume_flag = True

      if ch == " ":
        continue

      elif ch in SYMBOLS:
        token = Token('symbol', ch)
        yield token

      elif ch in DIGITS:
        int_lit = ""
        while ch in DIGITS:
          int_lit += ch
          ch = text.popleft()
        consume_flag = False
        yield Token("integerConstant", int_lit)

      elif ch in IDENTIFIER_START:
        word = ""
        while ch in IDENTIFIER_BODY:
          word += ch
          ch = text.popleft()
        consume_flag = False
        if word in KEYWORDS:
          yield Token("keyword", word)
        else:
          yield Token("identifier", word)

      elif ch == '"':
        ch = text.popleft()
        string_lit = ""
        while ch != '"':
          string_lit += ch
          ch = text.popleft()
        yield Token("stringConstant", string_lit)

      else:
        print("something broke with character", ch)
