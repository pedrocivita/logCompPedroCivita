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
        # Skip whitespace
        while self.position < len(self.source) and self.source[self.position].isspace():
            self.position += 1

        if self.position == len(self.source):
            self.next = Token('EOF', None)
            return

        current_char = self.source[self.position]

        # Recognize strings enclosed in double quotes
        if current_char == '"':
            self.position += 1  # Consume the initial quote
            string = ''
            while self.position < len(self.source) and self.source[self.position] != '"':
                string += self.source[self.position]
                self.position += 1
            if self.position == len(self.source):
                raise Exception("String não finalizada")
            self.position += 1  # Consume the closing quote
            self.next = Token('STRING', string)

        # Recognize integers
        elif current_char.isdigit():
            num = ''
            while self.position < len(self.source) and self.source[self.position].isdigit():
                num += self.source[self.position]
                self.position += 1
            self.next = Token('INT', int(num))

        # Recognize identifiers, reserved words, and special functions
        elif current_char.isalpha() or current_char == '_':
            identifier = ''
            while self.position < len(self.source) and (self.source[self.position].isalnum() or self.source[self.position] == '_'):
                identifier += self.source[self.position]
                self.position += 1

            # Add support for reserved words
            if identifier in ['printf', 'if', 'while', 'scanf', 'int', 'str', 'else', 'return', 'void']:
                self.next = Token('RESERVED', identifier)
            else:
                self.next = Token('ID', identifier)

        # Recognize operators, including relational and boolean
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
        functions = []

        while Parser.tokenizer.next.type != 'EOF':
            if Parser.tokenizer.next.type == 'RESERVED' and Parser.tokenizer.next.value in ['int', 'void', 'str']:
                func_decl = Parser.parseFunctionDecl()
                functions.append(func_decl)
            else:
                break  # Exit loop to parse main function

        # Parse main function
        if Parser.tokenizer.next.type == 'RESERVED' and Parser.tokenizer.next.value in ['int', 'void', 'str']:
            main_func = Parser.parseFunctionDecl()
            if main_func.name != 'main':
                raise Exception("Esperado a função 'main'")
            functions.append(main_func)
        else:
            raise Exception("Esperado declaração de função")

        # Create a Program node to hold all functions
        return Program(functions)

    @staticmethod
    def parseFunctionDecl():
        if Parser.tokenizer.next.type == 'RESERVED' and Parser.tokenizer.next.value in ['int', 'void', 'str']:
            return_type = Parser.tokenizer.next.value
            Parser.tokenizer.selectNext()

            if Parser.tokenizer.next.type != 'ID':
                raise Exception("Esperado nome da função após o tipo")
            func_name = Parser.tokenizer.next.value
            Parser.tokenizer.selectNext()

            if Parser.tokenizer.next.value != '(':
                raise Exception("Esperado '(' após o nome da função")
            Parser.tokenizer.selectNext()

            params = []
            if Parser.tokenizer.next.value != ')':
                while True:
                    param_type = Parser.tokenizer.next.value
                    if param_type not in ['int', 'str']:
                        raise Exception("Esperado tipo do parâmetro")
                    Parser.tokenizer.selectNext()

                    if Parser.tokenizer.next.type != 'ID':
                        raise Exception("Esperado nome do parâmetro")
                    param_name = Parser.tokenizer.next.value
                    Parser.tokenizer.selectNext()

                    params.append((param_type, param_name))

                    if Parser.tokenizer.next.value == ',':
                        Parser.tokenizer.selectNext()
                        continue
                    elif Parser.tokenizer.next.value == ')':
                        break
                    else:
                        raise Exception("Esperado ',' ou ')' na lista de parâmetros")

            Parser.tokenizer.selectNext()  # Consume ')'

            if Parser.tokenizer.next.value != '{':
                raise Exception("Esperado '{' para iniciar o corpo da função")

            body = Parser.parseBlock()

            return FuncDec(return_type, func_name, params, body)
        else:
            raise Exception("Esperado declaração de função")

    @staticmethod
    def parseBlock():
        if Parser.tokenizer.next.value != '{':
            raise Exception("Esperado '{' no início do bloco")

        Parser.tokenizer.selectNext()  # Consume '{'

        statements = []

        # Continue consuming statements until '}'
        while Parser.tokenizer.next.value != '}':
            if Parser.tokenizer.next.type == 'EOF':
                raise Exception("Esperado '}' no final do bloco")
            statement = Parser.parseStatement()
            statements.append(statement)
            # Consume semicolons after each statement
            while Parser.tokenizer.next.value == ';':
                Parser.tokenizer.selectNext()

        Parser.tokenizer.selectNext()  # Consume '}'

        return Block(statements)

    @staticmethod
    def parseStatement():
        # Ignore multiple ';'
        while Parser.tokenizer.next.value == ';':
            Parser.tokenizer.selectNext()

        # Variable declaration
        if Parser.tokenizer.next.type == 'RESERVED' and Parser.tokenizer.next.value in ['int', 'str']:
            var_type = Parser.tokenizer.next.value
            Parser.tokenizer.selectNext()
            var_list = []

            while True:
                if Parser.tokenizer.next.type != 'ID':
                    raise Exception("Esperado identificador após o tipo")
                var_name = Parser.tokenizer.next.value
                Parser.tokenizer.selectNext()

                # Optional assignment in declaration
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
                else:
                    raise Exception("Esperado ';' após expressão")
                return Assignment(identifier, expr)
            elif Parser.tokenizer.next.value == '(':
                # Function call
                Parser.tokenizer.selectNext()
                args = []
                if Parser.tokenizer.next.value != ')':
                    while True:
                        arg = Parser.parseExpression()
                        args.append(arg)
                        if Parser.tokenizer.next.value == ',':
                            Parser.tokenizer.selectNext()
                            continue
                        elif Parser.tokenizer.next.value == ')':
                            break
                        else:
                            raise Exception("Esperado ',' ou ')' nos argumentos da chamada de função")
                Parser.tokenizer.selectNext()  # Consume ')'
                if Parser.tokenizer.next.value == ';':
                    Parser.tokenizer.selectNext()
                else:
                    raise Exception("Esperado ';' após chamada de função")
                return FuncCall(identifier, args)
            else:
                raise Exception("Esperado '=' ou '(' após identificador")

        elif Parser.tokenizer.next.value == 'printf':
            Parser.tokenizer.selectNext()
            if Parser.tokenizer.next.value == '(':
                Parser.tokenizer.selectNext()
                expr = Parser.parseExpression()
                if Parser.tokenizer.next.value == ')':
                    Parser.tokenizer.selectNext()
                    if Parser.tokenizer.next.value == ';':
                        Parser.tokenizer.selectNext()
                    else:
                        raise Exception("Esperado ';' após printf")
                    return Print(expr)
                else:
                    raise Exception("Esperado ')' após expressão em printf")
            else:
                raise Exception("Esperado '(' após printf")

        elif Parser.tokenizer.next.value == 'return':
            Parser.tokenizer.selectNext()
            expr = Parser.parseExpression()
            if Parser.tokenizer.next.value == ';':
                Parser.tokenizer.selectNext()
            else:
                raise Exception("Esperado ';' após return")
            return ReturnNode(expr)

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
            if unary == -1 or logical_not:
                result = UnOp('-' if unary == -1 else '!', result)
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
            if logical_not:
                result = UnOp('!', result)
            if unary == -1:
                result = UnOp('-', result)
            return result

        elif Parser.tokenizer.next.type == 'ID':
            identifier = Parser.tokenizer.next.value
            Parser.tokenizer.selectNext()
            if Parser.tokenizer.next.value == '(':
                # Function call
                Parser.tokenizer.selectNext()
                args = []
                if Parser.tokenizer.next.value != ')':
                    while True:
                        arg = Parser.parseExpression()
                        args.append(arg)
                        if Parser.tokenizer.next.value == ',':
                            Parser.tokenizer.selectNext()
                            continue
                        elif Parser.tokenizer.next.value == ')':
                            break
                        else:
                            raise Exception("Esperado ',' ou ')' nos argumentos da chamada de função")
                Parser.tokenizer.selectNext()  # Consume ')'
                result = FuncCall(identifier, args)
                if unary == -1 or logical_not:
                    result = UnOp('-' if unary == -1 else '!', result)
                return result
            else:
                # Variable
                result = Identifier(identifier)
                if unary == -1 or logical_not:
                    result = UnOp('-' if unary == -1 else '!', result)
                return result

        else:
            raise Exception("Esperado um inteiro, string, sub-expressão ou identificador")

