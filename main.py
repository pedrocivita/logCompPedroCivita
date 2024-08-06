import sys

class Calculator:
    def __init__(self, expression):
        self.expression = expression
        self.tokens = self.tokenize(expression)

    def tokenize(self, expression):
        tokens = []
        current_number = []
        
        for char in expression:
            if char.isdigit():
                current_number.append(char)
            elif char in '+-':
                if not tokens and not current_number:
                    raise ValueError(f"Invalid expression: starts with operator {char}")
                if current_number:
                    tokens.append(''.join(current_number))
                    current_number = []
                if tokens and tokens[-1] in '+-':
                    raise ValueError(f"Invalid sequence of operators: {tokens[-1]}{char}")
                tokens.append(char)
            elif char.isspace():
                raise ValueError("Invalid character found: space")
            else:
                raise ValueError(f"Invalid character found: {char}")
        
        if current_number:
            tokens.append(''.join(current_number))
        
        if not tokens or tokens[-1] in '+-':
            raise ValueError(f"Invalid expression: ends with operator {tokens[-1]}")
        
        return tokens

    def evaluate(self):
        def helper(index):
            total = 0
            current_operator = '+'
            while index < len(self.tokens):
                token = self.tokens[index]
                if token.isdigit():
                    number = int(token)
                    if current_operator == '+':
                        total += number
                    elif current_operator == '-':
                        total -= number
                else:
                    current_operator = token
                index += 1
            return total
        
        return helper(0)

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py '<expression>'", file=sys.stderr)
        return
    
    expression = sys.argv[1]
    
    try:
        calculator = Calculator(expression)
        result = calculator.evaluate()
        print(result)
    except ValueError as ve:
        print(f"Error: {ve}", file=sys.stderr)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
