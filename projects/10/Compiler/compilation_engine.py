
# Step 1: parse every element except Expressions and array Statements
# Step 2: handle Expressions
# Step 3: handle Array oriented statements (whileStatement)

# Base case will be a terminal
# If non-terminal, keep recursing until a terminal is reached

from jack_tokenizer import Token, Tokenizer
import sys

KC = set(['true', 'false', 'null', 'this'])
OP = set(['+', '-', '*', '/', '&', '|', '<', '>', '='])
UOP = set(['-', '~'])

class CompilationEngine:
  """
  LL(2) parser. Frankly, we usually just need LL(1), but might as well make it LL(2) to deal with
  the few cases where we need that second token.
  """
  def __init__ (self, start_token, in_file: str, out_file: str) -> None:
    self.current_token = start_token;
    self.next_token = self.get_next_token;
    self.token_gen = Tokenizer(in_file).get_token()

    with open(out_file, "w") as out:
      self.file = out

  def write_token_to_xml(self, token) -> None:
    """
    Replaces XML markup symbols with valid alternatives
    and writes the token to the output file
    """
    # Replace XML markup symbols with alternatives
    value = token.value
    type = token.type
    if value == '<':
      value = '&lt;'
    if value == '>':
      value = '&gt;'
    if value == '"':
      value = '&quot;'
    if value == '&':
      value = '&amp;'
    self.file.write(f"<{type}> {value} </{type}>\n")


  def get_next_token(self) -> None:
    """
    Loads the next token. Mutates the class state.
    """
    self.current_token = self.next_token
    # pull the new token
    # make sure we handle an exception if one might be raised by the token generator?
    # could use try - except
    try:
      self.next_token = next(self.token_gen)
    except (StopIteration):
      print("we triggered the exception")
      sys.exit("done")


  def process(self, token_id, token_val=[]) -> None:
    """
    Process the current token. Raises a SyntaxError if token is not accepted.
    """
    is_valid = False
    if token_id == 'keyword':
      if token_id == self.current_token.type:
        for val in token_val:
          if


    # elif token_id == 'identifier':
    #   pass

    else:
      if token_id == self.current_token.type:
        if not token_val:
          is_valid = True
        else:
          for val in token_val:
            if val == self.current_token.value:
              is_valid = True
              break

    if is_valid:
      self.write_token_to_xml(self.current_token)
      self.get_next_token()
    else:
      self.file.write(f"Syntax error when parsing <{self.current_token.type}> {self.current_token.value} </{self.current_token.type}>\n")
      raise SyntaxError(f"Syntax error when parsing <{self.current_token.type}> {self.current_token.value} </{self.current_token.type}>")


  def compileClass(self):
    """
    class:'class' className '{' classVarDec* subroutineDec* '}'

    compileClass will always be the first function called. Since Jack requires that
    every file is a class, the class declaration is the root of the parse tree
    """
    self.file.write(f"<class>\n")
    self.process("keyword", ["class"])
    self.process("identifier")
    self.process("symbol", ["{"])
    while self.current_token.value in ["static", "field"]:
      self.compileClassVarDec()
    while self.current_token.value in ["constructor", "function", "method"]:
      self.compileSubroutine()
    self.process("symbol", ["}"])
    self.file.write(f"</class>\n")

  def compileClassVarDec(self):
    """
    ^classVarDec (CVD):('static'|'field') type varName(',' varName)* ';'
    """
    self.file.write(f"<classVarDec>\n")
    self.process("keyword, ")
    self.process("keyword", ["int", "char", "boolean"])

    self.file.write(f"</classVarDec>\n")

  def compileSubroutine(self):
    """
    ^subroutineDec (SD):('constructor'|'function'|'method') ('void'|type) subroutineName '('parameterList')' subroutineBody
    """
    raise NotImplementedError

  def compileParameterList(self):
    raise NotImplementedError

  def compileSubroutineBody(self):
    raise NotImplementedError

  def compileVarDec(self):
    raise NotImplementedError

  def compileStatements(self):
    raise NotImplementedError

  def compileLet(self):
    raise NotImplementedError

  def compileIf(self):
    raise NotImplementedError

  def compileWhile(self):
    raise NotImplementedError

  def compileDo(self):
    raise NotImplementedError

  def compileReturn(self):
    raise NotImplementedError

  def compileExpression(self):
    raise NotImplementedError

  def compileTerm(self):
    # requires two term lookahead if the current token is an identifier
    # second term resoves the identifier into a
    # variable (second term = '.')
    # array element (second term = '[')
    # or a subroutineCall (second temr = '(')
    raise NotImplementedError

def compileExpressionList(self) -> int:
  """
  Returns count of expressions
  """
