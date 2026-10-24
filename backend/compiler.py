"""
Compiler Orchestrator for Boolean Expressions.
Executes the compilation pipeline step-by-step:
1. Input Validation
2. Lexical Analysis (Tokens)
3. Syntax Analysis & AST Construction
4. Semantic Analysis & Type Checking
5. Optional Expression Evaluation
6. Structured Result Generation
"""

import time
from typing import Dict, Any, Optional, List
from .lexer import Lexer, LexicalError, Token
from .parser import Parser, ParseError
from .ast_nodes import ASTNode, render_ast_tree
from .semantic_analyzer import (
    SemanticAnalyzer,
    SemanticError,
    SymbolTable,
    Type,
)


class CompilationResult:
    """Encapsulates the structured output of the compilation process."""

    def __init__(self):
        self.success: bool = False
        self.expression: str = ""
        self.tokens: List[Dict[str, Any]] = []
        self.ast: Optional[Dict[str, Any]] = None
        self.ast_tree_str: str = ""
        self.phases: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.symbol_table: List[Dict[str, Any]] = []
        self.used_variables: Dict[str, Dict[str, Any]] = {}
        self.inferred_type: Optional[str] = None
        self.evaluation: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "expression": self.expression,
            "tokens": self.tokens,
            "ast": self.ast,
            "ast_tree_str": self.ast_tree_str,
            "phases": self.phases,
            "errors": self.errors,
            "warnings": self.warnings,
            "symbol_table": self.symbol_table,
            "used_variables": self.used_variables,
            "inferred_type": self.inferred_type,
            "evaluation": self.evaluation,
        }


