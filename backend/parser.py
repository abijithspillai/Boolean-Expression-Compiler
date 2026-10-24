"""
Recursive-Descent Parser for Boolean Expressions.
Builds an Abstract Syntax Tree (AST) enforcing precedence and associativity:
1. Primary / Parentheses
2. Unary NOT (!) [Right-associative]
3. Relational comparisons (>, <, ==, !=) [Non-chaining]
4. Logical AND (&&) [Left-associative]
5. Logical OR (||) [Left-associative]
"""

from typing import List, Optional, Dict, Any
from .lexer import Token, TokenType
from .ast_nodes import (
    ASTNode,
    NumberNode,
    BooleanNode,
    IdentifierNode,
    UnaryOpNode,
    BinaryOpNode,
)


class ParseError(Exception):
    """Exception raised for syntax errors during parsing."""

    def __init__(
        self,
        message: str,
        line: int,
        column: int,
        expected: Optional[str] = None,
        found: Optional[str] = None,
        suggestion: Optional[str] = None,
    ):
        super().__init__(f"Syntax Error at line {line}, column {column}: {message}")
        self.message = message
        self.line = line
        self.column = column
        self.expected = expected
        self.found = found
        self.suggestion = suggestion

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": "Syntax",
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "expected": self.expected,
            "found": self.found,
            "suggestion": self.suggestion,
        }


