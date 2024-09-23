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
        # Ignora espaços em branco e quebras de linha
        while self.position < len(self.source) and self.source[self.position] in [' ', '\n', '\t', '\r']:
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

        # Detecta identificadores (variáveis, printf, if, while, read, scanf)
        elif current_char.isalpha() or current_char == '_':
            identifier = ''
            while self.position < len(self.source) and (self.source[self.position].isalnum() or self.source[self.position] == '_'):
                identifier += self.source[self.position]
                self.position += 1
            if identifier == 'printf':
                self.next = Token('PRINT', None)
            elif identifier == 'if':
                self.next = Token('IF', None)
            elif identifier == 'else':
                self.next = Token('ELSE', None)
            elif identifier == 'while':
                self.next = Token('WHILE', None)
            elif identifier == 'read':
                self.next = Token('READ', None)
            elif identifier == 'scanf':
                self.next = Token('SCANF', None)
            else:
                self.next = Token('ID', identifier)

        # Operadores booleanos
        elif current_char == '&' and self.position + 1 < len(self.source) and self.source[self.position + 1] == '&':
            self.position += 2
            self.next = Token('AND', None)
        elif current_char == '|' and self.position + 1 < len(self.source) and self.source[self.position + 1] == '|':
            self.position += 2
            self.next = Token('OR', None)
        elif current_char == '!':
            if self.position + 1 < len(self.source) and self.source[self.position + 1] == '=':
                self.position += 2
                self.next = Token('NEQ', None)
            else:
                self.next = Token('NOT', None)
                self.position += 1

        # Operadores relacionais
        elif current_char == '=' and self.position + 1 < len(self.source) and self.source[self.position + 1] == '=':
            self.position += 2
            self.next = Token('EQ', None)
        elif current_char == '<':
            if self.position + 1 < len(self.source) and self.source[self.position + 1] == '=':
                self.position += 2
                self.next = Token('LE', None)
            else:
                self.next = Token('LT', None)
                self.position += 1
        elif current_char == '>':
            if self.position + 1 < len(self.source) and self.source[self.position + 1] == '=':
                self.position += 2
                self.next = Token('GE', None)
            else:
                self.next = Token('GT', None)
                self.position += 1

        # Operadores básicos
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

        elif current_char == '=':
            self.next = Token('ASSIGN', None)
            self.position += 1

        elif current_char == ';':
            self.next = Token('SEMICOLON', None)
            self.position += 1

        # Parênteses e blocos
        elif current_char == '(':
            self.next = Token('LPAREN', None)
            self.position += 1

        elif current_char == ')':
            self.next = Token('RPAREN', None)
            self.position += 1

        elif current_char == '{':
            self.next = Token('LBRACE', None)
            self.position += 1

        elif current_char == '}':
            self.next = Token('RBRACE', None)
            self.position += 1

        else:
            raise ValueError(f"Unexpected character: {current_char}")