class PrePro:
    @staticmethod
    def filter(code: str) -> str:
        # Remove comments of the type /* */
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code

class Node(ABC):
    def __init__(self, value=None):
        self.value = value
        self.children = []

    @abstractmethod
    def Evaluate(self, symbol_table, func_table):
        pass

class Program(Node):
    def __init__(self, functions):
        super().__init__()
        self.functions = functions

    def Evaluate(self, symbol_table, func_table):
        for func in self.functions:
            func.Evaluate(symbol_table, func_table)

class FuncDec(Node):
    def __init__(self, return_type, name, params, body):
        super().__init__()
        self.return_type = return_type
        self.name = name
        self.params = params  # List of (type, name) tuples
        self.body = body

    def Evaluate(self, symbol_table, func_table):
        func_table.declare(self.name, self)

class FuncCall(Node):
    def __init__(self, name, args):
        super().__init__()
        self.name = name
        self.args = args

    def Evaluate(self, symbol_table, func_table):
        # Retrieve the function declaration
        func_decl = func_table.get(self.name)

        # Check argument count
        if len(self.args) != len(func_decl.params):
            raise Exception(f"Função '{self.name}' chamada com número incorreto de argumentos")

        # Create a new symbol table for the function scope
        local_symbol_table = SymbolTable(parent=None)

        # Assign arguments to parameters
        for arg_expr, (param_type, param_name) in zip(self.args, func_decl.params):
            arg_value, arg_type = arg_expr.Evaluate(symbol_table, func_table)
            if arg_type != param_type and not (param_type == 'int' and arg_type == 'bool'):
                raise Exception(f"Tipo incompatível na chamada da função '{self.name}' para o parâmetro '{param_name}'")
            local_symbol_table.declare(param_name, param_type)
            local_symbol_table.set(param_name, arg_value, arg_type)

        # Evaluate the function body
        try:
            func_decl.body.Evaluate(local_symbol_table, func_table)
            # If function has no return, return None or default value
            return (None, 'void')
        except ReturnException as ret:
            return (ret.value, ret.var_type)

