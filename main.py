import sys
from abc import ABC, abstractmethod
import re

class Token:
    def __init__(self, type: str, value: int):
        self.type = type
        self.value = value

class Tokenizer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.next = None

    def selectNext(self):
        # Ignora espaços em branco
        while self.position < len(self.source) and self.source[self.position] == ' ':
            self.position += 1

        if self.position >= len(self.source):
            self.next = Token('EOF', None)
            return

        current_char = self.source[self.position]

        # Detecta números inteiros
        if current_char.isdigit():
            value = 0
            while self.position < len(self.source) and self.source[self.position].isdigit():
                value = value * 10 + int(self.source[self.position])
                self.position += 1
            self.next = Token('INT', value)

        # Detecta identificadores (variáveis ou 'printf')
        elif current_char.isalpha():
            identifier = ''
            while self.position < len(self.source) and self.source[self.position].isalnum():
                identifier += self.source[self.position]
                self.position += 1
            if identifier == 'printf':
                self.next = Token('PRINT', None)
            else:
                self.next = Token('ID', identifier)

        # Operadores básicos
        elif current_char == '+':
            self.next = Token('PLUS', None)
            self.position += 1

        elif current_char == '-':
            self.next = Token('MINUS', None)
            self.position += 1

        elif current_char == '*':
            if self.position + 1 < len(self.source) and self.source[self.position + 1] == '*':
                self.position += 2
                raise ValueError("Invalid operator: '**'")
            self.next = Token('MULT', None)
            self.position += 1

        elif current_char == '/':
            if self.position + 1 < len(self.source) and self.source[self.position + 1] == '/':
                self.position += 2
                raise ValueError("Invalid operator: '//'")
            self.next = Token('DIV', None)
            self.position += 1

        elif current_char == '=':
            self.next = Token('ASSIGN', None)
            self.position += 1

        elif current_char == ';':
            self.next = Token('SEMICOLON', None)
            self.position += 1

        # Parênteses
        elif current_char == '(':
            self.next = Token('LPAREN', None)
            self.position += 1

        elif current_char == ')':
            self.next = Token('RPAREN', None)
            self.position += 1

        else:
            raise ValueError(f"Unexpected character: {current_char}")

class Parser:
    @staticmethod
    def parseStatement():
        if Parser.tokenizer.next.type == 'ID':
            identifier = Parser.tokenizer.next.value
            Parser.tokenizer.selectNext()
            if Parser.tokenizer.next.type == 'ASSIGN':
                Parser.tokenizer.selectNext()
                expr = Parser.parseExpression()
                return Assignment(identifier, expr)
        elif Parser.tokenizer.next.type == 'PRINT':
            Parser.tokenizer.selectNext()
            if Parser.tokenizer.next.type == 'LPAREN':
                Parser.tokenizer.selectNext()
                expr = Parser.parseExpression()
                if Parser.tokenizer.next.type != 'RPAREN':
                    raise ValueError("Syntax Error: Expected ')'")
                Parser.tokenizer.selectNext()
                return Print(expr)
        else:
            return NoOp()

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
        elif Parser.tokenizer.next.type == 'ID':
            result = Identifier(Parser.tokenizer.next.value)
            Parser.tokenizer.selectNext()
            return result
        else:
            raise ValueError("Syntax Error: Expected INT or '('")

    @staticmethod
    def run(code: str):
        try:
            code = PrePro.filter(code)
            Parser.tokenizer = Tokenizer(code)
            Parser.tokenizer.selectNext()
            ast = []
            while Parser.tokenizer.next.type != 'EOF':
                ast.append(Parser.parseStatement())  # Coleta múltiplos statements
                if Parser.tokenizer.next.type == 'SEMICOLON':
                    Parser.tokenizer.selectNext()  # Avança após o ponto e vírgula
            return ast
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

class PrePro:
    @staticmethod
    def filter(code: str) -> str:
        # Remove comentários do tipo /* */, mas não interfere em // que não são comentários
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code

# Classe Node (abstrata) e suas subclasses
class Node(ABC):
    def __init__(self, value=None):
        self.value = value
        self.children = []

    @abstractmethod
    def Evaluate(self, symbol_table):
        pass

# Classe BinOp - Operação binária (2 filhos)
class BinOp(Node):
    def __init__(self, value, left, right):
        super().__init__(value)
        self.children = [left, right]

    def Evaluate(self, symbol_table):
        left_val = self.children[0].Evaluate(symbol_table)
        right_val = self.children[1].Evaluate(symbol_table)
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

# Classe UnOp - Operação unária (1 filho)
class UnOp(Node):
    def __init__(self, value, child):
        super().__init__(value)
        self.children = [child]

    def Evaluate(self, symbol_table):
        child_val = self.children[0].Evaluate(symbol_table)
        if self.value == '+':
            return child_val
        elif self.value == '-':
            return -child_val

# Classe IntVal - Valor inteiro (sem filhos)
class IntVal(Node):
    def __init__(self, value):
        super().__init__(value)

    def Evaluate(self, symbol_table):
        return self.value

# Classe NoOp - Operação nula (sem filhos)
class NoOp(Node):
    def Evaluate(self, symbol_table):
        return None

class SymbolTable:
    def __init__(self):
        self.symbols = {}

    def get(self, identifier):
        if identifier in self.symbols:
            return self.symbols[identifier]
        else:
            raise ValueError(f"Variable '{identifier}' not found.")

    def set(self, identifier, value):
        self.symbols[identifier] = value

# Novos Nós para as variáveis, atribuições e o comando printf
class Identifier(Node):
    def __init__(self, value):
        super().__init__(value)

    def Evaluate(self, symbol_table):
        return symbol_table.get(self.value)

class Assignment(Node):
    def __init__(self, identifier, expression):
        super().__init__()
        self.identifier = identifier
        self.children = [expression]

    def Evaluate(self, symbol_table):
        value = self.children[0].Evaluate(symbol_table)
        symbol_table.set(self.identifier, value)

class Print(Node):
    def __init__(self, expression):
        super().__init__()
        self.children = [expression]

    def Evaluate(self, symbol_table):
        value = self.children[0].Evaluate(symbol_table)
        print(value)

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

    try:
        # Remove comentários do código
        filtered_code = PrePro.filter(code)

        # Executa o Parser e gera a AST (lista de statements)
        ast = Parser.run(filtered_code)

        # Criação da tabela de símbolos (SymbolTable)
        symbol_table = SymbolTable()

        # Executa cada statement na AST
        for statement in ast:
            statement.Evaluate(symbol_table)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
