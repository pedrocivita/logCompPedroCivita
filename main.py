import sys
from abc import ABC, abstractmethod
import re

class Token:
    def __init__(self, type: str, value: int):
        self.type = type
        self.value = value

class Tokenizer:
    def __init__(self, source):
        self.source = source.strip()
        self.position = 0
        self.next = None
        self.selectNext()

    def selectNext(self):
        # Pula espaços em branco
        while self.position < len(self.source) and self.source[self.position].isspace():
            self.position += 1

        if self.position == len(self.source):
            self.next = Token('EOF', None)
            return

        current_char = self.source[self.position]

        # Reconhece números inteiros
        if current_char.isdigit():
            num = ''
            while self.position < len(self.source) and self.source[self.position].isdigit():
                num += self.source[self.position]
                self.position += 1
            self.next = Token('INT', int(num))
        
        # Reconhece identificadores, palavras reservadas e funções especiais
        elif current_char.isalpha() or current_char == '_':
            identifier = ''
            while self.position < len(self.source) and (self.source[self.position].isalnum() or self.source[self.position] == '_'):
                identifier += self.source[self.position]
                self.position += 1
            
            # Adicionando suporte para palavras reservadas como if, while, printf, e scanf
            if identifier in ['printf', 'if', 'while', 'scanf']:
                self.next = Token('RESERVED', identifier)
            else:
                self.next = Token('ID', identifier)

        # Reconhece operadores, incluindo relacionais e booleanos
        elif current_char in '+-*/(){}=;><!&|':
            if self.source[self.position:self.position+2] in ['<=', '>=', '==', '!=', '&&', '||']:
                self.next = Token('OPERATOR', self.source[self.position:self.position+2])
                self.position += 2
            else:
                self.next = Token('OPERATOR', current_char)
                self.position += 1

        else:
            raise Exception(f"Unexpected character: {current_char}")

class Parser:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    @staticmethod
    def run(code):
        Parser.tokenizer = Tokenizer(code)
        result = Parser.parseBlock()
        if Parser.tokenizer.next.type != 'EOF':
            raise Exception("Unexpected data after block")
        return result

    @staticmethod
    def parseBlock():
        if Parser.tokenizer.next.value != '{':
            raise Exception("Expected '{' at the start of block")
        
        Parser.tokenizer.selectNext()  # Consome o '{'

        statements = []

        # Continue a consumir statements até encontrar '}'
        while Parser.tokenizer.next.value != '}':
            if Parser.tokenizer.next.type == 'EOF':
                raise Exception("Expected '}' at the end of block")
            statements.append(Parser.parseStatement())

        Parser.tokenizer.selectNext()  # Consome o '}'

        return Block(statements)


    @staticmethod
    def parseStatement():
        # Ignorar múltiplos ';'
        while Parser.tokenizer.next.value == ';':
            Parser.tokenizer.selectNext()

        if Parser.tokenizer.next.type == 'ID':
            identifier = Parser.tokenizer.next.value
            Parser.tokenizer.selectNext()
            if Parser.tokenizer.next.value == '=':
                Parser.tokenizer.selectNext()
                expr = Parser.parseExpression()
                if Parser.tokenizer.next.value == ';':
                    Parser.tokenizer.selectNext()
                    return Assignment(identifier, expr)
                else:
                    raise Exception("Expected ';' after expression")
            else:
                raise Exception("Expected '=' after identifier")

        elif Parser.tokenizer.next.value == 'printf':
            Parser.tokenizer.selectNext()
            if Parser.tokenizer.next.value == '(':
                Parser.tokenizer.selectNext()
                expr = Parser.parseExpression()
                if Parser.tokenizer.next.value == ')':
                    Parser.tokenizer.selectNext()
                    if Parser.tokenizer.next.value == ';':
                        Parser.tokenizer.selectNext()
                        return Print(expr)
                    else:
                        raise Exception("Expected ';' after printf")
                else:
                    raise Exception("Expected ')' after printf expression")
            else:
                raise Exception("Expected '(' after printf")

        # Suporte a scanf()
        elif Parser.tokenizer.next.value == 'scanf':
            Parser.tokenizer.selectNext()
            if Parser.tokenizer.next.value == '(':
                Parser.tokenizer.selectNext()
                if Parser.tokenizer.next.value == ')':
                    Parser.tokenizer.selectNext()
                    if Parser.tokenizer.next.value == ';':
                        Parser.tokenizer.selectNext()
                        return ScanfNode()
                    else:
                        raise Exception("Expected ';' after scanf")
                else:
                    raise Exception("Expected ')' after scanf")
            else:
                raise Exception("Expected '(' after scanf")

        elif Parser.tokenizer.next.value == 'if':
            Parser.tokenizer.selectNext()
            if Parser.tokenizer.next.value == '(':
                Parser.tokenizer.selectNext()
                condition = Parser.parseExpression()
                if Parser.tokenizer.next.value == ')':
                    Parser.tokenizer.selectNext()
                    true_block = Parser.parseStatement()
                    if Parser.tokenizer.next.value == 'else':
                        Parser.tokenizer.selectNext()
                        false_block = Parser.parseStatement()
                        return IfNode(condition, true_block, false_block)
                    return IfNode(condition, true_block)
                else:
                    raise Exception("Expected ')' after condition")
            else:
                raise Exception("Expected '(' after 'if'")

        elif Parser.tokenizer.next.value == 'while':
            Parser.tokenizer.selectNext()
            if Parser.tokenizer.next.value == '(':
                Parser.tokenizer.selectNext()
                condition = Parser.parseExpression()
                if Parser.tokenizer.next.value == ')':
                    Parser.tokenizer.selectNext()
                    body = Parser.parseStatement()
                    return WhileNode(condition, body)
                else:
                    raise Exception("Expected ')' after condition")
            else:
                raise Exception("Expected '(' after 'while'")

        elif Parser.tokenizer.next.value == '{':
            return Parser.parseBlock()

        else:
            if Parser.tokenizer.next.type != 'EOF':
                raise Exception(f"Unexpected token: {Parser.tokenizer.next.value}")
            return NoOp()


    @staticmethod
    def parseExpression():
        result = Parser.parseTerm()

        while Parser.tokenizer.next.type == 'OPERATOR' and Parser.tokenizer.next.value in ('+', '-', '==', '!=', '>', '<', '>=', '<=', '&&', '||'):
            op = Parser.tokenizer.next.value
            Parser.tokenizer.selectNext()
            new_node = BinOp(op)
            new_node.add_child(result)
            new_node.add_child(Parser.parseTerm())
            result = new_node

        return result


    @staticmethod
    def parseTerm():
        result = Parser.parseFactor()
        while Parser.tokenizer.next.type == 'OPERATOR' and Parser.tokenizer.next.value in ('*', '/'):
            op = Parser.tokenizer.next.value
            Parser.tokenizer.selectNext()
            new_node = BinOp(op)
            new_node.add_child(result)
            new_node.add_child(Parser.parseFactor())
            result = new_node
        return result

    @staticmethod
    def parseFactor():
        unary = 1
        logical_not = False  # Para lidar com o operador `!`

        while Parser.tokenizer.next.type == 'OPERATOR' and Parser.tokenizer.next.value in ('-', '+', '!'):
            if Parser.tokenizer.next.value == '-':
                unary *= -1  # Inverte o sinal para números negativos
            elif Parser.tokenizer.next.value == '!':
                logical_not = not logical_not  # Define se devemos aplicar negação lógica
            Parser.tokenizer.selectNext()

        if Parser.tokenizer.next.value == '(':
            Parser.tokenizer.selectNext()
            result = Parser.parseExpression()
            if Parser.tokenizer.next.value != ')':
                raise Exception("Missing closing parenthesis")
            Parser.tokenizer.selectNext()
            if unary == -1:
                result = UnOp('-', result)
            if logical_not:
                result = UnOp('!', result)
            return result

        elif Parser.tokenizer.next.type == 'INT':
            result = IntVal(Parser.tokenizer.next.value * unary)
            Parser.tokenizer.selectNext()
            if logical_not:
                result = UnOp('!', result)
            return result

        elif Parser.tokenizer.next.type == 'ID':
            result = Identifier(Parser.tokenizer.next.value)
            Parser.tokenizer.selectNext()
            if unary == -1:
                result = UnOp('-', result)
            if logical_not:
                result = UnOp('!', result)
            return result

        else:
            raise Exception("Expected an integer, sub-expression, or identifier")


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
        elif self.value == '&&':
            return left_val and right_val
        elif self.value == '||':
            return left_val or right_val
        elif self.value == '==':
            return left_val == right_val
        elif self.value == '!=':
            return left_val != right_val
        elif self.value == '<':
            return left_val < right_val
        elif self.value == '<=':
            return left_val <= right_val
        elif self.value == '>':
            return left_val > right_val
        elif self.value == '>=':
            return left_val >= right_val

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
        elif self.value == '!':
            return not child_val

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
        if self.value[0].isdigit():  # Isso deve garantir que um erro seja gerado aqui.
            raise ValueError(f"Syntax Error: Invalid identifier '{self.value}'")
        return symbol_table.get(self.value)


