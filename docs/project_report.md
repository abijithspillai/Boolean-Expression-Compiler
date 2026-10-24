# Compiler Design Project Report

## Boolean Expression Compiler: Front-End Architecture, Semantic Validation, and AST Visualization

**Course:** Compiler Design (Academic Mini Project)  
**Project Type:** Mini Compiler / Compiler Front-End  
**Language:** Python & Web Interface  

---

## 1. Abstract
This project presents the design and implementation of a modular, fully functional compiler front-end for a domain-specific Boolean Expression Language. The system encompasses all classic front-end phases: character-level lexical analysis utilizing maximal-munch tokenization, predictive syntax analysis via a non-left-recursive recursive-descent parser, dynamic Abstract Syntax Tree (AST) construction, static semantic type-checking with an interactive symbol table, and safe expression evaluation without runtime `eval()`. The compiler backend is developed in Python 3.12 utilizing the Flask micro-framework and Gunicorn WSGI server, paired with a modern, responsive web workbench in HTML5, CSS3, and JavaScript that visualizes the token stream, AST graph, grammar derivation, and diagnostic errors.

---

## 2. Introduction
In standard software engineering and formal verification systems, Boolean expressions form the cornerstone of control flow predicates, relational database queries, query optimizers, and automated theorem provers. Understanding how high-level logical expressions are ingested, verified, and translated into structured intermediate representations is a core pedagogical objective of compiler theory.

This mini project demonstrates the practical realization of compiler design principles. Rather than resorting to superficial string pattern matching or client-side evaluation, this compiler systematically transitions source characters into tokens, constructs a validated AST conforming to strict precedence rules, applies type invariants via a symbol table, and provides real-time feedback through an interactive developer interface.

---

## 3. Problem Statement
Many introductory compiler projects use superficial shortcuts, such as validating syntax through basic regular expressions, delegating execution directly to JavaScript's `eval()` function, or collapsing parsing and evaluation into a single unstructured pass. Such approaches fail to demonstrate:
1. Decoupling of lexical, syntax, and semantic error reporting.
2. The construction and manipulation of Abstract Syntax Trees.
3. Rigorous type validation and operator precedence management.
4. Robust defensive compilation that prevents crashing upon malformed input.

The goal of this project is to build an extensible, academically rigorous compiler front-end that addresses these deficiencies while remaining intuitive and visually demonstrative for live classroom presentations.

---

## 4. Objectives
1. **Design a Formal Grammar:** Formulate an unambiguous Context-Free Grammar (CFG) for Boolean expressions incorporating logical operators (`&&`, `||`, `!`), relational comparisons (`>`, `<`, `==`, `!=`), and parentheses.
2. **Implement Lexical Scanning:** Develop a character-by-character lexer with longest-match recognition, tracking exact source line and column numbers.
3. **Construct a Recursive-Descent Parser:** Implement top-down parsing that rejects chained comparisons (such as `a < b < c`) and enforces left/right associativity.
4. **Generate Dynamic ASTs:** Define structured AST node classes with JSON serialization and ASCII/SVG visualization.
5. **Enforce Semantic Type Invariants:** Implement a Symbol Table supporting `number` and `boolean` types with strict and lenient modes.
6. **Deploy Cloud-Ready Solution:** Ensure production deployment readiness on Render using Gunicorn and standardized REST API endpoints.

---

## 5. Language Specification
The language accepts Boolean and relational expressions over numeric and truth literals, identifiers, and relational/logical operators.

### 5.1 Supported Literals and Identifiers
- **Identifiers:** Variable names starting with an alphabetic character or underscore, followed by alphanumeric characters or underscores (e.g. `a`, `b`, `x1`, `isValid`).
- **Numeric Literals:** Signed or unsigned integer and decimal values (e.g. `10`, `42`, `3.1415`, `0.5`).
- **Boolean Literals:** `true` and `false`.

### 5.2 Supported Operators
- **Relational:** `>` (Greater than), `<` (Less than).
- **Equality:** `==` (Equal to), `!=` (Not equal to).
- **Logical:** `&&` (Logical AND), `||` (Logical OR), `!` (Logical NOT).
- **Delimiters:** `(` and `)` for explicit sub-expression grouping.

---

## 6. Compiler Architecture
The compiler follows a decoupled, sequential pipeline architecture:

