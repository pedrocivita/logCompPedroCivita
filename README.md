# logCompPedroCivita
---
## Repositório Para a Disciplina Lógica da Computação do 7o Semestre de Eng. Comp - Insper

![git status](http://3.129.230.99/svg/pedrocivita/logCompPedroCivita/)

---
## Diagrama Sintático

![DiagramaSintatico_Roteiro9](https://github.com/user-attachments/assets/b306d703-e88e-45e2-b2c9-6b731ddb3f5d)

---

## **EBNF**

#### **Definições Básicas**

```ebnf
LETTER          = "a" | "b" | ... | "z" | "A" | "B" | ... | "Z" ;
DIGIT           = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
IDENTIFIER      = LETTER, { LETTER | DIGIT | "_" } ;
NUMBER          = DIGIT, { DIGIT } ;
STRING_LITERAL  = '"', { qualquer caractere exceto '"' }, '"' ;
```

#### **Estrutura do Programa**

```ebnf
PROGRAM             = { FUNCTION_DECLARATION } ;
```

#### **Declarações de Funções**

```ebnf
FUNCTION_DECLARATION = TYPE, IDENTIFIER, "(", [ PARAMETER_LIST ], ")", BLOCK ;
PARAMETER_LIST       = PARAMETER, { ",", PARAMETER } ;
PARAMETER            = VARIABLE_TYPE, IDENTIFIER ;
```

#### **Tipos**

```ebnf
TYPE                = "int" | "str" | "void" ;
VARIABLE_TYPE       = "int" | "str" ;
```

#### **Blocos e Comandos**

```ebnf
BLOCK               = "{", { STATEMENT }, "}" ;
STATEMENT           = VARIABLE_DECLARATION ";"
                    | ASSIGNMENT ";"
                    | PRINT ";"
                    | SCANF ";"
                    | RETURN_STATEMENT ";"
                    | IF_STATEMENT
                    | WHILE_STATEMENT
                    | FUNCTION_CALL ";"
                    | BLOCK
                    | ";" ;
```

#### **Declaração de Variáveis**

```ebnf
VARIABLE_DECLARATION = VARIABLE_TYPE, VARIABLE_LIST ;
VARIABLE_LIST        = VARIABLE_ENTRY, { ",", VARIABLE_ENTRY } ;
VARIABLE_ENTRY       = IDENTIFIER, [ "=", EXPRESSION ] ;
```

#### **Retorno**

```ebnf
RETURN_STATEMENT     = "return", EXPRESSION ;
```

#### **Atribuição e Expressões**

```ebnf
ASSIGNMENT          = IDENTIFIER, "=", EXPRESSION ;
EXPRESSION          = TERM, { ( "+" | "-" | "==" | "!=" | "<" | ">" | "<=" | ">=" | "&&" | "||" ), TERM } ;
TERM                = FACTOR, { ( "*" | "/" ), FACTOR } ;
FACTOR              = [ ( "+" | "-" | "!" ) ], (
                        NUMBER
                      | STRING_LITERAL
                      | "(", EXPRESSION, ")"
                      | IDENTIFIER
                      | FUNCTION_CALL
                      | SCANF_CALL
                      ) ;
```

#### **Chamada de Função**

```ebnf
FUNCTION_CALL       = IDENTIFIER, "(", [ ARGUMENT_LIST ], ")" ;
ARGUMENT_LIST       = EXPRESSION, { ",", EXPRESSION } ;
```

#### **Entrada e Saída**

```ebnf
PRINT               = "printf", "(", EXPRESSION, ")" ;
SCANF               = "scanf", "(", ")" ;
SCANF_CALL          = SCANF ;
```

#### **Estruturas de Controle**

```ebnf
IF_STATEMENT        = "if", "(", EXPRESSION, ")", STATEMENT, [ "else", STATEMENT ] ;
WHILE_STATEMENT     = "while", "(", EXPRESSION, ")", STATEMENT ;
```

#### **Operadores e Símbolos**

```ebnf
OPERATOR            = "+" | "-" | "*" | "/" | "==" | "!=" | "<" | ">" | "<=" | ">=" | "&&" | "||" | "!" ;
SEPARATOR           = ";" | "," ;
BRACKET_OPEN        = "(" ;
BRACKET_CLOSE       = ")" ;
BRACE_OPEN          = "{" ;
BRACE_CLOSE         = "}" ;
```

---
