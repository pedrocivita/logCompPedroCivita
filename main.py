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

            # Verifica se a expressão contém apenas caracteres permitidos (números, operadores e parênteses)
            for char in clean_expression:
                if not (char.isdigit() or char in '+-*/().'):
                    return f"Erro: Caractere inválido '{char}' na expressão"
            
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
