"""Token definitions shared by the NovaLang lexer and parser."""

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    # Literals and names
    IDENTIFIER = auto()
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()

    # Keywords and boolean literals
    LET = auto()
    PRINT = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    TRUE = auto()
    FALSE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()

    # Arithmetic operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()

    # Relational and equality operators
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    BANG_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()

    # Logical operators (symbolic forms)
    BANG = auto()
    AMPERSAND_AMPERSAND = auto()
    PIPE_PIPE = auto()

    # Punctuation
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    SEMICOLON = auto()

    EOF = auto()


@dataclass(frozen=True)
class Token:
    """A source token, including its original spelling and source location."""

    type: TokenType
    lexeme: str
    literal: object | None
    line: int
    column: int

    def __repr__(self) -> str:
        if self.literal is not None:
            return f"Token({self.type.name}, {self.lexeme!r}, {self.literal!r}, line={self.line}, col={self.column})"
        return f"Token({self.type.name}, {self.lexeme!r}, line={self.line}, col={self.column})"
