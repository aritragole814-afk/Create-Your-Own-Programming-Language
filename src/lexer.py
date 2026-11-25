"""Convert NovaLang source text into a sequence of tokens."""

from src.tokens import Token, TokenType


class NovaLexError(Exception):
    """Raised when source text contains an invalid character or literal."""

    def __init__(self, message: str, line: int, column: int) -> None:
        super().__init__(f"Lexical error at line {line}, column {column}: {message}")
        self.line = line
        self.column = column


class Lexer:
    KEYWORDS = {
        "let": TokenType.LET,
        "print": TokenType.PRINT,
        "if": TokenType.IF,
        "else": TokenType.ELSE,
        "while": TokenType.WHILE,
        "true": TokenType.TRUE,
        "false": TokenType.FALSE,
        "and": TokenType.AND,
        "or": TokenType.OR,
        "not": TokenType.NOT,
    }

    def __init__(self, source: str) -> None:
        self.source = source
        self.tokens: list[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        self.start_line = 1
        self.start_column = 1

    def tokenize(self) -> list[Token]:
        """Return all tokens, including a final EOF token."""
        while not self._is_at_end():
            self.start = self.current
            self.start_line = self.line
            self.start_column = self.column
            self._scan_token()

        self.tokens.append(
            Token(TokenType.EOF, "", None, self.line, self.column)
        )
        return self.tokens

    def _scan_token(self) -> None:
        character = self._advance()

        single_character_tokens = {
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.STAR,
            "%": TokenType.PERCENT,
            "(": TokenType.LEFT_PAREN,
            ")": TokenType.RIGHT_PAREN,
            "{": TokenType.LEFT_BRACE,
            "}": TokenType.RIGHT_BRACE,
            ";": TokenType.SEMICOLON,
            ",": TokenType.COMMA,
        }

        if character in single_character_tokens:
            self._add_token(single_character_tokens[character])
        elif character == "/":
            if self._match("/"):
                # Single-line comment
                while self._peek() not in ("\n", "\0"):
                    self._advance()
            elif self._match("*"):
                # Multi-line comment
                self._block_comment()
            else:
                self._add_token(TokenType.SLASH)
        elif character == "=":
            self._add_token(
                TokenType.EQUAL_EQUAL if self._match("=") else TokenType.EQUAL
            )
        elif character == "!":
            self._add_token(
                TokenType.BANG_EQUAL if self._match("=") else TokenType.BANG
            )
        elif character == ">":
            self._add_token(
                TokenType.GREATER_EQUAL if self._match("=") else TokenType.GREATER
            )
        elif character == "<":
            self._add_token(
                TokenType.LESS_EQUAL if self._match("=") else TokenType.LESS
            )
        elif character == "&":
            if self._match("&"):
                self._add_token(TokenType.AMPERSAND_AMPERSAND)
            else:
                self._error("Expected '&' after '&'.")
        elif character == "|":
            if self._match("|"):
                self._add_token(TokenType.PIPE_PIPE)
            else:
                self._error("Expected '|' after '|'.")
        elif character == '"':
            self._string()
        elif character.isspace():
            return
        elif character.isdigit():
            self._number()
        elif character.isalpha() or character == "_":
            self._identifier()
        else:
            self._error(f"Invalid character {character!r}.")

    def _block_comment(self) -> None:
        start_line = self.start_line
        start_column = self.start_column
        while not self._is_at_end():
            if self._peek() == "*" and self._peek_next() == "/":
                self._advance()  # consume '*'
                self._advance()  # consume '/'
                return
            self._advance()
        raise NovaLexError("Unterminated multi-line comment.", start_line, start_column)

    def _string(self) -> None:
        characters: list[str] = []
        while not self._is_at_end() and self._peek() != '"':
            character = self._advance()
            if character == "\n":
                self._error("A string cannot continue onto another line.")
            if character == "\\":
                if self._is_at_end():
                    self._error("Unterminated escape sequence in string.")
                escaped = self._advance()
                escape_sequences = {
                    '"': '"',
                    "\\": "\\",
                    "n": "\n",
                    "t": "\t",
                    "r": "\r",
                }
                if escaped not in escape_sequences:
                    self._error(f"Unknown string escape '\\{escaped}'.")
                characters.append(escape_sequences[escaped])
            else:
                characters.append(character)

        if self._is_at_end():
            self._error("Unterminated string.")

        self._advance()  # Closing quote
        self._add_token(TokenType.STRING, "".join(characters))

    def _number(self) -> None:
        while self._peek().isdigit():
            self._advance()

        is_float = self._peek() == "." and self._peek_next().isdigit()
        if is_float:
            self._advance()
            while self._peek().isdigit():
                self._advance()

        text = self.source[self.start : self.current]
        literal: int | float = float(text) if is_float else int(text)
        self._add_token(TokenType.FLOAT if is_float else TokenType.INTEGER, literal)

    def _identifier(self) -> None:
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()

        text = self.source[self.start : self.current]
        token_type = self.KEYWORDS.get(text, TokenType.IDENTIFIER)
        literal = text == "true" if token_type == TokenType.TRUE else None
        if token_type == TokenType.FALSE:
            literal = False
        self._add_token(token_type, literal)

    def _add_token(
        self, token_type: TokenType, literal: object | None = None
    ) -> None:
        lexeme = self.source[self.start : self.current]
        self.tokens.append(
            Token(token_type, lexeme, literal, self.start_line, self.start_column)
        )

    def _advance(self) -> str:
        character = self.source[self.current]
        self.current += 1
        if character == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return character

    def _match(self, expected: str) -> bool:
        if self._is_at_end() or self.source[self.current] != expected:
            return False
        self._advance()
        return True

    def _peek(self) -> str:
        if self._is_at_end():
            return "\0"
        return self.source[self.current]

    def _peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def _error(self, message: str) -> None:
        raise NovaLexError(message, self.start_line, self.start_column)
