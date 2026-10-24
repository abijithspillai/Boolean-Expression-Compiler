# Boolean Expression Compiler 🚀

A complete, professional **Mini Compiler / Compiler Front-End for Boolean Expressions** built as a **Compiler Design** academic project.

This application demonstrates actual compiler engineering principles: lexical scanning using longest-match tokenization, syntax validation with a recursive-descent parser, dynamic Abstract Syntax Tree (AST) construction, static semantic type-checking with an interactive symbol table, and safe expression evaluation without relying on `eval()`.

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask%203.x-green.svg)](https://flask.palletsprojects.com/)
[![Tests](https://img.shields.io/badge/Unit%20Tests-43%20Passed-brightgreen.svg)]()

---

## 📑 Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Compiler Architecture](#compiler-architecture)
- [Grammar & Operator Precedence](#grammar--operator-precedence)
- [Supported Operators & Syntax](#supported-operators--syntax)
- [Quick Start (Local Setup)](#quick-start-local-setup)
- [Automated Testing](#automated-testing)
- [REST API Reference](#rest-api-reference)
- [Academic Deliverables & Documentation](#academic-deliverables--documentation)
- [License](#license)

---

## 🌟 Project Overview

- **Subject:** Compiler Design
- **Project Type:** Compiler Front-End / Interactive Mini Compiler
- **Primary Language:** Python 3.12
- **Backend Framework:** Flask
- **Frontend:** HTML5, CSS3 (Modern Developer Studio Theme), Vanilla JavaScript
- **Execution:** Local Web Application / Production WSGI

Unlike trivial expression evaluators that use regex or JavaScript's `eval()`, this project implements genuine, decoupled compiler stages that isolate lexical, syntax, and semantic errors.

---

## ✨ Key Features

1. **Maximal-Munch Lexical Scanning (`lexer.py`):**
   - Longest-match recognition (e.g. `==` vs `=`, `!=` vs `!`, `&&` vs `&`, `||` vs `|`).
   - Tracks 1-indexed line and column numbers.
   - Detects and isolates invalid characters with actionable suggestions.

2. **Recursive-Descent Parser (`parser.py`):**
   - Strictly enforces operator precedence and associativity.
   - Explicitly rejects chained comparisons (`a < b < c`).
   - Validates matching parentheses and detects missing operands/operators.

3. **Dynamic AST Visualizer (`ast_nodes.py`):**
   - Renders interactive SVG tree diagrams with operator and operand badges.
   - Provides indented ASCII tree representations.
   - One-click copy for JSON AST data.

4. **Static Semantic Analyzer & Symbol Table (`semantic_analyzer.py`):**
   - Interactive symbol table for declaring variables, types (`number`, `boolean`), and sample values.
   - Enforces strict type rules: relational (`>`, `<`) require numbers; equality (`==`, `!=`) require matching types; logical (`&&`, `||`, `!`) require booleans.
   - Strict mode vs lenient mode with diagnostic warnings.

5. **Safe Expression Evaluator:**
   - Evaluates boolean expressions via AST tree traversal without `eval()` or `exec()`.

6. **Modern Developer Studio UI:**
   - Dark theme inspired by modern devtools (Linear, VS Code).
   - Real-time line-numbered editor with `Ctrl + Enter` shortcut.
   - Pre-loaded gallery of valid and error-inducing expressions.
   - Backend health monitoring and execution duration breakdown.

---

## 🏗️ Compiler Architecture

```
[ User Input Expression ]
           │
           ▼
┌───────────────────────┐
│   Input Validation    │  Length & non-empty string check
└──────────┬────────────┘
           ▼
┌───────────────────────┐
│   Lexical Analyzer    │  Character scanning, maximal munch, line/col tracking
│     (lexer.py)        │  Tokens: IDENTIFIER, NUMBER, BOOLEAN, RelOp, LogOp
└──────────┬────────────┘
           ▼
┌───────────────────────┐
│     Syntax Parser     │  Recursive-descent parsing based on CFG
│     (parser.py)       │  Enforces precedence, associativity, & no chained comps
└──────────┬────────────┘
           ▼
┌───────────────────────┐
│    AST Construction   │  BinaryOpNode, UnaryOpNode, IdentifierNode, etc.
│    (ast_nodes.py)     │  JSON serialization & ASCII tree formatting
└──────────┬────────────┘
           ▼
┌───────────────────────┐
│   Semantic Analyzer   │  Symbol Table lookup & type-checking rules
│(semantic_analyzer.py) │  Enforces: Num vs Num, Bool vs Bool, Logical bool-only
└──────────┬────────────┘
           ▼
┌───────────────────────┐
│ Optional Evaluator    │  Safe tree traversal to compute truth value
│(semantic_analyzer.py) │  (Runs only when sample values are provided)
└──────────┬────────────┘
           ▼
[ Structured JSON API Output / Interactive Web UI ]
```

---

## 📐 Grammar & Operator Precedence

### Context-Free Grammar (CFG)

```
Expression      → ORExpression
ORExpression    → ANDExpression ( '||' ANDExpression )*
ANDExpression   → NOTExpression ( '&&' NOTExpression )*
NOTExpression   → '!' NOTExpression | Comparison
Comparison      → Primary ( RelOp Primary )?
RelOp           → '>' | '<' | '==' | '!='
Primary         → IDENTIFIER | NUMBER | BOOLEAN | '(' Expression ')'
```

### Precedence Hierarchy

| Level | Operator(s) | Precedence | Associativity | Description |
|:---:|:---:|:---:|:---:|:---|
| **1** | `( )`, Literals, IDs | Highest | Non-associative | Grouping and primary operands |
| **2** | `!` | High | Right-to-Left | Unary logical NOT |
| **3** | `>`, `<`, `==`, `!=` | Medium | Non-chaining | Relational and equality comparisons |
| **4** | `&&` | Low | Left-to-Right | Logical AND conjunction |
| **5** | `||` | Lowest | Left-to-Right | Logical OR disjunction |

---

## 🔣 Supported Operators & Syntax

- **Identifiers:** `a`, `b`, `x1`, `isValid` (starts with letter/underscore, followed by alphanumeric/underscore).
- **Literals:**
  - Numbers: `10`, `25.5`, `0.75` (integers and decimals)
  - Booleans: `true`, `false`
- **Relational Operators:** `>` (greater than), `<` (less than)
- **Equality Operators:** `==` (equal), `!=` (not equal)
- **Logical Operators:** `&&` (AND), `||` (OR), `!` (NOT)
- **Grouping:** `(` expression `)`

---

## 💻 Quick Start (Local Setup)

### Prerequisites

- Python 3.10+ installed
- Git installed

### 1. Clone the Repository

```bash
git clone https://github.com/abijithspillai/Boolean-Expression-Compiler.git
cd Boolean-Expression-Compiler
```

### 2. Create a Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Automated Testing

The project includes an automated test suite with **43 unit tests** covering valid expressions, invalid syntax, lexical errors, semantic type mismatches, operator precedence, and evaluation.

To run the test suite:

```bash
python -m unittest discover -s tests -v
```

### Sample Test Output:

```
test_invalid_01_trailing_operator (test_compiler.TestInvalidSyntax) ... ok
test_invalid_11_chained_comparisons (test_compiler.TestInvalidSyntax) ... ok
test_basic_token_stream (test_compiler.TestLexer) ... ok
test_precedence_and_over_or (test_compiler.TestPrecedenceAndEvaluation) ... ok
test_number_with_logical_and (test_compiler.TestSemanticAnalysis) ... ok
test_valid_10_mixed_precedence (test_compiler.TestValidSyntax) ... ok
----------------------------------------------------------------------
Ran 43 tests in 0.004s

OK
```

---

## 🌐 REST API Reference

### Health Check

- **Endpoint:** `GET /api/health`
- **Response:**
  ```json
  {
    "status": "online",
    "service": "Boolean Expression Compiler",
    "version": "1.0.0",
    "python_version": "3.12.10",
    "features": [...]
  }
  ```

### Compile Expression

- **Endpoint:** `POST /api/compile`
- **Headers:** `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "expression": "a > b && c != d",
    "symbols": [
      { "name": "a", "type": "number", "value": 15 },
      { "name": "b", "type": "number", "value": 10 },
      { "name": "c", "type": "number", "value": 20 },
      { "name": "d", "type": "number", "value": 30 }
    ],
    "options": {
      "strict_mode": true,
      "evaluate": true
    }
  }
  ```
- **Response Body:**
  ```json
  {
    "success": true,
    "expression": "a > b && c != d",
    "tokens": [...],
    "ast": { ... },
    "ast_tree_str": "AND\n├── GREATER_THAN\n│   ├── Identifier(a: number)\n│   └── Identifier(b: number)\n└── NOT_EQUAL\n    ├── Identifier(c: number)\n    └── Identifier(d: number)",
    "inferred_type": "boolean",
    "evaluation": {
      "computed": true,
      "result": true,
      "result_str": "true",
      "status": "Evaluated Successfully"
    },
    "phases": [...]
  }
  ```

---

## 📚 Academic Deliverables & Documentation

Complete academic deliverables are located in the `docs/` directory:

1. [docs/project_report.md](docs/project_report.md) — 19-section formal project report.
2. [docs/grammar.md](docs/grammar.md) — Context-Free Grammar, derivations, left-recursion analysis, and AST proofs.
3. [docs/presentation_outline.md](docs/presentation_outline.md) — Slide-by-slide presentation outline and 20 Viva questions & answers.

---

## 📜 License

- **Course:** Compiler Design Mini Project
- **License:** MIT License

