# Formal Grammar & Transformations: Boolean Expression Language

**Subject:** Compiler Design  
**Project:** Boolean Expression Compiler  
**Language Specification:** Boolean Expressions Front-End  

---

## 1. Context-Free Grammar (CFG) Specification

The formal Context-Free Grammar $G = (V, \Sigma, R, S)$ defining our Boolean Expression Language is given below:

### Non-Terminals ($V$):
- $S = \text{Expression}$ (Start Symbol)
- $\text{ORExpression}$
- $\text{ANDExpression}$
- $\text{NOTExpression}$
- $\text{Comparison}$
- $\text{RelOp}$
- $\text{Primary}$

### Terminals ($\Sigma$):
- `IDENTIFIER` (variable names e.g., `a`, `b`, `isValid`)
- `NUMBER` (numeric literals e.g., `10`, `3.14`)
- `BOOLEAN` (`true`, `false`)
- `>` (Greater Than)
- `<` (Less Than)
- `==` (Equal To)
- `!=` (Not Equal To)
- `&&` (Logical AND)
- `||` (Logical OR)
- `!` (Logical NOT)
- `(` (Left Parenthesis)
- `)` (Right Parenthesis)

### Production Rules ($R$):

```
1.  Expression    → ORExpression

2.  ORExpression  → ANDExpression ORExpression'
    ORExpression' → '||' ANDExpression ORExpression'
                  | ε

3.  ANDExpression → NOTExpression ANDExpression'
    ANDExpression'→ '&&' NOTExpression ANDExpression'
                  | ε

4.  NOTExpression → '!' NOTExpression
                  | Comparison

5.  Comparison    → Primary Comparison'
    Comparison'   → RelOp Primary
                  | ε

6.  RelOp         → '>'
                  | '<'
                  | '=='
                  | '!='

7.  Primary        → IDENTIFIER
                  | NUMBER
                  | BOOLEAN
                  | '(' Expression ')'
```

---

## 2. Precedence and Associativity Rules

Our grammar naturally encodes the operator precedence hierarchy via its layered stratification:

| Precedence | Operator / Construct | Associativity | Grammar Non-Terminal | Description |
|:---:|:---:|:---:|:---:|:---|
| **1 (Highest)** | `( )`, Literals, IDs | Non-associative | `Primary` | Grouping parentheses and basic atomic terms |
| **2** | `!` (NOT) | Right-to-Left | `NOTExpression` | Unary logical negation (allows `!!a`) |
| **3** | `>`, `<`, `==`, `!=` | Non-chaining | `Comparison` | Relational and equality comparisons |
| **4** | `&&` (AND) | Left-to-Right | `ANDExpression` | Conjunction operator |
| **5 (Lowest)** | `||` (OR) | Left-to-Right | `ORExpression` | Disjunction operator |

### Precedence Encoding Mechanism
In a stratified grammar, operators with lower precedence are placed closer to the start symbol ($S$), while operators with higher precedence are placed deeper in the derivation hierarchy. Thus, `||` (at `ORExpression`) is resolved last, while `Primary` is evaluated first.

---

## 3. Left-Recursion Elimination & Associativity

### Why Avoid Left-Recursion?
Standard recursive-descent parsers are top-down parsers. A grammar with left-recursive productions of the form:
$$A \to A \alpha \mid \beta$$
causes an infinite recursive loop because the parser attempts to expand non-terminal $A$ repeatedly without consuming any input tokens from the token stream.

### Grammar Transformation Applied
To eliminate immediate left-recursion while preserving left-associativity in our iterative parser, productions such as:
$$E \to E \text{ '\|\|' } T \mid T$$
were transformed into:
$$E \to T (\text{'\|\|' } T)^*$$

In our Python recursive-descent parser (`parser.py`), this is directly mapped to a `while` loop that constructs left-associative AST binary trees:

```python
def or_expression(self) -> ASTNode:
    left = self.and_expression()
    while self._match(TokenType.OR):
        op_tok = self._advance()
        right = self.and_expression()
        left = BinaryOpNode(op_tok.lexeme, left, right, op_tok.line, op_tok.column)
    return left
```

This guarantees:
1. No infinite recursion.
2. Exact left-to-right tree balancing for operators of equal precedence.

---

## 4. Rejection of Chained Comparisons

In standard mathematical notation, people sometimes write $a < b < c$. In programming languages like C, Java, and JavaScript, $a < b < c$ evaluates $(a < b) < c$, comparing a Boolean result against a numeric value, which causes runtime errors or subtle bugs. In Python, it represents chained comparisons.

In our Boolean language, **chained comparisons are explicitly rejected at the grammar level**:
$$\text{Comparison} \to \text{Primary } (\text{RelOp Primary})^?$$

After parsing one `RelOp Primary`, if the lookahead token is another relational operator (`>`, `<`, `==`, `!=`), the parser raises a descriptive syntax error:
```
Syntax Error: Chained comparisons such as '... < ... < ...' are not permitted.
Suggestion: Combine multiple comparisons using '&&', e.g. '(a < b) && (b < c)'
```

---

## 5. Step-by-Step Derivation Example

Input String:
```
a > b && c != d
```

### Derivation Steps:

1. `Expression`
2. $\Rightarrow$ `ORExpression`
3. $\Rightarrow$ `ANDExpression`
4. $\Rightarrow$ `NOTExpression && NOTExpression`
5. $\Rightarrow$ `Comparison && NOTExpression`
6. $\Rightarrow$ `Primary RelOp Primary && NOTExpression`
7. $\Rightarrow$ `a > b && NOTExpression`
8. $\Rightarrow$ `a > b && Comparison`
9. $\Rightarrow$ `a > b && Primary RelOp Primary`
10. $\Rightarrow$ `a > b && c != d`

---

## 6. Resulting Abstract Syntax Tree (AST)

The resulting Abstract Syntax Tree for `a > b && c != d`:

```
AND
├── GREATER_THAN
│   ├── Identifier(a: number)
│   └── Identifier(b: number)
└── NOT_EQUAL
    ├── Identifier(c: number)
    └── Identifier(d: number)
```

In JSON representation:
```json
{
  "node_type": "BinaryOpNode",
  "operator": "&&",
  "operator_name": "AND",
  "left": {
    "node_type": "BinaryOpNode",
    "operator": ">",
    "operator_name": "GREATER_THAN",
    "left": { "node_type": "IdentifierNode", "name": "a" },
    "right": { "node_type": "IdentifierNode", "name": "b" }
  },
  "right": {
    "node_type": "BinaryOpNode",
    "operator": "!=",
    "operator_name": "NOT_EQUAL",
    "left": { "node_type": "IdentifierNode", "name": "c" },
    "right": { "node_type": "IdentifierNode", "name": "d" }
  }
}
```
