import sys
from abc import ABC, abstractmethod
import re

class Token:
    def __init__(self, type: str, value):
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

        # Reconhece strings entre aspas duplas
        if current_char == '"':
            self.position += 1  # Consome a aspas inicial
            string = ''
            while self.position < len(self.source) and self.source[self.position] != '"':
                string += self.source[self.position]
                self.position += 1
            if self.position == len(self.source):
                raise Exception("String não finalizada")
            self.position += 1  # Consome a aspas final
            self.next = Token('STRING', string)

        # Reconhece números inteiros
        elif current_char.isdigit():
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

            # Adicionando suporte para palavras reservadas
            if identifier in ['printf', 'if', 'while', 'scanf', 'int', 'str']:
                self.next = Token('RESERVED', identifier)
            else:
                self.next = Token('ID', identifier)

        # Reconhece operadores, incluindo relacionais e booleanos
        elif current_char in '+-*/(){}=;><!&|,':
            if self.source[self.position:self.position+2] in ['<=', '>=', '==', '!=', '&&', '||']:
                self.next = Token('OPERATOR', self.source[self.position:self.position+2])
                self.position += 2
            else:
                self.next = Token('OPERATOR', current_char)
                self.position += 1

        else:
            raise Exception(f"Caractere inesperado: {current_char}")

class Parser:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    @staticmethod
    def run(code):
        Parser.tokenizer = Tokenizer(code)
        result = Parser.parseBlock()
        if Parser.tokenizer.next.type != 'EOF':
            raise Exception("Dados inesperados após o bloco")
        return result

    @staticmethod
    def parseBlock():
        if Parser.tokenizer.next.value != '{':
            raise Exception("Esperado '{' no início do bloco")

        Parser.tokenizer.selectNext()  # Consome o '{'

        statements = []

        # Continua consumindo statements até encontrar '}'
        while Parser.tokenizer.next.value != '}':
            if Parser.tokenizer.next.type == 'EOF':
                raise Exception("Esperado '}' no final do bloco")
            statements.append(Parser.parseStatement())

        Parser.tokenizer.selectNext()  # Consome o '}'

        return Block(statements)

    @staticmethod
    def parseStatement():
        # Ignorar múltiplos ';'
        while Parser.tokenizer.next.value == ';':
            Parser.tokenizer.selectNext()

        # Declaração de variáveis
        if Parser.tokenizer.next.type == 'RESERVED' and Parser.tokenizer.next.value in ['int', 'str']:
            var_type = Parser.tokenizer.next.value
            Parser.tokenizer.selectNext()
            var_list = []

            while True:
                if Parser.tokenizer.next.type != 'ID':
                    raise Exception("Esperado identificador após o tipo")
                var_name = Parser.tokenizer.next.value
                Parser.tokenizer.selectNext()

                # Atribuição opcional na declaração
                if Parser.tokenizer.next.value == '=':
                    Parser.tokenizer.selectNext()
                    expr = Parser.parseExpression()
                    var_list.append((var_name, expr))
                else:
                    var_list.append((var_name, None))

                if Parser.tokenizer.next.value == ',':
                    Parser.tokenizer.selectNext()
                    continue
                elif Parser.tokenizer.next.value == ';':
                    Parser.tokenizer.selectNext()
                    break
                else:
                    raise Exception("Esperado ',' ou ';' após declaração")

            return VarDec(var_type, var_list)

        elif Parser.tokenizer.next.type == 'ID':
            identifier = Parser.tokenizer.next.value
            Parser.tokenizer.selectNext()
            if Parser.tokenizer.next.value == '=':
                Parser.tokenizer.selectNext()
                expr = Parser.parseExpression()
                if Parser.tokenizer.next.value == ';':
                    Parser.tokenizer.selectNext()
                    return Assignment(identifier, expr)
                else:
                    raise Exception("Esperado ';' após expressão")
            else:
                raise Exception("Esperado '=' após identificador")

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
                        raise Exception("Esperado ';' após printf")
                else:
                    raise Exception("Esperado ')' após expressão printf")
            else:
                raise Exception("Esperado '(' após printf")

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
                        raise Exception("Esperado ';' após scanf")
                else:
                    raise Exception("Esperado ')' após scanf")
            else:
                raise Exception("Esperado '(' após scanf")

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
                    raise Exception("Esperado ')' após condição")
            else:
                raise Exception("Esperado '(' após 'if'")

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
                    raise Exception("Esperado ')' após condição")
            else:
                raise Exception("Esperado '(' após 'while'")

        elif Parser.tokenizer.next.value == '{':
            return Parser.parseBlock()

        else:
            if Parser.tokenizer.next.type != 'EOF':
                raise Exception(f"Token inesperado: {Parser.tokenizer.next.value}")
            return NoOp()

    @staticmethod
    def parseExpression():
        result = Parser.parseTerm()

        while Parser.tokenizer.next.type == 'OPERATOR' and Parser.tokenizer.next.value in ('+', '-', '==', '!=', '>', '<', '>=', '<=', '&&', '||'):
            op = Parser.tokenizer.next.value
            Parser.tokenizer.selectNext()
            right = Parser.parseTerm()
            result = BinOp(op, result, right)

        return result

    @staticmethod
    def parseTerm():
        result = Parser.parseFactor()

        while Parser.tokenizer.next.type == 'OPERATOR' and Parser.tokenizer.next.value in ('*', '/'):
            op = Parser.tokenizer.next.value
            Parser.tokenizer.selectNext()
            right = Parser.parseFactor()
            result = BinOp(op, result, right)

        return result

    @staticmethod
    def parseFactor():
        unary = 1
        logical_not = False

        while Parser.tokenizer.next.type == 'OPERATOR' and Parser.tokenizer.next.value in ('-', '+', '!'):
            if Parser.tokenizer.next.value == '-':
                unary *= -1
            elif Parser.tokenizer.next.value == '!':
                logical_not = not logical_not
            Parser.tokenizer.selectNext()

        if Parser.tokenizer.next.value == 'scanf':
            Parser.tokenizer.selectNext()
            if Parser.tokenizer.next.value == '(':
                Parser.tokenizer.selectNext()
                if Parser.tokenizer.next.value == ')':
                    Parser.tokenizer.selectNext()
                    result = ScanfNode()
                    return result
                else:
                    raise Exception("Esperado ')' após 'scanf'")
            else:
                raise Exception("Esperado '(' após 'scanf'")

        if Parser.tokenizer.next.value == '(':
            Parser.tokenizer.selectNext()
            result = Parser.parseExpression()
            if Parser.tokenizer.next.value != ')':
                raise Exception("Faltando parêntese de fechamento")
            Parser.tokenizer.selectNext()
            if unary == -1:
                result = UnOp('-', result)
            if logical_not:
                result = UnOp('!', result)
            return result

        elif Parser.tokenizer.next.type == 'INT':
            result = IntVal(Parser.tokenizer.next.value)
            Parser.tokenizer.selectNext()
            if unary == -1 or logical_not:
                result = UnOp('-' if unary == -1 else '!', result)
            return result

        elif Parser.tokenizer.next.type == 'STRING':
            result = StringVal(Parser.tokenizer.next.value)
            Parser.tokenizer.selectNext()
            return result

        elif Parser.tokenizer.next.type == 'ID':
            result = Identifier(Parser.tokenizer.next.value)
            Parser.tokenizer.selectNext()
            if unary == -1 or logical_not:
                result = UnOp('-' if unary == -1 else '!', result)
            return result

        else:
            raise Exception("Esperado um inteiro, string, sub-expressão ou identificador")

