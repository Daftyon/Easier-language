from utils.constants import *
from utils.data_classes import Token

RESERVED_KEYWORDS = {
    PROGRAM: Token(PROGRAM, PROGRAM),
    BEGIN: Token(BEGIN, BEGIN),
    END: Token(END, END),
    COMMA: Token(COMMA, COMMA),
    DO: Token(DO, DO),
    COLON: Token(COLON, COLON),
    DIV: Token(INTEGER_DIV, INTEGER_DIV),
    INTEGER: Token(INTEGER, INTEGER),
    INT: Token(INTEGER, INTEGER),
    FLOAT: Token(FLOAT, FLOAT),
    REAL: Token(REAL, REAL),
    VAR: Token(VAR, VAR),
    PROCEDURE: Token(PROCEDURE, PROCEDURE),
    STRING: Token(STRING, STRING),
    STR: Token(STRING, STRING),
    FUNCTION: Token(FUNCTION, FUNCTION),
    RETURN: Token(RETURN, RETURN),
    BOOLEAN: Token(BOOLEAN, BOOLEAN),
    TRUE: Token(BOOLEAN, TRUE),
    FALSE: Token(BOOLEAN, FALSE),
    FOR: Token(FOR, FOR),
    WHILE: Token(WHILE, WHILE),
    BREAK: Token(BREAK, BREAK),
    OBJECT: Token(OBJECT, OBJECT),
    SHOW: Token(SHOW, SHOW),
    INVOLVE: Token(INVOLVE, INVOLVE),
    SWITCH: Token(SWITCH, SWITCH),
    CASE: Token(CASE, CASE),
    DEFAULT: Token(DEFAULT, DEFAULT),
    CONST: Token(CONST, CONST),
    REALISTIC: Token(BOOLEAN, REALISTIC),  # Treat as boolean type but with realistic value
    THEOREM: Token(THEOREM, THEOREM),  # New theorem keyword
    PROOF: Token(PROOF, PROOF),
    QED: Token(QED, QED),
    HYPOTHESIS: Token(HYPOTHESIS, HYPOTHESIS),
    TEST: Token(TEST, TEST),
    AXIOM: Token(AXIOM, AXIOM),

}
