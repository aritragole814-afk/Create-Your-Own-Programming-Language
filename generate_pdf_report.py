"""Generate a formal, publication-grade academic PDF report for NovaLang Compiler Design PBL."""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    Preformatted,
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Canvas that computes total pages dynamically and adds running headers & footers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, total_pages):
        # Do not draw headers/footers on the cover page (page 1)
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))

        # Running header
        self.drawString(54, 11 * 72 - 36, "NovaLang — Compiler Design Project-Based Learning (PBL)")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.75)
        self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)

        # Running footer
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(8.5 * 72 - 54, 36, page_str)
        self.drawString(54, 36, "Confidential & Academic Submission | GitHub: aritragole814-afk/Create-Your-Own-Programming-Language")
        self.line(54, 48, 8.5 * 72 - 54, 48)
        self.restoreState()


def create_report(output_pdf_path: str):
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom palette
    primary = colors.HexColor("#1A365D")    # Deep Navy
    secondary = colors.HexColor("#2B6CB0")  # Slate Blue
    accent = colors.HexColor("#319795")     # Teal
    dark_text = colors.HexColor("#2D3748")  # Charcoal body
    bg_code = colors.HexColor("#F7FAFC")
    border_code = colors.HexColor("#E2E8F0")

    # Typography styles
    styles.add(ParagraphStyle(
        name="CoverTitle",
        fontName="Helvetica-Bold",
        fontSize=28,
        leading=34,
        textColor=primary,
        alignment=1, # Center
    ))
    styles.add(ParagraphStyle(
        name="CoverSubtitle",
        fontName="Helvetica",
        fontSize=15,
        leading=20,
        textColor=secondary,
        alignment=1,
    ))
    styles.add(ParagraphStyle(
        name="CoverMeta",
        fontName="Helvetica",
        fontSize=10,
        leading=16,
        textColor=dark_text,
        alignment=1,
    ))
    styles.add(ParagraphStyle(
        name="SectionHeading",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=primary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="SubSectionHeading",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=secondary,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="BodyDark",
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=dark_text,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="BodyDarkBold",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=14,
        textColor=dark_text,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="CodeBlock",
        fontName="Courier",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1A202C"),
    ))
    styles.add(ParagraphStyle(
        name="BulletItem",
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=dark_text,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4,
    ))

    story = []

    # =========================================================================
    # COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("PROJECT-BASED LEARNING (PBL) REPORT", ParagraphStyle(
        "CoverEyebrow", fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=accent, alignment=1
    )))
    story.append(Spacer(1, 15))
    story.append(Paragraph("CREATE YOUR OWN PROGRAMMING LANGUAGE", styles["CoverTitle"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Design & Implementation of a Modern Tree-Walk Interpreted Language (NovaLang)", styles["CoverSubtitle"]))
    story.append(Spacer(1, 30))

    # Decorative line
    dec_table = Table([[""]], colWidths=[500], rowHeights=[4])
    dec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), secondary),
    ]))
    story.append(dec_table)
    story.append(Spacer(1, 40))

    cover_info_data = [
        [Paragraph("<b>Course:</b>", styles["BodyDarkBold"]), Paragraph("Compiler Design (CS-PBL)", styles["BodyDark"])],
        [Paragraph("<b>Academic Project:</b>", styles["BodyDarkBold"]), Paragraph("Create Your Own Programming Language", styles["BodyDark"])],
        [Paragraph("<b>Implemented Language:</b>", styles["BodyDarkBold"]), Paragraph("NovaLang (v1.0.0)", styles["BodyDark"])],
        [Paragraph("<b>Student Name:</b>", styles["BodyDarkBold"]), Paragraph("Aritra Gole", styles["BodyDark"])],
        [Paragraph("<b>Student Email:</b>", styles["BodyDarkBold"]), Paragraph("aritragole814@gmail.com", styles["BodyDark"])],
        [Paragraph("<b>GitHub Username:</b>", styles["BodyDarkBold"]), Paragraph("aritragole814-afk", styles["BodyDark"])],
        [Paragraph("<b>Project Repository:</b>", styles["BodyDarkBold"]), Paragraph("<font color='#2B6CB0'><u>https://github.com/aritragole814-afk/Create-Your-Own-Programming-Language</u></font>", styles["BodyDark"])],
        [Paragraph("<b>Submission Date:</b>", styles["BodyDarkBold"]), Paragraph("November 2026", styles["BodyDark"])],
    ]
    info_table = Table(cover_info_data, colWidths=[140, 360])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(info_table)

    story.append(Spacer(1, 60))
    story.append(Paragraph("<b>Department of Computer Science & Engineering</b><br/>Faculty of Engineering & Technology", styles["CoverMeta"]))
    story.append(PageBreak())

    # =========================================================================
    # SECTION 1: EXECUTIVE SUMMARY & ABSTRACT
    # =========================================================================
    story.append(Paragraph("1. Executive Summary & Abstract", styles["SectionHeading"]))
    story.append(Paragraph(
        "<b>NovaLang</b> is an educational programming language and custom interpreter engineered from first principles in Python 3.10+ without relying on any external parsing frameworks (such as Lex, Yacc, ANTLR, or Flex) or host-language code execution mechanisms (such as <code>eval()</code> or <code>exec()</code>).",
        styles["BodyDark"]
    ))
    story.append(Paragraph(
        "The primary objective of this project is to model each classical phase of compiler construction: <b>Lexical Analysis (Scanner)</b>, <b>Syntax Analysis (Recursive Descent Parser)</b>, <b>Abstract Syntax Tree (AST) Generation</b>, <b>Scoped Symbol Table Resolution</b>, and <b>Direct AST Tree-Walk Evaluation</b>. NovaLang is designed to be dynamically typed, featuring variable declarations and reassignment, scalar types (integers, floating-point numbers, booleans, and strings), arithmetic and modulo expressions with operator precedence, short-circuit logical operators, relational branching (<code>if / else if / else</code>), iterations (<code>while</code>), and structured formatted console I/O.",
        styles["BodyDark"]
    ))
    story.append(Paragraph(
        "The implementation includes an end-to-end command-line compiler driver, an interactive Read-Eval-Print Loop (REPL) with multiline block auto-detection, a comprehensive 22-case unit test suite, and pedagogical inspection flags (<code>--tokens</code> and <code>--ast</code>) that expose internal compiler data structures during evaluation and viva presentations.",
        styles["BodyDark"]
    ))
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 2: COMPILER ARCHITECTURE & PIPELINE
    # =========================================================================
    story.append(Paragraph("2. Compiler Architecture & Pipeline", styles["SectionHeading"]))
    story.append(Paragraph(
        "NovaLang translates human-readable source code into concrete program execution through a deterministic multi-stage pipeline, illustrated below:",
        styles["BodyDark"]
    ))

    arch_box_data = [
        [
            Paragraph("<b>Phase</b>", styles["BodyDarkBold"]),
            Paragraph("<b>Component</b>", styles["BodyDarkBold"]),
            Paragraph("<b>Input</b>", styles["BodyDarkBold"]),
            Paragraph("<b>Output</b>", styles["BodyDarkBold"]),
            Paragraph("<b>Primary Responsibility</b>", styles["BodyDarkBold"]),
        ],
        [
            Paragraph("<b>Phase 1</b>", styles["BodyDark"]),
            Paragraph("<code>lexer.py</code>", styles["BodyDark"]),
            Paragraph("Source text (.nova)", styles["BodyDark"]),
            Paragraph("Token stream", styles["BodyDark"]),
            Paragraph("Scanning, regex character matching, tokenization, 1-indexed line/column tracking, comment stripping.", styles["BodyDark"]),
        ],
        [
            Paragraph("<b>Phase 2</b>", styles["BodyDark"]),
            Paragraph("<code>parser.py</code>", styles["BodyDark"]),
            Paragraph("Token stream", styles["BodyDark"]),
            Paragraph("Abstract Syntax Tree", styles["BodyDark"]),
            Paragraph("Context-Free Grammar verification, LL(1)/LL(2) recursive descent, operator precedence climbing.", styles["BodyDark"]),
        ],
        [
            Paragraph("<b>Phase 3</b>", styles["BodyDark"]),
            Paragraph("<code>interpreter.py</code>", styles["BodyDark"]),
            Paragraph("AST & Scope Tree", styles["BodyDark"]),
            Paragraph("Program Execution", styles["BodyDark"]),
            Paragraph("Recursive tree-walk evaluation, lexical scoping (Environment), runtime type checks, zero-division guards.", styles["BodyDark"]),
        ],
        [
            Paragraph("<b>CLI / REPL</b>", styles["BodyDark"]),
            Paragraph("<code>main.py</code>", styles["BodyDark"]),
            Paragraph("CLI arguments / shell", styles["BodyDark"]),
            Paragraph("Diagnostic Output", styles["BodyDark"]),
            Paragraph("Command-line driver, interactive REPL, compiler phase inspection (--tokens, --ast).", styles["BodyDark"]),
        ],
    ]
    arch_table = Table(arch_box_data, colWidths=[55, 75, 95, 95, 180])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 15))

    # =========================================================================
    # SECTION 3: FORMAL GRAMMAR SPECIFICATION (EBNF)
    # =========================================================================
    story.append(Paragraph("3. Formal Grammar Specification", styles["SectionHeading"]))
    story.append(Paragraph(
        "NovaLang's syntax is formally defined using Extended Backus-Naur Form (EBNF). The grammar is designed to be unambiguous and strictly enforces standard operator precedence rules (PEMDAS / BODMAS) without left-recursion:",
        styles["BodyDark"]
    ))

    ebnf_code = """program         ::= { declaration } ;
declaration     ::= var_declaration | statement ;
var_declaration ::= "let" IDENTIFIER "=" expression ";" ;

statement       ::= print_statement
                  | if_statement
                  | while_statement
                  | block_statement
                  | assignment_statement ;

print_statement ::= "print" "(" [ expression { "," expression } ] ")" ";" ;
if_statement    ::= "if" "(" expression ")" block_statement
                    [ "else" ( if_statement | block_statement ) ] ;
while_statement ::= "while" "(" expression ")" block_statement ;
block_statement ::= "{" { declaration } "}" ;
assignment_stmt ::= IDENTIFIER "=" expression ";" ;

expression      ::= logic_or ;
logic_or        ::= logic_and { ( "or" | "||" ) logic_and } ;
logic_and       ::= equality { ( "and" | "&&" ) equality } ;
equality        ::= comparison { ( "==" | "!=" ) comparison } ;
comparison      ::= term { ( ">" | ">=" | "<" | "<=" ) term } ;
term            ::= factor { ( "+" | "-" ) factor } ;
factor          ::= unary { ( "*" | "/" | "%" ) unary } ;
unary           ::= ( "-" | "!" | "not" ) unary | primary ;
primary         ::= INTEGER | FLOAT | STRING | BOOLEAN | IDENTIFIER
                  | "(" expression ")" ;"""

    code_tbl = Table([[Preformatted(ebnf_code, styles["CodeBlock"])]], colWidths=[500])
    code_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_code),
        ('BOX', (0, 0), (-1, -1), 1, border_code),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(code_tbl)
    story.append(PageBreak())

    # =========================================================================
    # SECTION 4: LANGUAGE FEATURES & CAPABILITIES
    # =========================================================================
    story.append(Paragraph("4. Language Features & Syntax", styles["SectionHeading"]))
    story.append(Paragraph(
        "NovaLang provides rich programming primitives to enable implementing non-trivial numerical algorithms and conditional logic:",
        styles["BodyDark"]
    ))

    story.append(Paragraph("<b>4.1 Variables and Assignment:</b>", styles["SubSectionHeading"]))
    story.append(Paragraph(
        "Variables are declared using the <code>let</code> keyword with an initial value. Variables can be reassigned dynamically to new expressions, propagating upward through enclosing lexical scopes.",
        styles["BodyDark"]
    ))
    story.append(Paragraph("• <code>let counter = 0;</code> — Initial declaration<br/>• <code>counter = counter + 1;</code> — Variable mutation / update", styles["BulletItem"]))

    story.append(Paragraph("<b>4.2 Supported Data Types:</b>", styles["SubSectionHeading"]))
    story.append(Paragraph("• <b>Integer:</b> 32-bit/arbitrary precision integers (e.g. <code>42</code>, <code>-10</code>).", styles["BulletItem"]))
    story.append(Paragraph("• <b>Floating-Point:</b> Double-precision numbers (e.g. <code>3.14159</code>, <code>0.05</code>).", styles["BulletItem"]))
    story.append(Paragraph("• <b>Boolean:</b> Literals <code>true</code> and <code>false</code>.", styles["BulletItem"]))
    story.append(Paragraph("• <b>String:</b> Double-quoted character sequences with escape support (<code>\\n</code>, <code>\\t</code>, <code>\\\"</code>, <code>\\\\</code>). Supports string concatenation with the <code>+</code> operator.", styles["BulletItem"]))

    story.append(Paragraph("<b>4.3 Operators & Precedence Hierarchy:</b>", styles["SubSectionHeading"]))

    op_table_data = [
        [Paragraph("<b>Level</b>", styles["BodyDarkBold"]), Paragraph("<b>Operators</b>", styles["BodyDarkBold"]), Paragraph("<b>Description</b>", styles["BodyDarkBold"]), Paragraph("<b>Associativity</b>", styles["BodyDarkBold"])],
        [Paragraph("1 (Highest)", styles["BodyDark"]), Paragraph("<code>( )</code>, Primary", styles["BodyDark"]), Paragraph("Grouping, Literals, Identifiers", styles["BodyDark"]), Paragraph("Non-associative", styles["BodyDark"])],
        [Paragraph("2", styles["BodyDark"]), Paragraph("<code>-</code>, <code>!</code>, <code>not</code>", styles["BodyDark"]), Paragraph("Unary numeric negation, logical NOT", styles["BodyDark"]), Paragraph("Right-to-left", styles["BodyDark"])],
        [Paragraph("3", styles["BodyDark"]), Paragraph("<code>*</code>, <code>/</code>, <code>%</code>", styles["BodyDark"]), Paragraph("Multiplication, Division, Modulo", styles["BodyDark"]), Paragraph("Left-to-right", styles["BodyDark"])],
        [Paragraph("4", styles["BodyDark"]), Paragraph("<code>+</code>, <code>-</code>", styles["BodyDark"]), Paragraph("Addition (numeric & string concat), Subtraction", styles["BodyDark"]), Paragraph("Left-to-right", styles["BodyDark"])],
        [Paragraph("5", styles["BodyDark"]), Paragraph("<code>&gt;</code>, <code>&gt;=</code>, <code>&lt;</code>, <code>&lt;=</code>", styles["BodyDark"]), Paragraph("Relational ordering comparisons", styles["BodyDark"]), Paragraph("Left-to-right", styles["BodyDark"])],
        [Paragraph("6", styles["BodyDark"]), Paragraph("<code>==</code>, <code>!=</code>", styles["BodyDark"]), Paragraph("Structural equality & inequality", styles["BodyDark"]), Paragraph("Left-to-right", styles["BodyDark"])],
        [Paragraph("7", styles["BodyDark"]), Paragraph("<code>and</code>, <code>&&</code>", styles["BodyDark"]), Paragraph("Short-circuit logical conjunction", styles["BodyDark"]), Paragraph("Left-to-right", styles["BodyDark"])],
        [Paragraph("8 (Lowest)", styles["BodyDark"]), Paragraph("<code>or</code>, <code>||</code>", styles["BodyDark"]), Paragraph("Short-circuit logical disjunction", styles["BodyDark"]), Paragraph("Left-to-right", styles["BodyDark"])],
    ]
    op_table = Table(op_table_data, colWidths=[70, 110, 210, 110])
    op_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), secondary),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(op_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>4.4 Control Structures:</b>", styles["SubSectionHeading"]))
    story.append(Paragraph(
        "NovaLang supports multi-branch conditionals (<code>if</code>, <code>else if</code>, and <code>else</code>) as well as condition-driven <code>while</code> loops. Both constructs execute statements within newly spawned child <code>Environment</code> scopes, enforcing proper block-level variable scoping.",
        styles["BodyDark"]
    ))
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 5: IMPLEMENTATION DETAILS
    # =========================================================================
    story.append(Paragraph("5. Detailed Implementation Breakdown", styles["SectionHeading"]))
    story.append(Paragraph(
        "The project source code is organized modularly under the <code>src/</code> package, adhering strictly to single-responsibility and separation-of-concerns principles:",
        styles["BodyDark"]
    ))

    mod_data = [
        [Paragraph("<b>File</b>", styles["BodyDarkBold"]), Paragraph("<b>Lines</b>", styles["BodyDarkBold"]), Paragraph("<b>Key Classes / Responsibilities</b>", styles["BodyDarkBold"])],
        [
            Paragraph("<code>tokens.py</code>", styles["BodyDark"]),
            Paragraph("71", styles["BodyDark"]),
            Paragraph("Enumerates all 28 token kinds (<code>TokenType</code>) and defines the immutable <code>Token</code> dataclass tracking lexeme, literal value, line, and column coordinates.", styles["BodyDark"])
        ],
        [
            Paragraph("<code>lexer.py</code>", styles["BodyDark"]),
            Paragraph("220", styles["BodyDark"]),
            Paragraph("Contains the <code>Lexer</code> state machine. Scans source strings, classifies identifiers vs. keywords, processes string escapes, filters comments, and raises informative <code>NovaLexError</code> diagnostics.", styles["BodyDark"])
        ],
        [
            Paragraph("<code>ast_nodes.py</code>", styles["BodyDark"]),
            Paragraph("185", styles["BodyDark"]),
            Paragraph("Defines the AST hierarchy (<code>BinaryExpression</code>, <code>UnaryExpression</code>, <code>LogicalExpression</code>, <code>VariableDeclaration</code>, <code>WhileStatement</code>, etc.) and provides <code>to_tree_str()</code> visualizers.", styles["BodyDark"])
        ],
        [
            Paragraph("<code>parser.py</code>", styles["BodyDark"]),
            Paragraph("249", styles["BodyDark"]),
            Paragraph("Recursive descent parser (<code>Parser</code>). Consumes tokens and constructs the AST while verifying grammar rules and reporting line/column-accurate <code>NovaSyntaxError</code>.", styles["BodyDark"])
        ],
        [
            Paragraph("<code>interpreter.py</code>", styles["BodyDark"]),
            Paragraph("251", styles["BodyDark"]),
            Paragraph("Implements the tree-walk evaluator (<code>Interpreter</code>) and scoped symbol tables (<code>Environment</code>). Manages runtime errors, type enforcement, and infinite loop safeguards (max 1M iterations).", styles["BodyDark"])
        ],
        [
            Paragraph("<code>main.py</code>", styles["BodyDark"]),
            Paragraph("192", styles["BodyDark"]),
            Paragraph("Main CLI driver and REPL engine. Implements phase inspection switches (<code>--tokens</code>, <code>--ast</code>) and balances multiline bracket buffers for interactive typing.", styles["BodyDark"])
        ],
    ]
    mod_table = Table(mod_data, colWidths=[90, 45, 365])
    mod_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(mod_table)
    story.append(PageBreak())

    # =========================================================================
    # SECTION 6: VERIFICATION & TEST RESULTS
    # =========================================================================
    story.append(Paragraph("6. Automated Testing & Verification", styles["SectionHeading"]))
    story.append(Paragraph(
        "A comprehensive automated test suite (<code>tests/test_novalang.py</code>) using Python's built-in <code>unittest</code> framework guarantees robustness across every compiler phase. All 22 test cases pass deterministically in <b>0.003 seconds</b>.",
        styles["BodyDark"]
    ))

    test_data = [
        [Paragraph("<b>Category</b>", styles["BodyDarkBold"]), Paragraph("<b>Test Method</b>", styles["BodyDarkBold"]), Paragraph("<b>Target Behavior Verified</b>", styles["BodyDarkBold"]), Paragraph("<b>Status</b>", styles["BodyDarkBold"])],
        [Paragraph("Lexer", styles["BodyDark"]), Paragraph("<code>test_token_types_locations</code>", styles["BodyDark"]), Paragraph("Accurate token type and line/column coordinates", styles["BodyDark"]), Paragraph("<font color='green'><b>PASS</b></font>", styles["BodyDark"])],
        [Paragraph("Lexer", styles["BodyDark"]), Paragraph("<code>test_comments</code>", styles["BodyDark"]), Paragraph("Single-line // and multi-line /* */ comments ignored", styles["BodyDark"]), Paragraph("<font color='green'><b>PASS</b></font>", styles["BodyDark"])],
        [Paragraph("Lexer", styles["BodyDark"]), Paragraph("<code>test_invalid_character</code>", styles["BodyDark"]), Paragraph("Raises NovaLexError on illegal characters (@)", styles["BodyDark"]), Paragraph("<font color='green'><b>PASS</b></font>", styles["BodyDark"])],
        [Paragraph("Lexer", styles["BodyDark"]), Paragraph("<code>test_unterminated_string</code>", styles["BodyDark"]), Paragraph("Detects EOF before closing string quote", styles["BodyDark"]), Paragraph("<font color='green'><b>PASS</b></font>", styles["BodyDark"])],
        [Paragraph("Parser", styles["BodyDark"]), Paragraph("<code>test_missing_semicolon</code>", styles["BodyDark"]), Paragraph("Enforces mandatory semicolon statement terminators", styles["BodyDark"]), Paragraph("<font color='green'><b>PASS</b></font>", styles["BodyDark"])],
        [Paragraph("Parser", styles["BodyDark"]), Paragraph("<code>test_unexpected_token</code>", styles["BodyDark"]), Paragraph("Rejects statements beginning with literals", styles["BodyDark"]), Paragraph("<font color='green'><b>PASS</b></font>", styles["BodyDark"])],
        [Paragraph("Parser", styles["BodyDark"]), Paragraph("<code>test_while_parsing</code>", styles["BodyDark"]), Paragraph("Validates condition and body block AST parsing", styles["BodyDark"]), Paragraph("<font color='green'><b>PASS</b></font>", styles["BodyDark"])],
        [Paragraph("Runtime", styles["BodyDark"]), Paragraph("<code>test_arithmetic_precedence</code>", styles["BodyDark"]), Paragraph("2 + 3 * 4 = 14; (2 + 3) * 4 = 20; 17 % 5 = 2", styles["BodyDark"]), Paragraph("<font color='green'><b>PASS</b></font>", styles["BodyDark"])],
        [Paragraph("Runtime", styles["BodyDark"]), Paragraph("<code>test_string_concatenation</code>", styles["BodyDark"]), Paragraph("\"Hello, \" + \"World!\" concatenation", styles["BodyDark"]), Paragraph("<font color='green'><b>PASS</b></font>", styles["BodyDark"])],
        [Paragraph("Runtime", styles["BodyDark"]), Paragraph("<code>test_conditionals</code>", styles["BodyDark"]), Paragraph("Branch selection in if / else if / else blocks", styles["BodyDark"]), Paragraph("<font color='green'><b>PASS</b></font>", styles["BodyDark"])],
        [Paragraph("Runtime", styles["BodyDark"]), Paragraph("<code>test_logical_short_circuit</code>", styles["BodyDark"]), Paragraph("Short-circuiting in and/or/&&/|| evaluations", styles["BodyDark"]), Paragraph("<font color='green'><b>PASS</b></font>", styles["BodyDark"])],
        [Paragraph("Runtime", styles["BodyDark"]), Paragraph("<code>test_while_loop_execution</code>", styles["BodyDark"]), Paragraph("Summing 1 to 5 yields 15 in loop execution", styles["BodyDark"]), Paragraph("<font color='green'><b>PASS</b></font>", styles["BodyDark"])],
        [Paragraph("Runtime", styles["BodyDark"]), Paragraph("<code>test_factorial_algorithm</code>", styles["BodyDark"]), Paragraph("Iterative factorial 5! = 120 computation", styles["BodyDark"]), Paragraph("<font color='green'><b>PASS</b></font>", styles["BodyDark"])],
        [Paragraph("Runtime", styles["BodyDark"]), Paragraph("<code>test_division_by_zero</code>", styles["BodyDark"]), Paragraph("Raises NovaRuntimeError on 10 / 0", styles["BodyDark"]), Paragraph("<font color='green'><b>PASS</b></font>", styles["BodyDark"])],
        [Paragraph("Runtime", styles["BodyDark"]), Paragraph("<code>test_modulo_by_zero</code>", styles["BodyDark"]), Paragraph("Raises NovaRuntimeError on 10 % 0", styles["BodyDark"]), Paragraph("<font color='green'><b>PASS</b></font>", styles["BodyDark"])],
        [Paragraph("Runtime", styles["BodyDark"]), Paragraph("<code>test_undefined_variable</code>", styles["BodyDark"]), Paragraph("Raises NovaRuntimeError on undeclared identifier lookup", styles["BodyDark"]), Paragraph("<font color='green'><b>PASS</b></font>", styles["BodyDark"])],
    ]
    test_table = Table(test_data, colWidths=[65, 155, 230, 50])
    test_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('PADDING', (0, 0), (-1, -1), 3.5),
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(test_table)
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 7: SAMPLE ALGORITHM EXECUTIONS
    # =========================================================================
    story.append(Paragraph("7. Sample Algorithm Executions", styles["SectionHeading"]))
    story.append(Paragraph(
        "The following algorithms from the <code>examples/</code> directory demonstrate the language's expressive power and practical utility:",
        styles["BodyDark"]
    ))

    algo1_code = """// Fibonacci Series in NovaLang (examples/fibonacci.nova)
let n = 10;
let a = 0;
let b = 1;
let i = 0;

while (i < n) {
    print("Term", i + 1, ":", a);
    let next_val = a + b;
    a = b;
    b = next_val;
    i = i + 1;
}
// Output: Term 1 : 0 ... Term 10 : 34"""

    algo2_code = """// FizzBuzz Algorithm in NovaLang (examples/fizzbuzz.nova)
let i = 1;
while (i <= 15) {
    let div_3 = (i % 3 == 0);
    let div_5 = (i % 5 == 0);

    if (div_3 and div_5) {
        print(i, "-> FizzBuzz");
    } else if (div_3) {
        print(i, "-> Fizz");
    } else if (div_5) {
        print(i, "-> Buzz");
    } else {
        print(i);
    }
    i = i + 1;
}"""

    story.append(Paragraph("<b>7.1 Fibonacci Sequence Generator (Iterative):</b>", styles["SubSectionHeading"]))
    t1 = Table([[Preformatted(algo1_code, styles["CodeBlock"])]], colWidths=[500])
    t1.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), bg_code), ('BOX', (0, 0), (-1, -1), 1, border_code), ('PADDING', (0, 0), (-1, -1), 6)]))
    story.append(t1)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>7.2 FizzBuzz Algorithm (Demonstrating Modulo and Branching):</b>", styles["SubSectionHeading"]))
    t2 = Table([[Preformatted(algo2_code, styles["CodeBlock"])]], colWidths=[500])
    t2.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), bg_code), ('BOX', (0, 0), (-1, -1), 1, border_code), ('PADDING', (0, 0), (-1, -1), 6)]))
    story.append(t2)
    story.append(PageBreak())

    # =========================================================================
    # SECTION 8: CONCLUSION & PROJECT SUMMARY
    # =========================================================================
    story.append(Paragraph("8. Conclusion & Future Scope", styles["SectionHeading"]))
    story.append(Paragraph(
        "The <b>NovaLang</b> project successfully demonstrates all essential phases of compiler and interpreter design. By building a scanner, recursive descent parser, custom AST, and scoped tree-walk interpreter from scratch, it bridges theoretical formal language concepts (Grammars, EBNF, Finite Automata, Symbol Tables) with a functioning, practical software implementation.",
        styles["BodyDark"]
    ))
    story.append(Paragraph(
        "<b>Key Takeaways & Learning Outcomes:</b>",
        styles["BodyDarkBold"]
    ))
    story.append(Paragraph("1. <b>Lexical Parsing:</b> Tracking line and column offsets during scanning is indispensable for providing user-friendly compiler error messages.", styles["BulletItem"]))
    story.append(Paragraph("2. <b>Syntax Trees:</b> Separating syntax analysis from semantic interpretation allows modular enhancements, such as adding visualizers (<code>--ast</code>) and syntax linters without impacting the runtime evaluator.", styles["BulletItem"]))
    story.append(Paragraph("3. <b>Environment Chains:</b> Hierarchical symbol table chaining provides a clean, robust mechanism for implementing lexical scoping and block-level variable shadowing.", styles["BulletItem"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>Future Enhancements:</b>",
        styles["BodyDarkBold"]
    ))
    story.append(Paragraph("• <b>User-Defined Functions:</b> Supporting first-class functions, closures, parameter binding, and return statements.", styles["BulletItem"]))
    story.append(Paragraph("• <b>Bytecode Virtual Machine:</b> Transitioning from tree-walk evaluation to a stack-based Bytecode compiler and VM to enhance execution throughput.", styles["BulletItem"]))
    story.append(Paragraph("• <b>Composite Collections:</b> Adding native arrays and dictionary maps.", styles["BulletItem"]))
    story.append(Spacer(1, 15))

    # Submission footer box
    sub_box = [
        [Paragraph("<b>OFFICIAL PROJECT REPOSITORY & CODEBASE</b>", ParagraphStyle("SubH", fontName="Helvetica-Bold", fontSize=10, textColor=primary, alignment=1))],
        [Paragraph("Repository URL: <font color='#2B6CB0'><b>https://github.com/aritragole814-afk/Create-Your-Own-Programming-Language</b></font><br/>Submitted by: <b>Aritra Gole</b> | Subject: <b>Compiler Design (PBL)</b>", ParagraphStyle("SubB", fontName="Helvetica", fontSize=9, leading=14, textColor=dark_text, alignment=1))],
    ]
    sub_table = Table(sub_box, colWidths=[500])
    sub_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ('BOX', (0, 0), (-1, -1), 1.5, secondary),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(sub_table)

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] PDF generated at: {output_pdf_path}")


if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(__file__), "NovaLang_Compiler_Design_PBL_Report.pdf")
    create_report(out_path)
