# main.py
import sys

def evaluate_expression(expression):
    def parse_expression(expr):
        num = 0
        sign = 1
        stack = []
        i = 0
        
        while i < len(expr):
            char = expr[i]
            
            if char.isdigit():
                num = num * 10 + int(char)
            elif char == '+':
                stack.append(sign * num)
                num = 0
                sign = 1
            elif char == '-':
                stack.append(sign * num)
                num = 0
                sign = -1
            i += 1
        
        stack.append(sign * num)
        return sum(stack)

    # Removing spaces from the expression
    expression = expression.replace(" ", "")
    return parse_expression(expression)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py '<expression>'")
        sys.exit(1)
    
    expression = sys.argv[1]
    result = evaluate_expression(expression)
    print(result)
