# Jina Walbourne
# B00930225

class TokenType:
    # define token types
    LBRACE = 'LBRACE'
    RBRACE = 'RBRACE'
    LBRACKET = 'LBRACKET'
    RBRACKET = 'RBRACKET'
    COLON = 'COLON'
    COMMA = 'COMMA'
    TRUE = 'TRUE'
    FALSE = 'FALSE'
    NULL = 'NULL'
    STRING = 'STRING'
    NUMBER = 'NUMBER'

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return f"<{self.type}: {self.value}>"

# Lexer class to tokenize input
class Lexer:
    def __init__(self, input_string):
        self.input_string = input_string # input of strings
        self.length = len(self.input_string)  # length of input
        self.position = 0  # current position in the input
        self.current_char = self.input_string[self.position] if self.input_string else None  # current character
        self.tokens = [] # store tokens
        self.token_index = 0

    def get_next_token(self):
        if not self.tokens:
            self.tokenize()

        if self.token_index < len(self.tokens):
            token = self.tokens[self.token_index]
            self.token_index += 1
            return token
        else:
            return None

    # method to move to the next character in the input
    def advance(self):
        self.position += 1
        if self.position < len(self.input_string):
            self.current_char = self.input_string[self.position] # moves to next character
        else:
            self.current_char = None

    # method that skips over any white space
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    # method that returns a string token
    def recognize_string(self):
        self.advance()
        result = ''
        while self.current_char is not None and self.current_char != '"':
            result += self.current_char
            self.advance()
        if self.current_char == '"': # closing string
            self.advance()
            return Token(TokenType.STRING, result)
        else:
            print(f"String is unterminated: {self.position}")
            return None

    # method that returns boolean true, false, or null
    def recognize_boolean(self):
        result = ''
        while self.current_char is not None and self.current_char.isalpha():
            result += self.current_char
            self.advance()
        if result == 'true':
            return Token(TokenType.TRUE, result)
        elif result == 'false':
            return Token(TokenType.FALSE, result)
        elif result == 'null':
            return Token(TokenType.NULL, result)
        else:
            # print lexical errors
            print(f"Invalid keyword: '{result}' at position {self.position - len(result)}")
            return None

    # method that recognizes numbers (integers or floats)
    def recognize_number(self):
        result = ''
        if self.current_char == '-': # negative numbers
            result += self.current_char
            self.advance()
        decimal_point = False # track if decimal point is already present

        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                # if a second decimal point is encountered
                if decimal_point:
                    print(f"Invalid number: '{result}' at position {self.position}")
                    return None
                decimal_point = True
            result += self.current_char
            self.advance()

            # check if result is a complete number
            if result == '-' or result == '.' or result == '-.':
                # print lexical error
                print(f"Invalid number: '{result}' at position {self.position - len(result)}")
                return None

        return Token(TokenType.NUMBER, result)

    # method that recognizes symbols
    def recognize_symbol(self):
        symbols = {
            '{': TokenType.LBRACE, '}': TokenType.RBRACE, '[': TokenType.LBRACKET, ']': TokenType.RBRACKET, ':': TokenType.COLON, ',': TokenType.COMMA,
        }
        # match token type
        token_type = symbols.get(self.current_char)
        if token_type:
            token = Token(token_type, self.current_char)
            self.advance()
            return token
        else:
            # print lexical error
            print(f"Invalid character: '{self.current_char}' at position {self.position}")
            self.advance()
            return None

    # method to tokenize input
    def tokenize(self):

        while self.current_char is not None:
            self.skip_whitespace()

            # set token to none
            token = None

            if self.current_char == '"':
                token = self.recognize_string()
            elif self.current_char.isdigit() or self.current_char == '-':
                token = self.recognize_number()
            elif self.current_char.isalpha():
                token = self.recognize_boolean()
            elif self.current_char in ['{', '}', '[', ']', ':', ',']:
                token = self.recognize_symbol()
            else:
                print(f"Invalid character: '{self.current_char}' at position {self.position}")
                self.advance()

            # append token if valid
            if token:
                self.tokens.append(token)

        # return list of tokens
        return self.tokens

# test the scanner
if __name__ == '__main__':
    input_string = '{"grades": [90.8, 85.0, 70.5], "subjects": ["Math", "Science", "History"]}'

    # Initialize Lexer
    lexer = Lexer(input_string)

    # Tokenize the input and print tokens
    tokens = lexer.tokenize()
    for token in tokens:
        print(token)