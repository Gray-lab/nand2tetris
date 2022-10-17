

# Jack Grammar (^element indicates elements that need to be explicitly tagged in XML output)
# =====================================================================================================================================================
# Lexical elements (tokens from tokenizer)
#   keyword
#   symbol
#   integerConstant
#   stringConstant
#   identifier
# -----------------------------------------------------------------------------------------------------------------------------------------------------
# Program structure
#  ^class (C):              'class' className '{' classVarDec* subroutineDec* '}'
#  ^classVarDec (CVD):      ('static'|'field') type varName(',' varName)* ';'
#   type (TY):               'int' | 'char' | 'boolean' className
#  ^subroutineDec (SD):     ('constructor'|'function'|'method') ('void'|type) subroutineName '('parameterList')' subroutineBody
#  ^parameterList (PL):     ((type varName)) (',' type varName)*?
#  ^subroutineBody (SB):    '{'varDec* statements'}'
#  ^varDec (VD):            'var' type varName(',' varName)* ';'
#   className (cn):         identifier
#   subroutineName (sn):    identifier
#   varName (vn):           identifier
# -----------------------------------------------------------------------------------------------------------------------------------------------------
# Statements
#  ^statements (SS):       statement*
#   statement (S):         letStatement | ifStatement | whileStatement | doStatement | returnStatement    **handle in compileStatements
#  ^letStatement (LS):     'let' varName ('['expression']')? '=' expression ';'
#  ^ifStatement (IS):      'if' '('expression')' '{'statements'}'('else' '{'statements'}')?
#  ^whileStatement (WS):   'while' '('expression')' '{'statements'}' 
#  ^returnStatement (RS):  'return' expression? ';'
#  ^doStatement (DS):      'do' subroutineCall ';'                                                        **recommended to parse this as 'do' expression ';' 
# -----------------------------------------------------------------------------------------------------------------------------------------------------
# Expressions
#  ^expression (E):        term (op term)*
#  ^term (TR):             integerConstant|stringConstant|keywordConstant|varName|varName'['expression']'|'('expression')'|(unaryOp term)|subroutineCall
#   subroutineCall (SC):   subroutineName'('expressionList')'|(className|varName)'.'subroutineName'('expressionList')'    **handle in compileTerm
#  ^expressionList (EL):   (expression(',' expression)*)?
#   op (op):               '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
#   unaryOp (uop):          '-' | '~'
#   keywordConstant (kc):  'true' | 'false' | 'null' | 'this'
# =====================================================================================================================================================



# Step 1: parse every element except Expressions and array Statements 
# Step 2: handle Expressions
# Step 3: handle Array oriented statements (whileStatement)

# Base case will be a terminal 
# If non-terminal, keep recursing until a terminal is reached

import jacktokenizer as jtk

KC = set(['true', 'false', 'null', 'this'])
OP = set(['+', '-', '*', '/', '&', '|', '<', '>', '='])
UOP = set(['-', '~'])

class CompilationEngine:
  """
  LL(2) parser. Frankly, we usually just need LL(1), but might as well make it LL(2) to deal with
  the few cases where we need that second token.
  """
  def __init__ (self, start_token: str, in_file: str, out_file: str) -> None:
    self.next_token1 = start_token;
    self.next_token2 = self.next_token;
    self.tokenizer = jtk.Tokenizer(in_file).get_token()

    with open(out_file, "w") as out:
      self.file = out

  def write_token_to_xml(self, token) -> None:
    """
    Replaces XML markup symbols with valid alternatives
    and writes the token to the output file
    """
    # Replace XML markup symbols with alternatives
    value = token.value
    ident = token.ident
    if value == '<':
      value = '&lt;'
    if value == '>':
      value = '&gt;'
    if value == '"':
      value = '&quot;'
    if value == '&':
      value = '&amp;'
    self.file.write(f"<{ident}> {value} </{ident}>\n")

  def get_next_token(self) -> None:
    """
    Loads the next token. Mutates the class state.
    """
    self.next_token1 = self.next_token2
    if self.tokenizer.hasNext():
      


  def process(self, token) -> None:
    """
    Process the current token. Raises a SyntaxError if token is not accepted.
    """
    if self.next_token == token:
      self.write_token_to_xml(token)
      self.get_next_token()
    else:
      self.file.write(f"Syntax error when parsing <{token.ident}> {token.value} </{token.ident}>\n")
      raise SyntaxError(f"Syntax error when parsing <{token.ident}> {token.value} </{token.ident}>")



  def compileClass(self):
    """
    class:'class' className '{' classVarDec* subroutineDec* '}'

    compileClass will always be the first function called. Since Jack requires that
    every file is a class, the class declaration is the root of the parse tree
    """
    if self.next_token.value != 'class':
      raise SyntaxError("File must begin with a class declaration") 
    else:

  def compileClassVarDec(self):
    raise NotImplementedError

  def compileSubroutine(self):
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