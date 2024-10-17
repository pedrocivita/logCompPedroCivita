import sys
import re
from abc import ABC, abstractmethod

class Token:
    def __init__(self, tipo, valor):
        self.tipo = tipo
        self.valor = valor

class Tokenizer:
    def __init__(self, fonte):
        self.fonte = fonte.strip()
        self.posicao = 0
        self.next = None
        self.selectNext()

    def selectNext(self):
        while self.posicao < len(self.fonte) and self.fonte[self.posicao].isspace():
            self.posicao += 1

        if self.posicao >= len(self.fonte):
            self.next = Token('EOF', None)
            return

        char_atual = self.fonte[self.posicao]

        if char_atual == '"':
            self.posicao += 1  # Consome a aspas inicial
            string = ''
            while self.posicao < len(self.fonte) and self.fonte[self.posicao] != '"':
                string += self.fonte[self.posicao]
                self.posicao += 1
            if self.posicao >= len(self.fonte):
                raise Exception("String não finalizada")
            self.posicao += 1  # Consome a aspas final
            self.next = Token('STRING', string)
            return

        if char_atual.isdigit():
            numero = ''
            while self.posicao < len(self.fonte) and self.fonte[self.posicao].isdigit():
                numero += self.fonte[self.posicao]
                self.posicao += 1
            self.next = Token('INT', int(numero))
            return

        if char_atual.isalpha() or char_atual == '_':
            identificador = ''
            while self.posicao < len(self.fonte) and (self.fonte[self.posicao].isalnum() or self.fonte[self.posicao] == '_'):
                identificador += self.fonte[self.posicao]
                self.posicao += 1
            if identificador in ['printf', 'scanf', 'if', 'else', 'while', 'int', 'str']:
                self.next = Token('RESERVED', identificador)
            else:
                self.next = Token('ID', identificador)
            return

        if char_atual in '+-*/(){}=;><!&|,':
            if self.fonte[self.posicao:self.posicao+2] in ['<=', '>=', '==', '!=', '&&', '||']:
                self.next = Token('OPERATOR', self.fonte[self.posicao:self.posicao+2])
                self.posicao += 2
            else:
                self.next = Token('OPERATOR', char_atual)
                self.posicao += 1
            return

        raise Exception(f"Caractere inesperado: {char_atual}")

