"""Comprehensive automated tests for NovaLang compiler phases and runtime."""

import contextlib
import io
import sys
from pathlib import Path
import unittest

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.interpreter import Interpreter, NovaRuntimeError
from src.lexer import Lexer, NovaLexError
from src.main import compile_and_run
from src.parser import NovaSyntaxError, Parser
from src.tokens import TokenType


class LexerTests(unittest.TestCase):
    def test_token_types_and_source_locations(self) -> None:
        source = "let count = 12;\nprint(count);"
        tokens = Lexer(source).tokenize()

        expected_types = [
            TokenType.LET,
            TokenType.IDENTIFIER,
            TokenType.EQUAL,
            TokenType.INTEGER,
            TokenType.SEMICOLON,
            TokenType.PRINT,
            TokenType.LEFT_PAREN,
            TokenType.IDENTIFIER,
            TokenType.RIGHT_PAREN,
            TokenType.SEMICOLON,
            TokenType.EOF,
        ]
        self.assertEqual([t.type for t in tokens], expected_types)
        # Line 2 column 1 is print
        self.assertEqual((tokens[5].line, tokens[5].column), (2, 1))

    def test_single_and_multi_line_comments(self) -> None:
        source = """
        // This is a single line comment
        let x = 10;
        /* This is a
           multi-line comment */
        let y = 20;
        """
        tokens = Lexer(source).tokenize()
        meaningful = [t for t in tokens if t.type != TokenType.EOF]
        self.assertEqual(meaningful[0].type, TokenType.LET)
        self.assertEqual(meaningful[1].lexeme, "x")
        self.assertEqual(meaningful[5].type, TokenType.LET)
        self.assertEqual(meaningful[6].lexeme, "y")

    def test_logical_operators_tokens(self) -> None:
        source = "and or not && || !"
        tokens = Lexer(source).tokenize()
        types = [t.type for t in tokens if t.type != TokenType.EOF]
        self.assertEqual(
            types,
            [
                TokenType.AND,
                TokenType.OR,
                TokenType.NOT,
                TokenType.AMPERSAND_AMPERSAND,
                TokenType.PIPE_PIPE,
                TokenType.BANG,
            ],
        )

    def test_modulo_and_arithmetic_tokens(self) -> None:
        source = "10 % 3 + 4 * 2 / 1 - 5;"
        tokens = Lexer(source).tokenize()
        types = [t.type for t in tokens if t.type != TokenType.EOF]
        self.assertIn(TokenType.PERCENT, types)

    def test_invalid_character_raises_lex_error(self) -> None:
        with self.assertRaises(NovaLexError):
            Lexer("@").tokenize()

    def test_unterminated_string_raises_lex_error(self) -> None:
        with self.assertRaises(NovaLexError):
            Lexer('"unterminated string').tokenize()


class ParserTests(unittest.TestCase):
    def test_reports_missing_semicolon(self) -> None:
        with self.assertRaises(NovaSyntaxError):
            compile_and_run('print("missing semicolon")')

    def test_reports_unexpected_token(self) -> None:
        with self.assertRaises(NovaSyntaxError):
            compile_and_run("42;")

    def test_parses_variable_reassignment(self) -> None:
        tokens = Lexer("x = 50;").tokenize()
        parser = Parser(tokens)
        statements = parser.parse()
        self.assertEqual(len(statements), 1)

    def test_parses_while_loop(self) -> None:
        tokens = Lexer("while (x < 10) { x = x + 1; }").tokenize()
        parser = Parser(tokens)
        statements = parser.parse()
        self.assertEqual(len(statements), 1)


class InterpreterTests(unittest.TestCase):
    def run_source(self, source: str) -> tuple[str, Interpreter]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            interpreter = compile_and_run(source)
        return output.getvalue(), interpreter

    def test_variable_declaration_and_printing(self) -> None:
        source = """
        let name = "Nova";
        let count = 42;
        let pi = 3.14;
        let flag = true;
        print(name, count, pi, flag);
        """
        out, _ = self.run_source(source)
        self.assertEqual(out.strip(), "Nova 42 3.14 true")

    def test_variable_reassignment(self) -> None:
        source = """
        let x = 10;
        x = x + 5;
        print(x);
        """
        out, _ = self.run_source(source)
        self.assertEqual(out.strip(), "15")

    def test_arithmetic_precedence(self) -> None:
        source = """
        print(2 + 3 * 4);
        print((2 + 3) * 4);
        print(17 % 5);
        """
        out, _ = self.run_source(source)
        self.assertEqual(out.strip().splitlines(), ["14", "20", "2"])

    def test_string_concatenation(self) -> None:
        source = """
        let first = "Hello, ";
        let second = "World!";
        print(first + second);
        """
        out, _ = self.run_source(source)
        self.assertEqual(out.strip(), "Hello, World!")

    def test_conditionals_if_else_if_else(self) -> None:
        source = """
        let score = 85;
        if (score >= 90) {
            print("Grade A");
        } else if (score >= 80) {
            print("Grade B");
        } else {
            print("Grade C");
        }
        """
        out, _ = self.run_source(source)
        self.assertEqual(out.strip(), "Grade B")

    def test_logical_operators_and_short_circuit(self) -> None:
        source = """
        print(true and false);
        print(true or false);
        print(not false);
        print(true && true);
        print(false || true);
        """
        out, _ = self.run_source(source)
        self.assertEqual(out.strip().splitlines(), ["false", "true", "true", "true", "true"])

    def test_while_loop_execution(self) -> None:
        source = """
        let sum = 0;
        let i = 1;
        while (i <= 5) {
            sum = sum + i;
            i = i + 1;
        }
        print(sum);
        """
        out, _ = self.run_source(source)
        self.assertEqual(out.strip(), "15")

    def test_factorial_algorithm(self) -> None:
        source = """
        let n = 5;
        let fact = 1;
        while (n > 1) {
            fact = fact * n;
            n = n - 1;
        }
        print(fact);
        """
        out, _ = self.run_source(source)
        self.assertEqual(out.strip(), "120")

    def test_division_by_zero_error(self) -> None:
        with self.assertRaisesRegex(NovaRuntimeError, "Division by zero"):
            self.run_source("print(10 / 0);")

    def test_modulo_by_zero_error(self) -> None:
        with self.assertRaisesRegex(NovaRuntimeError, "Modulo by zero"):
            self.run_source("print(10 % 0);")

    def test_undefined_variable_error(self) -> None:
        with self.assertRaisesRegex(NovaRuntimeError, "Undefined variable"):
            self.run_source("print(non_existent);")

    def test_assignment_to_undefined_variable_error(self) -> None:
        with self.assertRaisesRegex(NovaRuntimeError, "Cannot assign to undefined variable"):
            self.run_source("undeclared = 50;")


if __name__ == "__main__":
    unittest.main()
