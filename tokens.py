import re
import tokenize
from io import BytesIO
import sys
sys.platform = "win32" 
class Interpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}

    def interpret(self, code):
        code = code.replace('\n', '')
        # Define a regular expression pattern to match tokens
        pattern = r'\b(?:PROGRAM|VAR|LCBRACE|RCBRACE|LPARENT|RPARENT|SEMI|ID|COLON|COMMA|ASSIGN|PLUS|MINUS|MULT|DIV|FLOAT_DIV|INTEGER|REAL_INTEGER|STRING|SHOW|FUNCTION|IF|ELSE|FOR|IN|RANGE|WHILE|DO|BREAK|AND|OR|NOT|TRUE|FALSE)\b|\b(?:[a-zA-Z_][a-zA-Z_0-9]*|[0-9]+(?:\.[0-9]*)?)\b|".*?"|\S'
        # Tokenize the code using the re module
        tokens = re.findall(pattern, code)
        # Remove empty tokens
        tokens = [token for token in tokens if token.strip()]
        # Print the tokens for debugging
        print("Tokens:", tokens)
        # Convert the list of tokens to an iterator
        token_iterator = iter(tokens)
        self.program(token_iterator)
    def program(self, tokens):
        program_name = self.match(tokens, "PROGRAM")
        if program_name.isidentifier():
            self.variable_declaration(tokens)
            self.block(tokens)
        else:
            raise SyntaxError("Invalid program name")



    def block(self, tokens):
        self.match(tokens, "LCBRACE")
        self.declarations(tokens)
        self.compound_statement(tokens)
        self.match(tokens, "RCBRACE")

    def declarations(self, tokens):
        if self.peek(tokens) == "VAR":
            self.match(tokens, "VAR")
            while self.peek(tokens) == "ID":
                self.variable_declaration(tokens)
                self.match(tokens, "SEMI")
        elif self.peek(tokens) == "FUNCTION":
            self.match(tokens, "FUNCTION")
            func_name = self.match(tokens, "ID")
            parameters = []
            if self.peek(tokens) == "LPARENT":
                self.match(tokens, "LPARENT")
                parameters = self.formal_parameter_list(tokens)
                self.match(tokens, "RPARENT")
            self.functions[func_name] = {"parameters": parameters, "block": self.block(tokens)}

    def formal_parameter_list(self, tokens):
        parameters = [self.formal_parameter(tokens)]
        while self.peek(tokens) == "SEMI":
            self.match(tokens, "SEMI")
            parameters.append(self.formal_parameter(tokens))
        return parameters

    def formal_parameter(self, tokens):
        param_name = self.match(tokens, "ID")
        while self.peek(tokens) == "COMMA":
            self.match(tokens, "COMMA")
            self.match(tokens, "ID")
        self.match(tokens, "COLON")
        return {"name": param_name, "type": self.match(tokens, "OBJECT")}

    def variable_declaration(self, tokens):
        var_names = [self.match(tokens, "ID")]
        while self.peek(tokens) == "COMMA":
            self.match(tokens, "COMMA")
            var_names.append(self.match(tokens, "ID"))
        self.match(tokens, "COLON")
        var_type = self.match(tokens, "OBJECT")
        for var_name in var_names:
            if self.peek(tokens) == "ASSIGN":
                self.match(tokens, "ASSIGN")
                var_value = self.base_expr(tokens)
                self.variables[var_name] = {"type": var_type, "value": var_value}
            else:
                self.variables[var_name] = {"type": var_type}

    def compound_statement(self, tokens):
        self.statement_list(tokens)

    def statement_list(self, tokens):
        self.statement(tokens)
        while self.peek(tokens) == "SEMI":
            self.match(tokens, "SEMI")
            self.statement(tokens)

    def statement(self, tokens):
        if self.peek(tokens) == "ID":
            self.assignment_statement(tokens)
        elif self.peek(tokens) == "SHOW":
            self.show_statement(tokens)
        elif self.peek(tokens) == "RETURN":
            self.return_statement(tokens)
        elif self.peek(tokens) == "VAR" or self.peek(tokens) == "FUNCTION":
            self.declarations(tokens)
        elif self.peek(tokens) == "IF":
            self.if_statement(tokens)
        elif self.peek(tokens) == "FOR":
            self.for_loop(tokens)
        elif self.peek(tokens) == "BREAK":
            self.match(tokens, "BREAK")
        elif self.peek(tokens) == "WHILE":
            self.while_loop(tokens)
        elif self.peek(tokens) == "DO":
            self.do_while_loop(tokens)

    def assignment_statement(self, tokens):
        var_name = self.match(tokens, "ID")
        self.match(tokens, "ASSIGN")
        var_value = self.base_expr(tokens)
        self.variables[var_name]["value"] = var_value

    def show_statement(self, tokens):
        self.match(tokens, "SHOW")
        self.match(tokens, "LPARENT")
        value = self.base_expr(tokens)
        print(value)
        self.match(tokens, "RPARENT")

    def return_statement(self, tokens):
        self.match(tokens, "RETURN")
        value = self.base_expr(tokens)
        return value

    def if_statement(self, tokens):
        self.match(tokens, "IF")
        condition = self.bool_expr(tokens)
        self.match(tokens, "DO")
        block = self.block(tokens)
        if condition:
            self.interpret(block)

    def for_loop(self, tokens):
        self.match(tokens, "FOR")
        self.match(tokens, "ID")
        self.match(tokens, "IN")
        self.match(tokens, "RANGE")
        self.match(tokens, "LPARENT")
        start = int(self.match(tokens, "INTEGER"))
        self.match(tokens, "COMMA")
        end = int(self.match(tokens, "INTEGER"))
        self.match(tokens, "RPARENT")
        self.match(tokens, "DO")
        block = self.block(tokens)
        for i in range(start, end + 1):
            self.variables[tokens[1]] = {"type": "INTEGER", "value": i}
            self.interpret(block)

    def while_loop(self, tokens):
        self.match(tokens, "WHILE")
        condition = self.bool_expr(tokens)
        self.match(tokens, "DO")
        block = self.block(tokens)
        while condition:
            self.interpret(block)
            condition = self.bool_expr(tokens)

    def do_while_loop(self, tokens):
        self.match(tokens, "DO")
        block = self.block(tokens)
        self.match(tokens, "WHILE")
        condition = self.bool_expr(tokens)
        while condition:
            self.interpret(block)
            condition = self.bool_expr(tokens)

    def base_expr(self, tokens):
        return self.expr(tokens)

    def bool_expr(self, tokens):
        return self.bool_term(tokens)

    def bool_term(self, tokens):
        return self.bool_factor(tokens)

    def bool_factor(self, tokens):
        if self.peek(tokens) == "NOT":
            self.match(tokens, "NOT")
            return not self.bool_term(tokens)
        elif self.peek(tokens) == "LPARENT":
            self.match(tokens, "LPARENT")
            result = self.bool_expr(tokens)
            self.match(tokens, "RPARENT")
            return result
        elif self.peek(tokens) == "TRUE":
            self.match(tokens, "TRUE")
            return True
        elif self.peek(tokens) == "FALSE":
            self.match(tokens, "FALSE")
            return False
        elif self.peek(tokens) == "ID" and self.tokens[1] not in ("AND", "OR"):
            return self.variables[self.match(tokens, "ID")]["value"]
        elif self.peek(tokens) == "FUNCTION":
            return self.function_call(tokens)
        else:
            left = self.bool_term(tokens)
            while self.peek(tokens) in ("OR", "AND"):
                operator = self.match(tokens, "OR", "AND")
                right = self.bool_term(tokens)
                if operator == "OR":
                    left = left or right
                elif operator == "AND":
                    left = left and right
            return left

    def expr(self, tokens):
        return self.term(tokens)

    def term(self, tokens):
        left = self.factor(tokens)
        while self.peek(tokens) in ("PLUS", "MINUS"):
            operator = self.match(tokens, "PLUS", "MINUS")
            right = self.factor(tokens)
            if operator == "PLUS":
                left += right
            elif operator == "MINUS":
                left -= right
        return left

    def factor(self, tokens):
        left = self.base(tokens)
        while self.peek(tokens) in ("MULT", "DIV", "FLOAT_DIV"):
            operator = self.match(tokens, "MULT", "DIV", "FLOAT_DIV")
            right = self.base(tokens)
            if operator == "MULT":
                left *= right
            elif operator == "DIV":
                left /= right
            elif operator == "FLOAT_DIV":
                left //= right
        return left

    def base(self, tokens):
        if self.peek(tokens) == "PLUS":
            self.match(tokens, "PLUS")
            return self.base(tokens)
        elif self.peek(tokens) == "MINUS":
            self.match(tokens, "MINUS")
            return -self.base(tokens)
        elif self.peek(tokens) == "INTEGER":
            return int(self.match(tokens, "INTEGER"))
        elif self.peek(tokens) == "REAL_INTEGER":
            return float(self.match(tokens, "REAL_INTEGER"))
        elif self.peek(tokens) == "LPARENT":
            self.match(tokens, "LPARENT")
            result = self.expr(tokens)
            self.match(tokens, "RPARENT")
            return result
        elif self.peek(tokens) == "ID":
            return self.variables[self.match(tokens, "ID")]["value"]
        elif self.peek(tokens) == "FUNCTION":
            return self.function_call(tokens)
        else:
            raise SyntaxError(f"Unexpected token: {self.peek(tokens)}")

    def function_call(self, tokens):
        func_name = self.match(tokens, "ID")
        self.match(tokens, "LPARENT")
        args = []
        if self.peek(tokens) != "RPARENT":
            args.append(self.base_expr(tokens))
            while self.peek(tokens) == "COMMA":
                self.match(tokens, "COMMA")
                args.append(self.base_expr(tokens))
        self.match(tokens, "RPARENT")
        if func_name in self.functions:
            func_params = self.functions[func_name]["parameters"]
            if len(func_params) != len(args):
                raise ValueError(f"Function {func_name} expects {len(func_params)} arguments, but {len(args)} provided.")
            local_variables = {param["name"]: {"type": param["type"], "value": arg} for param, arg in zip(func_params, args)}
            old_variables = self.variables
            self.variables = local_variables
            self.interpret(self.functions[func_name]["block"])
            self.variables = old_variables
        else:
            raise ValueError(f"Function {func_name} is not defined.")

    def match(self, tokens, *expected):
        token = next(tokens)
        if token in expected:
            return token
        else:
            raise SyntaxError(f"Unexpected token: {token}")

    def peek(self, tokens):
        return next(tokens, None)


# Example usage
code = """
PROGRAM example_program
VAR
    x, y: INTEGER = 5;
    s: STRING = "Hello, " + "world!";

SHOW s;
SHOW x + y;
"""

interpreter = Interpreter()
interpreter.interpret(code)



