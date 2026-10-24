"""
Lexical Analyzer for Boolean Expressions.
Scans source string character-by-character, recognizes tokens,
tracks line/column numbers, and rejects invalid characters or malformed operators.
"""

from enum import Enum, auto
from typing import List, Optional, Any, Dict


class TokenType(Enum):
    # Literals & Identifiers
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"

    # Relational Operators
    GT = "GT"            # >
    LT = "LT"            # <
    EQ = "EQ"            # ==
    NEQ = "NEQ"          # !=

    # Logical Operators
    AND = "AND"          # &&
    OR = "OR"            # ||
    NOT = "NOT"          # !

    # Delimiters
    LPAREN = "LPAREN"    # (
    RPAREN = "RPAREN"    # )

    # End of Input
    EOF = "EOF"


class Token:
    """Represents a lexical token with metadata."""

    def __init__(
        self,
        type_: TokenType,
        lexeme: str,
        line: int,
        column: int,
        value: Optional[Any] = None,
    ):
        self.type = type_
        self.lexeme = lexeme
        self.line = line
        self.column = column
        self.value = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert token to JSON-serializable dictionary."""
        return {
            "type": self.type.value,
            "lexeme": self.lexeme,
            "line": self.line,
            "column": self.column,
            "value": self.value,
        }

    def __repr__(self) -> str:
        val_str = f", val={self.value}" if self.value is not None else ""
        return f"Token({self.type.value}, '{self.lexeme}', L{self.line}:C{self.column}{val_str})"


class LexicalError(Exception):
    """Exception raised for invalid characters or malformed tokens."""

    def __init__(self, message: str, line: int, column: int, suggestion: Optional[str] = None):
        super().__init__(f"Lexical Error at line {line}, column {column}: {message}")
        self.message = message
        self.line = line
        self.column = column
        self.suggestion = suggestion

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": "Lexical",
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "suggestion": self.suggestion,
        }


class Lexer:
    """
    Tokenizer scanning input expressions character-by-character.
    Implements maximal munch (longest-match) recognition.
    """

    def __init__(self, source: str):
        self.source = source or ""
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

    def _peek(self, offset: int = 0) -> Optional[str]:
        idx = self.pos + offset
        if idx < len(self.source):
            return self.source[idx]
        return None

    def _advance(self) -> Optional[str]:
        if self.pos < len(self.source):
            ch = self.source[self.pos]
            self.pos += 1
            if ch == "\n":
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            return ch
        return None

    def tokenize(self) -> List[Token]:
        """Scans the entire source code into a list of Tokens ending with EOF."""
        self.tokens = []
        self.pos = 0
        self.line = 1
        self.column = 1

        while self.pos < len(self.source):
            ch = self._peek()

            # Skip whitespace
            if ch in (" ", "\t", "\r", "\n"):
                self._advance()
                continue

            start_line = self.line
            start_col = self.column

            # Parentheses
            if ch == "(":
                self._advance()
                self.tokens.append(Token(TokenType.LPAREN, "(", start_line, start_col))
                continue
            if ch == ")":
                self._advance()
                self.tokens.append(Token(TokenType.RPAREN, ")", start_line, start_col))
                continue

            # Relational & Equality operators
            if ch == ">":
                self._advance()
                self.tokens.append(Token(TokenType.GT, ">", start_line, start_col))
                continue

            if ch == "<":
                self._advance()
                self.tokens.append(Token(TokenType.LT, "<", start_line, start_col))
                continue

            if ch == "=":
                self._advance()
                next_ch = self._peek()
                if next_ch == "=":
                    self._advance()
                    self.tokens.append(Token(TokenType.EQ, "==", start_line, start_col))
                else:
                    raise LexicalError(
                        "Single '=' is assignment; Boolean comparison requires '=='",
                        start_line,
                        start_col,
                        suggestion="Replace '=' with '==' for equality comparison",
                    )
                continue

            if ch == "!":
                self._advance()
                next_ch = self._peek()
                if next_ch == "=":
                    self._advance()
                    self.tokens.append(Token(TokenType.NEQ, "!=", start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.NOT, "!", start_line, start_col))
                continue

            # Logical AND
            if ch == "&":
                self._advance()
                next_ch = self._peek()
                if next_ch == "&":
                    self._advance()
                    self.tokens.append(Token(TokenType.AND, "&&", start_line, start_col))
                else:
                    raise LexicalError(
                        "Single '&' is not supported; use '&&' for logical AND",
                        start_line,
                        start_col,
                        suggestion="Use '&&' instead of '&'",
                    )
                continue

            # Logical OR
            if ch == "|":
                self._advance()
                next_ch = self._peek()
                if next_ch == "|":
                    self._advance()
                    self.tokens.append(Token(TokenType.OR, "||", start_line, start_col))
                else:
                    raise LexicalError(
                        "Single '|' is not supported; use '||' for logical OR",
                        start_line,
                        start_col,
                        suggestion="Use '||' instead of '|'",
                    )
                continue

            # Number literal (Integer or Decimal)
            if ch.isdigit():
                num_str = ""
                has_dot = False
                while self._peek() is not None:
                    curr = self._peek()
                    if curr.isdigit():
                        num_str += curr
                        self._advance()
                    elif curr == ".":
                        if has_dot:
                            # Second decimal point encountered
                            raise LexicalError(
                                f"Malformed numeric literal '{num_str}.'",
                                start_line,
                                self.column,
                                suggestion="A number cannot contain multiple decimal points",
                            )
                        # Check character after dot
                        next_after_dot = self._peek(1)
                        if next_after_dot is None or not next_after_dot.isdigit():
                            raise LexicalError(
                                f"Numeric literal '{num_str}.' must have digits after the decimal point",
                                start_line,
                                self.column,
                                suggestion=f"Add digits after '.' or remove the decimal point: '{num_str}'",
                            )
                        has_dot = True
                        num_str += curr
                        self._advance()
                    else:
                        break

                val: Any = float(num_str) if has_dot else int(num_str)
                self.tokens.append(Token(TokenType.NUMBER, num_str, start_line, start_col, value=val))
                continue

            # Identifier or Boolean literal
            if ch.isalpha() or ch == "_":
                ident_str = ""
                while self._peek() is not None and (self._peek().isalnum() or self._peek() == "_"):
                    ident_str += self._advance()

                if ident_str == "true":
                    self.tokens.append(Token(TokenType.BOOLEAN, ident_str, start_line, start_col, value=True))
                elif ident_str == "false":
                    self.tokens.append(Token(TokenType.BOOLEAN, ident_str, start_line, start_col, value=False))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, ident_str, start_line, start_col, value=ident_str))
                continue

            # Unknown/unsupported character
            bad_char = self._advance()
            raise LexicalError(
                f"Unexpected character '{bad_char}' (ASCII: {ord(bad_char)})",
                start_line,
                start_col,
                suggestion=f"Remove or replace unsupported character '{bad_char}'",
            )

        # Append EOF token
        self.tokens.append(Token(TokenType.EOF, "<EOF>", self.line, self.column))
        return self.tokens
