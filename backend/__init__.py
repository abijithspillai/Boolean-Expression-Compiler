"""
Boolean Expression Compiler Backend Package.
Provides lexical analysis, recursive-descent parsing, AST construction,
semantic type-checking, and evaluation for Boolean expressions.
"""

from .lexer import Lexer, Token, TokenType, LexicalError
from .ast_nodes import (
    ASTNode,
    IdentifierNode,
    NumberNode,
    BooleanNode,
    UnaryOpNode,
    BinaryOpNode,
)
from .parser import Parser, ParseError
from .semantic_analyzer import (
    SemanticAnalyzer,
    SemanticError,
    SymbolTable,
    Symbol,
    Type,
)
from .compiler import compile_expression, CompilationResult

__all__ = [
    "Lexer",
    "Token",
    "TokenType",
    "LexicalError",
    "ASTNode",
    "IdentifierNode",
    "NumberNode",
    "BooleanNode",
    "UnaryOpNode",
    "BinaryOpNode",
    "Parser",
    "ParseError",
    "SemanticAnalyzer",
    "SemanticError",
    "SymbolTable",
    "Symbol",
    "Type",
    "compile_expression",
    "CompilationResult",
]