class Parser:
    @staticmethod
    def run(codigo):
        Parser.tokenizer = Tokenizer(codigo)
        resultado = Parser.parseBlock()
        if Parser.tokenizer.next.tipo != 'EOF':
            raise Exception("Erro: código após o fim do programa")
        return resultado

    @staticmethod
    def parseBlock():
        if Parser.tokenizer.next.valor != '{':
            raise Exception("Esperado '{'")
        Parser.tokenizer.selectNext()
        comandos = []
        while Parser.tokenizer.next.valor != '}':
            comandos.append(Parser.parseStatement())
        Parser.tokenizer.selectNext()  # Consome '}'
        return Block(comandos)

    @staticmethod
    def parseStatement():
        if Parser.tokenizer.next.valor == ';':
            Parser.tokenizer.selectNext()
            return NoOp()

        if Parser.tokenizer.next.tipo == 'RESERVED':
            if Parser.tokenizer.next.valor in ['int', 'str']:
                tipo = Parser.tokenizer.next.valor
                Parser.tokenizer.selectNext()
                if Parser.tokenizer.next.tipo != 'ID':
                    raise Exception("Esperado identificador")
                nome_var = Parser.tokenizer.next.valor
                Parser.tokenizer.selectNext()
                if Parser.tokenizer.next.valor == '=':
                    Parser.tokenizer.selectNext()
                    expressao = Parser.parseExpression()
                else:
                    expressao = None
                if Parser.tokenizer.next.valor != ';':
                    raise Exception("Esperado ';'")
                Parser.tokenizer.selectNext()
                return VarDec(tipo, [(nome_var, expressao)])
            elif Parser.tokenizer.next.valor == 'printf':
                Parser.tokenizer.selectNext()
                if Parser.tokenizer.next.valor != '(':
                    raise Exception("Esperado '(' após 'printf'")
                Parser.tokenizer.selectNext()
                expressao = Parser.parseExpression()
                if Parser.tokenizer.next.valor != ')':
                    raise Exception("Esperado ')' após expressão em 'printf'")
                Parser.tokenizer.selectNext()
                if Parser.tokenizer.next.valor != ';':
                    raise Exception("Esperado ';'")
                Parser.tokenizer.selectNext()
                return Print(expressao)
            elif Parser.tokenizer.next.valor == 'while':
                Parser.tokenizer.selectNext()
                if Parser.tokenizer.next.valor != '(':
                    raise Exception("Esperado '(' após 'while'")
                Parser.tokenizer.selectNext()
                condicao = Parser.parseExpression()
                if Parser.tokenizer.next.valor != ')':
                    raise Exception("Esperado ')' após condição")
                Parser.tokenizer.selectNext()
                comando = Parser.parseStatement()
                return WhileNode(condicao, comando)
            elif Parser.tokenizer.next.valor == 'if':
                Parser.tokenizer.selectNext()
                if Parser.tokenizer.next.valor != '(':
                    raise Exception("Esperado '(' após 'if'")
                Parser.tokenizer.selectNext()
                condicao = Parser.parseExpression()
                if Parser.tokenizer.next.valor != ')':
                    raise Exception("Esperado ')' após condição")
                Parser.tokenizer.selectNext()
                comando = Parser.parseStatement()
                if Parser.tokenizer.next.valor == 'else':
                    Parser.tokenizer.selectNext()
                    comando_else = Parser.parseStatement()
                    return IfNode(condicao, comando, comando_else)
                return IfNode(condicao, comando)
        elif Parser.tokenizer.next.tipo == 'ID':
            nome_var = Parser.tokenizer.next.valor
            Parser.tokenizer.selectNext()
            if Parser.tokenizer.next.valor != '=':
                raise Exception("Esperado '=' após identificador")
            Parser.tokenizer.selectNext()
            expressao = Parser.parseExpression()
            if Parser.tokenizer.next.valor != ';':
                raise Exception("Esperado ';'")
            Parser.tokenizer.selectNext()
            return Assignment(nome_var, expressao)
        elif Parser.tokenizer.next.valor == '{':
            return Parser.parseBlock()
        else:
            raise Exception(f"Comando desconhecido: {Parser.tokenizer.next.valor}")

    @staticmethod
    def parseExpression():
        resultado = Parser.parseTerm()
        while Parser.tokenizer.next.valor in ['+', '-', '||', '==', '!=', '<', '>', '<=', '>=']:
            operador = Parser.tokenizer.next.valor
            Parser.tokenizer.selectNext()
            direita = Parser.parseTerm()
            resultado = BinOp(operador, resultado, direita)
        return resultado

    @staticmethod
    def parseTerm():
        resultado = Parser.parseFactor()
        while Parser.tokenizer.next.valor in ['*', '/', '&&']:
            operador = Parser.tokenizer.next.valor
            Parser.tokenizer.selectNext()
            direita = Parser.parseFactor()
            resultado = BinOp(operador, resultado, direita)
        return resultado

    @staticmethod
    def parseFactor():
        if Parser.tokenizer.next.valor == '(':
            Parser.tokenizer.selectNext()
            resultado = Parser.parseExpression()
            if Parser.tokenizer.next.valor != ')':
                raise Exception("Esperado ')'")
            Parser.tokenizer.selectNext()
            return resultado
        elif Parser.tokenizer.next.valor == '!':
            Parser.tokenizer.selectNext()
            fator = Parser.parseFactor()
            return UnOp('!', fator)
        elif Parser.tokenizer.next.valor == '-':
            Parser.tokenizer.selectNext()
            fator = Parser.parseFactor()
            return UnOp('-', fator)
        elif Parser.tokenizer.next.tipo == 'INT':
            valor = Parser.tokenizer.next.valor
            Parser.tokenizer.selectNext()
            return IntVal(valor)
        elif Parser.tokenizer.next.tipo == 'ID':
            nome_var = Parser.tokenizer.next.valor
            Parser.tokenizer.selectNext()
            return Identifier(nome_var)
        else:
            raise Exception(f"Fator inesperado: {Parser.tokenizer.next.valor}")

class PrePro:
    @staticmethod
    def filter(codigo):
        codigo = re.sub(r'/\*.*?\*/', '', codigo, flags=re.DOTALL)
        return codigo

class Node(ABC):
    i = 0

    def __init__(self, valor=None):
        self.valor = valor
        self.children = []
        self.id = Node.newId()

    @staticmethod
    def newId():
        Node.i += 1
        return Node.i

    @abstractmethod
    def Evaluate(self, tabela_simbolos):
        pass

class SymbolTable:
    def __init__(self):
        self.tabela = {}
        self.offset = 0

    def declare(self, nome, tipo):
        if nome in self.tabela:
            raise Exception(f"Variável '{nome}' já declarada")
        self.offset -= 4  # DWORD ocupa 4 bytes
        self.tabela[nome] = {'tipo': tipo, 'offset': self.offset}

    def getter(self, nome):
        if nome in self.tabela:
            return self.tabela[nome]
        else:
            raise Exception(f"Variável '{nome}' não declarada")

