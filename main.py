import sys

class AvaliarConta:
    def __init__(self, expression):
        self.expression = expression

    def avaliar(self):
        if not self.expression.strip():
            return "Erro: Expressão vazia"

        try:
            clean_expression = self.expression.replace(" ", "")

            for char in clean_expression:
                if not (char.isdigit() or char in '+-*/().'):
                    return f"Erro: Caractere inválido '{char}' na expressão"
            
            result = eval(clean_expression)
            return result
        except SyntaxError:
            return "Erro: Sintaxe inválida na expressão"
        except ZeroDivisionError:
            return "Erro: Divisão por zero"
        except Exception as e:
            return f"Erro: {e}"

def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py 'expressão'")
        sys.exit(1)

    expression = sys.argv[1]
    evaluator = AvaliarConta(expression)
    print(evaluator.avaliar())

if __name__ == "__main__":
    main()