class PrePro:
    @staticmethod
    def filter(code: str) -> str:
        # Remove comentários do tipo /* */
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code

class Node(ABC):
    def __init__(self, value=None):
        self.value = value
        self.children = []

    @abstractmethod
    def Evaluate(self, symbol_table):
        pass

class BinOp(Node):
    def __init__(self, value, left, right):
        super().__init__(value)
        self.children = [left, right]

    def Evaluate(self, symbol_table):
        left_val, left_type = self.children[0].Evaluate(symbol_table)
        right_val, right_type = self.children[1].Evaluate(symbol_table)

        # Operações aritméticas
        if self.value in ('+', '-', '*', '/'):
            if self.value == '+':
                # Concatenação de strings
                if left_type == 'str' or right_type == 'str':
                    return (str(left_val) + str(right_val), 'str')
                # Operação numérica
                elif left_type == 'int' and right_type == 'int':
                    return (left_val + right_val, 'int')
                else:
                    raise Exception("Tipos incompatíveis para '+'")
            elif self.value == '-':
                if left_type == 'int' and right_type == 'int':
                    return (left_val - right_val, 'int')
                else:
                    raise Exception("Tipos incompatíveis para '-'")
            elif self.value == '*':
                if left_type == 'int' and right_type == 'int':
                    return (left_val * right_val, 'int')
                else:
                    raise Exception("Tipos incompatíveis para '*'")
            elif self.value == '/':
                if left_type == 'int' and right_type == 'int':
                    if right_val == 0:
                        raise ValueError("Divisão por zero")
                    return (left_val // right_val, 'int')
                else:
                    raise Exception("Tipos incompatíveis para '/'")

        # Operadores lógicos
        elif self.value in ('&&', '||'):
            if left_type in ('int', 'bool') and right_type in ('int', 'bool'):
                left_bool = bool(left_val)
                right_bool = bool(right_val)
                if self.value == '&&':
                    return (int(left_bool and right_bool), 'bool')
                elif self.value == '||':
                    return (int(left_bool or right_bool), 'bool')
            else:
                raise Exception("Tipos incompatíveis para operadores lógicos")

        # Operadores relacionais
        elif self.value in ('==', '!=', '<', '<=', '>', '>='):
            if left_type == right_type:
                if self.value == '==':
                    return (int(left_val == right_val), 'bool')
                elif self.value == '!=':
                    return (int(left_val != right_val), 'bool')
                elif self.value == '<':
                    return (int(left_val < right_val), 'bool')
                elif self.value == '<=':
                    return (int(left_val <= right_val), 'bool')
                elif self.value == '>':
                    return (int(left_val > right_val), 'bool')
                elif self.value == '>=':
                    return (int(left_val >= right_val), 'bool')
            else:
                raise Exception("Tipos incompatíveis para operadores relacionais")

class UnOp(Node):
    def __init__(self, value, child):
        super().__init__(value)
        self.children = [child]

    def Evaluate(self, symbol_table):
        child_val, child_type = self.children[0].Evaluate(symbol_table)

        if self.value == '+':
            if child_type == 'int':
                return (child_val, 'int')
            else:
                raise Exception("Operador '+' unário aplicado a tipo inválido")
        elif self.value == '-':
            if child_type == 'int':
                return (-child_val, 'int')
            else:
                raise Exception("Operador '-' unário aplicado a tipo inválido")
        elif self.value == '!':
            if child_type in ('int', 'bool'):
                return (int(not bool(child_val)), 'bool')
            else:
                raise Exception("Operador '!' aplicado a tipo inválido")

class IntVal(Node):
    def __init__(self, value):
        super().__init__(value)

    def Evaluate(self, symbol_table):
        return (self.value, 'int')

class StringVal(Node):
    def __init__(self, value):
        super().__init__(value)

    def Evaluate(self, symbol_table):
        return (self.value, 'str')

class NoOp(Node):
    def Evaluate(self, symbol_table):
        return (None, None)

class SymbolTable:
    def __init__(self):
        self.symbols = {}

    def declare(self, identifier, var_type):
        if identifier in self.symbols:
            raise Exception(f"Variável '{identifier}' já declarada.")
        self.symbols[identifier] = [None, var_type]

    def get(self, identifier):
        if identifier in self.symbols:
            value, var_type = self.symbols[identifier]
            return value, var_type
        else:
            raise Exception(f"Variável '{identifier}' não declarada.")

    def set(self, identifier, value, var_type):
        if identifier in self.symbols:
            expected_type = self.symbols[identifier][1]
            if var_type != expected_type:
                raise Exception(f"Tipo incompatível para '{identifier}'. Esperado '{expected_type}', recebido '{var_type}'.")
            self.symbols[identifier][0] = value
        else:
            raise Exception(f"Variável '{identifier}' não declarada.")

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
        value, var_type = self.children[0].Evaluate(symbol_table)
        symbol_table.set(self.identifier, value, var_type)

class VarDec(Node):
    def __init__(self, var_type, var_list):
        super().__init__()
        self.var_type = var_type
        self.var_list = var_list  # Lista de tuplas (nome, expressão ou None)

    def Evaluate(self, symbol_table):
        for var_name, expr in self.var_list:
            symbol_table.declare(var_name, self.var_type)
            if expr:
                value, expr_type = expr.Evaluate(symbol_table)
                if expr_type != self.var_type:
                    raise Exception(f"Tipo incompatível na atribuição para '{var_name}'.")
                symbol_table.set(var_name, value, self.var_type)

class ScanfNode(Node):
    def Evaluate(self, symbol_table):
        value = int(input())
        return (value, 'int')

class Print(Node):
    def __init__(self, expression):
        super().__init__()
        self.children = [expression]

    def Evaluate(self, symbol_table):
        value, var_type = self.children[0].Evaluate(symbol_table)
        print(value)

class Block(Node):
    def __init__(self, statements):
        super().__init__()
        self.children = statements

    def Evaluate(self, symbol_table):
        for statement in self.children:
            statement.Evaluate(symbol_table)

class IfNode(Node):
    def __init__(self, condition, if_block, else_block=None):
        super().__init__()
        self.children = [condition, if_block]
        if else_block:
            self.children.append(else_block)

    def Evaluate(self, symbol_table):
        condition_val, condition_type = self.children[0].Evaluate(symbol_table)
        if condition_type not in ('int', 'bool'):
            raise Exception("Condição do 'if' deve ser do tipo 'int' ou 'bool'")
        if bool(condition_val):
            self.children[1].Evaluate(symbol_table)
        elif len(self.children) == 3:
            self.children[2].Evaluate(symbol_table)

class WhileNode(Node):
    def __init__(self, condition, block):
        super().__init__()
        self.children = [condition, block]

    def Evaluate(self, symbol_table):
        while True:
            condition_val, condition_type = self.children[0].Evaluate(symbol_table)
            if condition_type not in ('int', 'bool'):
                raise Exception("Condição do 'while' deve ser do tipo 'int' ou 'bool'")
            if not bool(condition_val):
                break
            self.children[1].Evaluate(symbol_table)

def main():
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
        try:
            with open(file_name, 'r') as file:
                code = file.read()
        except FileNotFoundError:
            print(f"Erro: Arquivo '{file_name}' não encontrado.", file=sys.stderr)
            sys.exit(1)
    else:
        print("Erro: Nenhum arquivo de entrada fornecido.", file=sys.stderr)
        sys.exit(1)

    try:
        # Remove comentários do código
        filtered_code = PrePro.filter(code)

        # Executa o Parser e gera a AST
        ast = Parser.run(filtered_code)

        # Criação da tabela de símbolos
        symbol_table = SymbolTable()

        # Executa a AST
        ast.Evaluate(symbol_table)

    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
