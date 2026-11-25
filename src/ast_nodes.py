"""Abstract syntax tree node definitions for NovaLang."""

from dataclasses import dataclass
from src.tokens import Token


class ASTNode:
    """Base class for all AST nodes with pretty-printing capabilities."""

    def to_tree_str(self, indent: int = 0) -> str:
        prefix = "  " * indent
        return f"{prefix}{self.__class__.__name__}"


class Expression(ASTNode):
    """Base class for expression nodes."""


class Statement(ASTNode):
    """Base class for statement nodes."""


@dataclass(frozen=True)
class NumberExpression(Expression):
    value: int | float
    line: int

    def to_tree_str(self, indent: int = 0) -> str:
        prefix = "  " * indent
        return f"{prefix}Number({self.value})"


@dataclass(frozen=True)
class StringExpression(Expression):
    value: str
    line: int

    def to_tree_str(self, indent: int = 0) -> str:
        prefix = "  " * indent
        return f"{prefix}String({self.value!r})"


@dataclass(frozen=True)
class BooleanExpression(Expression):
    value: bool
    line: int

    def to_tree_str(self, indent: int = 0) -> str:
        prefix = "  " * indent
        return f"{prefix}Boolean({str(self.value).lower()})"


@dataclass(frozen=True)
class VariableExpression(Expression):
    name: str
    line: int

    def to_tree_str(self, indent: int = 0) -> str:
        prefix = "  " * indent
        return f"{prefix}Variable({self.name})"


@dataclass(frozen=True)
class UnaryExpression(Expression):
    operator: Token
    operand: Expression

    def to_tree_str(self, indent: int = 0) -> str:
        prefix = "  " * indent
        lines = [f"{prefix}Unary({self.operator.lexeme})"]
        lines.append(self.operand.to_tree_str(indent + 1))
        return "\n".join(lines)


@dataclass(frozen=True)
class BinaryExpression(Expression):
    left: Expression
    operator: Token
    right: Expression

    def to_tree_str(self, indent: int = 0) -> str:
        prefix = "  " * indent
        lines = [f"{prefix}Binary({self.operator.lexeme})"]
        lines.append(self.left.to_tree_str(indent + 1))
        lines.append(self.right.to_tree_str(indent + 1))
        return "\n".join(lines)


@dataclass(frozen=True)
class LogicalExpression(Expression):
    left: Expression
    operator: Token
    right: Expression

    def to_tree_str(self, indent: int = 0) -> str:
        prefix = "  " * indent
        lines = [f"{prefix}Logical({self.operator.lexeme})"]
        lines.append(self.left.to_tree_str(indent + 1))
        lines.append(self.right.to_tree_str(indent + 1))
        return "\n".join(lines)


@dataclass(frozen=True)
class VariableDeclaration(Statement):
    name: Token
    initializer: Expression

    def to_tree_str(self, indent: int = 0) -> str:
        prefix = "  " * indent
        lines = [f"{prefix}VariableDeclaration({self.name.lexeme})"]
        lines.append(self.initializer.to_tree_str(indent + 1))
        return "\n".join(lines)


@dataclass(frozen=True)
class AssignmentStatement(Statement):
    name: Token
    value: Expression

    def to_tree_str(self, indent: int = 0) -> str:
        prefix = "  " * indent
        lines = [f"{prefix}Assignment({self.name.lexeme})"]
        lines.append(self.value.to_tree_str(indent + 1))
        return "\n".join(lines)


@dataclass(frozen=True)
class PrintStatement(Statement):
    expressions: list[Expression]

    def to_tree_str(self, indent: int = 0) -> str:
        prefix = "  " * indent
        lines = [f"{prefix}PrintStatement"]
        for expr in self.expressions:
            lines.append(expr.to_tree_str(indent + 1))
        return "\n".join(lines)


@dataclass(frozen=True)
class IfStatement(Statement):
    condition: Expression
    then_branch: list[Statement]
    else_branch: list[Statement] | None

    def to_tree_str(self, indent: int = 0) -> str:
        prefix = "  " * indent
        lines = [f"{prefix}IfStatement"]
        lines.append(f"{prefix}  Condition:")
        lines.append(self.condition.to_tree_str(indent + 2))
        lines.append(f"{prefix}  Then:")
        for stmt in self.then_branch:
            lines.append(stmt.to_tree_str(indent + 2))
        if self.else_branch is not None:
            lines.append(f"{prefix}  Else:")
            for stmt in self.else_branch:
                lines.append(stmt.to_tree_str(indent + 2))
        return "\n".join(lines)


@dataclass(frozen=True)
class WhileStatement(Statement):
    condition: Expression
    body: list[Statement]

    def to_tree_str(self, indent: int = 0) -> str:
        prefix = "  " * indent
        lines = [f"{prefix}WhileStatement"]
        lines.append(f"{prefix}  Condition:")
        lines.append(self.condition.to_tree_str(indent + 2))
        lines.append(f"{prefix}  Body:")
        for stmt in self.body:
            lines.append(stmt.to_tree_str(indent + 2))
        return "\n".join(lines)


@dataclass(frozen=True)
class BlockStatement(Statement):
    statements: list[Statement]

    def to_tree_str(self, indent: int = 0) -> str:
        prefix = "  " * indent
        lines = [f"{prefix}BlockStatement"]
        for stmt in self.statements:
            lines.append(stmt.to_tree_str(indent + 1))
        return "\n".join(lines)
