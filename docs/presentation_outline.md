# Presentation Outline & Viva Preparation

**Project Title:** Boolean Expression Compiler  
**Subject:** Compiler Design  
**Author:** Abijith S Pillai  
**Technology:** Python, Flask, HTML5, CSS3, JavaScript  

---

## Part 1: Slide-by-Slide Presentation Outline (12 Slides)

### Slide 1: Title & Project Overview
- **Header:** Boolean Expression Compiler
- **Subtitle:** An Interactive Compiler Front-End for Boolean Expressions
- **Subject:** Compiler Design Academic Mini Project
- **Presenter:** Abijith S Pillai
- **Key Points:**
  - Full front-end compiler pipeline implemented in Python.
  - Interactive Developer Studio UI with live AST rendering.
  - Strict separation of Lexical, Syntax, and Semantic analysis.

### Slide 2: Objectives & Problem Statement
- **Problem Statement:** Most online expression tools rely on naive regex patterns or insecure `eval()` execution, ignoring fundamental compiler phases.
- **Objectives:**
  - Build a bona fide compiler front-end enforcing Context-Free Grammar.
  - Isolate lexical, syntactic, and semantic type errors.
  - Dynamically construct and visualize the Abstract Syntax Tree (AST).
  - Provide an interactive symbol table with sample value evaluation.

### Slide 3: Language Specification & Supported Operators
- **Data Types:** Number (Integers & Decimals), Boolean (`true`, `false`).
- **Operators:**
  - Relational: `>`, `<`
  - Equality: `==`, `!=`
  - Logical: `&&` (AND), `||` (OR), `!` (NOT)
  - Grouping: `( )`
- **Identifiers:** Variable names (`a`, `b`, `x1`, `isValid`).

### Slide 4: End-to-End Compiler Architecture
- **Pipeline Stages:**
  1. Input Validation (string integrity check)
  2. Lexical Analyzer (`lexer.py`)
  3. Recursive-Descent Parser (`parser.py`)
  4. AST Construction (`ast_nodes.py`)
  5. Semantic Analyzer & Symbol Table (`semantic_analyzer.py`)
  6. Safe Expression Evaluator (no `eval()`)
  7. JSON Response & Interactive UI

### Slide 5: Lexical Analysis & Token Generation
- **Token Class:** Type, Lexeme, Line, Column, Literal Value.
- **Maximal-Munch (Longest-Match) Rule:**
  - Distinguishes `==` from assignment `=`.
  - Distinguishes `!=` from logical `!`.
  - Distinguishes `&&` from bitwise `&`.
- **Lexical Errors:** Immediate rejection of unsupported characters (`@`, `$`) and malformed floats (`10.20.30`).

### Slide 6: Context-Free Grammar (CFG) & Operator Precedence
- **Precedence Hierarchy (Top to Bottom):**
  1. Primary & Parentheses `( )` (Highest)
  2. Unary NOT `!` (Right-to-Left)
  3. Relational & Equality Comparisons `>`, `<`, `==`, `!=` (Non-chaining)
  4. Logical AND `&&` (Left-to-Right)
  5. Logical OR `||` (Lowest, Left-to-Right)
- **Elimination of Left Recursion:** Converted left-recursive rules into EBNF iteration to support top-down parsing.

### Slide 7: Parsing Technique & AST Construction
- **Algorithm:** Top-Down Recursive-Descent with single-token lookahead.
- **Explicit Syntactic Safeguards:**
  - Rejection of chained comparisons (`a < b < c`).
  - Strict matching of parentheses (`(` without `)`).
  - Detection of missing operands (`a >` or `&& a`).
- **AST Nodes:** `BinaryOpNode`, `UnaryOpNode`, `IdentifierNode`, `NumberNode`, `BooleanNode`.

### Slide 8: Semantic Analysis & Symbol Table
- **Type Invariants:**
  - Relational (`>`, `<`) requires both operands to be `number`.
  - Equality (`==`, `!=`) requires operands of identical type (`number` vs `number` or `bool` vs `bool`).
  - Logical (`&&`, `||`, `!`) requires operands to be `boolean`.