class Parser:
    """
    Recursive-descent parser translating token stream into an AST.
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    @property
    def current(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # Return last token (usually EOF)

    def _peek_next(self) -> Optional[Token]:
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return None

    def _advance(self) -> Token:
        tok = self.current
        if tok.type != TokenType.EOF:
            self.pos += 1
        return tok

    def _match(self, *types: TokenType) -> bool:
        return self.current.type in types

    def _consume(self, expected_type: TokenType, err_msg: str, suggestion: Optional[str] = None) -> Token:
        if self.current.type == expected_type:
            return self._advance()
        raise ParseError(
            err_msg,
            self.current.line,
            self.current.column,
            expected=expected_type.value,
            found=self.current.lexeme,
            suggestion=suggestion,
        )

    def parse(self) -> ASTNode:
        """Entry point for parsing. Parses Expression and checks for EOF."""
        if not self.tokens or (len(self.tokens) == 1 and self.tokens[0].type == TokenType.EOF):
            raise ParseError("Empty expression input", 1, 1, suggestion="Enter a valid Boolean expression, e.g. 'a > b'")

        ast = self.expression()

        # Check for remaining unexpected tokens
        if self.current.type != TokenType.EOF:
            if self.current.type == TokenType.RPAREN:
                raise ParseError(
                    "Unexpected closing parenthesis ')' without matching opening parenthesis",
                    self.current.line,
                    self.current.column,
                    suggestion="Remove extra ')' or ensure opening '(' is placed correctly",
                )
            elif self.current.type in (TokenType.IDENTIFIER, TokenType.NUMBER, TokenType.BOOLEAN):
                raise ParseError(
                    f"Unexpected token '{self.current.lexeme}'; missing operator between expressions",
                    self.current.line,
                    self.current.column,
                    suggestion=f"Insert an operator (such as '&&', '||', '==') before '{self.current.lexeme}'",
                )
            else:
                raise ParseError(
                    f"Unexpected token '{self.current.lexeme}' after complete expression",
                    self.current.line,
                    self.current.column,
                    suggestion="Check for trailing or unneeded characters at the end of expression",
                )

        return ast

    def expression(self) -> ASTNode:
        """Expression → ORExpression"""
        return self.or_expression()

    def or_expression(self) -> ASTNode:
        """ORExpression → ANDExpression ( '||' ANDExpression )*"""
        left = self.and_expression()

        while self._match(TokenType.OR):
            op_tok = self._advance()
            if self.current.type == TokenType.EOF:
                raise ParseError(
                    f"Expected expression after operator '{op_tok.lexeme}' at end of input",
                    op_tok.line,
                    op_tok.column + len(op_tok.lexeme),
                    suggestion=f"Provide a right-hand operand after '{op_tok.lexeme}'",
                )
            right = self.and_expression()
            left = BinaryOpNode(op_tok.lexeme, left, right, op_tok.line, op_tok.column)

        return left

    def and_expression(self) -> ASTNode:
        """ANDExpression → NOTExpression ( '&&' NOTExpression )*"""
        left = self.not_expression()

        while self._match(TokenType.AND):
            op_tok = self._advance()
            if self.current.type == TokenType.EOF:
                raise ParseError(
                    f"Expected expression after operator '{op_tok.lexeme}' at end of input",
                    op_tok.line,
                    op_tok.column + len(op_tok.lexeme),
                    suggestion=f"Provide a right-hand operand after '{op_tok.lexeme}'",
                )
            right = self.not_expression()
            left = BinaryOpNode(op_tok.lexeme, left, right, op_tok.line, op_tok.column)

        return left

    def not_expression(self) -> ASTNode:
        """NOTExpression → '!' NOTExpression | Comparison"""
        if self._match(TokenType.NOT):
            not_tok = self._advance()
            if self.current.type == TokenType.EOF:
                raise ParseError(
                    "Expected operand after logical NOT '!' at end of input",
                    not_tok.line,
                    not_tok.column + 1,
                    suggestion="Provide a boolean expression or identifier after '!' (e.g. '!isValid')",
                )
            operand = self.not_expression()
            return UnaryOpNode(not_tok.lexeme, operand, not_tok.line, not_tok.column)

        return self.comparison()

    def comparison(self) -> ASTNode:
        """
        Comparison → Primary ( RelOp Primary )?
        RelOp → '>' | '<' | '==' | '!='
        Rejects chained comparisons like `a < b < c`.
        """
        left = self.primary()

        if self._match(TokenType.GT, TokenType.LT, TokenType.EQ, TokenType.NEQ):
            op_tok = self._advance()
            if self.current.type == TokenType.EOF:
                raise ParseError(
                    f"Expected operand after comparison operator '{op_tok.lexeme}' at end of input",
                    op_tok.line,
                    op_tok.column + len(op_tok.lexeme),
                    suggestion=f"Provide a right operand after '{op_tok.lexeme}' (e.g. '{op_tok.lexeme} 10')",
                )

            # Check if user placed another relational operator without operand (e.g. `a < < b`)
            if self._match(TokenType.GT, TokenType.LT, TokenType.EQ, TokenType.NEQ):
                raise ParseError(
                    f"Consecutive comparison operator '{self.current.lexeme}' is invalid",
                    self.current.line,
                    self.current.column,
                    suggestion="Remove duplicate or misplaced comparison operator",
                )

            right = self.primary()

            # Reject chained comparisons such as `a < b < c` or `a == b == c`
            if self._match(TokenType.GT, TokenType.LT, TokenType.EQ, TokenType.NEQ):
                chain_op = self.current
                raise ParseError(
                    f"Chained comparisons such as '... {op_tok.lexeme} ... {chain_op.lexeme} ...' are not permitted",
                    chain_op.line,
                    chain_op.column,
                    suggestion="Combine multiple comparisons using '&&', e.g. '(a < b) && (b < c)'",
                )

            return BinaryOpNode(op_tok.lexeme, left, right, op_tok.line, op_tok.column)

        return left

    def primary(self) -> ASTNode:
        """
        Primary → IDENTIFIER | NUMBER | BOOLEAN | '(' Expression ')'
        """
        tok = self.current

        if tok.type == TokenType.NUMBER:
            self._advance()
            return NumberNode(tok.value, tok.line, tok.column)

        if tok.type == TokenType.BOOLEAN:
            self._advance()
            return BooleanNode(tok.value, tok.line, tok.column)

        if tok.type == TokenType.IDENTIFIER:
            self._advance()
            return IdentifierNode(tok.lexeme, tok.line, tok.column)

        if tok.type == TokenType.LPAREN:
            open_paren = self._advance()
            inner_expr = self.expression()
            if self.current.type != TokenType.RPAREN:
                raise ParseError(
                    f"Unclosed parenthesis; missing matching ')' for '(' opened at line {open_paren.line}, column {open_paren.column}",
                    self.current.line,
                    self.current.column,
                    expected=")",
                    found=self.current.lexeme,
                    suggestion="Add closing ')' to properly close the grouped sub-expression",
                )
            self._advance()  # Consume ')'
            return inner_expr

        # Error handling for unexpected operators or EOF
        if tok.type == TokenType.EOF:
            raise ParseError(
                "Unexpected end of input; expected an identifier, literal, or '('",
                tok.line,
                tok.column,
                suggestion="Complete the expression with an operand",
            )

        if tok.type in (TokenType.AND, TokenType.OR):
            raise ParseError(
                f"Unexpected operator '{tok.lexeme}'; expected an operand or expression before it",
                tok.line,
                tok.column,
                suggestion=f"Provide a left-hand operand before '{tok.lexeme}'",
            )

        if tok.type in (TokenType.GT, TokenType.LT, TokenType.EQ, TokenType.NEQ):
            raise ParseError(
                f"Unexpected comparison operator '{tok.lexeme}'; expected a leading operand",
                tok.line,
                tok.column,
                suggestion=f"Provide a left operand before '{tok.lexeme}'",
            )

        raise ParseError(
            f"Unexpected token '{tok.lexeme}'; expected identifier, number, boolean, or '('",
            tok.line,
            tok.column,
            found=tok.lexeme,
            suggestion="Check syntax around this token",
        )
