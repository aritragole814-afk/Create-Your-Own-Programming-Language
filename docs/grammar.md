# NovaLang Formal Grammar Specification

## Lexical Grammar

```ebnf
IDENTIFIER   ::= ( [a-z] | [A-Z] | "_" ) { [a-z] | [A-Z] | [0-9] | "_" } ;
INTEGER      ::= [0-9]+ ;
FLOAT        ::= [0-9]+ "." [0-9]+ ;
STRING       ::= '"' { any_character_except_quote_or_newline | escape_sequence } '"' ;
BOOLEAN      ::= "true" | "false" ;

KEYWORD      ::= "let" | "print" | "if" | "else" | "while" 
               | "true" | "false" | "and" | "or" | "not" ;
```

## Syntactic Grammar (EBNF)

```ebnf
program        ::= { declaration } ;

declaration    ::= var_declaration | statement ;
var_declaration::= "let" IDENTIFIER "=" expression ";" ;

statement      ::= print_statement
                 | if_statement
                 | while_statement
                 | block_statement
                 | assignment_statement ;

print_statement::= "print" "(" [ expression { "," expression } ] ")" ";" ;
if_statement   ::= "if" "(" expression ")" block_statement
                   [ "else" ( if_statement | block_statement ) ] ;
while_statement::= "while" "(" expression ")" block_statement ;
block_statement::= "{" { declaration } "}" ;
assignment_statement ::= IDENTIFIER "=" expression ";" ;

expression     ::= logic_or ;
logic_or       ::= logic_and { ( "or" | "||" ) logic_and } ;
logic_and      ::= equality { ( "and" | "&&" ) equality } ;
equality       ::= comparison { ( "==" | "!=" ) comparison } ;
comparison     ::= term { ( ">" | ">=" | "<" | "<=" ) term } ;
term           ::= factor { ( "+" | "-" ) factor } ;
factor         ::= unary { ( "*" | "/" | "%" ) unary } ;
unary          ::= ( "-" | "!" | "not" ) unary | primary ;
primary        ::= INTEGER
                 | FLOAT
                 | STRING
                 | BOOLEAN
                 | IDENTIFIER
                 | "(" expression ")" ;
```
