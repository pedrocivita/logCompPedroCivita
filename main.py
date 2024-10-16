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
        while self.position < len(self.source) and \
              self.source[self.position].isspace():
            self.position += 1

        if self.position == len(self.source):
            self.next = Token('EOF', None)
            return

        current_char = self.source[self.position]

        # Reconhece strings entre aspas duplas
        if current_char == '"':
            self.position += 1  # Consome a aspas inicial
            string = ''
            while self.position < len(self.source) and \
                  self.source[self.position] != '"':
                string += self.source[self.position]
                self.position += 1
            if self.position == len(self.source):
                raise Exception("String não finalizada")
            self.position += 1  # Consome a aspas final
            self.next = Token('STRING', string)

        # Reconhece números inteiros
        elif current_char.isdigit():
            num = ''
            while self.position < len(self.source) and \
                  self.source[self.position].isdigit():
                num += self.source[self.position]
                self.position += 1
            self.next = Token('INT', int(num))

        # Reconhece identificadores e palavras reservadas
        elif current_char.isalpha() or current_char == '_':
            identifier = ''
            while self.position < len(self.source) and \
                 (self.source[self.position].isalnum() or \
                  self.source[self.position] == '_'):
                identifier += self.source[self.position]
                self.position += 1

            if identifier in ['printf', 'if', 'while', 'scanf',
                              'int', 'str', 'else']:
                self.next = Token('RESERVED', identifier)
            else:
                self.next = Token('ID', identifier)

        # Reconhece operadores
        elif current_char in '+-*/(){}=;><!&|,':
            if self.source[self.position:self.position+2] in \
               ['<=', '>=', '==', '!=', '&&', '||']:
                self.next = Token('OPERATOR',
                                  self.source[self.position:self.position+2])
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

        Parser.tokenizer.selectNext()  # Consome '{'

        statements = []

        while Parser.tokenizer.next.value != '}':
            if Parser.tokenizer.next.type == 'EOF':
                raise Exception("Esperado '}' no final do bloco")
            statement = Parser.parseStatement()
            statements.append(statement)
            while Parser.tokenizer.next.value == ';':
                Parser.tokenizer.selectNext()

        Parser.tokenizer.selectNext()  # Consome '}'

        return Block(statements)

    @staticmethod
    def parseStatement():
        while Parser.tokenizer.next.value == ';':
            Parser.tokenizer.selectNext()

        # Declaração de variáveis
        if Parser.tokenizer.next.type == 'RESERVED' and \
           Parser.tokenizer.next.value in ['int', 'str']:
            var_type = Parser.tokenizer.next.value
            Parser.tokenizer.selectNext()
            var_list = []

            while True:
                if Parser.tokenizer.next.type != 'ID':
                    raise Exception("Esperado identificador após o tipo")
                var_name = Parser.tokenizer.next.value
                Parser.tokenizer.selectNext()

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
                    else:
                        raise Exception("Esperado ';' após printf")
                    return Print(expr)
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
                    else:
                        raise Exception("Esperado ';' após scanf")
                    return ScanfNode()
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
                raise Exception(f"Token inesperado: "
                                f"{Parser.tokenizer.next.value}")
            return NoOp()

    @staticmethod
    def parseExpression():
        result = Parser.parseTerm()

        while Parser.tokenizer.next.type == 'OPERATOR' and \
              Parser.tokenizer.next.value in ('+', '-', '==', '!=', '>',
                                              '<', '>=', '<=', '&&', '||'):
            op = Parser.tokenizer.next.value
            Parser.tokenizer.selectNext()
            right = Parser.parseTerm()
            result = BinOp(op, result, right)

        return result

    @staticmethod
    def parseTerm():
        result = Parser.parseFactor()

        while Parser.tokenizer.next.type == 'OPERATOR' and \
              Parser.tokenizer.next.value in ('*', '/'):
            op = Parser.tokenizer.next.value
            Parser.tokenizer.selectNext()
            right = Parser.parseFactor()
            result = BinOp(op, result, right)

        return result

    @staticmethod
    def parseFactor():
        unary = 1
        logical_not = False

        while Parser.tokenizer.next.type == 'OPERATOR' and \
              Parser.tokenizer.next.value in ('-', '+', '!'):
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
            result = Identifier(Parser.tokenizer.next.value)
            Parser.tokenizer.selectNext()
            if unary == -1 or logical_not:
                result = UnOp('-' if unary == -1 else '!', result)
            return result

        else:
            raise Exception("Esperado um inteiro, string, sub-expressão ou "
                            "identificador")

class PrePro:
    @staticmethod
    def filter(code: str) -> str:
        # Remove comentários do tipo /* */
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code

class Node(ABC):
    i = 0  # Contador estático para IDs únicos

    def __init__(self, value=None):
        self.value = value
        self.children = []
        self.id = Node.newId()

    @staticmethod
    def newId():
        Node.i += 1
        return Node.i

    @abstractmethod
    def Evaluate(self, symbol_table):
        pass

