from compiler.lexer import Lexer
from utils.constants import *
from utils.data_classes import *
from utils.errors import ParserError, ErrorCode


class Parser:
    """
    --------- GRAMMAR ---------------
    program: PROGRAM variable block
    block:  LCBRACE declarations compound_statement RCBRACE
    declarations:
        VAR (variable_declaration SEMI)+
        | FUNCTION ID (LPARENT formal_parameter_list RPARENT)? block
        | empty
    formal_parameter_list: formal_parameter (SEMI format_parameter)*
    format_parameter: ID (COMMA ID)* COLON base_type
    variable_declaration: ID (COMMA, ID)* COLON base_type (ASSIGN base_expr)?
    base_type: INTEGER | REAL | STRING | BOOLEAN | OBJECT
    compound_statement: statement_list
    statement_list: statement (SEMI statement)*
    statement: assignment_statement
        | function_call | return | declarations | if_statement | for_loop
        | empty | BREAK
    function_call: ID LPARENT (base_expr (COMMA base_expr)*)* RPARENT SEMI
    show_statement: SHOW LPARENT base_expr RPARENT SEMI
    while_loop: WHILE bool_expr DO block
    do_while_loop: DO block WHILE bool_expr
    empty:
    return: RETURN base_expr
    assignment_statement: variable ASSIGN base_expr
    base_expr: expr | str_expr | bool_expr
    bool_expr: bool_term ((OR, AND) bool_term)*
    bool_term: bool_factor ((>, >=, <, <=, !=, ==) bool_factor)*
    bool_factor: NOT bool_term | LPARENT bool_expr RPARENT | TRUE | FALSE | ID | function_call
    str_expr: STRING (PLUS (STRING|variable))*
    expr: term ((PLUS, MINUS) term)*
    term: factor ((DIV, MULT, FLOAT_DIV) factor)*
    factor: PLUS factor | MINUS factor | INTEGER | REAL_INTEGER | LPARENT expr RPARENT | variable | function_call
    variable: ID
    expression : IDENTIFIER LBRACKET expression RBRACKET
    """

    def __init__(self, text):
        self.lexer = Lexer(text)

    @staticmethod
    def emtpy():
        return NoOp()

    def print_surrounding_tokens(self):
        self.lexer.save_current_state()
        print("surrounding tokens")
        print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        for i in range(5):
            if self.lexer.get_current_token().type is not EOF:
                #print(self.lexer.get_current_token())
                self.lexer.go_forward()
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>")
        self.lexer.use_saved_state()

    def is_function_call(self):
        return self.next_tokens_are(ID, LPARENT)

    def is_assignment(self):
        flag = self.next_tokens_are(ID, ASSIGN)
        return flag

    def is_declaration(self):
        token = self.lexer.get_current_token()
        return token.type in (VAR, FUNCTION)

    def next_token_is(self, token_type):
        return self.next_tokens_are(token_type)

    def next_tokens_are(self, *args):
        self.lexer.save_current_state()
        state = True
        for arg in args:
            token = self.lexer.get_current_token()
            if token.type is not arg:
                state = False
                break
            self.lexer.go_forward()

        self.lexer.use_saved_state()
        return state

    def match_next_tokens_to_any(self, *token_types):
        self.lexer.save_current_state()
        token = self.lexer.get_current_token()
        while token.type is not SEMI and token.type is not LCBRACE and token.type is not EOF \
                and (token.type is not EOF):
            token = self.lexer.get_current_token()
            if token.type in token_types:
                self.lexer.use_saved_state()
                return True
            self.lexer.go_forward()
        self.lexer.use_saved_state()
        return False
    def parse_imports(self):
        imports = []
        while self.is_import_statement():
            imports.append(self.import_statement())
        return imports

    def program(self):
        self.match(PROGRAM)
        self.variable()
        block = self.block()
        return Program(block)

    def block(self):
        self.match(LCBRACE)
        declarations = self.declarations()
        compound_statement = self.compound_statement()
        self.match(RCBRACE)
        return Block(declarations, compound_statement)

    def function_block(self):
        declarations = self.declarations()
        compound_statement = self.compound_statement()
        return Block(declarations, compound_statement)

    def function_return_statement(self):
        returns = None
        if self.next_tokens_are(RETURN):
            self.match(RETURN)
            returns = self.base_expr()
            self.match(SEMI)
        returns = ReturnStat(returns)
        return returns

    def declarations(self) -> list:
        # check functions and  declaration
        declarations = []
        while self.lexer.get_current_token().type in (VAR, FUNCTION):
            if self.lexer.get_current_token().type is VAR:
                self.match(VAR)
                while self.next_tokens_are(ID, COMMA) or self.next_tokens_are(ID, COLON):
                    # var x, y || var x : integer
                    declarations.append(self.variable_declaration())
                    self.match(SEMI)

            while self.lexer.get_current_token().type is FUNCTION:
                self.match(FUNCTION)
                proc_name = self.lexer.get_current_token().value
                self.match(ID)

                parameters_list = []
                if self.lexer.current_token.type is LPARENT:
                    self.match(LPARENT)
                    parameters_list = self.parameters_list()
                    self.match(RPARENT)

                self.match(LCBRACE)
                block = self.function_block()
                self.match(RCBRACE)

                function_decl = FunctionDecl(proc_name, parameters_list, block)
                declarations.append(function_decl)

        return declarations

    def parameters_list(self) -> list:
        """
        ( a , b : INTEGER; c : REAL ) or ()
        """

        declarations = []

        if self.lexer.get_current_token().type is RPARENT:
            return declarations

        var = self.lexer.get_current_token().value
        declarations.append(var)
        self.match(ID)

        while self.lexer.get_current_token().type is COMMA:
            self.match(COMMA)
            var = self.lexer.get_current_token().value
            declarations.append(var)
            self.match(ID)

        self.match(COLON)
        base_type = self.base_type()
        declarations = list(map(lambda x: VarSymbol(x, base_type.value), declarations))

        if self.lexer.get_current_token().type is not RPARENT:
            self.match(SEMI)
            declarations.extend(self.parameters_list())

        return declarations

    def variable_declaration(self):
        variables = []
        if self.lexer.get_current_token().type is not ID:
            self.error('should be ID, got: ' + self.lexer.get_current_token().type)

        variables.append(self.lexer.get_current_token())
        self.lexer.go_forward()

        while self.lexer.get_current_token().type is COMMA:
            self.lexer.go_forward()
            var = self.lexer.get_current_token()
            if var.type is not ID:
                self.error('should be ID, got: ' + self.lexer.get_current_token().type)
            variables.append(var)
            self.lexer.go_forward()

        self.match(COLON)
        base_type = self.base_type()

        val = None
        if self.next_token_is(ASSIGN):
            self.match(ASSIGN)
            val = self.base_expr()

        return VarDecs(variables, base_type, val)

    def base_type(self):
        token = self.lexer.get_current_token()
        if token.type in (INTEGER, REAL, STRING, BOOLEAN, OBJECT):
            self.lexer.go_forward()
            return token

        self.error('should be integer|real|string|boolean|object, got ' + token.type)

    def integer_type(self):
        token = self.lexer.get_current_token()
        if token.type in (INTEGER, REAL):
            self.lexer.go_forward()
            return token

        self.error('should be integer|real, got ' + token.type)

    def compound_statement(self):
        nodes = self.statement_list()
        compound = Compound()
        for node in nodes:
            compound.add(node)

        return compound

    def is_if_statement(self):
        return self.next_tokens_are(IF)

    def is_for_loop(self):
        return self.next_tokens_are(FOR)

    def is_break(self):
        return self.next_tokens_are(BREAK)

    def is_return_stat(self):
        return self.next_token_is(RETURN)
    def is_show(self):
        return self.next_tokens_are(SHOW) or self.next_tokens_are(SHOW, LPARENT)
    def is_compound_statement(self):
        return self.is_function_call()\
               or self.is_assignment() \
               or self.is_declaration() \
               or self.is_if_statement() \
               or self.is_for_loop() \
               or self.is_while_loop() \
               or self.is_do_while_loop() \
               or self.is_break() \
                or self.is_return_stat()\
                or self.is_show()\
                 or self.is_switch_statement() \
               or self.is_theorem_statement() \
               or self.is_proof_block() \
               or self.is_hypothesis() \
               or self.is_test_statement()\
                or self.is_axiom_statement()  # ← ADD THIS LINE



    def statement_list(self):
        children = []
        statement = self.statement()
        if isinstance(statement, list):
            for node in statement:
                children.append(node)
        else:
            children.append(statement)

        while self.is_compound_statement():
            statement = self.statement_list()
            if isinstance(statement, list):
                for node in statement:
                    children.append(node)
            else:
                children.append(statement)

        return children
    def is_import_statement(self):
            return self.next_tokens_are(IMPORT, ID, SEMI)

    def import_statement(self):
        self.match(IMPORT)
        module_name = self.lexer.get_current_token().value
        self.match(ID)
        self.match(SEMI)
        return ImportStatement(module_name)
    def statement(self):
        token = self.lexer.get_current_token()

        if self.is_function_call():
            # function call
            node = self.function_call()
            self.match(SEMI)
            return node
        elif self.is_assignment():
            # assignment
            node = self.assignment_statement()
            self.match(SEMI)
            return node
        elif self.is_declaration():
            # variable or function declaration
            return self.declarations()
        elif self.is_if_statement():
            #
            return self.if_statement()
        elif self.is_for_loop():
            #
            return self.for_loop()
        elif self.is_break():
            self.match(BREAK)
            self.match(SEMI)
            return Break()
        elif self.is_return_stat():
            #
            return self.function_return_statement()
        elif self.is_show():  # Add this line for SHOW statement
            return self.show_statement()
        elif self.is_while_loop():  # Add this line for SHOW statement
            return self.while_loop()
        elif self.is_do_while_loop():  # Add this line for SHOW statement
            return self.do_while_loop()
        elif token.type == RCBRACE:
            return self.emtpy()
        elif self.is_import_statement():
            return self.import_statement()
        elif self.is_switch_statement():
            return self.switch_statement()
        elif self.is_theorem_statement():
            return self.theorem_statement()
        elif self.is_proof_block():
            return self.proof_block()
        elif self.is_hypothesis():
            return self.hypothesis_statement()
        elif self.is_test_statement():
            return self.test_statement()
        elif self.next_token_is(AXIOM):
            return self.axiom_statement()

        #print(token)
        self.error("should be ID or LPARENT, got {}".format(token))

    def for_loop(self):
        self.match(FOR)
        base = self.assignment_statement()
        self.match(SEMI)
        bool_expr = self.bool_expr()
        self.match(SEMI)
        then = self.assignment_statement()
        block = self.block()
        return ForLoop(base, bool_expr, then, block)

    def if_statement(self):
        self.match(IF)
        bool_expr = self.bool_expr()
        block = self.block()
        if_blocks = [IfBlock(bool_expr, block)]
        else_block = None
        while self.lexer.get_current_token().type is ELIF:
            self.match(ELIF)
            bool_expr = self.bool_expr()
            block = self.block()
            if_blocks.append(IfBlock(bool_expr, block))
        if self.lexer.get_current_token().type is ELSE:
            self.match(ELSE)
            else_block = self.block()
        return IfStat(if_blocks, else_block)

    def function_call(self):
        """
        function_call: ID LPARENT (base_expr (COMMA base_expr)*)* RPARENT
        """
        current_token = self.lexer.get_current_token()
        proc_name = self.lexer.get_current_token().value
        self.match(ID)
        self.match(LPARENT)
        if self.lexer.get_current_token().type is RPARENT:
            self.match(RPARENT)
            # no parameters
            return FunctionCall(proc_name, [], current_token)
        else:
            params = [self.base_expr()]
            while self.lexer.get_current_token().type is COMMA:
                self.match(COMMA)
                params.append(self.base_expr())
            self.match(RPARENT)
            return FunctionCall(proc_name, params, current_token)

    def assignment_statement(self):
        var = self.variable()
        self.match(ASSIGN)
        base_expr = self.base_expr()
        return Assign(var, Token(ASSIGN, Assign), base_expr)

    def is_next_function_call(self):
        return self.next_tokens_are(ID, LPARENT)

    def is_next_bool_expr(self):
        return self.match_next_tokens_to_any(AND, OR, BOOLEAN, NOT, NOT_EQUAL, GREATER_THAN, GREATER_THAN_OR_EQUAL,
                                             LESS_THAN, LESS_THAN_OR_EQUAL, IS_EQUAL)

    def is_next_expr(self):
        return self.match_next_tokens_to_any(MULT, DIV, FLOAT_DIV, MINUS, PLUS, ID, INTEGER, FLOAT)

    def is_next_str_expr(self):
        node = self.match_next_tokens_to_any(STRING)
        return node

    def base_expr(self):
        if self.is_next_str_expr():
            return self.str_expr()
        elif self.is_next_bool_expr():
            return self.bool_expr()
        elif self.is_next_expr():
            return self.expr()

        #print(self.lexer.get_current_token())
        self.error("can't decide current expression type")

    @staticmethod
    def is_boolean_token_type(token_type):
        return token_type in (
            OR, AND, GREATER_THAN, GREATER_THAN_OR_EQUAL, LESS_THAN, LESS_THAN_OR_EQUAL, NOT_EQUAL, IS_EQUAL)

    def bool_expr(self):
        #  bool_expr: bool_term ((OR, AND) bool_term)*
        bool_term = self.bool_term()
        while self.lexer.get_current_token().type in (OR, AND):
            op: Token = self.lexer.get_current_token()
            self.lexer.go_forward()
            if op.type is OR:
                bool_term = BoolOr(bool_term, self.bool_term())
            elif op.type is AND:
                bool_term = BoolAnd(bool_term, self.bool_term())
            else:
                self.error('not supported boolean token')

        return bool_term

    def bool_term(self):
        # bool_term: bool_factor ((>, >=, <, <=, !=, ==) bool_factor)*
        bool_factor = self.bool_factor()
        while self.lexer.get_current_token().type in (
                GREATER_THAN, GREATER_THAN_OR_EQUAL, LESS_THAN, LESS_THAN_OR_EQUAL, NOT_EQUAL, IS_EQUAL):

            op: Token = self.lexer.get_current_token()
            self.lexer.go_forward()

            if op.type is NOT_EQUAL:
                bool_factor = BoolNotEqual(bool_factor, self.bool_factor())
            elif op.type is GREATER_THAN:
                bool_factor = BoolGreaterThan(bool_factor, self.bool_factor())
            elif op.type is GREATER_THAN_OR_EQUAL:
                bool_factor = BoolGreaterThanOrEqual(bool_factor, self.bool_factor())
            elif op.type is LESS_THAN:
                bool_factor = BoolLessThan(bool_factor, self.bool_factor())
            elif op.type is LESS_THAN_OR_EQUAL:
                bool_factor = BoolLessThanOrEqual(bool_factor, self.bool_factor())
            elif op.type is IS_EQUAL:
                bool_factor = BoolIsEqual(bool_factor, self.bool_factor())
            else:
                self.error('not supported boolean token')

        return bool_factor

    def bool_factor(self):
        #  bool_term: NOT bool_term | LPARENT bool_expr RPARENT | TRUE | FALSE | ID | function_call
        token = self.lexer.get_current_token()
        if token.type is NOT:
            self.match(NOT)
            return NotOp(self.bool_term())

        if token.type is BOOLEAN:
            self.match(BOOLEAN)
            if token.value == REALISTIC:
                return RealisticSymbol(token.value, token)
            else:
                return BooleanSymbol(token.value, token)

        if self.is_next_function_call():
            return self.function_call()

        if token.type is ID:
            self.match(ID)
            return Var(token)

        if token.type is INTEGER:
            self.match(INTEGER)
            return Num(token)

        if token.type is FLOAT:
            self.match(FLOAT)
            return Num(token)

        if token.type is LPARENT:
            self.match(LPARENT)
            node = self.bool_expr()
            self.match(RPARENT)
            return node

        self.error("error in bool_term, got {}".format(token))

    def str_expr(self):
        var = self.lexer.current_token
        if var.type is STRING:
            var = Str(var)
        elif self.is_next_function_call():
            return self.function_call()
        elif var.type is ID:
            var = Var(var)
        else:
            self.error("string assignment can only contain string literals")

        self.lexer.go_forward()
        while self.lexer.get_current_token().type is PLUS:
            self.match(PLUS)
            var = StrOp(var, Token(PLUS, PLUS), self.str_expr())

        return var

    def variable(self):
        token = self.lexer.get_current_token()
        if token.type is ID:
            self.lexer.go_forward()
            return Var(token)

        self.error("error in variable")

    def error(self, message, error_code=None):
        self.print_surrounding_tokens()

        if error_code is None:
            error_code = ErrorCode.PARSER_ERROR
        raise ParserError(
            error_code=error_code,
            message=f'{error_code.value} -> {message}',
        )

    def match(self, token_type: str):
        token = self.lexer.get_current_token()
        if token.type is not token_type:
            print('-----------------------')
            print(token)
            print('should be: ' + token_type)
            print('-----------------------')
            self.error("incorrect expression")
        self.lexer.go_forward()

    def expr(self):
        node = self.term()
        while self.lexer.get_current_token().type in (PLUS, MINUS):
            current_op_token = self.lexer.get_current_token()
            self.lexer.go_forward()
            node = BinOp(node, current_op_token, self.term())
        return node

    def term(self):
        node = self.factor()
        while self.lexer.get_current_token().type in (MULT, FLOAT_DIV, INTEGER_DIV):
            current_op_token = self.lexer.get_current_token()
            self.lexer.go_forward()
            node = BinOp(node, current_op_token, self.factor())
        return node

    def factor(self):
        token = self.lexer.get_current_token()
        if token.type is PLUS:
            self.match(PLUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type is MINUS:
            self.match(MINUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == INTEGER:
            self.lexer.go_forward()
            return Num(token)
        elif token.type == FLOAT:
            self.lexer.go_forward()
            return Num(token)
        elif token.type is LPARENT:
            self.match(LPARENT)
            node = self.expr()
            self.match(RPARENT)
            return node
        elif self.is_function_call():
            return self.function_call()
        elif token.type is ID:
            self.lexer.go_forward()
            return Var(token)
        else:
            self.error("incorrect expression: (from factor)")

    def parse(self):
        program = self.program()

        if self.lexer.is_pointer_out_of_text():
            # all characters consumed
            return program

        self.error("Syntax error at position " + str(self.lexer.get_position()))

    def show_statement(self):
        self.match(SHOW)
        if self.next_token_is(LPARENT):
            self.match(LPARENT)
            expression = self.base_expr()
            self.match(RPARENT)
        else:
            # Without parentheses
            expression = self.base_expr()
        self.match(SEMI)
        return ShowStatement(expression)

    def is_while_loop(self):
        return self.next_tokens_are(WHILE)
    def is_do_while_loop(self):
        return self.next_tokens_are(DO, LCBRACE)



    def while_loop(self):
        self.match(WHILE)
        condition = self.bool_expr()
        self.match(DO)
        self.match(LCBRACE)
        statements = self.statement_list()
        self.match(RCBRACE)
        return WhileLoop(condition, statements)
    
    def do_while_loop(self):
        self.match(DO)
        self.match(LCBRACE)
        statements = self.statement_list()
        self.match(RCBRACE)
        self.match(WHILE)
        condition = self.bool_expr()
        return DoWhileLoop(statements, condition)
    def is_switch_statement(self):
        """Check if next tokens form a switch statement"""
        return self.next_tokens_are(SWITCH)
    
    def switch_statement(self):
        """
        Grammar:
        switch_statement: SWITCH LPARENT base_expr RPARENT LCBRACE case_list RCBRACE
        case_list: case_block+
        case_block: CASE base_expr COLON statement_list
                  | DEFAULT COLON statement_list
        """
        self.match(SWITCH)
        self.match(LPARENT)
        expression = self.base_expr()
        self.match(RPARENT)
        self.match(LCBRACE)
        
        case_blocks = []
        
        # Parse case blocks
        while self.lexer.get_current_token().type in (CASE, DEFAULT):
            case_blocks.append(self.case_block())
        
        self.match(RCBRACE)
        return SwitchStatement(expression, case_blocks)
    
    def case_block(self):
        """Parse a single case or default block"""
        token = self.lexer.get_current_token()
        
        if token.type == CASE:
            self.match(CASE)
            value = self.base_expr()
            self.match(COLON)
            statements = self.case_statement_list()
            return CaseBlock(value, statements)
        
        elif token.type == DEFAULT:
            self.match(DEFAULT)
            self.match(COLON)
            statements = self.case_statement_list()
            return CaseBlock(None, statements)  # None indicates default case
        
        else:
            self.error(f"Expected CASE or DEFAULT, got {token.type}")
    
    def case_statement_list(self):
        """Parse statements within a case block until next case/default/closing brace"""
        statements = []
        
        while (self.lexer.get_current_token().type not in (CASE, DEFAULT, RCBRACE) 
               and self.lexer.get_current_token().type != EOF):
            if self.is_compound_statement():
                stmt = self.statement()
                if isinstance(stmt, list):
                    statements.extend(stmt)
                else:
                    statements.append(stmt)
            else:
                break
        return statements
    def is_const_declaration(self):
            """Check if next tokens form a constant declaration"""
            return self.next_tokens_are(CONST)
    
    def const_declaration(self):
        """
        Grammar:
        const_declaration: CONST ID (COMMA ID)* COLON base_type ASSIGN base_expr
        
        Note: Constants MUST be initialized with a value
        """
        self.match(CONST)
        
        variables = []
        if self.lexer.get_current_token().type is not ID:
            self.error('Expected identifier after CONST, got: ' + self.lexer.get_current_token().type)

        variables.append(self.lexer.get_current_token())
        self.lexer.go_forward()

        # Handle multiple constants: const x, y, z: integer = 5;
        while self.lexer.get_current_token().type is COMMA:
            self.lexer.go_forward()
            var = self.lexer.get_current_token()
            if var.type is not ID:
                self.error('Expected identifier after comma, got: ' + self.lexer.get_current_token().type)
            variables.append(var)
            self.lexer.go_forward()

        self.match(COLON)
        base_type = self.base_type()

        # Constants MUST have a value
        if not self.next_token_is(ASSIGN):
            self.error('Constants must be initialized with a value')
        
        self.match(ASSIGN)
        val = self.base_expr()

        return ConstDeclaration(variables, base_type, val)
    
    def is_declaration(self):
        """Updated to include const declarations"""
        token = self.lexer.get_current_token()
        return token.type in (VAR, FUNCTION, CONST)
    
    def declarations(self) -> list:
        """Updated declarations method to handle constants"""
        declarations = []
        
        while self.lexer.get_current_token().type in (VAR, FUNCTION, CONST):
            # Handle variable declarations
            if self.lexer.get_current_token().type is VAR:
                self.match(VAR)
                while self.next_tokens_are(ID, COMMA) or self.next_tokens_are(ID, COLON):
                    declarations.append(self.variable_declaration())
                    self.match(SEMI)
            
            # Handle constant declarations
            elif self.lexer.get_current_token().type is CONST:
                declarations.append(self.const_declaration())
                self.match(SEMI)
            
            # Handle function declarations
            while self.lexer.get_current_token().type is FUNCTION:
                self.match(FUNCTION)
                proc_name = self.lexer.get_current_token().value
                self.match(ID)

                parameters_list = []
                if self.lexer.current_token.type is LPARENT:
                    self.match(LPARENT)
                    parameters_list = self.parameters_list()
                    self.match(RPARENT)

                self.match(LCBRACE)
                block = self.function_block()
                self.match(RCBRACE)

                function_decl = FunctionDecl(proc_name, parameters_list, block)
                declarations.append(function_decl)

        return declarations
    def is_theorem_statement(self):
        """Check if next tokens form a theorem"""
        return self.next_tokens_are(THEOREM)
    
    def is_proof_block(self):
        """Check if next tokens form a proof"""
        return self.next_tokens_are(PROOF)
    
    def is_hypothesis(self):
        """Check if next tokens form a hypothesis"""
        return self.next_tokens_are(HYPOTHESIS)
    
    def is_test_statement(self):
        """Check if next tokens form a test"""
        return self.next_tokens_are(TEST)
    
    def theorem_statement(self):
        """
        Grammar:
        theorem_statement: THEOREM ID COLON logical_expression
        """
        self.match(THEOREM)
        theorem_name = self.lexer.get_current_token().value
        self.match(ID)
        self.match(COLON)
        statement = self.logical_expression()
        self.match(SEMI)
        
        return TheoremStatement(theorem_name, statement)
    
    def proof_block(self):
        """
        Grammar:
        proof_block: PROOF ID LCBRACE proof_steps QED RCBRACE
        """
        self.match(PROOF)
        theorem_name = self.lexer.get_current_token().value
        self.match(ID)
        self.match(LCBRACE)
        
        steps = self.proof_steps()
        
        self.match(QED)
        self.match(RCBRACE)
        
        return ProofBlock(theorem_name, steps)
    
    def proof_steps(self):
        """Parse sequence of proof steps"""
        steps = []
        
        while (self.lexer.get_current_token().type not in (QED, RCBRACE) and 
               self.lexer.get_current_token().type != EOF):
            steps.append(self.proof_step())
        
        return steps
    
    def proof_step(self):
        """
        Grammar:
        proof_step: step_type logical_expression (BY justification)? SEMI
        step_type: ASSUME | GIVEN | THEREFORE | HYPOTHESIS
        """
        step_type = self.lexer.get_current_token().type
        
        if step_type in (ASSUME, GIVEN, THEREFORE, HYPOTHESIS):
            self.lexer.go_forward()  # consume step type
            statement = self.logical_expression()
            
            justification = None
            if self.next_token_is(BY):
                self.match(BY)
                justification = self.justification()
            
            self.match(SEMI)
            return ProofStep(step_type, statement, justification)
        
        else:
            self.error(f"Expected proof step keyword, got {step_type}")
    
    def logical_expression(self):
        """
        Grammar:
        logical_expression: quantified_expr | implication_expr | base_expr
        """
        if self.next_token_is(FORALL) or self.next_token_is(EXISTS):
            return self.quantified_expression()
        elif self.match_next_tokens_to_any(IMPLIES, IFF):
            return self.implication_expression()
        else:
            return self.base_expr()
    
    def quantified_expression(self):
        """
        Grammar:
        quantified_expr: (FORALL | EXISTS) ID COMMA logical_expression
        """
        quantifier = self.lexer.get_current_token().type
        self.lexer.go_forward()  # consume FORALL/EXISTS
        
        variable = self.lexer.get_current_token().value
        self.match(ID)
        self.match(COMMA)
        
        expression = self.logical_expression()
        
        return LogicalExpression(quantifier, expression, None, quantifier, variable)
    
    def implication_expression(self):
        """
        Grammar:
        implication_expr: logical_expression (IMPLIES | IFF) logical_expression
        """
        left = self.base_expr()
        
        if self.lexer.get_current_token().type in (IMPLIES, IFF):
            operator = self.lexer.get_current_token().type
            self.lexer.go_forward()
            right = self.logical_expression()
            
            return LogicalExpression(operator, left, right)
        
        return left
    
    def justification(self):
        """Parse justification for a proof step"""
        # This could be a reference to an axiom, previous step, or logical rule
        return self.base_expr()
    
    def hypothesis_statement(self):
        """
        Grammar:
        hypothesis_statement: HYPOTHESIS ID COLON logical_expression SEMI
        """
        self.match(HYPOTHESIS)
        name = self.lexer.get_current_token().value
        self.match(ID)
        self.match(COLON)
        statement = self.logical_expression()
        self.match(SEMI)
        
        return Hypothesis(name, statement)
    
    def test_statement(self):
        """
        Grammar:
        test_statement: TEST ID LCBRACE test_cases RCBRACE
        """
        self.match(TEST)
        target = self.lexer.get_current_token().value
        self.match(ID)
        self.match(LCBRACE)
        
        test_cases = self.test_cases()
        
        self.match(RCBRACE)
        
        return TestStatement(target, test_cases)
    
    def test_cases(self):
        """Parse test cases for theorem verification"""
        cases = []
        
        while (self.lexer.get_current_token().type not in (RCBRACE,) and 
               self.lexer.get_current_token().type != EOF):
            cases.append(self.base_expr())
            if self.next_token_is(SEMI):
                self.match(SEMI)
        
        return cases
    def is_axiom_statement(self):
        """Check if next tokens form an axiom"""
        return self.next_tokens_are(AXIOM)
    def axiom_statement(self):
        """
        Grammar:
        axiom_statement: AXIOM ID COLON logical_expression SEMI
        """
        self.match(AXIOM)
        name = self.lexer.get_current_token().value
        self.match(ID)
        self.match(COLON)
        statement = self.logical_expression()
        self.match(SEMI)
        
        return AxiomStatement(name, statement)    
    

    

