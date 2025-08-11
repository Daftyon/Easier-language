from utils.constants import *
from utils.data_classes import Token
from utils.errors import LexerError, ErrorCode
from system.reserved import RESERVED_KEYWORDS


class Lexer(object):
    def __init__(self, text):
        self.pos = 0
        self.text = text
        self.lineno = 1
        self.column = 1
        self._saved_states = list()
        self.current_token = None
        self.get_next_token()

    def error(self, message):
        s = f'Lexer error on {self.get_current_character()};' \
            f' line: {self.lineno};' \
            f' column: {self.column} ' \
            f' message: {message}'

        raise LexerError(ErrorCode, s)

    def save_current_state(self):
        self._saved_states.append({
            "pos": self.pos,
            "lineno": self.lineno,
            "column": self.column,
            "current_token": self.current_token,
        })

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

    def use_saved_state(self):
        if len(self._saved_states) == 0:
            self.error('_saved_state is None')

        last_state = self._saved_states.pop()
        for key, val in last_state.items():
            self.__setattr__(key, val)

    def is_pointer_out_of_text(self, pos=None):
        if pos is None:
            pos = self.pos

        return pos >= len(self.text)

    def get_position(self):
        return self.pos

    def get_current_token(self) -> Token:
        return self.current_token

    def peek_next_token(self):
        cur_pos = self.pos
        current_token = self.get_current_token()
        next_token = self.get_next_token()
        self.pos = cur_pos
        self.current_token = current_token
        return next_token

    def go_forward(self):
        # this will match next token and save it in current_token variable
        self.get_next_token()

    def get_character(self, pos):
        if pos == len(self.text):
            return None
        if pos > len(self.text):
            raise Exception('no characters left')
        return self.text[pos]

    def get_current_character(self) -> str:
        return self.get_character(self.pos)

    def next_characters_are(self, chars):
        self.save_current_state()

        for char in chars:
            cur = self.get_character(self.pos)
            if cur != char:
                self.use_saved_state()
                return False
            self.advance()
        self.use_saved_state()
        return True

    @staticmethod
    def is_digit(num):
        if isinstance(num, str):
            return num.isdigit()
        return False

    def is_not_digit(self, s):
        return self.is_digit(s) is False

    @staticmethod
    def is_operator(p):
        return p in "+-*/()"

    def get_char_type(self, p):
        types = {
            "+": PLUS,
            "-": MINUS,
            "*": MULT,
            "/": FLOAT_DIV,
            "(": LPARENT,
            ")": RPARENT
        }

        element_type = types.get(p, None)
        if element_type is None:
            self.error("Unsupported character " + p)

        return element_type

    def advance(self, num_of_chars=1):
        for _ in range(num_of_chars):
            if self.get_current_character() == '\n':
                self.lineno += 1
                self.column = 1
            else:
                self.column += 1

            self.pos = self.pos + 1

    def peek(self):
        if self.is_pointer_out_of_text(self.get_position() + 1):
            return None
        return self.get_character(self.get_position() + 1)

    @staticmethod
    def get_reserved_keyword_token(token_type):
        return RESERVED_KEYWORDS.get(token_type)

    def _id(self):
        result = ""
        while self.get_current_character() is not None and self.get_current_character().isalnum():
            result += self.get_current_character()
            self.advance()

        if result.upper() in RESERVED_KEYWORDS:
            result = result.upper()
            return self.get_reserved_keyword_token(result)
        elif result.lower() in RESERVED_KEYWORDS:
            result = result.lower()
            return self.get_reserved_keyword_token(result)

        return Token(ID, result)

    def _string(self):
        cur_char = self.get_current_character()
        string = ""
        self.advance()
        while self.get_current_character() != cur_char:
            string += self.get_current_character()
            self.advance()
        self.advance()
        return Token(STRING, string)

    def _number(self):
        cur_char = self.get_current_character()
        while True:
            self.advance()
            char = self.get_current_character()
            if self.is_digit(char) or char == '.':
                cur_char += char
            else:
                break

        cnt = cur_char.count('.')
        if cnt > 1:
            self.error('incorrect number ' + cur_char)

        if cnt == 0:
            num = int(cur_char)
            return Token(INTEGER, num)
        else:
            num = float(cur_char)
            return Token(FLOAT, num)

    def skip_comment(self):
        while self.get_current_character() != "}":
            self.advance()

        # skip '}'
        cur_char = self.get_current_character()
        self.advance()

        # peek next character
        next_char = self.get_current_character()

        # commend should end with '}}'
        if cur_char != next_char or cur_char != "}":
            return self.error("Expected ']}' for comment, got {}".format(cur_char + next_char))

        self.advance()

    def skip_one_line_comment(self):
        while self.get_current_character() != "\n":
            self.advance()
        self.advance()

    def get_next_token(self) -> Token:
        cur_char = self.get_current_character()
        if cur_char is None:
            self.current_token = Token(EOF, EOF)
            return self.current_token
        if self.is_digit(cur_char):
            # NUMBER
            self.current_token = self._number()
            return self.current_token
        elif cur_char in ("'", '"'):
            # STRING
            self.current_token = self._string()
            return self.current_token
        elif self.next_characters_are("//"):
            # one line comment
            self.skip_one_line_comment()
            return self.get_next_token()
        elif self.next_characters_are("or"):
            self.advance(2)
            self.current_token = Token(OR, OR)
            return self.current_token
        elif self.next_characters_are("and"):
            self.advance(3)
            self.current_token = Token(AND, AND)
            return self.current_token
        elif self.next_characters_are("if"):
            self.advance(2)
            self.current_token = Token(IF, IF)
            return self.current_token
        elif self.next_characters_are("elif"):
            self.advance(4)
            self.current_token = Token(ELIF, ELIF)
            return self.current_token
        elif self.next_characters_are("else"):
            self.advance(4)
            self.current_token = Token(ELSE, ELSE)
            return self.current_token
        elif self.next_characters_are("realistic"):
            self.advance(9)
            self.current_token = Token(BOOLEAN, REALISTIC)
            return self.current_token
        elif cur_char.isalpha():
            # ID
            self.current_token = self._id()
            return self.current_token
        elif self.is_operator(cur_char):
            # OPERATOR (+-*/())
            self.advance()
            self.current_token = Token(self.get_char_type(cur_char), cur_char)
            return self.current_token
        elif cur_char == '.':
            # DOT
            self.advance()
            self.current_token = Token(DOT, DOT)
            return self.current_token
        elif cur_char == ';':
            # SEMI
            self.advance()
            self.current_token = Token(SEMI, SEMI)
            return self.current_token
        elif self.next_characters_are("{{"):
            self.skip_comment()
            return self.get_next_token()
        elif cur_char == "{":
            self.advance()
            self.current_token = Token(LCBRACE, LCBRACE)
            return self.current_token
        elif cur_char == "}":
            self.advance()
            self.current_token = Token(RCBRACE, RCBRACE)
            return self.current_token
        elif cur_char == ":":
            self.advance()
            self.current_token = Token(COLON, COLON)
            return self.current_token
        elif cur_char == ',':
            self.advance()
            self.current_token = Token(COMMA, COMMA)
            return self.current_token
        elif cur_char == "[":
            self.advance()
            self.current_token = Token(LBRACKET, LBRACKET)
            return self.current_token

        elif cur_char == "]":
            self.advance()
            self.current_token = Token(RBRACKET, RBRACKET)
            return self.current_token

        elif cur_char == '.':
            self.advance()
            self.current_token = Token(DOT, DOT)
            return self.current_token
        elif self.next_characters_are("!="):
            self.advance(2)
            self.current_token = Token(NOT_EQUAL, NOT_EQUAL)
            return self.current_token
        elif self.next_characters_are(">="):
            self.advance(2)
            self.current_token = Token(GREATER_THAN_OR_EQUAL, GREATER_THAN_OR_EQUAL)
            return self.current_token
        elif self.next_characters_are("<="):
            self.advance(2)
            self.current_token = Token(LESS_THAN_OR_EQUAL, LESS_THAN_OR_EQUAL)
            return self.current_token
        elif cur_char == ">":
            self.advance()
            self.current_token = Token(GREATER_THAN, GREATER_THAN)
            return self.current_token
        elif cur_char == "<":
            self.advance()
            self.current_token = Token(LESS_THAN, LESS_THAN)
            return self.current_token
        elif self.next_characters_are('==='):
            self.advance(3)
            self.current_token = Token(IS_EQUAL, IS_EQUAL)
            return self.current_token
        elif cur_char == "=":
            # ASSIGNMENT
            self.advance()
            self.current_token = Token(ASSIGN, ASSIGN)
            return self.current_token
        elif cur_char == "!":
            self.advance()
            self.current_token = Token(NOT, NOT)
            return self.current_token
        elif self.next_characters_are("switch"):
            self.advance(6)
            self.current_token = Token(SWITCH, SWITCH)
            return self.current_token
        elif self.next_characters_are("case"):
            self.advance(4)
            self.current_token = Token(CASE, CASE)
            return self.current_token
        elif self.next_characters_are("default"):
            self.advance(7)
            self.current_token = Token(DEFAULT, DEFAULT)
            return self.current_token
        elif self.next_characters_are("const"):
            self.advance(5)
            self.current_token = Token(CONST, CONST)
            return self.current_token
        elif self.next_characters_are("theorem"):
            self.advance(7)
            self.current_token = Token(THEOREM, THEOREM)
            return self.current_token
        elif self.next_characters_are("proof"):
            self.advance(5)
            self.current_token = Token(PROOF, PROOF)
            return self.current_token
        elif self.next_characters_are("qed"):
            self.advance(3)
            self.current_token = Token(QED, QED)
            return self.current_token
        elif self.next_characters_are("hypothesis"):
            self.advance(10)  # "hypothesis" is 10 characters
            self.current_token = Token(HYPOTHESIS, HYPOTHESIS)
            return self.current_token
        elif self.next_characters_are("test"):
            self.advance(4)  # "test" is 4 characters
            self.current_token = Token(TEST, TEST)
            return self.current_token
        elif self.next_characters_are("axiom"):
            self.advance(5)  # "axiom" is 5 characters
            self.current_token = Token(AXIOM, AXIOM)
            return self.current_token
        elif self.next_characters_are("definition"):
            self.advance(10)  # "definition" is 10 characters
            self.current_token = Token(DEFINITION, DEFINITION)
            return self.current_token
        elif self.next_characters_are("bring"):
            self.advance(5)  # "bring" is 5 characters
            self.current_token = Token(BRING, BRING)
            return self.current_token
        elif self.next_characters_are("from"):
            self.advance(4)  # "from" is 4 characters
            self.current_token = Token(FROM, FROM)
            return self.current_token
        elif self.next_characters_are("as"):
            self.advance(2)  # "as" is 2 characters
            self.current_token = Token(AS, AS)
            return self.current_token
                    
        else:
            if cur_char.isspace():
                while self.get_current_character() is not None and self.get_current_character().isspace():
                    self.advance()
                return self.get_next_token()
            self.error('syntax error "' + cur_char + '" is not valid character')
        self.error('unrecognized character ' + cur_char)
