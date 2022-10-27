
# Step 1: parse every element except Expressions and array Statements
# Step 2: handle Expressions
# Step 3: handle Array oriented statements (whileStatement)

# Base case will be a terminal
# If non-terminal, keep recursing until a terminal is reached

from jack_tokenizer import Tokenizer
from jack_token import Token
import vm_writer
from symbol_table import SymbolTable

KC = set(['true', 'false', 'null', 'this'])
OP = set(['+', '-', '*', '/', '&', '|', '<', '>', '='])
UOP = set(['-', '~'])

class CompilationEngine:
    """
    LL(2) parser. Frankly, we usually just need LL(1), but might as well make it LL(2) to deal with
    the few cases where we need that second token.
    """

    def __init__(self, in_file: str, out_file: str) -> None:
        self.token_gen = Tokenizer(in_file).get_token_generator()
        #self.writer = VMwriter(out_file)
        self.current_token = None
        self.next_token = None
        
        # Initialize the symbol tables
        self.class_table = SymbolTable()
        self.subroutine_table = SymbolTable()

        # Load the first two tokens
        self.get_next_token()
        self.get_next_token()

        # Initialize symbol state variables
        self.current_class = None
        self.current_subroutine = None
        self.symbol_name = None
        self.symbol_type = None     # int | bool | char | className
        self.symbol_kind = None     # static or field for class variables, var or arg for subroutine
        self.symbol_category = None # field | static | var | arg | class | subroutine
        self.symbol_usage = None    # declared (in var declaration) | used (in expression)

        with open(out_file, "w") as out:
            self.file = out
            # Initialize compilation
            self.compileClass()

        print("Class symbol table:")
        print(self.class_table)

    def get_next_token(self) -> None:
        """
        Loads the next token. Mutates the class state.
        """
        self.current_token = self.next_token
        # Grab the new token
        try:
            self.next_token = next(self.token_gen)
        except (StopIteration):
            # if we run out of tokens we have reached the end of the file and 
            # compileClass will wrap up and return
            pass

    def write_identifier_token(self):
        """
        Writes an identifier token using the following XML format:
        <identifier>
            <name> name </name>
            <type> type </type>
            <kind> kind </kind>
            <index> index </index>
        </identifier>
        """
        table = None
        var_name = self.current_token.value
        # method symbol name is 'this'
        if self.symbol_category == "method":
            var_name = self.symbol_name

        if var_name in self.subroutine_table:
            table = self.subroutine_table
            var_type = table.type_of(var_name)
            var_kind = table.kind_of(var_name)
            var_index = table.index_of(var_name)

        elif var_name in self.class_table:
            table = self.class_table
            var_type = table.type_of(var_name)
            var_kind = table.kind_of(var_name)
            var_index = table.index_of(var_name)
        
        else:
            var_type = "Not in symbol table"
            var_kind = "Not in symbol table"
            var_index = "Not in symbol table"
        

        ident_string = ("<identifier>\n"
                        f"\t<symbol name: {self.symbol_name} >\t<table name: {var_name} > \n"
                        f"\t<symbol type: {self.symbol_type} >\t<table type: {var_type} >\n"
                        f"\t<symbol kind: {self.symbol_kind} >\t<table kind: {var_kind} >\n"
                        f"\t<table index: {var_index} >\n"
                        f"\t<category: {self.symbol_category} >\n"
                        f"\t<usage: {self.symbol_usage} >\n"
                        "</identifier>")
        #print(ident_string)
        self.file.write(ident_string)

    def process(self, token_label, token_val=[]) -> None:
        """
        Process the current token. Raises a SyntaxError if token is not accepted.
        
        #===============================#
        # Naming: 
        # Xxx.jack is compiled to Xxx.vm
        # subroutine yyy in Xxx.jack is compiled into function Xxx.yyy

        #===============================#
        # Identifiers need to contain the following data:
        # name (value)
        # category (field|static|var|arg|class|subroutine)
        # index (only for field, static, var, arg variables - provided by symbol table)
        # usage (is it being declared(appears in static/field/var) or used(jack expression))
        # No need to track the class identifier, as it doesn't ever get called after the first time
        
        #===============================#
        # Memory Mapping
        # static vars: static 0, static 1,...
        # field vars: this 0, this 1,...
        # local vars: local 0, local 1, ...
        # argument var declared in function or constructor (not method): argument 0, argument 1,...
        # argument var declared in method: argument 1, argument 2,...   (arg 0 is the object?)
        # To align the virtual segment 'this' with object passed by the caller 
        # of a method, use VM commands: 'push argument 0', 'pop pointer 0'
        """

        is_valid = False
        # check that token label is correct
        #print(f"<{self.current_token.label}> {self.current_token.value} </{self.current_token.label}>")
        #print(f"<{token_label}> {token_val} </{token_label}>")
        if token_label == self.current_token.label:
            if not token_val:
                is_valid = True
            else:
                # check that current token value matches one of the valid values
                for val in token_val:
                    if val == self.current_token.value:
                        is_valid = True

        if is_valid:
            if self.current_token.label == "identifier":
                self.write_identifier_token()
            else:
                self.file.write(str(self.current_token))
            self.get_next_token()
        else:
            raise SyntaxError(f"\n\
                expected: <{token_label}> {token_val} </{token_label}>\n\
                received: <{self.current_token.label}> {self.current_token.value} </{self.current_token.label}>")

    def compileType(self):
        """
        type (TY): 'int' | 'char' | 'boolean' | className
        """
        if self.current_token.label == 'keyword':
            self.process("keyword", ["int", "char", "boolean"])
        else:
            self.process("identifier", [])

    def compileClass(self): #set class name
        """
        class:'class' className '{' classVarDec* subroutineDec* '}'

        compileClass will always be the first function called. Since Jack requires that
        every file is a class, the class declaration is the root of the parse tree
        """
        self.file.write(f"<class>\n")
        self.process("keyword", ["class"])

        #====Set class name====#
        self.current_class = self.current_token.value
        self.symbol_category = "class definition"
        self.symbol_usage = "declaration"

        self.process("identifier", [])
        self.process("symbol", ["{"])
        while self.current_token.value in ["static", "field"]:
            self.compileClassVarDec()
        while self.current_token.value in ["constructor", "function", "method"]:
            self.compileSubroutine()
        self.process("symbol", ["}"])
        self.file.write(f"</class>\n")
        print("Finished!")

    def compileClassVarDec(self): #declare static or field variables
        """
        classVarDec (CVD):('static'|'field') type varName(',' varName)* ';'

        Class variable declarations
        """
        self.file.write(f"<classVarDec>\n")
        
        #====Get kind of variable (static or field)====#
        self.symbol_category = self.current_token.value
        if self.symbol_category == "static":
            self.symbol_kind = "static"
        if self.symbol_category == "field":
            self.symbol_kind = "this"
        self.symbol_usage = "declaration"
        self.process("keyword", ["static", "field"])

        #====Get type of variable====#
        self.symbol_type = self.current_token.value
        self.compileType()

        #====Add class variable to class symbol table====#
        self.symbol_name = self.current_token.value
        self.class_table.define(self.symbol_name, self.symbol_type, self.symbol_kind)
        self.process("identifier", [])

        while self.current_token.value != ";":
            self.process("symbol", [","])

            #====Add class variable to class symbol table====#
            self.symbol_name = self.current_token.value
            self.class_table.define(self.symbol_name, self.symbol_type, self.symbol_kind)
            self.process("identifier", [])

        self.process("symbol", [";"])
        self.file.write(f"</classVarDec>\n")

    def compileSubroutine(self): #set subroutine name, if method: this->arg0
        """
        subroutineDec (SD):('constructor'|'function'|'method') ('void'|type) subroutineName '('parameterList')' subroutineBody
        """
        self.file.write(f"<subroutineDec>\n")

        #====Reset subroutine table====#
        self.subroutine_table.reset()
        
        #====Get subroutine kind====#
        self.symbol_category = self.current_token.value

        self.process("keyword", ["constructor", "function", "method"])

        #====Get subroutine type====#
        # Will be either "void, int, char, boolean, or className"
        self.symbol_type = self.current_token.value

        if self.current_token.value == 'void':
            self.process("keyword", ["void"])
        else:
            self.compileType()
        
        #====Set subroutine name====#
        self.current_subroutine  = self.current_token.value
        #====Add subroutine variable to subroutine symbol table if it is a method====#
        if self.symbol_category == "method":
            # Set kind to arg for method call so that 
            self.symbol_name  = "this"
            self.symbol_kind = "argument"
            self.symbol_usage = "declaration"
            self.subroutine_table.define(self.symbol_name, self.symbol_type, self.symbol_kind)
        
        self.process("identifier", [])
        self.process("symbol", ["("])
        self.compileParameterList()
        self.process("symbol", [")"])
        self.compileSubroutineBody()
        self.file.write(f"</subroutineDec>\n")
        #=====Debugging print of subroutine table====#
        print(f"Subroutine symbol table at subroutine:{self.current_class}.{self.current_subroutine}")
        print(self.subroutine_table)

    def compileParameterList(self): #declare args
        """
        parameterList (PL): ((type varName)) (',' type varName)*)?
        """
        self.file.write(f"<parameterList>\n")

        # End of parameter list is defined by a close paren
        if self.current_token.value != ')':
            #====Get symbol kind====#
            self.symbol_kind = "argument"
            self.symbol_category = "argument"
            self.symbol_usage = "declaration"

            #====Get symbol type====#
            self.symbol_type = self.current_token.value
            self.compileType()

            #====Get symbol name and add to subroutine table====#
            self.symbol_name = self.current_token.value
            self.subroutine_table.define(self.symbol_name, self.symbol_type, self.symbol_kind)
            self.process("identifier", [])
            while self.current_token.value != ')':
                self.process("symbol", [","])

                #====Get symbol type====#
                self.symbol_type = self.current_token.value
                self.compileType()

                #====Get symbol name and add to subroutine table====#
                self.symbol_name = self.current_token.value
                self.subroutine_table.define(self.symbol_name, self.symbol_type, self.symbol_kind)

                self.process("identifier", [])

        self.file.write(f"</parameterList>\n")

    def compileSubroutineBody(self): #no symbols
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

    def compileVarDec(self): #declare vars
        """
        varDec (VD):'var' type varName(',' varName)* ';'
        """
        self.file.write(f"<varDec>\n")
        #====Get symbol kind====#
        self.symbol_kind = "local"
        self.symbol_category = "var"
        self.symbol_usage = "declaration"
        self.process("keyword", ["var"])

        #====Get symbol type====#
        self.symbol_type = self.current_token.value
        self.compileType()

        #====Get symbol name and add to subroutine table====#
        self.symbol_name = self.current_token.value
        self.subroutine_table.define(self.symbol_name, self.symbol_type, self.symbol_kind)

        self.process("identifier", [])
        while self.current_token.value != ";":
            self.process("symbol", [","])

            #====Get symbol name and add to subroutine table====#
            self.symbol_name = self.current_token.value
            self.subroutine_table.define(self.symbol_name, self.symbol_type, self.symbol_kind)

            self.process("identifier", [])
        self.process("symbol", ";")
        self.file.write(f"</varDec>\n")

    def compileStatements(self): #no symbols
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

    def compileLet(self): #call variables
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

    def compileIf(self): #no symbols
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

    def compileWhile(self): #no symbols
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

    def compileDo(self): #no symbols
        """
        doStatement (DS): 'do' subroutineCall ';'
        """
        self.file.write(f"<doStatement>\n")
        self.process("keyword", ["do"])
        self.compileSubroutineCall()
        self.process("symbol", [";"])
        self.file.write(f"</doStatement>\n")

    def compileReturn(self): #no symbols
        """
        returnStatement (RS): 'return' expression? ';'
        """
        self.file.write(f"<returnStatement>\n")
        self.process("keyword", ["return"])
        if self.current_token.value != ";":
            self.compileExpression()
        self.process("symbol", [";"])
        self.file.write(f"</returnStatement>\n")

    def compileExpression(self): #no symbols
        """
        expression (E): term (op term)*
        """
        self.file.write(f"<expression>\n")
        self.compileTerm()
        while self.current_token.value in OP:
            self.process("symbol", OP)
            self.compileTerm()
        self.file.write(f"</expression>\n")

    def compileTerm(self): #call variable
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
            self.file.write("Something broke in compileTerm main branch")

        # This is temporary for partial testing before implementing expressions
        # if self.current_token.label == "identifier":
        #   self.process("identifier", [])
        # elif self.current_token.value in KC:
        #   self.process("keyword", KC)
        self.file.write(f"</term>\n")

    def compileSubroutineCall(self): #call function or method
        """
        subroutineCall (SC): subroutineName'('expressionList')'|
                             (className|varName)'.'subroutineName'('expressionList')'
        """
        # do 2 token lookead to decide whether we are calling a method or a function

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
            self.file.write("Something broke in compileSubroutineCall")

    def compileExpressionList(self) -> int: #no symbols
        """
        expressionList (EL): (expression(',' expression)*)?
        Returns count of expressions
        """
        expression_count = 0
        self.file.write(f"<expressionList>\n")
        # End of parameter list is defined by a close paren
        if self.current_token.value != ')':
            self.compileExpression()
            expression_count += 1
            while self.current_token.value != ')':
                self.process("symbol", [","])
                self.compileExpression()
                expression_count += 1
        self.file.write(f"</expressionList>\n")
        return expression_count