- **Modes:**
  - *Strict Mode:* Undeclared variable triggers a Semantic Error.
  - *Lenient Mode:* Undeclared variable generates diagnostic warnings.

### Slide 9: Automated Test Suite & Quality Verification
- **Test Framework:** Python `unittest`.
- **Coverage:** 43 automated unit tests executed in < 0.01s:
  - 13 Valid expressions (mixed precedence, nested parens).
  - 12 Invalid syntax expressions (unclosed parens, chained comps, missing operands).
  - 8 Lexical error tests (longest match, bad characters).
  - 6 Semantic error tests (type mismatches, strict mode checks).
  - 4 Precedence and evaluation tests.

### Slide 10: Live Demonstration & Web Interface
- **Developer Studio UI Highlights:**
  - Line-numbered code editor with `Ctrl + Enter` shortcut.
  - Real-time backend status indicator.
  - Interactive Symbol Table with dynamic variable addition.
  - Interactive SVG AST Tree layout and Indented Text View.
  - Token stream table and CFG explanation panel.
  - Error diagnostic cards with proactive suggestions.

### Slide 11: Deployment & Cloud Hosting
- **Production Server:** Gunicorn WSGI.
- **Platform:** Render Web Service.
- **Continuous Deployment:** Direct GitHub integration (`https://github.com/abijithspillai/Boolean-Expression-Compiler`).
- **Configuration:** `Procfile`, `render.yaml`, and environment-aware `PORT` binding.

### Slide 12: Conclusion & Future Enhancements
- **Summary:** Successfully built a full-fledged compiler front-end strictly adhering to compiler design theory.
- **Future Work:**
  - Intermediate Code Generation (Three-Address Code / Quadruples).
  - Code Optimization (Constant folding, short-circuit dead code elimination).
  - Target Code Generation (Bytecode or assembly generation).

---

## Part 2: Viva Preparation: 20 Common Questions & Answers

### Q1: What is the primary role of a Lexical Analyzer (Lexer)?
**Answer:** The lexer (tokenizer) reads the raw input source code character-by-character and groups characters into meaningful linguistic units called tokens (e.g. `IDENTIFIER`, `NUMBER`, `AND`), while discarding insignificant whitespace and tracking source line and column numbers.

### Q2: What is the "Maximal Munch" or "Longest Match" rule?
**Answer:** It is a lexical analysis principle where the lexer always matches the longest valid character sequence. For example, when encountering `!=`, the lexer reads both characters as the single `NEQ` token rather than splitting it into `NOT` (`!`) followed by `=`.

### Q3: What is a Context-Free Grammar (CFG)?
**Answer:** A CFG is a 4-tuple $(V, \Sigma, R, S)$ where $V$ is a set of non-terminals, $\Sigma$ is a set of terminal symbols, $R$ is a set of production rules of the form $A \to \alpha$, and $S$ is the start symbol. It describes the formal syntax of programming language constructs.

### Q4: Why can't a top-down recursive-descent parser use a left-recursive grammar?
**Answer:** In left-recursive rules like $A \to A \alpha$, a top-down parser calling the function for $A$ immediately calls $A$ again before consuming any input token, resulting in an infinite recursion and a stack overflow.

### Q5: How did you eliminate left-recursion in your parser?
**Answer:** We transformed left-recursive productions into iterative loops using EBNF notation. For example, $E \to E \text{ '\|\|' } T \mid T$ was rewritten as $E \to T (\text{'\|\|' } T)^*$, which is parsed using a `while` loop that constructs left-associative binary nodes.

### Q6: What is an Abstract Syntax Tree (AST) and how does it differ from a Parse Tree?
**Answer:** A parse tree (concrete syntax tree) contains every grammatical production including punctuation like parentheses and commas. An AST is a pruned, abstract representation containing only semantic nodes (operators and operands), which is more efficient for semantic analysis and code generation.

