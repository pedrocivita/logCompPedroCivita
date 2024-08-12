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