```
Source Expression
       │
       ▼
[ Lexical Analyzer ] ────(Lexical Error)────► Terminate with Line/Col Diagnostic
       │
   Token Stream
       │
       ▼
[ Syntax Parser ] ───────(Syntax Error)─────► Terminate with Expected/Found Token
       │
 Abstract Syntax Tree
       │
       ▼
[ Semantic Analyzer ] ───(Semantic Error)───► Terminate with Type Incompatibility
       │
 Validated AST + Symbol Table
       │
       ▼
[ Safe Evaluator ] ─────────────────────────► Optional Boolean Result
       │
       ▼
Structured JSON Response / Web Workbench UI
```

Each stage operates independently. If a phase fails, earlier data (such as scanned tokens) is preserved, while subsequent stages are bypassed cleanly without throwing uncaught exceptions.

---

## 7. Lexical Analysis
Implemented in `backend/lexer.py`, the lexical analyzer scans the input string character-by-character.

### 7.1 Longest-Match Recognition
To distinguish compound operators from single-character prefixes:
- An `=` character triggers a peek at the next character. If followed by another `=`, an `EQ` (`==`) token is produced. A single `=` raises an immediate `LexicalError` advising that equality comparisons require `==`.
- A `!` character followed by `=` emits `NEQ` (`!=`), otherwise emitting unary `NOT` (`!`).
- Single `&` and `|` characters are immediately flagged as invalid with suggestions to use `&&` and `||`.

### 7.2 Position Tracking
The lexer tracks both `line` (incremented on newline) and `column` (incremented per character, reset on newline). Every token records its starting coordinate, enabling source-level error localization.

---

## 8. Context-Free Grammar (CFG)
The formal grammar avoids immediate left-recursion to facilitate top-down recursive descent:

```
Expression      → ORExpression
ORExpression    → ANDExpression ( '||' ANDExpression )*
ANDExpression   → NOTExpression ( '&&' NOTExpression )*
NOTExpression   → '!' NOTExpression | Comparison
Comparison      → Primary ( RelOp Primary )?
RelOp           → '>' | '<' | '==' | '!='
Primary         → IDENTIFIER | NUMBER | BOOLEAN | '(' Expression ')'
```

---

## 9. Grammar Explanation and Precedence
The grammar stratifies operators into distinct non-terminal layers, automatically establishing precedence:

1. **Parentheses & Primary (Level 1 - Highest):** Handled by `Primary`. Parentheses reset the grammar evaluation to `Expression`.
2. **Unary NOT (Level 2):** Handled by `NOTExpression`, which is right-recursive to handle chained negations such as `!!isValid`.
3. **Relational Operators (Level 3):** Handled by `Comparison`. Relational operators bind tighter than `&&` and `||`.
4. **Logical AND (Level 4):** Handled by `ANDExpression`. Binds tighter than `||`.
5. **Logical OR (Level 5 - Lowest):** Handled by `ORExpression`.

---

## 10. Parsing Technique
The parser (`backend/parser.py`) is implemented using recursive-descent predictive parsing with single-token lookahead.

### 10.1 Syntactic Validation
- **Missing Operands:** Detects trailing operators (`a >` or `a &&`) and unexpected EOF.
- **Unclosed Parentheses:** Ensures every `(` is matched with a corresponding `)`.
- **Chained Comparisons:** Detects constructs like `a < b < c` and instructs the user to write `(a < b) && (b < c)`.

---

## 11. AST Generation
Defined in `backend/ast_nodes.py`, the AST comprises strongly typed nodes:
- `IdentifierNode(name, line, column)`
- `NumberNode(value, line, column)`
- `BooleanNode(value, line, column)`
- `UnaryOpNode(operator, operand, line, column)`
- `BinaryOpNode(operator, left, right, line, column)`

Each node provides:
1. `to_dict()`: JSON serialization for API transmission.
2. `to_tree_str()`: Pretty ASCII tree representation with box-drawing characters (`├──`, `└──`).

---

## 12. Semantic Analysis and Symbol Table
The `SemanticAnalyzer` (`backend/semantic_analyzer.py`) inspects the AST to verify type compatibility:

### 12.1 Type Rules
- **Relational (`>`, `<`):** Requires numeric operands on both sides. Inferred type: `boolean`.
- **Equality (`==`, `!=`):** Requires matching operand types (`number == number` or `boolean == boolean`). Comparing a number to a boolean triggers a `SemanticError`.
- **Logical (`&&`, `||`):** Requires boolean operands on both sides. Supplying a number triggers a `SemanticError`.
- **Unary NOT (`!`):** Requires a boolean operand. Applying `!` to a number triggers a `SemanticError`.

