import sys
from abc import ABC, abstractmethod
import re

class Token:
    def __init__(self, type: str, value: int):
        self.type = type
        self.value = value
class Tokenizer:
    def __init__(self, source):
        self.source = source
        self.position = 0
        self.next = None

    def selectNext(self):
        # Ignora espaços em branco
        while self.position < len(self.source) and self.source[self.position].isspace():
            self.position += 1

        # Fim do código fonte
        if self.position >= len(self.source):
            self.next = Token("EOF", None)
            return

        current_char = self.source[self.position]

        # Detecta números inteiros
        if current_char.isdigit():
            num_value = 0
            while self.position < len(self.source) and self.source[self.position].isdigit():
                num_value = num_value * 10 + int(self.source[self.position])
                self.position += 1
            self.next = Token("INT", num_value)
            return

        # Verifica operadores e operadores inválidos
        if current_char in '+-*/':
            # Verifica se há dois asteriscos '**' (operador inválido)
            if current_char == '*' and self.position + 1 < len(self.source) and self.source[self.position + 1] == '*':
                self.position += 2
                raise Exception("Invalid operator: '**'")
            # Verifica se há dois slashes '//' (operador inválido)
            if current_char == '/' and self.position + 1 < len(self.source) and self.source[self.position + 1] == '/':
                self.position += 2
                raise Exception("Invalid operator: '//'")
            self.next = Token("OPERATOR", current_char)
            self.position += 1
            return

        # Detecta parênteses
        if current_char in '()':
            self.next = Token("PARENTHESIS", current_char)
            self.position += 1
            return

        # Ignora caracteres que não são parte de expressões aritméticas
        if current_char.isalpha() or current_char == '=':
            while self.position < len(self.source) and (self.source[self.position].isalpha() or self.source[self.position].isdigit() or self.source[self.position] == '='):
                self.position += 1
            self.selectNext()  # Tenta novamente após ignorar a palavra
            return

        # Levanta um erro se um caractere inesperado for encontrado
        raise Exception(f"Unexpected character: {current_char}")

class Parser:
    @staticmethod
    def parseExpression():
        result = Parser.parseTerm()

        while Parser.tokenizer.next.type in ['PLUS', 'MINUS']:
            op_type = Parser.tokenizer.next.type
            Parser.tokenizer.selectNext()
            result2 = Parser.parseTerm()

            if op_type == 'PLUS':
                result = BinOp('+', result, result2)
            elif op_type == 'MINUS':
                result = BinOp('-', result, result2)

        return result

    @staticmethod
    def parseTerm():
        result = Parser.parseFactor()

        while Parser.tokenizer.next.type in ['MULT', 'DIV']:
            op_type = Parser.tokenizer.next.type
            Parser.tokenizer.selectNext()
            result2 = Parser.parseFactor()

            if op_type == 'MULT':
                result = BinOp('*', result, result2)
            elif op_type == 'DIV':
                result = BinOp('/', result, result2)

        return result

    @staticmethod
    def parseFactor():
        if Parser.tokenizer.next.type == 'PLUS':
            Parser.tokenizer.selectNext()
            return UnOp('+', Parser.parseFactor())
        elif Parser.tokenizer.next.type == 'MINUS':
            Parser.tokenizer.selectNext()
            return UnOp('-', Parser.parseFactor())
        elif Parser.tokenizer.next.type == 'LPAREN':
            Parser.tokenizer.selectNext()
            result = Parser.parseExpression()
            if Parser.tokenizer.next.type != 'RPAREN':
                raise ValueError("Syntax Error: Expected ')'")
            Parser.tokenizer.selectNext()
            return result
        elif Parser.tokenizer.next.type == 'INT':
            result = IntVal(Parser.tokenizer.next.value)
            Parser.tokenizer.selectNext()
            return result
        else:
            raise ValueError("Syntax Error: Expected INT or '('")

    @staticmethod
    def run(code: str):
        try:
            # Remove comentários usando a classe PrePro
            code = PrePro.filter(code)
            
            Parser.tokenizer = Tokenizer(code)
            Parser.tokenizer.selectNext()
            ast = Parser.parseExpression()

            if Parser.tokenizer.next.type != 'EOF':
                raise ValueError("Syntax Error: Expected EOF at the end of expression")

            # Executa o método Evaluate na raiz da árvore (AST)
            result = ast.Evaluate()
            print(result)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


class PrePro:
    @staticmethod
    def filter(code: str) -> str:
        # Remove comentários do tipo /* */ e também // (caso exista)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        code = re.sub(r'//.*', '', code)
        return code


# Classe abstrata Node
class Node(ABC):
    def __init__(self, value=None):
        self.value = value
        self.children = []

    @abstractmethod
    def Evaluate(self):
        pass


# Classe BinOp - Operação binária (2 filhos)
class BinOp(Node):
    def __init__(self, value, left, right):
        super().__init__(value)
        self.children = [left, right]

    def Evaluate(self):
        # Executa recursivamente o método Evaluate nos filhos
        left_val = self.children[0].Evaluate()
        right_val = self.children[1].Evaluate()
        if self.value == '+':
            return left_val + right_val
        elif self.value == '-':
            return left_val - right_val
        elif self.value == '*':
            return left_val * right_val
        elif self.value == '/':
            if right_val == 0:
                raise ValueError("Division by zero")
            return left_val // right_val
        else:
            raise ValueError(f"Invalid operation: {self.value}")


# Classe UnOp - Operação unária (1 filho)
class UnOp(Node):
    def __init__(self, value, child):
        super().__init__(value)
        self.children = [child]

    def Evaluate(self):
        # Executa recursivamente o método Evaluate no filho
        child_val = self.children[0].Evaluate()
        if self.value == '+':
            return child_val
        elif self.value == '-':
            return -child_val
        else:
            raise ValueError(f"Invalid unary operation: {self.value}")


# Classe IntVal - Valor inteiro (sem filhos)
class IntVal(Node):
    def __init__(self, value):
        super().__init__(value)

    def Evaluate(self):
        # Retorna o próprio valor
        return self.value


# Classe NoOp - Operação nula (sem filhos)
class NoOp(Node):
    def Evaluate(self):
        return None


def main():
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
        try:
            with open(file_name, 'r') as file:
                code = file.read()
        except FileNotFoundError:
            print(f"Error: File '{file_name}' not found.", file=sys.stderr)
            sys.exit(1)
    else:
        print("Error: No input file provided.", file=sys.stderr)
        sys.exit(1)

    # Executa o compilador com o código do arquivo
    Parser.run(code)


if __name__ == "__main__":
    main()
