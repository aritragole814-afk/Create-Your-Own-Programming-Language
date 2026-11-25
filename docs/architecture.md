# NovaLang Architecture and Design

## Compiler Design Pipeline

NovaLang follows a traditional multi-phase interpreter architecture:

```
[Source Text (.nova)]
        │
        ▼ (Character stream)
┌─────────────────┐
│     Lexer       │  Phase 1: Tokenization, keyword matching, line/column tracking
└─────────────────┘
        │
        ▼ (Token sequence)
┌─────────────────┐
│     Parser      │  Phase 2: Recursive Descent Parsing, EBNF grammar, precedence
└─────────────────┘
        │
        ▼ (Abstract Syntax Tree)
┌─────────────────┐
│   Interpreter   │  Phase 3: Tree-walk evaluation with scoped Symbol Tables
└─────────────────┘
        │
        ▼
 [Program Output]
```

---

## 1. Lexical Analysis (`src/lexer.py`)
- Scans source characters sequentially.
- Converts literals, keywords, identifiers, and punctuation into `Token` objects.
- Retains 1-indexed source line and column numbers for precise diagnostic error messages.
- Strips whitespace and comments (`//` single line and `/* ... */` block comments).

## 2. Syntax Analysis (`src/parser.py`)
- Implements an LL(1) / LL(k) Recursive Descent Parser.
- Recognizes declarations, statements, expressions, and blocks.
- Solves operator precedence via hierarchical grammar methods:
  - Logical OR (`or`, `||`)
  - Logical AND (`and`, `&&`)
  - Equality (`==`, `!=`)
  - Comparison (`<`, `<=`, `>`, `>=`)
  - Term (`+`, `-`)
  - Factor (`*`, `/`, `%`)
  - Unary (`!`, `not`, `-`)
  - Primary (Literals, Identifiers, Grouped Expressions)

## 3. Environment & Symbol Table (`src/interpreter.py`)
- Employs a tree of `Environment` instances representing lexical scopes.
- Supports nested block scoping (inner blocks can read and shadow outer variables).
- Assignment traverses the environment hierarchy to mutate the originating variable scope.

## 4. Evaluation Engine (`src/interpreter.py`)
- Directly evaluates AST nodes recursively without emitting host Python source or using `eval()`.
- Catches runtime issues:
  - Undefined variable access.
  - Type errors (e.g. attempting arithmetic on booleans or invalid types).
  - Division by zero and modulo by zero.
  - Loop iteration guard to prevent runaway infinite loops.
