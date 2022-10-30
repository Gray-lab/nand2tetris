
# Step 1: parse every element except Expressions and array Statements
# Step 2: handle Expressions
# Step 3: handle Array oriented statements (whileStatement)

# Base case will be a terminal
# If non-terminal, keep recursing until a terminal is reached

import string
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
        self.current_subroutine_kind = None
        self.current_subroutine_type = None
        self.symbol_name = None
        self.symbol_type = None     # int | bool | char | className
        self.symbol_kind = None     # static or field for class variables, var or arg for subroutine
        self.symbol_category = None # field | static | var | arg | class | subroutine
        self.symbol_usage = None    # declared (in var declaration) | used (in expression)
        self.if_label_counter = 0
        self.while_label_counter = 0
        self.num_fields = 0

        with open(out_file, "w") as out:
            self.file = out
            # Initialize compilation
            self.compile_class()

        # print("Class symbol table:")
        # print(self.class_table)

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

        if token_label == self.current_token.label:
            if not token_val:
                is_valid = True
            else:
                # check that current token value matches one of the valid values
                for val in token_val:
                    if val == self.current_token.value:
                        is_valid = True

        if is_valid:
            # if self.current_token.label == "identifier":
                # self.write_identifier_token()
            # else:
                # self.file.write(str(self.current_token))
            self.get_next_token()
        else:
            raise SyntaxError(f"\n\
                expected: <{token_label}> {token_val} </{token_label}>\n\
                received: <{self.current_token.label}> {self.current_token.value} </{self.current_token.label}>")

    def compile_type(self):
        """
        type (TY): 'int' | 'char' | 'boolean' | className
        """
        if self.current_token.label == 'keyword':
            self.process("keyword", ["int", "char", "boolean"])
        else:
            self.process("identifier", [])

    def compile_class(self): #set class name
        """
        class:'class' className '{' classVarDec* subroutineDec* '}'

        compileClass will always be the first function called. Since Jack requires that
        every file is a class, the class declaration is the root of the parse tree
        """
        # self.file.write(f"<class>\n")
        self.process("keyword", ["class"])

        #====Set class name====#
        self.current_class = self.current_token.value
        self.symbol_category = "class definition"
        self.symbol_usage = "declaration"

        self.process("identifier", [])
        self.process("symbol", ["{"])
        while self.current_token.value in ["static", "field"]:
            self.compile_class_var_dec()
        while self.current_token.value in ["constructor", "function", "method"]:
            self.compile_subroutine()
        self.process("symbol", ["}"])
        # self.file.write(f"</class>\n")
        print("Finished!")

    def compile_class_var_dec(self): #declare static or field variables
        """
        classVarDec (CVD):('static'|'field') type varName(',' varName)* ';'
        """       
        #====Get kind of variable (static or field)====#
        self.num_fields = 0
        self.symbol_category = self.current_token.value
        if self.symbol_category == "static":
            self.symbol_kind = "static"
        if self.symbol_category == "field":
            self.num_fields += 1
            self.symbol_kind = "this"
        self.symbol_usage = "declaration"
        self.process("keyword", ["static", "field"])

        #====Get type of variable====#
        self.symbol_type = self.current_token.value
        self.compile_type()

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

    def compile_subroutine(self): #set subroutine name, if method: this->arg0
        """
        subroutineDec (SD):('constructor'|'function'|'method') ('void'|type) subroutineName '('parameterList')' subroutineBody
        """
        
        # self.file.write(f"<subroutineDec>\n")

        #====Reset subroutine table====#
        self.subroutine_table.reset()
        
        #====Get subroutine kind====#
        self.current_subroutine_kind = self.current_token.value

        self.process("keyword", ["constructor", "function", "method"])

        #====Get subroutine type====#
        # Will be either "void, int, char, boolean, or className"
        self.current_subroutine_type = self.current_token.value

        if self.current_token.value == 'void':
            self.process("keyword", ["void"])
        else:
            self.compile_type()
        
        #====Set subroutine name====#
        self.current_subroutine = self.current_token.value

        #====Add method object to subroutine symbol table if it is a method====#
        if self.current_subroutine_kind == "method":
            self.symbol_usage = "declaration"
            self.subroutine_table.define("this", self.current_subroutine_type, "argument")
        
        self.process("identifier", [])
        self.process("symbol", ["("])
        self.compile_parameter_list()
        self.process("symbol", [")"])
        self.compile_subroutine_body()
        # self.file.write(f"</subroutineDec>\n")
        #=====Debugging print of subroutine table====#
        print(f"Subroutine symbol table at subroutine:{self.current_class}.{self.current_subroutine}")
        print(self.subroutine_table)

    def compile_parameter_list(self): #declare args
        """
        parameterList (PL): ((type varName)) (',' type varName)*)?
        """
        # self.file.write(f"<parameterList>\n")

        # End of parameter list is defined by a close paren
        if self.current_token.value != ')':
            #====Get symbol kind====#
            self.symbol_kind = "argument"
            self.symbol_category = "argument"
            self.symbol_usage = "declaration"

            #====Get symbol type====#
            self.symbol_type = self.current_token.value
            self.compile_type()

            #====Get symbol name and add to subroutine table====#
            self.symbol_name = self.current_token.value
            self.subroutine_table.define(self.symbol_name, self.symbol_type, self.symbol_kind)
            self.process("identifier", [])
            while self.current_token.value != ')':
                self.process("symbol", [","])

                #====Get symbol type====#
                self.symbol_type = self.current_token.value
                self.compile_type()

                #====Get symbol name and add to subroutine table====#
                self.symbol_name = self.current_token.value
                self.subroutine_table.define(self.symbol_name, self.symbol_type, self.symbol_kind)

                self.process("identifier", [])
        # self.file.write(f"</parameterList>\n")

    def compile_subroutine_body(self): #no symbols
        """
        subroutineBody (SB):'{'varDec* statements'}'
        """

        self.process("symbol", ["{"])

        num_vars = 0
        # Each variable declaration begins with "var". Intervening tokens will be consumed by compileVarDec
        while self.current_token.value == "var":
            num_vars += 1
            self.compile_var_dec()
        
        ### Start writing subroutine VM code ###
        self.file.write(vm_writer.function(f"{self.current_class}.{self.current_subroutine}", num_vars))
        if self.current_subroutine_kind == "method":
            self.file.write(vm_writer.push("argument", 0))
            self.file.write(vm_writer.pop("pointer", 0))
        if self.current_subroutine_kind == "constructor":
            self.file.write(vm_writer.push("constant", self.num_fields))
            self.file.write("call Memory.alloc 1\n")
            self.file.write(vm_writer.pop("pointer", 0))

            
        self.compile_statements()
        self.process("symbol", ["}"])
        if self.current_subroutine_kind in ["method", "function"] and self.current_subroutine_type == "void":
            self.file.write(vm_writer.push("constant", 0))
        if self.current_subroutine_kind == "constructor":
            self.file.write(vm_writer.push("pointer", 0))

    def compile_var_dec(self): #declare vars
        """
        varDec (VD):'var' type varName(',' varName)* ';'
        """
        #====Get symbol kind====#
        self.symbol_kind = "local"
        self.symbol_category = "var"
        self.symbol_usage = "declaration"
        self.process("keyword", ["var"])

        #====Get symbol type====#
        self.symbol_type = self.current_token.value
        self.compile_type()

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

    def compile_statements(self): #no symbols
        """
        statements (SS): statement*
        statement (S): letStatement | ifStatement | whileStatement | doStatement | returnStatement
        """
        while self.current_token.value in ["let", "if", "while", "do", "return"]:
            if self.current_token.value == "let":
                self.compile_let()
            if self.current_token.value == "if":
                self.compile_if()
            if self.current_token.value == "while":
                self.compile_while()
            if self.current_token.value == "do":
                self.compile_do()
            if self.current_token.value == "return":
                self.compile_return()

    def compile_let(self): #call variables
        """
        letStatement (LS): 'let' varName ('['expression']')? '=' expression ';'
        """

        self.process("keyword", ["let"])
        variable = self.current_token.value
        table = self.get_symbol_table(variable)  
        self.process("identifier", [])
        if self.current_token.value == "[":       
            # Handle case of varName[expression] = expression;
            ### push arr ###                                                                           
            self.file.write(vm_writer.push(table.kind_of(variable), table.index_of(variable)))

            self.process("symbol", ["["])
            self.compile_expression()
            self.process("symbol", ["]"])

            self.file.write("add\n")
            
            self.process("symbol", ["="])
            self.compile_expression()
            self.process("symbol", [";"])
            # Pop expression which will be bound to arr[exp], saving it to temp 0
            self.file.write(vm_writer.pop("temp", 0))

            # Move value at temp 0 to mem address arr[exp]
            self.file.write(vm_writer.pop("pointer", 1))
            self.file.write(vm_writer.push("temp", 0))
            self.file.write(vm_writer.pop("that", 0))
        
        else:
            # Handle case of varName = expression;
            self.process("symbol", ["="])
            self.compile_expression()
            self.process("symbol", [";"])
            self.file.write(vm_writer.pop(table.kind_of(variable), table.index_of(variable)))

    def compile_if(self): #no symbols
        """
        ifStatement (IS): 'if' '('expression')' '{'statements'}'('else' '{'statements'}')?
        """
        self.process("keyword", ["if"])
        self.process("symbol", ["("])
        self.compile_expression()
        self.process("symbol", [")"])
        
        # Get labels
        label1 = self.get_if_label()
        label2 = self.get_if_label()
        
        # Invert the value of the evaluated expression
        self.file.write("//compiling if, before not\n")
        self.file.write("not\n")
        # If if expression was false, this if_goto will be triggered
        self.file.write(vm_writer.if_goto(label1))

        self.process("symbol", ["{"])
        self.compile_statements()
        self.process("symbol", ["}"])

        # Goto for skipping else statement
        self.file.write(vm_writer.goto(label2))

        # Label for skipping if statement
        self.file.write(vm_writer.label(label1))

        if self.current_token.value == "else":
            self.process("keyword", ["else"])
            self.process("symbol", ["{"])
            self.compile_statements()
            self.process("symbol", ["}"])

        # Label for skipping else statement
        self.file.write(vm_writer.label(label2))

    def compile_while(self): #no symbols
        """
        whileStatement (WS): 'while' '('expression')' '{'statements'}'
        """
        # Get labels
        label1 = self.get_while_label()
        label2 = self.get_while_label()

        self.file.write(vm_writer.label(label1))

        self.process("keyword", ["while"])
        self.process("symbol", ["("])
        self.compile_expression()
        self.process("symbol", [")"])

        self.file.write("not\n")
        self.file.write(vm_writer.if_goto(label2))

        self.process("symbol", ["{"])
        self.compile_statements()
        self.process("symbol", ["}"])

        self.file.write(vm_writer.goto(label1))
        self.file.write(vm_writer.label(label2))

    def compile_do(self): #no symbols
        """
        doStatement (DS): 'do' subroutineCall ';'
        """
        self.process("keyword", ["do"])
        self.compile_subroutine_call()
        self.process("symbol", [";"])

        # When compiling do statements, the return value must be removed from the stack
        self.file.write(vm_writer.pop("temp", "0"))

    def compile_return(self): #no symbols
        """
        returnStatement (RS): 'return' expression? ';'
        """
        self.file.write(vm_writer.return_statement())

        self.process("keyword", ["return"])
        if self.current_token.value != ";":
            self.compile_expression()
        self.process("symbol", [";"])

    def compile_expression(self): #no symbols
        """
        expression (E): term (op term)*
        """
        self.compile_term()
        while self.current_token.value in OP:
            operator = self.current_token.value
            self.process("symbol", OP)
            self.compile_term()
            self.file.write(vm_writer.binary_arithmetic(operator))

    def compile_term(self): #call variable
        """
        term (TR): integerConstant|stringConstant|keywordConstant|varName|varName
                   '['expression']'|'('expression')'|(unaryOp term)|subroutineCall
        """
        # requires two term lookahead if the current token is an identifier
        # second term resoves the identifier into a
        # variable (second term = '.')
        # array element (second term = '[')
        # or a subroutineCall (second temr = '(')

        if self.current_token.label == "integerConstant":
            integer_constant = self.current_token.value
            self.file.write(vm_writer.push("constant", integer_constant))
            self.process("integerConstant", [])

        elif self.current_token.label == "stringConstant":
            string_constant = self.current_token.value
            self.file.write(vm_writer.push("constant", len(string_constant)))
            self.file.write(vm_writer.call("String.new", 1))
            for ch in string_constant:
                if ord(ch) < 32 or ord(ch) > 128:
                    raise SyntaxError("Invalid string character in string literal")
                self.file.write(vm_writer.push("constant", ord(ch)))
                self.file.write(vm_writer.call("String.appendChar", 2))
            
            # Push result to stack? -> no need, done by String.appendChar
            self.process("stringConstant", [])

        elif self.current_token.value in KC:
            keyword = self.current_token.value
            # This should get factored out to the vm writer
            match keyword:
                case "true":
                    # Push -1 to stack
                    self.file.write(vm_writer.push("constant", 1))
                    self.file.write("neg\n")
                case "this":
                    # Push pointer 0 to stack
                    self.file.write(vm_writer.push("pointer", 0))
                case other:
                    # null | false
                    self.file.write(vm_writer.push("constant", 0))
            self.process("keyword", KC)

        elif self.current_token.value in UOP:
            unary_operator = self.current_token.value
            self.process("symbol", UOP)
            self.compile_term()
            self.file.write(vm_writer.unary_arithmetic(unary_operator))

        elif self.current_token.value == "(":
            self.process("symbol", ["("])
            self.compile_expression()
            self.process("symbol", [")"])

        # the next 3 cases require LL(2)
        elif self.current_token.label == "identifier":
            
            if self.next_token.value == "[":
                # Array
                # varname '['expression']'
                ### push arr ###
                arr = self.current_token.value
                table = self.get_symbol_table(arr)                                                                               
                self.file.write(vm_writer.push(table.kind_of(arr), table.index_of(arr)))

                self.process("identifier", [])
                self.process("symbol", ["["])
                self.compile_expression()
                # value of [expression] is at top of stack now
                # add (adds arr + expression)
                self.file.write("add\n")
                # pop pointer 1
                self.file.write(vm_writer.pop("pointer", 1))
                # push that 0
                self.file.write(vm_writer.push("that", 0))

                self.process("symbol", ["]"])
            
            elif self.next_token.value in ["(", "."]:
                # subroutineCall
                self.compile_subroutine_call()

            else:
                ### push variable ###
                arr = self.current_token.value
                table = self.get_symbol_table(arr)                                                                               
                self.file.write(vm_writer.push(table.kind_of(arr), table.index_of(arr)))

                self.process("identifier", [])

        else:
            self.file.write("Something broke in compileTerm main branch")

    def compile_subroutine_call(self): #call function or method
        """
        subroutineCall (SC): subroutineName'('expressionList')'|
                             (className|varName)'.'subroutineName'('expressionList')'
        """
        # How do we know whether we are calling a function or a method?

        if self.next_token.value == "(":
            module_name = self.current_class
            subroutine_name = self.current_token.value
            self.process("identifier", [])
            self.process("symbol", ["("])
            num_args = self.compile_expression_list()
            self.process("symbol", [")"])
        elif self.next_token.value == ".":

            # We need to decide whether we are calling a method or a function/constructor
            # If the identifier is in the symbol tables then we know we are calling on
            # an object. Otherwise, it is a module call. 
            module_name = self.current_token.value
            method_flag = False
            if module_name in self.subroutine_table or module_name in self.class_table:
                method_flag = True

            self.process("identifier", [])
            self.process("symbol", ["."])
            subroutine_name = self.current_token.value
            self.process("identifier", [])
            self.process("symbol", ["("])
            num_args = self.compile_expression_list()
            if method_flag:
                # If method, we add one argument for the object
                num_args += 1
            
            self.process("symbol", [")"])
        else:
            self.file.write("Something broke in compileSubroutineCall")

            
        self.file.write(vm_writer.call(f"{module_name}.{subroutine_name}", num_args))

    def compile_expression_list(self) -> int: #no symbols
        """
        expressionList (EL): (expression(',' expression)*)?
        Returns count of expressions
        """
        expression_count = 0
        # self.file.write(f"<expressionList>\n")
        # End of parameter list is defined by a close paren
        if self.current_token.value != ')':
            self.compile_expression()
            expression_count += 1
            while self.current_token.value != ')':
                self.process("symbol", [","])
                self.compile_expression()
                expression_count += 1
        # self.file.write(f"</expressionList>\n")
        return expression_count

    def get_symbol_table(self, symbol: str) -> SymbolTable:
        if symbol in self.subroutine_table:
            return self.subroutine_table
        elif symbol in self.class_table:
            return self.class_table
        else:
            raise SyntaxError(f"Variable {symbol} not found at symbol table")

    def get_if_label(self) -> str:
        label_val = self.if_label_counter
        self.if_label_counter += 1
        return f"IF{label_val}"

    def get_while_label(self) -> str:
        label_val = self.while_label_counter
        self.while_label_counter += 1
        return f"WHILE{label_val}"