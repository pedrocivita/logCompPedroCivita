import sys

class AvaliarConta:
    def __init__(self, expression):
        self.expression = expression

    def avaliar(self):
        if not self.expression.strip():
            return "Erro: Expressão vazia"

        try:
            # Remover espaços desnecessários
            clean_expression = self.expression.replace(" ", "")

            # Verifica se a expressão contém apenas caracteres permitidos (números e operadores de adição/subtração)
            valid_chars = "0123456789+-"
            for char in clean_expression:
                if char not in valid_chars:
                    return f"Erro: Caractere inválido '{char}' na expressão"

            # Verifica erros de sintaxe simples
            if any(op in clean_expression for op in ["++", "--", "+-", "-+"]):
                return "Erro: Sintaxe inválida na expressão"

            if clean_expression[0] in "+-" or clean_expression[-1] in "+-":
                return "Erro: Sintaxe inválida na expressão"

            # Verifica se há números consecutivos sem operador entre eles
            i = 0
            while i < len(clean_expression):
                if clean_expression[i].isdigit():
                    num_start = i
                    while i < len(clean_expression) and clean_expression[i].isdigit():
                        i += 1
                    if i < len(clean_expression) and clean_expression[i].isdigit():
                        return "Erro: Sintaxe inválida na expressão"
                i += 1

            # Avalia a expressão de forma segura
            result = eval(clean_expression)
            return str(result)
        except SyntaxError:
            return "Erro: Sintaxe inválida na expressão"
        except ZeroDivisionError:
            return "Erro: Divisão por zero"
        except Exception as e:
            return f"Erro: {e}"

def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py 'expressão'", file=sys.stderr)
        sys.exit(1)

    expression = sys.argv[1]
    evaluator = AvaliarConta(expression)
    resultado = evaluator.avaliar()
    if resultado.startswith("Erro"):
        print(resultado, file=sys.stderr)
    else:
        print(resultado)

if __name__ == "__main__":
    main()