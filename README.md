# logCompPedroCivita
---
## Repositório Para a Disciplina Lógica da Computação do 7o Semestre de Eng. Comp - Insper

![git status](http://3.129.230.99/svg/pedrocivita/logCompPedroCivita/)

---
## Diagrama Sintático

![DS-Roteiro7 drawio](https://github.com/user-attachments/assets/ac69155a-0318-44c7-aeee-1ec3134e9f85)

## **EBNF**

#### **Definições Básicas**

```ebnf
LETTER          = "a" | "b" | ... | "z" | "A" | "B" | ... | "Z" ;
DIGIT           = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
IDENTIFIER      = LETTER, { LETTER | DIGIT | "_" } ;
NUMBER          = DIGIT, { DIGIT } ;
STRING_LITERAL  = '"', { any character except '"' }, '"' ;
```

#### **Estrutura do Programa**

```ebnf
PROGRAM         = BLOCK ;
BLOCK           = "{", { STATEMENT }, "}" ;
```

#### **Declarações e Comandos**

```ebnf
STATEMENT       = VARIABLE_DECLARATION ";"
                | ASSIGNMENT ";"
                | PRINT ";"
                | SCANF ";"
                | IF_STATEMENT
                | WHILE_STATEMENT
                | BLOCK
                | ";" ;
```

#### **Declaração de Variáveis**

```ebnf
VARIABLE_DECLARATION = TYPE, VARIABLE_LIST ;
TYPE                = "int" | "str" ;
VARIABLE_LIST       = VARIABLE_ENTRY, { ",", VARIABLE_ENTRY } ;
VARIABLE_ENTRY      = IDENTIFIER, [ "=", EXPRESSION ] ;
```

#### **Atribuição e Expressões**

```ebnf
ASSIGNMENT      = IDENTIFIER, "=", EXPRESSION ;
EXPRESSION      = TERM, { ( "+" | "-" | "==" | "!=" | "<" | ">" | "<=" | ">=" | "&&" | "||" ), TERM } ;
TERM            = FACTOR, { ( "*" | "/" ), FACTOR } ;
FACTOR          = [ ( "+" | "-" | "!" ) ], FACTOR
                | NUMBER
                | STRING_LITERAL
                | "(", EXPRESSION, ")"
                | IDENTIFIER
                | SCANF_CALL ;
```

#### **Entrada e Saída**

```ebnf
PRINT           = "printf", "(", EXPRESSION, ")" ;
SCANF           = "scanf", "(", ")" ;
SCANF_CALL      = SCANF ;
```

#### **Estruturas de Controle**

```ebnf
IF_STATEMENT    = "if", "(", EXPRESSION, ")", STATEMENT, [ "else", STATEMENT ] ;
WHILE_STATEMENT = "while", "(", EXPRESSION, ")", STATEMENT ;
```

#### **Operadores e Símbolos**

```ebnf
OPERATOR        = "+" | "-" | "*" | "/" | "==" | "!=" | "<" | ">" | "<=" | ">=" | "&&" | "||" | "!" ;
SEPARATOR       = ";" | "," ;
BRACKET_OPEN    = "(" ;
BRACKET_CLOSE   = ")" ;
BRACE_OPEN      = "{" ;
BRACE_CLOSE     = "}" ;
```