### Q7: How does your parser enforce operator precedence?
**Answer:** Through grammar stratification. Productions for lower-precedence operators (like `||`) are placed near the top of the grammar hierarchy and called first, while higher-precedence operators (like `!` and `Primary`) are situated deeper down and evaluated first.

### Q8: Why are chained comparisons like `a < b < c` disallowed?
**Answer:** Because in relational logic, $(a < b)$ produces a boolean, which cannot mathematically or semantically be compared against number $c$. Disallowing this prevents ambiguous evaluations and type errors.

### Q9: What is the difference between Syntax Analysis and Semantic Analysis?
**Answer:** Syntax analysis checks whether tokens conform to grammatical structure (e.g., matching parentheses, valid operator placements). Semantic analysis checks whether syntactically valid constructs obey language type rules and symbol definitions (e.g., ensuring logical operators receive booleans, not numbers).

### Q10: What is a Symbol Table and why is it needed?
**Answer:** A symbol table is a data structure used by the compiler to record information about identifiers (names, declared data types, scope, and values) to facilitate semantic type-checking and symbol resolution.

### Q11: How does your compiler detect type mismatches?
**Answer:** The `SemanticAnalyzer` traverses the AST recursively. At each `BinaryOpNode`, it evaluates the inferred types of the left and right children. If a relational operator has a boolean child or a logical operator has a number child, it raises a `SemanticError`.

### Q12: Why did you not use Python's built-in `eval()` function?
**Answer:** Using `eval()` bypasses the entire compiler pipeline, executes arbitrary code (introducing security vulnerabilities like code injection), and provides no insight into lexical tokens, parse trees, or type systems. Our evaluator recursively walks the AST safely.

### Q13: What is the difference between strict mode and lenient mode in your compiler?
**Answer:** In strict mode, using an undeclared variable halts compilation with a `SemanticError`. In lenient mode, it issues a diagnostic warning and assigns an `unknown` type, allowing partial analysis.

### Q14: How does your compiler track source locations for errors?
**Answer:** Every `Token` and `ASTNode` records its 1-indexed `line` and `column` numbers during lexical scanning. When a syntax or semantic error is detected, these coordinates are included in the error payload for precise diagnostics.

### Q15: What is the associativity of unary NOT (`!`) and how is it implemented?
**Answer:** Unary NOT is right-associative (e.g. `!!x` is parsed as `!(!x)`). In `parser.py`, this is implemented through right-recursion in the `not_expression` method: `operand = self.not_expression()`.

### Q16: How is the AST serialized for the web frontend?
**Answer:** Each AST node implements a `to_dict()` method that recursively converts the node hierarchy into a clean JSON object containing node types, operator names, line/column numbers, and child nodes.

### Q17: How is the dynamic SVG tree rendered on the frontend?
**Answer:** `app.js` runs a recursive tree-layout algorithm that calculates coordinates $(x, y)$ based on subtree leaf counts and depth, generating native SVG `<line>`, `<rect>`, and `<text>` elements.

### Q18: What is Gunicorn and why is it used for Render hosting?
**Answer:** Gunicorn (Green Unicorn) is a production-grade Python WSGI HTTP server. Unlike Flask's built-in single-threaded development server, Gunicorn handles concurrent requests, worker process management, and production stability.

### Q19: What HTTP endpoints does the Flask backend expose?
**Answer:**
- `GET /`: Serves the web application.
- `GET /api/health`: Returns service health, Python version, and compiler feature metadata.
- `POST /api/compile`: Accepts expression JSON and returns structured compilation diagnostics.

### Q20: How would you extend this compiler into a full compiler?
**Answer:** By adding:
1. An Intermediate Code Generator to emit Three-Address Code (TAC).
2. An Optimizer for constant folding (e.g. `true && false` $\to$ `false`).
3. A Code Generator to output bytecode (e.g., Python bytecode or LLVM IR) or assembly.
