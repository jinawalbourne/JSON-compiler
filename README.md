# JSON Semantic Analysis

## How to run the code:
1. Open project in IDE
2. Run the scanner program. The scanner class will output the recognized JSON input string and tokenize it (provided in the input_string variable)
3. Copy and paste the scanner result into inputs.txt (inputs.txt is there for testing, I changed the file path to testing/inputs/input_type1.txt for each input/output file)
4. Run the Parser class. If successful, an AST will print onto outputs.txt
5. If an error occurs, an error statement will print onto output.txt specifying its type

## Assumptions:
I assumed that input contains only valid characters and syntax

## Key parts of code:
- Parser class: This class takes a stream of tokens from the Lexer program and builds an AST using JSON grammar
- get_next_token: This method gets the next token from lexer
- eat: This method verifies the expected token type and moves onto next token
- check_numbers: This method takes care of all number rules
- SemanticError class: This class prints an error message with the type and the error
- Node class: This class represents the structure of an AST

## Credits:
-	Supplementary Materials: semantic files shown in class tutorials