class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

class Tokenizer:
    def __init__(self, source):
        self.source = source
        self.position = 0
        self.next = None

    def selectNext(self):
        if self.position >= len(self.source):
            self.next = Token("EOF", None)
            return

        current_char = self.source[self.position]

        if current_char.isdigit():
            number = ""
            while self.position < len(self.source) and self.source[self.position].isdigit():
                number += self.source[self.position]
                self.position += 1
            self.next = Token("NUMBER", int(number))
        elif current_char in "+-":
            self.next = Token("OPERATOR", current_char)
            self.position += 1
        elif current_char.isspace():
            self.position += 1
            self.selectNext()
        else:
            raise ValueError(f"Caractere inválido: {current_char}")

class Parser:
    @staticmethod
    def parseExpression():
        result = Parser.parseTerm()

        while Parser.tokenizer.next.type == "OPERATOR":
            if Parser.tokenizer.next.value == "+":
                Parser.tokenizer.selectNext()
                result += Parser.parseTerm()
            elif Parser.tokenizer.next.value == "-":
                Parser.tokenizer.selectNext()
                result -= Parser.parseTerm()

        return result

    @staticmethod
    def parseTerm():
        if Parser.tokenizer.next.type == "NUMBER":
            value = Parser.tokenizer.next.value
            Parser.tokenizer.selectNext()
            return value
        else:
            raise ValueError("Erro de sintaxe")

    @staticmethod
    def run(code):
        Parser.tokenizer = Tokenizer(code)
        Parser.tokenizer.selectNext()
        result = Parser.parseExpression()
        if Parser.tokenizer.next.type != "EOF":
            raise ValueError("Código não totalmente consumido")
        return result

def main():
    while True:
        try:
            code = input(">> ")
            result = Parser.run(code)
            print(result)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    main()