class CodeGenerator:
    code = []
    labels = set()

    @staticmethod
    def add_line(line):
        # Limita o comprimento da linha a 70 caracteres
        for l in line.split('\n'):
            CodeGenerator.code.append(l.strip()[:70])

    @staticmethod
    def get_code():
        return '\n'.join(CodeGenerator.code)

class BinOp(Node):
    def __init__(self, value, left, right):
        super().__init__(value)
        self.children = [left, right]

    def Evaluate(self, symbol_table):
        # Avalia lado esquerdo
        left_value, left_type = self.children[0].Evaluate(symbol_table)
        CodeGenerator.add_line("PUSH EAX")
        # Avalia lado direito
        right_value, right_type = self.children[1].Evaluate(symbol_table)
        CodeGenerator.add_line("POP EBX")

        if self.value == '+':
            CodeGenerator.add_line("ADD EAX, EBX")
            result_type = 'int'
        elif self.value == '-':
            CodeGenerator.add_line("SUB EAX, EBX")
            result_type = 'int'
        elif self.value == '*':
            CodeGenerator.add_line("IMUL EAX, EBX")
            result_type = 'int'
        elif self.value == '/':
            CodeGenerator.add_line("CDQ")
            CodeGenerator.add_line("IDIV EBX")
            result_type = 'int'
        elif self.value == '==':
            CodeGenerator.add_line("CMP EBX, EAX")
            CodeGenerator.add_line("CALL binop_je")
            CodeGenerator.add_line("MOV EAX, EBX")
            result_type = 'int'
        elif self.value == '<':
            CodeGenerator.add_line("CMP EAX, EBX")
            CodeGenerator.add_line("CALL binop_jl")
            CodeGenerator.add_line("MOV EAX, EBX")
            result_type = 'int'
        elif self.value == '>':
            CodeGenerator.add_line("CMP EAX, EBX")
            CodeGenerator.add_line("CALL binop_jg")
            CodeGenerator.add_line("MOV EAX, EBX")
            result_type = 'int'
        else:
            raise Exception(f"Operador '{self.value}' não suportado")

        return (None, result_type)

class UnOp(Node):
    def __init__(self, value, child):
        super().__init__(value)
        self.children = [child]

    def Evaluate(self, symbol_table):
        value, var_type = self.children[0].Evaluate(symbol_table)
        if self.value == '-':
            CodeGenerator.add_line("NEG EAX")
        elif self.value == '!':
            CodeGenerator.add_line("CMP EAX, 0")
            CodeGenerator.add_line("MOV EAX, 0")
            CodeGenerator.add_line("SETE AL")
        else:
            raise Exception(f"Operador unário '{self.value}' não suportado")
        return (None, var_type)

class IntVal(Node):
    def __init__(self, value):
        super().__init__(value)

    def Evaluate(self, symbol_table):
        CodeGenerator.add_line(f"MOV EAX, {self.value}")
        return (self.value, 'int')

class StringVal(Node):
    def __init__(self, value):
        super().__init__(value)

    def Evaluate(self, symbol_table):
        raise NotImplementedError("Strings não suportadas neste roteiro")

class NoOp(Node):
    def Evaluate(self, symbol_table):
        return (None, None)

class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.offset = 0  # Deslocamento atual do EBP

    def declare(self, identifier, var_type):
        if identifier in self.symbols:
            raise Exception(f"Variável '{identifier}' já declarada.")
        self.offset -= 4  # Cada variável ocupa 4 bytes
        self.symbols[identifier] = {
            'offset': self.offset,
            'type': var_type,
            'value': None
        }

    def get(self, identifier):
        if identifier in self.symbols:
            symbol = self.symbols[identifier]
            return symbol['value'], symbol['type'], symbol['offset']
        else:
            raise Exception(f"Variável '{identifier}' não declarada.")

    def set(self, identifier, value, var_type):
        if identifier in self.symbols:
            expected_type = self.symbols[identifier]['type']
            if var_type != expected_type and \
               not (expected_type == 'int' and var_type == 'bool'):
                raise Exception(f"Tipo incompatível para '{identifier}'. "
                                f"Esperado '{expected_type}', recebido "
                                f"'{var_type}'.")
            self.symbols[identifier]['value'] = value
        else:
            raise Exception(f"Variável '{identifier}' não declarada.")

class Identifier(Node):
    def __init__(self, value):
        super().__init__(value)

    def Evaluate(self, symbol_table):
        value, var_type, offset = symbol_table.get(self.value)
        CodeGenerator.add_line(f"MOV EAX, DWORD [EBP{offset}]")
        return (value, var_type)

class Assignment(Node):
    def __init__(self, identifier, expression):
        super().__init__()
        self.identifier = identifier
        self.children = [expression]

    def Evaluate(self, symbol_table):
        value, var_type = self.children[0].Evaluate(symbol_table)
        offset = symbol_table.symbols[self.identifier]['offset']
        CodeGenerator.add_line(f"MOV DWORD [EBP{offset}], EAX")
        symbol_table.set(self.identifier, value, var_type)

