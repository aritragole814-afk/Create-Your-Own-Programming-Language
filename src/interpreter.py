"""Evaluate NovaLang abstract syntax trees with scoped environments."""

from __future__ import annotations

from typing import Any

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


class NovaRuntimeError(Exception):
    """Raised when a valid NovaLang program encounters a runtime error."""

    def __init__(self, message: str, line: int | None = None) -> None:
        loc = f" at line {line}" if line is not None else ""
        super().__init__(f"Runtime error{loc}: {message}")
        self.line = line


class Environment:
    """Symbol table and environment supporting lexical scoping."""

    def __init__(self, enclosing: Environment | None = None) -> None:
        self.values: dict[str, Any] = {}
        self.enclosing: Environment | None = enclosing

    def define(self, name: str, value: Any) -> None:
        """Define a new variable in the current scope."""
        self.values[name] = value

    def assign(self, name_token: Token, value: Any) -> None:
        """Assign to an existing variable, searching enclosing scopes."""
        if name_token.lexeme in self.values:
            self.values[name_token.lexeme] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name_token, value)
            return
        raise NovaRuntimeError(
            f"Cannot assign to undefined variable {name_token.lexeme!r}.",
            name_token.line,
        )

    def get(self, name_token: Token | str, line: int | None = None) -> Any:
        """Retrieve variable value from current or enclosing scopes."""
        lexeme = name_token.lexeme if isinstance(name_token, Token) else name_token
        token_line = name_token.line if isinstance(name_token, Token) else line

        if lexeme in self.values:
            return self.values[lexeme]
        if self.enclosing is not None:
            return self.enclosing.get(name_token, token_line)
        raise NovaRuntimeError(f"Undefined variable {lexeme!r}.", token_line)


