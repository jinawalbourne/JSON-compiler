# Jina Walbourne
# B00930225

# import statements from scanner.py
from scanner import Lexer, TokenType, Token

# class that handles semantic errors from type, token, and error message
class SemanticError(Exception):
    def __init__(self, error_type, token, message):
        self.error_type = error_type
        self.token = token
        self.message = message
        super().__init__(f"Error: {error_type} at {token.value}: {message}")

# class Node representing a node in AST
class Node:
    def __init__(self, label=None, value=None, is_leaf=False):
        self.label = label  # node label
        self.value = value  # leaf node value
        self.children = []  # list of child nodes
        self.is_leaf = is_leaf  # check if node is a leaf

    # method that appends a child node to current node
    def add_child(self, child):
        self.children.append(child)

    # method that prints tree
    def print_tree(self, depth=0):
        indent = " " * depth
        if self.is_leaf:
            print(f"{indent}Leaf: {self.label} -> {self.value}")
        else:
            print(f"{indent}Node: {self.label}")
            for child in self.children:
                child.print_tree(depth + 1)

# initializes parser from lexer
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = None
        self.print_error = [] # used to store errors
        self.get_next_token() # used to get next token

    # method that gets next token from lexer
    def get_next_token(self):
        self.current_token = self.lexer.get_next_token()

    # method that verifies and reads in expected token
    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.get_next_token()
        else:
            # print error message for incorrect token type
            self.print_error.append(f"Error: Expected {token_type} but instead got {self.current_token.type}.")
            raise SemanticError(f"Error: Invalid token", self.current_token, f"Expected {token_type}.")

    # method that starts parsing JSON input and returns root node of AST
    def parse(self):
        ast = self.value()
        if self.current_token is not None:
            self.print_error.append(f"Error: Unexpected token {self.current_token.type}.")
        return ast

    # method that parses JSON values STRING, NUMBER, BOOLEAN, NULL, OBJECT, and ARRAY
    def value(self):
        if self.current_token.type == TokenType.STRING:
            return self.leaf("STRING")  # returns as string leaf node
        elif self.current_token.type == TokenType.NUMBER:
            self.check_number(self.current_token)
            return self.leaf("NUMBER")  # returns as number leaf node
        elif self.current_token.type == TokenType.TRUE:
            return self.leaf("BOOL", True)  # returns as boolean leaf node
        elif self.current_token.type == TokenType.FALSE:
            return self.leaf("BOOL", False)  # returns as boolean leaf node
        elif self.current_token.type == TokenType.NULL:
            return self.leaf("NULL", None)  # returns as null leaf node
        elif self.current_token.type == TokenType.LBRACKET:
            return self.array()  # returns as array node
        elif self.current_token.type == TokenType.LBRACE:
            return self.object()  # returns as object node
        else:
            # print error message for invalid token type
            self.print_error.append(f"Error: Invalid token {self.current_token.type}.")
            return None

    # method that makes a leaf node in AST and returns leaf node
    def leaf(self, label, value=None):
        value = value if value is not None else self.current_token.value
        if label == "STRING" and value in ["true", "false", "null"]:
            # checks for words reserved as strings (Type 7)
            self.print_error.append(f"Error Type 7 at {value}: Reserved Words as Strings.")
            self.eat(self.current_token.type)
            return None
        self.eat(self.current_token.type)
        return Node(label=label, value=value, is_leaf=True)

    # method that parses objects
    def object(self):
        # read in opening brace
        self.eat(TokenType.LBRACE)
        obj_node = Node(label="OBJECT")
        keys = set()  # set keys to track in dict

        # loop through tokens and parse each key-value node
        while self.current_token and self.current_token.type != TokenType.RBRACE:
            # add parsed key-value pair as a child of object node
            pair_node = self.pair(keys)
            obj_node.add_child(pair_node)

            # if token read is a comma, read it
            if self.current_token and self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
            elif self.current_token and self.current_token.type != TokenType.RBRACE:
                # prints an error message for missing objects
                self.print_error.append(
                    f"Error: Expected 'COMMA' or 'RBRACE' but found {self.current_token.type}.")
                return None

        # read in closing brace
        self.eat(TokenType.RBRACE)
        return obj_node

    # method that parses arrays
    def array(self):

        # read in opening bracket
        self.eat(TokenType.LBRACKET)
        array_node = Node(label="ARRAY")
        types = set() # tracks the type of element in array

        # loop through tokens until closing bracket is reached
        while self.current_token and self.current_token.type != TokenType.RBRACKET:
            # add parsed value as a child of array node
            value_node = self.value()
            if value_node:
                array_node.add_child(value_node)

            # if element types are not the same, print an error message (Type 6)
            if value_node.label not in types and types:
                self.print_error.append(f"Error Type 6 at {value_node.value}: Consistent Types for List Elements.")
                while self.current_token and self.current_token.type != TokenType.RBRACKET:
                    self.eat(self.current_token.type)
                break

            types.add(value_node.label)

            # read in commas between elements
            if self.current_token and self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
            elif self.current_token and self.current_token.type != TokenType.RBRACKET:
                # checks for consistent types in an array (Type 6)
                self.print_error.append(f"Error Type 6 at {self.current_token.value}: Consistent Types for List Elements.")
                while self.current_token and self.current_token.type != TokenType.RBRACKET:
                    self.eat(self.current_token.type)  # consume rest of input
                break
        if self.current_token and self.current_token.type == TokenType.RBRACKET:
            self.eat(TokenType.RBRACKET) # read in closing bracket
        else:
            # print an error if closing bracket is missing
            self.print_error.append(f"Error Type 6 at {self.current_token.value}: Consistent Types for List Elements.")
        return array_node

    # method that parses key-value pairs
    def pair(self, keys):
        # store and read in string token
        if self.current_token.type != TokenType.STRING:
            # checks for missing key (Type 2)
            self.print_error.append(f"Error Type 2 at {self.current_token.value}: Empty Key.")
            self.eat(self.current_token.type) # consume invalid error
            return None

        # initialize key value
        key = self.current_token.value.strip()
        if not key:
            # checks for missing key (Type 2)
            self.print_error.append(f"Error Type 2 at {self.current_token.value}: Empty Key.")
            self.eat(self.current_token.type)  # consume invalid error
            if self.current_token.type == TokenType.COLON:
                self.eat(TokenType.COLON)  # skip colon
            if self.current_token.type not in [TokenType.COMMA, TokenType.RBRACE]:
                self.eat(self.current_token.type)  # skip comma and right brace
            return None

        self.eat(TokenType.STRING)

        # check for reserved keys in dictionary (Type 4)
        if key in ["true", "false", "null"]:
            self.print_error.append(f"Error Type 4 at {key}: Reserved Words as Dictionary Key.")
            self.eat(self.current_token.type)  # consume invalid error
            if self.current_token.type == TokenType.COLON:
                self.eat(TokenType.COLON)  # skip colon
            if self.current_token.type not in [TokenType.COMMA, TokenType.RBRACE]:
                self.eat(self.current_token.type)  # skip comma and right brace
            return None

        # check for duplicate keys (Type 5)
        if key in keys:
            self.print_error.append(f"Error Type 5 at {key}: No Duplicate Keys in Dictionary.")
            self.eat(self.current_token.type)  # consume invalid error
            if self.current_token.type == TokenType.COLON:
                self.eat(TokenType.COLON)  # skip colon
            if self.current_token.type not in [TokenType.COMMA, TokenType.RBRACE]:
                self.eat(self.current_token.type)  # skip comma and right brace
            return None

        keys.add(key) # add key to keys that's been read in
        self.eat(TokenType.COLON) # read in colon
        value_node = self.value() # parse value
        pair_node = Node(label="PAIR") # create a node for key-value pair
        pair_node.add_child(Node(label="KEY", value=key, is_leaf=True)) # add key node
        pair_node.add_child(value_node) # add value node
        return pair_node

    # method that checks semantic rules for numbers
    def check_number(self, token):
        value = token.value

        # check for invalid decimal number (Type 1)
        if value.startswith(".") or value.endswith("."):
            self.print_error.append(f"Error Type 1 at {value}: Invalid Numbers.")
        # check for invalid number starting with 0 (Type 3)
        if value.startswith("0") and len(value) > 1 and not value.startswith("0."):
            self.print_error.append(f"Error Type 3 at {value}: Invalid Numbers.")
        # check for invalid numbers starting with + (Type 3)
        if value.startswith("+"):
            self.print_error.append(f"Error Type 3 at {value}: Invalid Numbers.")

    # method to read inputs from a file path
    def file_inputs(file_path):
        tokens = []
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                # keep ast in line
                if line.startswith('<') and line.endswith('>'):
                    line_content = line[1:-1]
                    parts = line_content.split(':', maxsplit=1)
                    token_type = parts[0].strip()
                    token_value = parts[1].strip() if len(parts) > 1 else None
                    tokens.append(Token(token_type, token_value))
                else:
                    print(f"Error: Invalid token format.")
        return tokens

    # method that prints parse tree onto output file
    def file_outputs(file_path, parse_tree):
        with open(file_path, "w") as f:
            def display_tree(node, depth=0):
                indent = " " * depth
                if node.is_leaf:
                    f.write(f"{indent}Leaf: {node.label} -> {node.value}\n")
                else:
                    f.write(f"{indent}Node: {node.label}\n")
                    for child in node.children:
                        display_tree(child, depth + 2)

            f.write("Abstract Syntax Tree:\n")
            display_tree(parse_tree)

# test the parser
if __name__ == '__main__':

    input_file = "tests/inputs/input_type1.txt"
    output_file = "tests/outputs/output_type1.txt"

    tokens = Parser.file_inputs(input_file)
    lexer = Lexer("")
    lexer.tokens = tokens

    parser = Parser(lexer)
    parse_tree = parser.parse()

    if parser.print_error:
        with open(output_file, "w") as f:
            f.write("Semantic errors:\n")
            for error in parser.print_error:
                f.write(f"-{error}\n")
        print(f"Errors: Printed on output file.")
    else:
        Parser.file_outputs(output_file, parse_tree)
        print(f"Abstract Syntax Tree is printed onto output file.")