class BinOp(Node):
    def __init__(self, valor, esquerda, direita):
        super().__init__(valor)
        self.children = [esquerda, direita]

    def Evaluate(self, tabela_simbolos):
        # Avalia o operando direito primeiro
        self.children[1].Evaluate(tabela_simbolos)
        CodeGenerator.add_line('PUSH EAX')  # Empilha o operando direito
        # Avalia o operando esquerdo
        self.children[0].Evaluate(tabela_simbolos)
        CodeGenerator.add_line('POP EBX')   # Desempilha para EBX (operando direito)
        # Agora, EAX tem o operando esquerdo, EBX tem o operando direito

        if self.valor == '+':
            CodeGenerator.add_line('ADD EAX, EBX')  # EAX = EAX + EBX
        elif self.valor == '-':
            CodeGenerator.add_line('SUB EAX, EBX')  # EAX = EAX - EBX
        elif self.valor == '*':
            CodeGenerator.add_line('IMUL EAX, EBX')  # EAX = EAX * EBX
        elif self.valor == '/':
            CodeGenerator.add_line('CDQ')           # Extende EAX para EDX:EAX
            CodeGenerator.add_line('IDIV EBX')      # EAX = EAX / EBX
        elif self.valor == '&&':
            CodeGenerator.add_line('AND EAX, EBX')
        elif self.valor == '||':
            CodeGenerator.add_line('OR EAX, EBX')
        elif self.valor in ['==', '!=', '<', '>', '<=', '>=']:
            CodeGenerator.add_line('CMP EAX, EBX')  # Compara EAX com EBX
            CodeGenerator.add_line('MOV EAX, 0')
            if self.valor == '==':
                CodeGenerator.add_line('SETE AL')
            elif self.valor == '!=':
                CodeGenerator.add_line('SETNE AL')
            elif self.valor == '<':
                CodeGenerator.add_line('SETL AL')
            elif self.valor == '>':
                CodeGenerator.add_line('SETG AL')
            elif self.valor == '<=':
                CodeGenerator.add_line('SETLE AL')
            elif self.valor == '>=':
                CodeGenerator.add_line('SETGE AL')
        else:
            raise Exception(f"Operador '{self.valor}' não suportado")

class UnOp(Node):
    def __init__(self, valor, filho):
        super().__init__(valor)
        self.children = [filho]

    def Evaluate(self, tabela_simbolos):
        self.children[0].Evaluate(tabela_simbolos)
        if self.valor == '-':
            CodeGenerator.add_line('NEG EAX')
        elif self.valor == '!':
            CodeGenerator.add_line('CMP EAX, 0')
            CodeGenerator.add_line('MOV EAX, 0')
            CodeGenerator.add_line('SETE AL')
        else:
            raise Exception(f"Operador '{self.valor}' não suportado")

class IntVal(Node):
    def __init__(self, valor):
        super().__init__(valor)

    def Evaluate(self, tabela_simbolos):
        CodeGenerator.add_line(f'MOV EAX, {self.valor}')

class Identifier(Node):
    def __init__(self, valor):
        super().__init__(valor)

    def Evaluate(self, tabela_simbolos):
        var_info = tabela_simbolos.getter(self.valor)
        offset = var_info['offset']
        CodeGenerator.add_line(f'MOV EAX, DWORD [EBP{offset}]')

class Assignment(Node):
    def __init__(self, nome, expressao):
        super().__init__()
        self.nome = nome
        self.children = [expressao]

    def Evaluate(self, tabela_simbolos):
        var_info = tabela_simbolos.getter(self.nome)
        offset = var_info['offset']
        self.children[0].Evaluate(tabela_simbolos)
        CodeGenerator.add_line(f'MOV DWORD [EBP{offset}], EAX')

class VarDec(Node):
    def __init__(self, tipo, lista_variaveis):
        super().__init__()
        self.tipo = tipo
        self.lista_variaveis = lista_variaveis

    def Evaluate(self, tabela_simbolos):
        for nome, expressao in self.lista_variaveis:
            tabela_simbolos.declare(nome, self.tipo)
            var_info = tabela_simbolos.getter(nome)
            offset = var_info['offset']
            CodeGenerator.add_line('PUSH DWORD 0')
            if expressao is not None:
                expressao.Evaluate(tabela_simbolos)
                CodeGenerator.add_line(f'MOV DWORD [EBP{offset}], EAX')