class VarDec(Node):
    def __init__(self, var_type, var_list):
        super().__init__()
        self.var_type = var_type
        self.var_list = var_list

    def Evaluate(self, symbol_table):
        for var_name, expr in self.var_list:
            symbol_table.declare(var_name, self.var_type)
            offset = symbol_table.symbols[var_name]['offset']
            if expr:
                value, expr_type = expr.Evaluate(symbol_table)
                if expr_type != self.var_type and \
                   not (self.var_type == 'int' and expr_type == 'bool'):
                    raise Exception(f"Tipo incompatível na atribuição para "
                                    f"'{var_name}'. Esperado '{self.var_type}',"
                                    f" recebido '{expr_type}'.")
                CodeGenerator.add_line(f"MOV DWORD [EBP{offset}], EAX")
            else:
                CodeGenerator.add_line(f"MOV DWORD [EBP{offset}], 0")

class ScanfNode(Node):
    def Evaluate(self, symbol_table):
        raise NotImplementedError("scanf não suportado neste roteiro")

class Print(Node):
    def __init__(self, expression):
        super().__init__()
        self.children = [expression]

    def Evaluate(self, symbol_table):
        value, var_type = self.children[0].Evaluate(symbol_table)
        CodeGenerator.add_line("PUSH EAX")
        CodeGenerator.add_line("CALL print")
        CodeGenerator.add_line("POP EAX")

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
        end_label = f"ENDIF_{self.id}"
        else_label = f"ELSE_{self.id}"

        value, var_type = self.children[0].Evaluate(symbol_table)
        CodeGenerator.add_line("CMP EAX, 0")
        if len(self.children) == 3:
            CodeGenerator.add_line(f"JE {else_label}")
            self.children[1].Evaluate(symbol_table)
            CodeGenerator.add_line(f"JMP {end_label}")
            CodeGenerator.add_line(f"{else_label}:")
            self.children[2].Evaluate(symbol_table)
        else:
            CodeGenerator.add_line(f"JE {end_label}")
            self.children[1].Evaluate(symbol_table)
        CodeGenerator.add_line(f"{end_label}:")

class WhileNode(Node):
    def __init__(self, condition, block):
        super().__init__()
        self.children = [condition, block]

    def Evaluate(self, symbol_table):
        start_label = f"LOOP_{self.id}"
        end_label = f"ENDLOOP_{self.id}"

        CodeGenerator.add_line(f"{start_label}:")
        value, var_type = self.children[0].Evaluate(symbol_table)
        CodeGenerator.add_line("CMP EAX, 0")
        CodeGenerator.add_line(f"JE {end_label}")
        self.children[1].Evaluate(symbol_table)
        CodeGenerator.add_line(f"JMP {start_label}")
        CodeGenerator.add_line(f"{end_label}:")

def main():
    if len(sys.argv) > 1:
        file_names = sys.argv[1:]  # Lista de arquivos de entrada
    else:
        print("Erro: Nenhum arquivo de entrada fornecido.", file=sys.stderr)
        sys.exit(1)

    for file_name in file_names:
        try:
            with open(file_name, 'r') as file:
                code = file.read()
        except FileNotFoundError:
            print(f"Erro: Arquivo '{file_name}' não encontrado.", file=sys.stderr)
            continue  # Passa para o próximo arquivo

        try:
            # Remove comentários do código
            filtered_code = PrePro.filter(code)

            # Executa o Parser e gera a AST
            ast = Parser.run(filtered_code)

            # Criação da tabela de símbolos
            symbol_table = SymbolTable()

            # Executa a AST para gerar o código assembly
            ast.Evaluate(symbol_table)

            # Lê o base.asm
            with open('base.asm', 'r') as f:
                base_asm = f.readlines()

            # Insere o código gerado no lugar apropriado
            final_asm = []
            for line in base_asm:
                if '; codigo gerado pelo compilador' in line:
                    # Insere o código gerado aqui
                    for asm_line in CodeGenerator.code:
                        final_asm.append('  ' + asm_line)
                else:
                    final_asm.append(line.rstrip())

            # Define o nome do arquivo de saída
            output_file = file_name.rsplit('.', 1)[0] + '.asm'

            # Escreve o código assembly final em um arquivo
            with open(output_file, 'w') as f:
                f.write('\n'.join(final_asm))

            print(f"Código assembly gerado em '{output_file}'.")

            # Limpa o código gerado e o contador de IDs para o próximo arquivo
            CodeGenerator.code = []
            Node.i = 0

        except Exception as e:
            print(f"Erro ao processar '{file_name}': {e}", file=sys.stderr)
            continue  # Passa para o próximo arquivo

if __name__ == "__main__":
    main()