def compile_expression(
    expression: str,
    symbol_declarations: Optional[List[Dict[str, Any]]] = None,
    options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Main compilation function. Runs all compiler phases in sequence,
    recording phase statuses, errors, and timing information.
    """
    result = CompilationResult()
    result.expression = expression if expression is not None else ""
    opts = options or {}
    strict_mode = opts.get("strict_mode", True)
    enable_eval = opts.get("evaluate", True)

    # Setup Symbol Table
    sym_table = SymbolTable()
    if symbol_declarations:
        for item in symbol_declarations:
            name = item.get("name", "").strip()
            type_str = item.get("type", "number")
            val = item.get("value")
            if name:
                sym_table.declare(name, type_str, val)

    result.symbol_table = sym_table.to_list()

    # Phase 1: Input Validation
    t0 = time.perf_counter()
    if not result.expression.strip():
        result.phases.append({
            "name": "Input Validation",
            "status": "failed",
            "duration_ms": round((time.perf_counter() - t0) * 1000, 3),
            "details": "Expression string is empty",
        })
        result.errors.append({
            "category": "Input",
            "message": "Input expression is empty. Please enter a valid Boolean expression.",
            "line": 1,
            "column": 1,
            "suggestion": "Try an expression like 'a > b && c != d'",
        })
        return result.to_dict()

    result.phases.append({
        "name": "Input Validation",
        "status": "success",
        "duration_ms": round((time.perf_counter() - t0) * 1000, 3),
        "details": f"Length: {len(result.expression)} characters",
    })

    # Phase 2: Lexical Analysis
    t0 = time.perf_counter()
    lexer = Lexer(result.expression)
    raw_tokens: List[Token] = []
    try:
        raw_tokens = lexer.tokenize()
        result.tokens = [t.to_dict() for t in raw_tokens]
        result.phases.append({
            "name": "Lexical Analysis",
            "status": "success",
            "duration_ms": round((time.perf_counter() - t0) * 1000, 3),
            "details": f"Generated {len(raw_tokens)} tokens (including EOF)",
        })
    except LexicalError as le:
        result.tokens = [t.to_dict() for t in lexer.tokens]  # Retain tokens scanned before failure
        result.phases.append({
            "name": "Lexical Analysis",
            "status": "failed",
            "duration_ms": round((time.perf_counter() - t0) * 1000, 3),
            "details": le.message,
        })
        result.errors.append(le.to_dict())
        return result.to_dict()
    except Exception as e:
        result.phases.append({
            "name": "Lexical Analysis",
            "status": "failed",
            "duration_ms": round((time.perf_counter() - t0) * 1000, 3),
            "details": str(e),
        })
        result.errors.append({
            "category": "Lexical",
            "message": f"Unexpected lexical analyzer failure: {str(e)}",
            "line": 1,
            "column": 1,
        })
        return result.to_dict()

    # Phase 3: Syntax Analysis (Parsing & AST Construction)
    t0 = time.perf_counter()
    parser = Parser(raw_tokens)
    ast_root: Optional[ASTNode] = None
    try:
        ast_root = parser.parse()
        result.ast = ast_root.to_dict()
        result.ast_tree_str = render_ast_tree(ast_root)
        result.phases.append({
            "name": "Syntax Analysis",
            "status": "success",
            "duration_ms": round((time.perf_counter() - t0) * 1000, 3),
            "details": f"Constructed AST rooted at {type(ast_root).__name__}",
        })
    except ParseError as pe:
        result.phases.append({
            "name": "Syntax Analysis",
            "status": "failed",
            "duration_ms": round((time.perf_counter() - t0) * 1000, 3),
            "details": pe.message,
        })
        result.errors.append(pe.to_dict())
        return result.to_dict()
    except Exception as e:
        result.phases.append({
            "name": "Syntax Analysis",
            "status": "failed",
            "duration_ms": round((time.perf_counter() - t0) * 1000, 3),
            "details": str(e),
        })
        result.errors.append({
            "category": "Syntax",
            "message": f"Unexpected parser failure: {str(e)}",
            "line": 1,
            "column": 1,
        })
        return result.to_dict()

    # Phase 4: Semantic Analysis & Type Checking
    t0 = time.perf_counter()
    analyzer = SemanticAnalyzer(symbol_table=sym_table, strict_mode=strict_mode)
    try:
        root_type = analyzer.analyze(ast_root)
        result.inferred_type = root_type.value
        result.warnings = analyzer.warnings
        result.used_variables = analyzer.used_variables
        # Refresh AST dict and tree str with annotated types
        result.ast = ast_root.to_dict()
        result.ast_tree_str = render_ast_tree(ast_root)

        result.phases.append({
            "name": "Semantic Analysis",
            "status": "success",
            "duration_ms": round((time.perf_counter() - t0) * 1000, 3),
            "details": f"Type check passed. Expression evaluates to '{root_type.value}'. Mode: {'strict' if strict_mode else 'lenient'}",
        })
    except SemanticError as se:
        result.warnings = analyzer.warnings
        result.used_variables = analyzer.used_variables
        result.phases.append({
            "name": "Semantic Analysis",
            "status": "failed",
            "duration_ms": round((time.perf_counter() - t0) * 1000, 3),
            "details": se.message,
        })
        result.errors.append(se.to_dict())
        return result.to_dict()
    except Exception as e:
        result.phases.append({
            "name": "Semantic Analysis",
            "status": "failed",
            "duration_ms": round((time.perf_counter() - t0) * 1000, 3),
            "details": str(e),
        })
        result.errors.append({
            "category": "Semantic",
            "message": f"Unexpected semantic analyzer failure: {str(e)}",
            "line": 1,
            "column": 1,
        })
        return result.to_dict()

    # Phase 5: Optional Expression Evaluation
    if enable_eval:
        t0 = time.perf_counter()
        eval_result = analyzer.evaluate(ast_root)
        result.evaluation = eval_result
        result.phases.append({
            "name": "Expression Evaluation",
            "status": "success" if eval_result.get("computed") else "skipped",
            "duration_ms": round((time.perf_counter() - t0) * 1000, 3),
            "details": eval_result.get("message", "Evaluation completed"),
        })

    # Overall compilation success
    result.success = len(result.errors) == 0
    return result.to_dict()