class Print(Node):
    def __init__(self, expressao):
        super().__init__()
        self.children = [expressao]

    def Evaluate(self, tabela_simbolos):
        self.children[0].Evaluate(tabela_simbolos)
        CodeGenerator.add_line('PUSH EAX')
        CodeGenerator.add_line('CALL print')
        CodeGenerator.add_line('ADD ESP, 4')

class Block(Node):
    def __init__(self, comandos):
        super().__init__()
        self.children = comandos

    def Evaluate(self, tabela_simbolos):
        for comando in self.children:
            comando.Evaluate(tabela_simbolos)

class WhileNode(Node):
    def __init__(self, condicao, comando):
        super().__init__()
        self.children = [condicao, comando]

    def Evaluate(self, tabela_simbolos):
        label_inicio = f'LOOP_{self.id}'
        label_fim = f'ENDLOOP_{self.id}'
        CodeGenerator.add_line(f'{label_inicio}:')
        self.children[0].Evaluate(tabela_simbolos)
        CodeGenerator.add_line('CMP EAX, 0')
        CodeGenerator.add_line(f'JE {label_fim}')
        self.children[1].Evaluate(tabela_simbolos)
        CodeGenerator.add_line(f'JMP {label_inicio}')
        CodeGenerator.add_line(f'{label_fim}:')

class IfNode(Node):
    def __init__(self, condicao, comando_if, comando_else=None):
        super().__init__()
        self.children = [condicao, comando_if]
        if comando_else:
            self.children.append(comando_else)

    def Evaluate(self, tabela_simbolos):
        label_else = f'ELSE_{self.id}'
        label_fim = f'ENDIF_{self.id}'
        self.children[0].Evaluate(tabela_simbolos)
        CodeGenerator.add_line('CMP EAX, 0')
        if len(self.children) == 3:
            CodeGenerator.add_line(f'JE {label_else}')
            self.children[1].Evaluate(tabela_simbolos)
            CodeGenerator.add_line(f'JMP {label_fim}')
            CodeGenerator.add_line(f'{label_else}:')
            self.children[2].Evaluate(tabela_simbolos)
            CodeGenerator.add_line(f'{label_fim}:')
        else:
            CodeGenerator.add_line(f'JE {label_fim}')
            self.children[1].Evaluate(tabela_simbolos)
            CodeGenerator.add_line(f'{label_fim}:')

class NoOp(Node):
    def Evaluate(self, tabela_simbolos):
        pass

class CodeGenerator:
    code = []

    @staticmethod
    def add_line(line):
        CodeGenerator.code.append(line.strip())

    @staticmethod
    def initialize():
        CodeGenerator.code = []
        # Não adicionamos 'global main' ou 'main:', pois o base.asm já define 'main'

    @staticmethod
    def finalize():
        pass  # Não precisamos adicionar código de finalização aqui

    @staticmethod
    def get_code():
        return '\n'.join(CodeGenerator.code)

def main():
    if len(sys.argv) > 1:
        nome_arquivo = sys.argv[1]
    else:
        print("Erro: Nenhum arquivo de entrada fornecido.")
        sys.exit(1)

    try:
        with open(nome_arquivo, 'r') as f:
            codigo = f.read()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{nome_arquivo}' não encontrado.")
        sys.exit(1)

    codigo_filtrado = PrePro.filter(codigo)

    try:
        ast = Parser.run(codigo_filtrado)
    except Exception as e:
        print(f"Erro de parsing: {e}")
        sys.exit(1)

    tabela_simbolos = SymbolTable()

    # Inicializa o CodeGenerator
    CodeGenerator.initialize()

    # Avalia a AST para gerar o código assembly
    ast.Evaluate(tabela_simbolos)

    # Finaliza o código gerado
    CodeGenerator.finalize()

    # Lê o base.asm
    try:
        with open('base.asm', 'r') as f:
            base_asm = f.readlines()
    except FileNotFoundError:
        print("Erro: Arquivo 'base.asm' não encontrado.")
        sys.exit(1)

    # Insere o código gerado no lugar apropriado
    final_asm = []
    for linha in base_asm:
        if '; codigo gerado pelo compilador' in linha:
            for linha_codigo in CodeGenerator.code:
                final_asm.append('  ' + linha_codigo)
        else:
            final_asm.append(linha.rstrip())

    # Determinação do nome do arquivo de saída
    nome_saida = nome_arquivo.rsplit('.', 1)[0] + '.asm'
    with open(nome_saida, 'w') as f:
        f.write('\n'.join(final_asm))

    print(f"Código assembly gerado em '{nome_saida}'.")

if __name__ == '__main__':
    main()
