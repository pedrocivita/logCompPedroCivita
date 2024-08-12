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
        else:
            raise ValueError(f"Unexpected character: {current_char}")


class Parser:
    @staticmethod
    def parseExpression():
        if Parser.tokenizer.next.type == 'INT':
            result = Parser.tokenizer.next.value
            Parser.tokenizer.selectNext()

            while Parser.tokenizer.next.type in ['PLUS', 'MINUS']:
                op_type = Parser.tokenizer.next.type
                Parser.tokenizer.selectNext()

                if Parser.tokenizer.next.type != 'INT':
                    raise ValueError(f"Syntax Error: Expected INT after {op_type}")
                
                if op_type == 'PLUS':
                    result += Parser.tokenizer.next.value
                elif op_type == 'MINUS':
                    result -= Parser.tokenizer.next.value
                
                Parser.tokenizer.selectNext()

            return result
        else:
            raise ValueError("Syntax Error: Expected INT at the start of expression")

    @staticmethod
    def run(code: str):
        Parser.tokenizer = Tokenizer(code)
        Parser.tokenizer.selectNext()

        if Parser.tokenizer.next.type == 'EOF':
            raise ValueError("Syntax Error: Empty input")

        result = Parser.parseExpression()

        if Parser.tokenizer.next.type != 'EOF':
            raise ValueError("Syntax Error: Expected EOF at the end of expression")

        return result


def main():
    code = input("Enter an expression: ")
    try:
        result = Parser.run(code)
        print(f"Result: {result}")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