class Parser:
    @staticmethod
    def run(code: str):
        try:
            code = PrePro.filter(code)  # Filtra comentários
            Parser.tokenizer = Tokenizer(code)
            Parser.tokenizer.selectNext()

            ast = Parser.parseBlock()  # Faz o parsing do bloco principal
            return ast

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    @staticmethod
    def parseStatement():
        if Parser.tokenizer.next.type == 'ID':  # Para atribuições
            identifier = Parser.tokenizer.next.value
            Parser.tokenizer.selectNext()
            if Parser.tokenizer.next.type == 'ASSIGN':
                Parser.tokenizer.selectNext()
                expr = Parser.parseExpression()
                if Parser.tokenizer.next.type == 'SEMICOLON':  # Certifica que o ';' seja consumido
                    Parser.tokenizer.selectNext()
                else:
                    raise ValueError("Syntax Error: Expected ';' at the end of statement")
                return Assignment(identifier, expr)

        elif Parser.tokenizer.next.type == 'PRINT':  # Para printf()
            Parser.tokenizer.selectNext()
            if Parser.tokenizer.next.type == 'LPAREN':
                Parser.tokenizer.selectNext()
                expr = Parser.parseExpression()
                if Parser.tokenizer.next.type != 'RPAREN':
                    raise ValueError("Syntax Error: Expected ')' after 'printf'")
                Parser.tokenizer.selectNext()
                if Parser.tokenizer.next.type == 'SEMICOLON':  # Certifica que o ';' seja consumido após printf()
                    Parser.tokenizer.selectNext()
                else:
                    raise ValueError("Syntax Error: Expected ';' at the end of statement")
                return Print(expr)
            else:
                raise ValueError("Syntax Error: Expected '(' after 'printf'")

        elif Parser.tokenizer.next.type == 'SCANF':  # Para scanf()
            return Parser.parseScanf()

        elif Parser.tokenizer.next.type == 'IF':  # Para if
            return Parser.parseIf()

        elif Parser.tokenizer.next.type == 'WHILE':  # Para while
            return Parser.parseWhile()

        elif Parser.tokenizer.next.type == 'LBRACE':  # Para blocos
            return Parser.parseBlock()

        else:
            raise ValueError("Syntax Error: Invalid statement")

    @staticmethod
    def parseIf():
        Parser.tokenizer.selectNext()  # Consome o 'if'
        if Parser.tokenizer.next.type == 'LPAREN':  # Verifica se '(' está presente
            Parser.tokenizer.selectNext()
            condition = Parser.parseExpression()  # Parseia a condição
            if Parser.tokenizer.next.type != 'RPAREN':
                raise ValueError("Syntax Error: Expected ')' after condition")
            Parser.tokenizer.selectNext()  # Consome ')'
            if Parser.tokenizer.next.type == 'LBRACE':  # Verifica se o bloco verdadeiro começa com '{'
                true_block = Parser.parseBlock()  # Parseia o bloco verdadeiro
                false_block = None
                if Parser.tokenizer.next.type == 'ELSE':
                    Parser.tokenizer.selectNext()  # Consome 'else'
                    if Parser.tokenizer.next.type == 'LBRACE':  # Verifica se o bloco falso começa com '{'
                        false_block = Parser.parseBlock()  # Parseia o bloco falso
                    else:
                        raise ValueError("Syntax Error: Expected '{' after 'else'")
                return IfNode(condition, true_block, false_block)
            else:
                raise ValueError("Syntax Error: Expected '{' after 'if' condition")

    @staticmethod
    def parseWhile():
        Parser.tokenizer.selectNext()  # Consome o 'while'
        if Parser.tokenizer.next.type == 'LPAREN':  # Verifica se '(' está presente
            Parser.tokenizer.selectNext()
            condition = Parser.parseExpression()  # Parseia a condição
            if Parser.tokenizer.next.type != 'RPAREN':
                raise ValueError("Syntax Error: Expected ')' after condition")
            Parser.tokenizer.selectNext()  # Consome ')'
            if Parser.tokenizer.next.type == 'LBRACE':  # Verifica se o bloco começa com '{'
                block = Parser.parseBlock()  # Parseia o bloco do 'while'
                return WhileNode(condition, block)
            else:
                raise ValueError("Syntax Error: Expected '{' after 'while' condition")

    @staticmethod
    def parseExpression():
        result = Parser.parseTerm()

        while Parser.tokenizer.next.type in ['PLUS', 'MINUS', 'AND', 'OR']:  # Inclui operadores booleanos
            op_type = Parser.tokenizer.next.type
            Parser.tokenizer.selectNext()
            result2 = Parser.parseTerm()

            if op_type == 'PLUS':
                result = BinOp('+', result, result2)
            elif op_type == 'MINUS':
                result = BinOp('-', result, result2)
            elif op_type == 'AND':
                result = BinOp('&&', result, result2)
            elif op_type == 'OR':
                result = BinOp('||', result, result2)

        return result

    @staticmethod
    def parseTerm():
        result = Parser.parseFactor()

        while Parser.tokenizer.next.type in ['MULT', 'DIV', 'EQ', 'NEQ', 'LT', 'LE', 'GT', 'GE']:  # Operadores de comparação
            op_type = Parser.tokenizer.next.type
            Parser.tokenizer.selectNext()
            result2 = Parser.parseFactor()

            if op_type == 'MULT':
                result = BinOp('*', result, result2)
            elif op_type == 'DIV':
                result = BinOp('/', result, result2)
            elif op_type == 'EQ':
                result = BinOp('==', result, result2)
            elif op_type == 'NEQ':
                result = BinOp('!=', result, result2)
            elif op_type == 'LT':
                result = BinOp('<', result, result2)
            elif op_type == 'LE':
                result = BinOp('<=', result, result2)
            elif op_type == 'GT':
                result = BinOp('>', result, result2)
            elif op_type == 'GE':
                result = BinOp('>=', result, result2)

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
                raise ValueError("Syntax Error: Expected ')' after expression")
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
            raise ValueError("Syntax Error: Expected INT, ID, or '('")
        
    @staticmethod
    def parseBlock():
        if Parser.tokenizer.next.type == 'LBRACE':  # Verifica se é um bloco
            Parser.tokenizer.selectNext()  # Avança sobre '{'
            block_statements = []
            while Parser.tokenizer.next.type != 'RBRACE':  # Continua até encontrar '}'
                block_statements.append(Parser.parseStatement())  # Adiciona cada statement no bloco
                if Parser.tokenizer.next.type == 'SEMICOLON':  # Consome o ';' após cada statement
                    Parser.tokenizer.selectNext()
                else:
                    raise ValueError("Syntax Error: Expected ';' at the end of statement")
            Parser.tokenizer.selectNext()  # Avança sobre '}'
            return Block(block_statements)  # Retorna o bloco de statements
        else:
            raise ValueError("Syntax Error: Expected '{'")

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
        return symbol_table.get(self.value)

class Assignment(Node):
    def __init__(self, identifier, expression):
        super().__init__()
        self.identifier = identifier
        self.children = [expression]

    def Evaluate(self, symbol_table):
        value = self.children[0].Evaluate(symbol_table)
        symbol_table.set(self.identifier, value)

class ScanfNode(Node):
    def __init__(self, identifier):
        super().__init__()
        self.identifier = identifier  # Armazenar o identificador

    def Evaluate(self, symbol_table):
        value = int(input())  # Leitura de valor do terminal
        symbol_table.set(self.identifier, value)  # Armazena o valor na tabela de símbolos
        return value

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