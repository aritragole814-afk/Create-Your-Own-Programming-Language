"""Recursive-descent parser that builds NovaLang abstract syntax trees."""

from src.ast_nodes import (
    AssignmentStatement,
    BinaryExpression,
    BlockStatement,
    BooleanExpression,
    Expression,
    IfStatement,
    LogicalExpression,
    NumberExpression,
    PrintStatement,
    Statement,
    StringExpression,
    UnaryExpression,
    VariableDeclaration,
    VariableExpression,
    WhileStatement,
)
from src.tokens import Token, TokenType


class NovaSyntaxError(Exception):
    """Raised when a token sequence does not match the NovaLang grammar."""

    def __init__(self, message: str, line: int, column: int) -> None:
        super().__init__(f"Syntax error at line {line}, column {column}: {message}")
        self.line = line
        self.column = column


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.current = 0

    def parse(self) -> list[Statement]:
        """Parse all tokens into a list of statement AST nodes."""
        statements: list[Statement] = []
        while not self._is_at_end():
            statements.append(self._declaration())
        return statements

    def _declaration(self) -> Statement:
        if self._match(TokenType.LET):
            return self._variable_declaration()
        return self._statement()

    def _variable_declaration(self) -> VariableDeclaration:
        name = self._consume(TokenType.IDENTIFIER, "Expected variable name after 'let'.")
        self._consume(TokenType.EQUAL, "Expected '=' after variable name.")
        initializer = self._expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' after variable declaration.")
        return VariableDeclaration(name, initializer)

    def _statement(self) -> Statement:
        if self._match(TokenType.PRINT):
            return self._print_statement()
        if self._match(TokenType.IF):
            return self._if_statement()
        if self._match(TokenType.WHILE):
            return self._while_statement()
        if self._match(TokenType.LEFT_BRACE):
            return BlockStatement(self._block_statements())
        if self._check(TokenType.IDENTIFIER) and self._check_next(TokenType.EQUAL):
            return self._assignment_statement()
        return self._error_statement()

    def _assignment_statement(self) -> AssignmentStatement:
        name = self._consume(TokenType.IDENTIFIER, "Expected variable identifier.")
        self._consume(TokenType.EQUAL, "Expected '=' in assignment.")
        value = self._expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' after assignment statement.")
        return AssignmentStatement(name, value)

    def _print_statement(self) -> PrintStatement:
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'print'.")
        expressions: list[Expression] = []
        if not self._check(TokenType.RIGHT_PAREN):
            expressions.append(self._expression())
            while self._match(TokenType.COMMA):
                expressions.append(self._expression())
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after print arguments.")
        self._consume(TokenType.SEMICOLON, "Expected ';' after print statement.")
        return PrintStatement(expressions)

    def _if_statement(self) -> IfStatement:
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'if'.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after if condition.")

        self._consume(TokenType.LEFT_BRACE, "Expected '{' before if branch.")
        then_branch = self._block_statements()

        else_branch = None
        if self._match(TokenType.ELSE):
            if self._match(TokenType.IF):
                # else if chained as an inner IfStatement inside else branch
                else_branch = [self._if_statement()]
            else:
                self._consume(TokenType.LEFT_BRACE, "Expected '{' before else branch.")
                else_branch = self._block_statements()

        return IfStatement(condition, then_branch, else_branch)

    def _while_statement(self) -> WhileStatement:
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'while'.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after while condition.")
        self._consume(TokenType.LEFT_BRACE, "Expected '{' before while loop body.")
        body = self._block_statements()
        return WhileStatement(condition, body)

    def _block_statements(self) -> list[Statement]:
        """Parse statements inside a block until the closing '}' is reached."""
        statements: list[Statement] = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            statements.append(self._declaration())
        self._consume(TokenType.RIGHT_BRACE, "Expected '}' after block.")
        return statements

    def _expression(self) -> Expression:
        return self._logic_or()

    def _logic_or(self) -> Expression:
        expression = self._logic_and()
        while self._match(TokenType.OR, TokenType.PIPE_PIPE):
            operator = self._previous()
            right = self._logic_and()
            expression = LogicalExpression(expression, operator, right)
        return expression

    def _logic_and(self) -> Expression:
        expression = self._equality()
        while self._match(TokenType.AND, TokenType.AMPERSAND_AMPERSAND):
            operator = self._previous()
            right = self._equality()
            expression = LogicalExpression(expression, operator, right)
        return expression

    def _equality(self) -> Expression:
        expression = self._comparison()
        while self._match(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            operator = self._previous()
            right = self._comparison()
            expression = BinaryExpression(expression, operator, right)
        return expression

    def _comparison(self) -> Expression:
        expression = self._term()
        while self._match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self._previous()
            right = self._term()
            expression = BinaryExpression(expression, operator, right)
        return expression

    def _term(self) -> Expression:
        expression = self._factor()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous()
            right = self._factor()
            expression = BinaryExpression(expression, operator, right)
        return expression

    def _factor(self) -> Expression:
        expression = self._unary()
        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            operator = self._previous()
            right = self._unary()
            expression = BinaryExpression(expression, operator, right)
        return expression

    def _unary(self) -> Expression:
        if self._match(TokenType.MINUS, TokenType.BANG, TokenType.NOT):
            operator = self._previous()
            return UnaryExpression(operator, self._unary())
        return self._primary()

    def _primary(self) -> Expression:
        if self._match(TokenType.INTEGER, TokenType.FLOAT):
            token = self._previous()
            return NumberExpression(token.literal, token.line)
        if self._match(TokenType.STRING):
            token = self._previous()
            return StringExpression(token.literal, token.line)
        if self._match(TokenType.TRUE, TokenType.FALSE):
            token = self._previous()
            return BooleanExpression(token.literal, token.line)
        if self._match(TokenType.IDENTIFIER):
            token = self._previous()
            return VariableExpression(token.lexeme, token.line)
        if self._match(TokenType.LEFT_PAREN):
            expression = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expected ')' after expression.")
            return expression
        self._error_at(self._peek(), "Expected an expression.")

    def _error_statement(self) -> Statement:
        token = self._peek()
        if token.type == TokenType.EOF:
            self._error_at(token, "Unexpected end of input; expected statement.")
        self._error_at(
            token,
            f"Unexpected token {token.lexeme!r}; expected 'let', 'print', 'if', 'while', assignment or '{{'.",
        )

    def _consume(self, token_type: TokenType, message: str) -> Token:
        if self._check(token_type):
            return self._advance()
        self._error_at(self._peek(), message)

    def _match(self, *token_types: TokenType) -> bool:
        for token_type in token_types:
            if self._check(token_type):
                self._advance()
                return True
        return False

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._peek().type == token_type

    def _check_next(self, token_type: TokenType) -> bool:
        if self.current + 1 >= len(self.tokens):
            return False
        return self.tokens[self.current + 1].type == token_type

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _error_at(self, token: Token, message: str) -> None:
        raise NovaSyntaxError(message, token.line, token.column)
