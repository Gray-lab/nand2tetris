
# Step 1: parse every element except Expressions and array Statements
# Step 2: handle Expressions
# Step 3: handle Array oriented statements (whileStatement)

# Base case will be a terminal
# If non-terminal, keep recursing until a terminal is reached

from jack_tokenizer import Tokenizer

KC = set(['true', 'false', 'null', 'this'])
OP = set(['+', '-', '*', '/', '&', '|', '<', '>', '='])
UOP = set(['-', '~'])


class CompilationEngine:
    """
    LL(2) parser. Frankly, we usually just need LL(1), but might as well make it LL(2) to deal with
    the few cases where we need that second token.
    """

    def __init__(self, in_file: str, out_file: str) -> None:
        self.token_gen = Tokenizer(in_file).get_token()
        self.current_token = None
        self.next_token = None
        # Load the first two tokens
        self.get_next_token()
        self.get_next_token()

        with open(out_file, "w") as out:
            self.file = out
            self.compileClass()

    def get_next_token(self) -> None:
        """
        Loads the next token. Mutates the class state.
        """
        self.current_token = self.next_token
        # Grab the new token
        try:
            self.next_token = next(self.token_gen)
        except (StopIteration):
            # if we run out of tokens we have reached the end of the file and compileClass will wrap up and return
            pass

    def process(self, token_label, token_val=[]) -> None:
        """
        Process the current token. Raises a SyntaxError if token is not accepted.
        """
        is_valid = False
        # check that token label is correct
        if token_label == self.current_token.label:
            if not token_val:
                is_valid = True
            else:
                # check that current token value matches one of the valid values
                for val in token_val:
                    if val == self.current_token.value:
                        is_valid = True

        if is_valid:
            self.file.write(str(self.current_token))
            self.get_next_token()
        else:
            raise SyntaxError(f"\n\
      expected: <{token_label}> {token_val} </{token_label}>\n\
      received: <{self.current_token.label}> {self.current_token.value} </{self.current_token.label}>")

    def compileType(self):
        """
        type (TY): int' | 'char' | 'boolean' | className
        """
        if self.current_token.label == 'keyword':
            self.process("keyword", ["int", "char", "boolean"])
        else:
            self.process("identifier", [])

    def compileClass(self):
        """
        class:'class' className '{' classVarDec* subroutineDec* '}'

        compileClass will always be the first function called. Since Jack requires that
        every file is a class, the class declaration is the root of the parse tree
        """
        self.file.write(f"<class>\n")
        self.process("keyword", ["class"])
        self.process("identifier", [])
        self.process("symbol", ["{"])
        while self.current_token.value in ["static", "field"]:
            self.compileClassVarDec()
        while self.current_token.value in ["constructor", "function", "method"]:
            self.compileSubroutine()
        self.process("symbol", ["}"])
        self.file.write(f"</class>\n")
        print("Finished!")

    def compileClassVarDec(self):
        """
        classVarDec (CVD):('static'|'field') type varName(',' varName)* ';'
        """
        self.file.write(f"<classVarDec>\n")
        # If we are here, we know that the next keyword should be either 'static' or 'field'
        self.process("keyword", ["static", "field"])
        self.compileType()
        self.process("identifier", [])
        while self.current_token.value != ";":
            self.process("symbol", [","])
            self.process("identifier", [])
        self.process("symbol", [";"])
        self.file.write(f"</classVarDec>\n")

    def compileSubroutine(self):
        """
        subroutineDec (SD):('constructor'|'function'|'method') ('void'|type) subroutineName '('parameterList')' subroutineBody
        """
        self.file.write(f"<subroutineDec>\n")
        # If we are here, we know that the next keyword should be either "constructor" or "function" or "method"
        self.process("keyword", ["constructor", "function", "method"])
        if self.current_token.value == 'void':
            self.process("keyword", ["void"])
        else:
            self.compileType()
        self.process("identifier", [])
        self.process("symbol", ["("])
        self.compileParameterList()
        self.process("symbol", [")"])
        self.compileSubroutineBody()
        self.file.write(f"</subroutineDec>\n")

    def compileParameterList(self):
        """
        parameterList (PL): ((type varName)) (',' type varName)*)?
        """
        self.file.write(f"<parameterList>\n")
        # End of parameter list is defined by a close paren
        if self.current_token.value != ')':
            self.compileType()
            self.process("identifier", [])
            while self.current_token.value != ')':
                self.process("symbol", [","])
                self.compileType()
                self.process("identifier", [])
        self.file.write(f"</parameterList>\n")

    def compileSubroutineBody(self):
        """
        subroutineBody (SB):'{'varDec* statements'}'
        """
        self.file.write(f"<subroutineBody>\n")
        self.process("symbol", ["{"])
        # Each variable declaration begins with "var". Intervening tokens will be consumed by compileVarDec
        while self.current_token.value == "var":
            self.compileVarDec()
        self.compileStatements()
        self.process("symbol", ["}"])
        self.file.write(f"</subroutineBody>\n")

    def compileVarDec(self):
        """
        varDec (VD):'var' type varName(',' varName)* ';'
        """
        self.file.write(f"<varDec>\n")
        self.process("keyword", ["var"])
        self.compileType()
        self.process("identifier", [])
        while self.current_token.value != ";":
            self.process("symbol", [","])
            self.process("identifier", [])
        self.process("symbol", ";")
        self.file.write(f"</varDec>\n")

    def compileStatements(self):
        """
        statements (SS): statement*
        statement (S): letStatement | ifStatement | whileStatement | doStatement | returnStatement
        """
        self.file.write(f"<statements>\n")
        while self.current_token.value in ["let", "if", "while", "do", "return"]:
            if self.current_token.value == "let":
                self.compileLet()
            if self.current_token.value == "if":
                self.compileIf()
            if self.current_token.value == "while":
                self.compileWhile()
            if self.current_token.value == "do":
                self.compileDo()
            if self.current_token.value == "return":
                self.compileReturn()
        self.file.write(f"</statements>\n")

    def compileLet(self):
        """
        letStatement (LS): 'let' varName ('['expression']')? '=' expression ';'
        """
        self.file.write(f"<letStatement>\n")
        self.process("keyword", ["let"])
        self.process("identifier", [])
        if self.current_token.value == "[":
            self.process("symbol", ["["])
            self.compileExpression()
            self.process("symbol", ["]"])
        self.process("symbol", ["="])
        self.compileExpression()
        self.process("symbol", [";"])
        self.file.write(f"</letStatement>\n")

    def compileIf(self):
        """
        ifStatement (IS): 'if' '('expression')' '{'statements'}'('else' '{'statements'}')?
        """
        self.file.write(f"<ifStatement>\n")
        self.process("keyword", ["if"])
        self.process("symbol", ["("])
        self.compileExpression()
        self.process("symbol", [")"])
        self.process("symbol", ["{"])
        self.compileStatements()
        self.process("symbol", ["}"])
        if self.current_token.value == "else":
            self.process("keyword", ["else"])
            self.process("symbol", ["{"])
            self.compileStatements()
            self.process("symbol", ["}"])
        self.file.write(f"</ifStatement>\n")

    def compileWhile(self):
        """
        whileStatement (WS): 'while' '('expression')' '{'statements'}'
        """
        self.file.write(f"<whileStatement>\n")
        self.process("keyword", ["while"])
        self.process("symbol", ["("])
        self.compileExpression()
        self.process("symbol", [")"])
        self.process("symbol", ["{"])
        self.compileStatements()
        self.process("symbol", ["}"])
        self.file.write(f"</whileStatement>\n")

    def compileDo(self):
        """
        doStatement (DS): 'do' subroutineCall ';'
        """
        self.file.write(f"<doStatement>\n")
        self.process("keyword", ["do"])
        self.compileSubroutineCall()
        self.process("symbol", [";"])
        self.file.write(f"</doStatement>\n")

    def compileReturn(self):
        """
        returnStatement (RS): 'return' expression? ';'
        """
        self.file.write(f"<returnStatement>\n")
        self.process("keyword", ["return"])
        if self.current_token.value != ";":
            self.compileExpression()
        self.process("symbol", [";"])
        self.file.write(f"</returnStatement>\n")

    def compileExpression(self):
        """
        expression (E): term (op term)*
        """
        self.file.write(f"<expression>\n")
        self.compileTerm()
        while self.current_token.value in OP:
            self.process("symbol", OP)
            self.compileTerm()
        self.file.write(f"</expression>\n")

    def compileTerm(self):
        """
        term (TR): integerConstant|stringConstant|keywordConstant|varName|varName
                   '['expression']'|'('expression')'|(unaryOp term)|subroutineCall
        """
        # requires two term lookahead if the current token is an identifier
        # second term resoves the identifier into a
        # variable (second term = '.')
        # array element (second term = '[')
        # or a subroutineCall (second temr = '(')
        self.file.write(f"<term>\n")

        if self.current_token.label == "integerConstant":
            self.process("integerConstant", [])

        elif self.current_token.label == "stringConstant":
            self.process("stringConstant", [])

        elif self.current_token.value in KC:
            self.process("keyword", KC)

        elif self.current_token.value in UOP:
            self.process("symbol", UOP)
            self.compileTerm()

        elif self.current_token.value == "(":
            self.process("symbol", ["("])
            self.compileExpression()
            self.process("symbol", [")"])

        # the next 4 cases require LL(2)
        elif self.current_token.label == "identifier":
            if self.next_token.value == "[":
                # varname '['expression']'
                self.process("identifier", [])
                self.process("symbol", ["["])
                self.compileExpression()
                self.process("symbol", ["]"])
            elif self.next_token.value in ["(", "."]:
                # subroutineCall
                self.compileSubroutineCall()
            else:
                # varname
                self.process("identifier", [])

        else:
            print("Something broke in compileTerm main branch")
            self.file.write("Something broke in compileTerm main branch")

        # This is temporary for partial testing before implementing expressions
        # if self.current_token.label == "identifier":
        #   self.process("identifier", [])
        # elif self.current_token.value in KC:
        #   self.process("keyword", KC)
        self.file.write(f"</term>\n")

    def compileSubroutineCall(self):
        """
        subroutineCall (SC): subroutineName'('expressionList')'|
                             (className|varName)'.'subroutineName'('expressionList')'
        """
        self.process("identifier", [])
        if self.current_token.value == "(":
            self.process("symbol", ["("])
            self.compileExpressionList()
            self.process("symbol", [")"])
        elif self.current_token.value == ".":
            self.process("symbol", ["."])
            self.process("identifier", [])
            self.process("symbol", ["("])
            self.compileExpressionList()
            self.process("symbol", [")"])
        else:
            print("Something broke in compileSubroutineCall")
            self.file.write("Something broke in compileSubroutineCall")

    def compileExpressionList(self) -> int:
        """
        expressionList (EL): (expression(',' expression)*)?
        Returns count of expressions
        """
        self.file.write(f"<expressionList>\n")
        # End of parameter list is defined by a close paren
        if self.current_token.value != ')':
            self.compileExpression()
            while self.current_token.value != ')':
                self.process("symbol", [","])
                self.compileExpression()
        self.file.write(f"</expressionList>\n")