class Interpreter:
    def __init__(self) -> None:
        self.globals: Environment = Environment()
        self.environment: Environment = self.globals
        self.max_loop_iterations: int = 1_000_000  # Protection against infinite loops

    def interpret(self, statements: list[Statement]) -> None:
        """Execute all statements in the AST."""
        for statement in statements:
            self._execute(statement)

    def _execute(self, statement: Statement) -> None:
        if isinstance(statement, VariableDeclaration):
            value = self._evaluate(statement.initializer)
            self.environment.define(statement.name.lexeme, value)
        elif isinstance(statement, AssignmentStatement):
            value = self._evaluate(statement.value)
            self.environment.assign(statement.name, value)
        elif isinstance(statement, PrintStatement):
            results = [self._format_value(self._evaluate(expr)) for expr in statement.expressions]
            print(" ".join(results))
        elif isinstance(statement, IfStatement):
            condition = self._evaluate(statement.condition)
            if not isinstance(condition, bool):
                self._runtime_error(
                    statement.condition, "An 'if' condition must evaluate to a boolean."
                )
            if condition:
                self._execute_block(statement.then_branch, Environment(self.environment))
            elif statement.else_branch is not None:
                self._execute_block(statement.else_branch, Environment(self.environment))
        elif isinstance(statement, WhileStatement):
            iterations = 0
            while True:
                condition = self._evaluate(statement.condition)
                if not isinstance(condition, bool):
                    self._runtime_error(
                        statement.condition, "A 'while' condition must evaluate to a boolean."
                    )
                if not condition:
                    break
                iterations += 1
                if iterations > self.max_loop_iterations:
                    self._runtime_error(
                        statement.condition, "Maximum loop iteration limit exceeded (infinite loop detected)."
                    )
                self._execute_block(statement.body, Environment(self.environment))
        elif isinstance(statement, BlockStatement):
            self._execute_block(statement.statements, Environment(self.environment))
        else:
            raise NovaRuntimeError("Unsupported statement type.")

    def _execute_block(self, statements: list[Statement], environment: Environment) -> None:
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self._execute(statement)
        finally:
            self.environment = previous

    def _evaluate(self, expression: Expression) -> Any:
        if isinstance(expression, NumberExpression):
            return expression.value
        if isinstance(expression, StringExpression):
            return expression.value
        if isinstance(expression, BooleanExpression):
            return expression.value
        if isinstance(expression, VariableExpression):
            return self.environment.get(expression.name, expression.line)
        if isinstance(expression, UnaryExpression):
            operand_val = self._evaluate(expression.operand)
            op = expression.operator.type
            if op == TokenType.MINUS:
                num = self._require_number(operand_val, expression)
                return -num
            if op in (TokenType.BANG, TokenType.NOT):
                b = self._require_boolean(operand_val, expression)
                return not b
            self._runtime_error(expression, f"Unsupported unary operator {expression.operator.lexeme!r}.")
        if isinstance(expression, BinaryExpression):
            return self._evaluate_binary(expression)
        if isinstance(expression, LogicalExpression):
            return self._evaluate_logical(expression)
        raise NovaRuntimeError("Unsupported expression type.")

    def _evaluate_logical(self, expression: LogicalExpression) -> bool:
        left_val = self._evaluate(expression.left)
        left_bool = self._require_boolean(left_val, expression.left)
        op = expression.operator.type

        # Short-circuit evaluation
        if op in (TokenType.OR, TokenType.PIPE_PIPE):
            if left_bool:
                return True
        elif op in (TokenType.AND, TokenType.AMPERSAND_AMPERSAND):
            if not left_bool:
                return False

        right_val = self._evaluate(expression.right)
        return self._require_boolean(right_val, expression.right)

    def _evaluate_binary(self, expression: BinaryExpression) -> Any:
        left = self._evaluate(expression.left)
        right = self._evaluate(expression.right)
        op = expression.operator.type

        # Equality operators
        if op in (TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            equal = self._values_equal(left, right)
            return equal if op == TokenType.EQUAL_EQUAL else not equal

        # String concatenation
        if op == TokenType.PLUS and (isinstance(left, str) or isinstance(right, str)):
            return f"{self._format_value(left)}{self._format_value(right)}"

        # Arithmetic and relational operators require numeric operands
        left_num = self._require_number(left, expression.left)
        right_num = self._require_number(right, expression.right)

        if op == TokenType.PLUS:
            return left_num + right_num
        if op == TokenType.MINUS:
            return left_num - right_num
        if op == TokenType.STAR:
            return left_num * right_num
        if op == TokenType.SLASH:
            if right_num == 0:
                self._runtime_error(expression, "Division by zero is not allowed.")
            return left_num / right_num
        if op == TokenType.PERCENT:
            if right_num == 0:
                self._runtime_error(expression, "Modulo by zero is not allowed.")
            return left_num % right_num
        if op == TokenType.GREATER:
            return left_num > right_num
        if op == TokenType.GREATER_EQUAL:
            return left_num >= right_num
        if op == TokenType.LESS:
            return left_num < right_num
        if op == TokenType.LESS_EQUAL:
            return left_num <= right_num

        self._runtime_error(expression, f"Unsupported binary operator {expression.operator.lexeme!r}.")

    def _require_number(self, value: Any, expression: Expression) -> int | float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            self._runtime_error(
                expression, f"Operand must be a number, got {type(value).__name__}."
            )
        return value

    def _require_boolean(self, value: Any, expression: Expression) -> bool:
        if not isinstance(value, bool):
            self._runtime_error(
                expression, f"Operand must be a boolean, got {type(value).__name__}."
            )
        return value

    def _values_equal(self, left: Any, right: Any) -> bool:
        if isinstance(left, bool) != isinstance(right, bool):
            return False
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left == right
        return type(left) is type(right) and left == right

    def _format_value(self, value: Any) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)

    def _runtime_error(self, node: Any, message: str) -> None:
        line = getattr(node, "line", None)
        if line is None:
            op = getattr(node, "operator", None)
            if op is not None:
                line = getattr(op, "line", None)
        raise NovaRuntimeError(message, line)