### 12.2 Symbol Table
Maintains mapping of variable names to their declared types (`number` or `boolean`) and optional sample values.
- In **Strict Mode**, undeclared identifiers produce an immediate error.
- In **Lenient Mode**, undeclared identifiers produce a warning and default to type `unknown`.

---

## 13. Error Handling
The compiler categorizes errors into three distinct classes:
1. **Lexical Error:** Invalid characters, single `&` or `|`, malformed numbers.
2. **Syntax Error:** Missing operands, unclosed parentheses, chained comparisons.
3. **Semantic Error:** Type incompatibilities, undeclared variables.

Every diagnostic error includes:
- Category badge
- Precise line and column numbers
- Explanatory message
- Actionable suggestion for correction

---

## 14. Implementation Details
- **Backend:** Flask web server (`app.py`), Python standard library (`enum`, `typing`, `dataclasses`, `time`).
- **Production Server:** Gunicorn with dynamic `PORT` binding.
- **Frontend Workbench:** Vanilla JavaScript (`app.js`) and CSS3 (`style.css`) without heavy external dependencies.
- **Dynamic AST Rendering:** SVG canvas layout algorithm that computes node widths, levels, and bezier connection lines.

---

## 15. Test Cases and Results
Automated testing in `tests/test_compiler.py` verifies 43 individual test scenarios:

| Category | Count | Sample Test | Result |
|:---|:---:|:---|:---:|
| Valid Expressions | 13 | `a > b && c < d`, `!(a > b)`, `(x1 > 10) && (x1 < 100)` | Pass |
| Invalid Syntax | 12 | `a >`, `&& a`, `a && && b`, `(a > b`, `a < b < c` | Pass |
| Lexical Analysis | 8 | `a & b`, `a | b`, `a = b`, `10.20.30`, `a @ b` | Pass |
| Semantic Analysis | 6 | `numA && flagA`, `!numA`, `numA == flagA`, `flagA > 5` | Pass |
| Precedence & Eval | 4 | `a \|\| b && c`, `!a && b`, `10 > 5 && 20 < 30` | Pass |

**Overall Result:** 43 passed in 0.004s.

---

## 16. Screenshots Section
*(Screenshots captured from live web workbench running at http://127.0.0.1:5000 and Render)*

- **Figure 1:** Main Developer Studio Workbench with expression editor and interactive Symbol Table.
- **Figure 2:** Token Stream table with syntax badge highlights and exact positions.
- **Figure 3:** Dynamic SVG Abstract Syntax Tree showing hierarchical operator nodes.
- **Figure 4:** Semantic Error diagnostic card illustrating proactive correction hints.

---

## 17. Limitations and Future Enhancements
### Limitations:
- The language currently focuses on Boolean expressions and comparisons, without assignment statements, loops, or user-defined functions.
- Arithmetic operators (`+`, `-`, `*`, `/`) within comparisons are not yet included.

### Future Enhancements:
- Intermediate Representation: Generation of Three-Address Code (TAC) and Quadruples.
- Optimization Passes: Constant folding (e.g., `true && false` $\to$ `false`) and short-circuit dead code elimination.
- Target Generation: Emitting WebAssembly (Wasm) or LLVM IR for high-speed native execution.

---

## 18. Conclusion
The Boolean Expression Compiler successfully fulfills all design requirements of an undergraduate Compiler Design mini project. By implementing true multi-pass compilation—spanning lexical scanning, recursive-descent parsing, AST construction, and semantic type analysis—the system demonstrates how compiler front-ends guarantee structural and logical correctness. The responsive web workbench and automated test coverage make the project accessible, demonstrable, and deployment-ready on modern cloud hosting platforms.

---

## 19. References
1. Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers: Principles, Techniques, and Tools* (2nd ed.). Addison-Wesley.
2. Cooper, K. D., & Torczon, L. (2011). *Engineering a Compiler* (2nd ed.). Morgan Kaufmann.
3. Nystrom, R. (2021). *Crafting Interpreters*. Genever Benning.
4. Grune, D., Bal, H. E., Jacobs, C. J., & Langendoen, K. G. (2012). *Modern Compiler Design*. Springer.