class ReturnNode(Node):
    def __init__(self, expression):
        super().__init__()
        self.expression = expression

    def Evaluate(self, symbol_table, func_table):
        value, var_type = self.expression.Evaluate(symbol_table, func_table)
        # Raise an exception to unwind the call stack
        raise ReturnException(value, var_type)

class ReturnException(Exception):
    def __init__(self, value, var_type):
        self.value = value
        self.var_type = var_type

class FuncTable:
    def __init__(self):
        self.functions = {}

    def declare(self, name, func_node):
        if name in self.functions:
            raise Exception(f"Função '{name}' já declarada")
        self.functions[name] = func_node

    def get(self, name):
        if name in self.functions:
            return self.functions[name]
        else:
            raise Exception(f"Função '{name}' não declarada")

class BinOp(Node):
    def __init__(self, value, left, right):
        super().__init__(value)
        self.children = [left, right]

    def Evaluate(self, symbol_table, func_table):
        left_val, left_type = self.children[0].Evaluate(symbol_table, func_table)
        right_val, right_type = self.children[1].Evaluate(symbol_table, func_table)

        # Arithmetic operations
        if self.value in ('+', '-', '*', '/'):
            if self.value == '+':
                # String concatenation
                if left_type == 'str' or right_type == 'str':
                    return (str(left_val) + str(right_val), 'str')
                # Numeric operation
                elif left_type in ('int', 'bool') and right_type in ('int', 'bool'):
                    return (int(left_val) + int(right_val), 'int')
                else:
                    raise Exception("Tipos incompatíveis para '+'")
            elif self.value == '-':
                if left_type in ('int', 'bool') and right_type in ('int', 'bool'):
                    return (int(left_val) - int(right_val), 'int')
                else:
                    raise Exception("Tipos incompatíveis para '-'")
            elif self.value == '*':
                if left_type in ('int', 'bool') and right_type in ('int', 'bool'):
                    return (int(left_val) * int(right_val), 'int')
                else:
                    raise Exception("Tipos incompatíveis para '*'")
            elif self.value == '/':
                if left_type in ('int', 'bool') and right_type in ('int', 'bool'):
                    if int(right_val) == 0:
                        raise ValueError("Divisão por zero")
                    return (int(left_val) // int(right_val), 'int')
                else:
                    raise Exception("Tipos incompatíveis para '/'")

        # Logical operators
        elif self.value in ('&&', '||'):
            if left_type in ('int', 'bool') and right_type in ('int', 'bool'):
                left_bool = bool(int(left_val))
                right_bool = bool(int(right_val))
                if self.value == '&&':
                    return (int(left_bool and right_bool), 'int')
                elif self.value == '||':
                    return (int(left_bool or right_bool), 'int')
            else:
                raise Exception("Tipos incompatíveis para operadores lógicos")

        # Relational operators
        elif self.value in ('==', '!=', '<', '<=', '>', '>='):
            if left_type == right_type:
                if self.value == '==':
                    return (int(left_val == right_val), 'int')
                elif self.value == '!=':
                    return (int(left_val != right_val), 'int')
                elif self.value == '<':
                    return (int(left_val < right_val), 'int')
                elif self.value == '<=':
                    return (int(left_val <= right_val), 'int')
                elif self.value == '>':
                    return (int(left_val > right_val), 'int')
                elif self.value == '>=':
                    return (int(left_val >= right_val), 'int')
            else:
                raise Exception("Tipos incompatíveis para operadores relacionais")

class UnOp(Node):
    def __init__(self, value, child):
        super().__init__(value)
        self.children = [child]

    def Evaluate(self, symbol_table, func_table):
        child_val, child_type = self.children[0].Evaluate(symbol_table, func_table)

        if self.value == '+':
            if child_type in ('int', 'bool'):
                return (int(child_val), 'int')
            else:
                raise Exception("Operador '+' unário aplicado a tipo inválido")
        elif self.value == '-':
            if child_type in ('int', 'bool'):
                return (-int(child_val), 'int')
            else:
                raise Exception("Operador '-' unário aplicado a tipo inválido")
        elif self.value == '!':
            if child_type in ('int', 'bool'):
                return (int(not bool(int(child_val))), 'int')
            else:
                raise Exception("Operador '!' aplicado a tipo inválido")

class IntVal(Node):
    def __init__(self, value):
        super().__init__(value)

    def Evaluate(self, symbol_table, func_table):
        return (self.value, 'int')

class StringVal(Node):
    def __init__(self, value):
        super().__init__(value)

    def Evaluate(self, symbol_table, func_table):
        return (self.value, 'str')

class NoOp(Node):
    def Evaluate(self, symbol_table, func_table):
        return (None, None)

class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def declare(self, identifier, var_type):
        if identifier in self.symbols:
            raise Exception(f"Variável '{identifier}' já declarada.")
        self.symbols[identifier] = [None, var_type]

    def get(self, identifier):
        if identifier in self.symbols:
            value, var_type = self.symbols[identifier]
            return value, var_type
        elif self.parent:
            return self.parent.get(identifier)
        else:
            raise Exception(f"Variável '{identifier}' não declarada.")

    def set(self, identifier, value, var_type):
        if identifier in self.symbols:
            expected_type = self.symbols[identifier][1]
            if var_type != expected_type and not (expected_type == 'int' and var_type == 'bool'):
                raise Exception(f"Tipo incompatível para '{identifier}'. Esperado '{expected_type}', recebido '{var_type}'.")
            self.symbols[identifier][0] = value
        elif self.parent:
            self.parent.set(identifier, value, var_type)
        else:
            raise Exception(f"Variável '{identifier}' não declarada.")

class Identifier(Node):
    def __init__(self, value):
        super().__init__(value)

    def Evaluate(self, symbol_table, func_table):
        return symbol_table.get(self.value)

class Assignment(Node):
    def __init__(self, identifier, expression):
        super().__init__()
        self.identifier = identifier
        self.children = [expression]

    def Evaluate(self, symbol_table, func_table):
        value, var_type = self.children[0].Evaluate(symbol_table, func_table)
        symbol_table.set(self.identifier, value, var_type)

class VarDec(Node):
    def __init__(self, var_type, var_list):
        super().__init__()
        self.var_type = var_type
        self.var_list = var_list  # List of tuples (name, expression or None)

    def Evaluate(self, symbol_table, func_table):
        for var_name, expr in self.var_list:
            symbol_table.declare(var_name, self.var_type)
            if expr:
                value, expr_type = expr.Evaluate(symbol_table, func_table)
                # Allow assignment of 'bool' to 'int'
                if expr_type != self.var_type and not (self.var_type == 'int' and expr_type == 'bool'):
                    raise Exception(f"Tipo incompatível na atribuição para '{var_name}'. Esperado '{self.var_type}', recebido '{expr_type}'.")
                symbol_table.set(var_name, value, expr_type)

class ScanfNode(Node):
    def Evaluate(self, symbol_table, func_table):
        value = int(input())
        return (value, 'int')

class Print(Node):
    def __init__(self, expression):
        super().__init__()
        self.children = [expression]

    def Evaluate(self, symbol_table, func_table):
        value, var_type = self.children[0].Evaluate(symbol_table, func_table)
        print(value)

class Block(Node):
    def __init__(self, statements):
        super().__init__()
        self.children = statements

    def Evaluate(self, symbol_table, func_table):
        for statement in self.children:
            statement.Evaluate(symbol_table, func_table)

class IfNode(Node):
    def __init__(self, condition, if_block, else_block=None):
        super().__init__()
        self.children = [condition, if_block]
        if else_block:
            self.children.append(else_block)

    def Evaluate(self, symbol_table, func_table):
        condition_val, condition_type = self.children[0].Evaluate(symbol_table, func_table)
        if condition_type not in ('int', 'bool'):
            raise Exception("Condição do 'if' deve ser do tipo 'int' ou 'bool'")
        if bool(int(condition_val)):
            self.children[1].Evaluate(symbol_table, func_table)
        elif len(self.children) == 3:
            self.children[2].Evaluate(symbol_table, func_table)

class WhileNode(Node):
    def __init__(self, condition, block):
        super().__init__()
        self.children = [condition, block]

    def Evaluate(self, symbol_table, func_table):
        while True:
            condition_val, condition_type = self.children[0].Evaluate(symbol_table, func_table)
            if condition_type not in ('int', 'bool'):
                raise Exception("Condição do 'while' deve ser do tipo 'int' ou 'bool'")
            if not bool(int(condition_val)):
                break
            self.children[1].Evaluate(symbol_table, func_table)

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
        # Remove comments from code
        filtered_code = PrePro.filter(code)

        # Run the parser and generate the AST
        ast = Parser.run(filtered_code)

        # Create the global symbol table and function table
        symbol_table = SymbolTable()
        func_table = FuncTable()

        # Evaluate the AST (Program node)
        ast.Evaluate(symbol_table, func_table)

        # Start execution by calling 'main' function
        main_call = FuncCall('main', [])
        main_call.Evaluate(symbol_table, func_table)

    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()