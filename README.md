# logCompPedroCivita
---
## Repositório Para a Disciplina Lógica da Computação do 7o Semestre de Eng. Comp - Insper

![git status](http://3.129.230.99/svg/pedrocivita/logCompPedroCivita/)

---
## Diagrama Sintático

![logCompR5 drawio](https://github.com/user-attachments/assets/558333dc-6abe-4e54-b128-0423407fad0a)

## EBNF

BLOCK = "{", { STATEMENT }, "}";

STATEMENT = ( λ | ASSIGNMENT | PRINT), ";" ;

ASSIGNMENT = IDENTIFIER, "=", EXPRESSION ;

PRINT = "printf", "(", EXPRESSION, ")" ;

EXPRESSION = TERM, { ("+" | "-"), TERM } ;

TERM = FACTOR, { ("*" | "/"), FACTOR } ;

FACTOR = (("+" | "-"), FACTOR) | NUMBER | "(", EXPRESSION, ")" | IDENTIFIER ;

IDENTIFIER = LETTER, { LETTER | DIGIT | "_" } ;

NUMBER = DIGIT, { DIGIT } ;

LETTER = ( a | ... | z | A | ... | Z ) ;

DIGIT = ( 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 0 ) ;
