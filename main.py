# import sys
# import re

# class Calculator:
#     def __init__(self, expression):
#         self.expression = expression
#         self.validate_expression()

#     def validate_expression(self):
#         # Check if the expression contains only valid characters (digits, spaces, +, -)
#         if not re.match(r'^[\d\s\+\-]+$', self.expression):
#             raise ValueError("Invalid characters in expression")
        
#         # Remove spaces for easier validation
#         clean_expression = self.expression.replace(' ', '')

#         # Check for invalid sequences like empty expression, operators at the start or end, or consecutive operators
#         if not clean_expression or clean_expression[0] in '+-' or clean_expression[-1] in '+-':
#             raise ValueError("Invalid expression format: cannot start or end with an operator")
#         if re.search(r'[\+\-]{2,}', clean_expression):
#             raise ValueError("Invalid expression format: consecutive operators")
    
#     def evaluate(self):
#         try:
#             result = eval(self.expression)
#             return result
#         except Exception as e:
#             raise ValueError(f"Error evaluating expression: {e}")

# def main():
#     if len(sys.argv) != 2:
#         print("Usage: python main.py '<expression>'", file=sys.stderr)
#         return
    
#     expression = sys.argv[1]
    
#     try:
#         calculator = Calculator(expression)
#         result = calculator.evaluate()
#         print(result)
#     except ValueError as ve:
#         print(f"Error: {ve}", file=sys.stderr)
#     except Exception as e:
#         print(f"Unexpected error: {e}", file=sys.stderr)

# if __name__ == "__main__":
#     main()

import sys

if len(sys.argv) != 2:
    print("Uso: python main.py 'expressão'", file=sys.stderr)
    sys.exit(1)

expression = sys.argv[1]

if not expression.strip():
    print("Erro: Expressão vazia", file=sys.stderr)
    sys.exit(1)

clean_expression = expression.replace(" ", "")

valid_chars = "0123456789+-"
for char in clean_expression:
    if char not in valid_chars:
        print(f"Erro: Caractere inválido '{char}' na expressão", file=sys.stderr)
        sys.exit(1)

if "+" not in clean_expression and "-" not in clean_expression:
    print("Erro: A expressão deve conter pelo menos um operador de adição ou subtração", file=sys.stderr)
    sys.exit(1)

if any(op in clean_expression for op in ["++", "--", "+-", "-+"]):
    print("Erro: Sintaxe inválida na expressão", file=sys.stderr)
    sys.exit(1)

if clean_expression[0] in "+-" or clean_expression[-1] in "+-":
    print("Erro: Sintaxe inválida na expressão", file=sys.stderr)
    sys.exit(1)

try:
    total = 0
    current_number = ""
    current_operator = "+"

    for char in clean_expression:
        if char.isdigit():
            current_number += char
        else:
            if current_operator == "+":
                total += int(current_number)
            elif current_operator == "-":
                total -= int(current_number)

            current_operator = char
            current_number = ""

    if current_number:
        if current_operator == "+":
            total += int(current_number)
        elif current_operator == "-":
            total -= int(current_number)

    print(total)
except Exception:
    print("Erro: Avaliação falhou", file=sys.stderr)
    sys.exit(1)
