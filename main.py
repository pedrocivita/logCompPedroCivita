import sys
import re

class Calculator:
    def __init__(self, expression):
        self.expression = expression
        self.validate_expression()

    def validate_expression(self):
        # Check if the expression contains only valid characters (digits, spaces, +, -)
        if not re.match(r'^[\d\s\+\-]+$', self.expression):
            raise ValueError("Invalid characters in expression")
        
        # Remove spaces for easier validation
        clean_expression = self.expression.replace(' ', '')

        # Check for invalid sequences like empty expression, operators at the start or end, or consecutive operators
        if not clean_expression or clean_expression[0] in '+-' or clean_expression[-1] in '+-':
            raise ValueError("Invalid expression format: cannot start or end with an operator")
        if re.search(r'[\+\-]{2,}', clean_expression):
            raise ValueError("Invalid expression format: consecutive operators")
    
    def evaluate(self):
        try:
            result = eval(self.expression)
            return result
        except Exception as e:
            raise ValueError(f"Error evaluating expression: {e}")

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
