from enum import Enum


class ErrorCode(Enum):
    UNEXPECTED_TOKEN = "Unexpected token"
    ID_NOT_FOUND = "Identifier not found"
    DUPLICATE_ID = "Duplicate id found"
    LEXER_ERROR = "Lexer error"
    PARSER_ERROR = "Parser error"
    SEMANTIC_ERROR = "Semantic error"
    INTERPRETER_ERROR = "Interpreter error"
    NUMBER_OF_ARGUMENTS_MISMATCH_ERROR = "Arguments error"
    WHILE_LOOP_CONDITION_BOOL = "while loop condition must be boolean"
    MULTIPLE_DEFAULT_CASES = "Multiple default cases in switch"
    DUPLICATE_CASE_VALUES = "Duplicate case values in switch"
    SWITCH_CASE_TYPE_MISMATCH = "Case value type doesn't match switch expression"
    CONST_NOT_INITIALIZED = "Constant must be initialized"
    CONST_MODIFICATION = "Cannot modify constant value"
    CONST_REDEFINITION = "Constant already defined"

class Error(Exception):
    def __init__(self, error_code, message):
        self.error_code = error_code
        self.message = f'{self.__class__.__name__}: {message}'

    def __str__(self):
        return self.message


class LexerError(Error):
    pass


class ParserError(Error):
    pass


class SemanticError(Error):
    pass


class InterpreterError(Error):
    pass
