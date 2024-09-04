import sys
from abc import ABC, abstractmethod
import re

# Classe PrePro para filtrar comentários
class PrePro:
    @staticmethod
    def filter(code: str) -> str:
        # Remover comentários de linha (--) e blocos de comentários (/* ... */)
        code = re.sub(r'--.*', '', code)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code.strip()

# Classe Node (abstrata) e suas subclasses
class Node(ABC):
    def __init__(self, value=None):
        self.value = value
        self.children = []

    @abstractmethod
    def Evaluate(self):
        pass

class BinOp(Node):
    def __init__(self, value, left, right):
        super().__init__(value)
        self.children = [left, right]

    def Evaluate(self):
        if self.value == 'PLUS':
            return self.children[0].Evaluate() + self.children[1].Evaluate()
        elif self.value == 'MINUS':
            return self.children[0].Evaluate() - self.children[1].Evaluate()
        elif self.value == 'MULT':
            return self.children[0].Evaluate() * self.children[1].Evaluate()
        elif self.value == 'DIV':
            return self.children[0].Evaluate() // self.children[1].Evaluate()

class UnOp(Node):
    def __init__(self, value, child):
        super().__init__(value)
        self.children = [child]

    def Evaluate(self):
        if self.value == 'PLUS':
            return +self.children[0].Evaluate()
        elif self.value == 'MINUS':
            return -self.children[0].Evaluate()

class IntVal(Node):
    def __init__(self, value):
        super().__init__(value)

    def Evaluate(self):
        return self.value

class NoOp(Node):
    def Evaluate(self):
        return 0

# Classe Token
class Token:
    def __init__(self, type: str, value: int):
        self.type = type
        self.value = value

# Classe Tokenizer
class Tokenizer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.next = None

    def selectNext(self):
        while self.position < len(self.source) and self.source[self.position] == ' ':
            self.position += 1

        if self.position >= len(self.source):
            self.next = Token('EOF', None)
            return

        current_char = self.source[self.position]

        if current_char.isdigit():
            value = 0
            while self.position < len(self.source) and self.source[self.position].isdigit():
                value = value * 10 + int(self.source[self.position])
                self.position += 1
            self.next = Token('INT', value)
        elif current_char == '+':
            self.next = Token('PLUS', None)
            self.position += 1
        elif current_char == '-':
            self.next = Token('MINUS', None)
            self.position += 1
        elif current_char == '*':
            self.next = Token('MULT', None)
            self.position += 1
        elif current_char == '/':
            self.next = Token('DIV', None)
            self.position += 1
        elif current_char == '(':
            self.next = Token('LPAREN', None)
            self.position += 1
        elif current_char == ')':
            self.next = Token('RPAREN', None)
            self.position += 1
        else:
            raise ValueError(f"Unexpected character: {current_char}")

# Classe Parser
class Parser:
    @staticmethod
    def parseExpression():
        left = Parser.parseTerm()

        while Parser.tokenizer.next.type in ['PLUS', 'MINUS']:
            op = Parser.tokenizer.next.type
            Parser.tokenizer.selectNext()
            right = Parser.parseTerm()
            left = BinOp(op, left, right)

        return left

    @staticmethod
    def parseTerm():
        left = Parser.parseFactor()

        while Parser.tokenizer.next.type in ['MULT', 'DIV']:
            op = Parser.tokenizer.next.type
            Parser.tokenizer.selectNext()
            right = Parser.parseFactor()
            left = BinOp(op, left, right)

        return left

    @staticmethod
    def parseFactor():
        # Lidar com múltiplos operadores unários
        op_count = 0

        while Parser.tokenizer.next.type in ['PLUS', 'MINUS']:
            if Parser.tokenizer.next.type == 'MINUS':
                op_count += 1
            Parser.tokenizer.selectNext()

        node = None
        if Parser.tokenizer.next.type == 'INT':
            node = IntVal(Parser.tokenizer.next.value)
            Parser.tokenizer.selectNext()
        elif Parser.tokenizer.next.type == 'LPAREN':
            Parser.tokenizer.selectNext()
            node = Parser.parseExpression()
            if Parser.tokenizer.next.type != 'RPAREN':
                raise ValueError("Syntax Error: Expected ')'")
            Parser.tokenizer.selectNext()
        else:
            raise ValueError("Syntax Error: Invalid token")

        # Aplicar o sinal unário, se necessário
        if op_count % 2 == 1:
            node = UnOp('MINUS', node)

        return node

    @staticmethod
    def run(code: str):
        Parser.tokenizer = Tokenizer(code)
        Parser.tokenizer.selectNext()
        return Parser.parseExpression()

# Programa principal
def main():
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
        with open(file_name, 'r') as file:
            code = file.read()
    else:
        print("Please provide a .lua file.")
        return

    try:
        filtered_code = PrePro.filter(code)
        tree = Parser.run(filtered_code)
        result = tree.Evaluate()
        print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
