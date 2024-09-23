# logCompPedroCivita
---
## Repositório Para a Disciplina Lógica da Computação do 7o Semestre de Eng. Comp - Insper

![git status](http://3.129.230.99/svg/pedrocivita/logCompPedroCivita/)

---
## Diagrama Sintático

![Design sem nome (5)](https://github.com/user-attachments/assets/3843d6c9-bc06-4f56-8620-d4280d8f12ba)

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