class Assignment(Node):
    def __init__(self, identifier, expression):
        super().__init__()
        self.identifier = identifier
        self.children = [expression]

    def Evaluate(self, symbol_table):
        value = self.children[0].Evaluate(symbol_table)
        symbol_table.set(self.identifier, value)

# Classe para leitura com scanf
class ScanfNode(Node):
    def Evaluate(self, symbol_table):
        return int(input())  # Leitura de valor do terminal

class Print(Node):
    def __init__(self, expression):
        super().__init__()
        self.children = [expression]

    def Evaluate(self, symbol_table):
        value = self.children[0].Evaluate(symbol_table)
        print(value)

class Block(Node):
    def __init__(self, statements):
        super().__init__()
        self.children = statements

    def Evaluate(self, symbol_table):
        for statement in self.children:
            statement.Evaluate(symbol_table)

# Classe para comandos if
class IfNode(Node):
    def __init__(self, condition, if_block, else_block=None):
        super().__init__()
        self.children = [condition, if_block]
        if else_block:
            self.children.append(else_block)

    def Evaluate(self, symbol_table):
        condition = self.children[0].Evaluate(symbol_table)
        if condition:
            self.children[1].Evaluate(symbol_table)
        elif len(self.children) == 3:
            self.children[2].Evaluate(symbol_table)

# Classe para comandos while
class WhileNode(Node):
    def __init__(self, condition, block):
        super().__init__()
        self.children = [condition, block]

    def Evaluate(self, symbol_table):
        while self.children[0].Evaluate(symbol_table):
            self.children[1].Evaluate(symbol_table)

# Classe para comandos read
class Read(Node):
    def __init__(self, identifier):
        super().__init__()
        self.value = identifier

    def Evaluate(self, symbol_table):
        value = int(input(f"Enter value for {self.value}: "))
        symbol_table.set(self.value, value)


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

        # Executa o Parser e gera a AST (um bloco principal de statements)
        ast = Parser.run(filtered_code)

        # Criação da tabela de símbolos (SymbolTable)
        symbol_table = SymbolTable()

        # Executa a AST (bloco principal)
        ast.Evaluate(symbol_table)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()