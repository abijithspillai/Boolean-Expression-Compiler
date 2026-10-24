"""
Semantic Analyzer and Symbol Table for Boolean Expressions.
Enforces static type-checking rules:
- '>' and '<' require numeric operands.
- '==' and '!=' require type-compatible operands (number vs number, or boolean vs boolean).
- '&&', '||', and '!' require boolean operands.
- Identifiers are verified against the Symbol Table.
- Optional evaluation evaluates expression if sample values are available.
"""

from typing import Dict, Any, Optional, List, Union
from enum import Enum
from .ast_nodes import (
    ASTNode,
    NumberNode,
    BooleanNode,
    IdentifierNode,
    UnaryOpNode,
    BinaryOpNode,
)


class Type(Enum):
    NUMBER = "number"
    BOOLEAN = "boolean"
    UNKNOWN = "unknown"


class Symbol:
    """Represents a symbol table entry with name, type, and optional value."""

    def __init__(self, name: str, type_: Type, value: Optional[Any] = None):
        self.name = name
        self.type = type_
        self.value = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type.value,
            "value": self.value,
        }


class SymbolTable:
    """Stores declared variables and their associated types and values."""

    def __init__(self):
        self._symbols: Dict[str, Symbol] = {}

    def declare(self, name: str, type_: Union[Type, str], value: Optional[Any] = None) -> None:
        if isinstance(type_, str):
            t_str = type_.lower().strip()
            if t_str in ("number", "int", "float", "double"):
                resolved_type = Type.NUMBER
            elif t_str in ("boolean", "bool"):
                resolved_type = Type.BOOLEAN
            else:
                resolved_type = Type.UNKNOWN
        else:
            resolved_type = type_

        # Sanitize/cast value if provided
        sanitized_value = None
        if value is not None and value != "":
            if resolved_type == Type.NUMBER:
                try:
                    sanitized_value = float(value) if "." in str(value) else int(value)
                except (ValueError, TypeError):
                    sanitized_value = None
            elif resolved_type == Type.BOOLEAN:
                if isinstance(value, bool):
                    sanitized_value = value
                elif str(value).lower() in ("true", "1", "yes"):
                    sanitized_value = True
                elif str(value).lower() in ("false", "0", "no"):
                    sanitized_value = False

        self._symbols[name] = Symbol(name, resolved_type, sanitized_value)

    def lookup(self, name: str) -> Optional[Symbol]:
        return self._symbols.get(name)

    def contains(self, name: str) -> bool:
        return name in self._symbols

    def to_dict(self) -> Dict[str, Any]:
        return {name: sym.to_dict() for name, sym in self._symbols.items()}

    def to_list(self) -> List[Dict[str, Any]]:
        return [sym.to_dict() for sym in self._symbols.values()]


class SemanticError(Exception):
    """Exception raised for semantic and type-checking errors."""

    def __init__(
        self,
        message: str,
        line: int,
        column: int,
        node: Optional[ASTNode] = None,
        suggestion: Optional[str] = None,
    ):
        super().__init__(f"Semantic Error at line {line}, column {column}: {message}")
        self.message = message
        self.line = line
        self.column = column
        self.node = node
        self.suggestion = suggestion

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": "Semantic",
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "suggestion": self.suggestion,
        }


class SemanticAnalyzer:
    """
    Performs type checking, symbol resolution, and expression evaluation.
    """

    def __init__(self, symbol_table: Optional[SymbolTable] = None, strict_mode: bool = True):
        self.symbol_table = symbol_table or SymbolTable()
        self.strict_mode = strict_mode
        self.errors: List[SemanticError] = []
        self.warnings: List[Dict[str, Any]] = []
        self.used_variables: Dict[str, Dict[str, Any]] = {}

    def analyze(self, ast: ASTNode) -> Type:
        """
        Traverses the AST, annotating nodes with inferred types and enforcing type rules.
        Returns the root expression's type.
        """
        self.errors.clear()
        self.warnings.clear()
        self.used_variables.clear()

        root_type = self._check_node(ast)
        return root_type

    def _check_node(self, node: ASTNode) -> Type:
        if isinstance(node, NumberNode):
            node.inferred_type = Type.NUMBER.value
            return Type.NUMBER

        if isinstance(node, BooleanNode):
            node.inferred_type = Type.BOOLEAN.value
            return Type.BOOLEAN

        if isinstance(node, IdentifierNode):
            sym = self.symbol_table.lookup(node.name)
            if sym is not None:
                node.inferred_type = sym.type.value
                self.used_variables[node.name] = {
                    "name": node.name,
                    "declared_type": sym.type.value,
                    "value": sym.value,
                    "status": "declared",
                }
                return sym.type
            else:
                if self.strict_mode:
                    raise SemanticError(
                        f"Undeclared identifier '{node.name}'. Variable must be declared in the symbol table before use.",
                        node.line,
                        node.column,
                        node=node,
                        suggestion=f"Declare '{node.name}' in the Symbol Table with type 'number' or 'boolean'",
                    )
                else:
                    self.warnings.append({
                        "message": f"Undeclared variable '{node.name}' used without explicit declaration (mode: lenient)",
                        "line": node.line,
                        "column": node.column,
                        "variable": node.name,
                    })
                    node.inferred_type = Type.UNKNOWN.value
                    self.used_variables[node.name] = {
                        "name": node.name,
                        "declared_type": "unknown",
                        "value": None,
                        "status": "undeclared",
                    }
                    return Type.UNKNOWN

        if isinstance(node, UnaryOpNode):
            if node.operator == "!":
                operand_type = self._check_node(node.operand)
                if operand_type == Type.NUMBER:
                    raise SemanticError(
                        f"Type mismatch: Operator '!' cannot be applied to numeric operand of type '{operand_type.value}'. Expected 'boolean'.",
                        node.line,
                        node.column,
                        node=node,
                        suggestion="Logical NOT '!' only operates on boolean values or boolean comparisons",
                    )
                node.inferred_type = Type.BOOLEAN.value
                return Type.BOOLEAN

        if isinstance(node, BinaryOpNode):
            left_type = self._check_node(node.left)
            right_type = self._check_node(node.right)

            # Relational operators: >, <
            if node.operator in (">", "<"):
                if left_type != Type.NUMBER or right_type != Type.NUMBER:
                    raise SemanticError(
                        f"Type mismatch: Relational operator '{node.operator}' requires numeric operands, but received '{left_type.value}' and '{right_type.value}'.",
                        node.line,
                        node.column,
                        node=node,
                        suggestion=f"Ensure both sides of '{node.operator}' are numbers or number variables",
                    )
                node.inferred_type = Type.BOOLEAN.value
                return Type.BOOLEAN

            # Equality operators: ==, !=
            if node.operator in ("==", "!="):
                # Compatible only if both are numbers or both are booleans
                if left_type != right_type and left_type != Type.UNKNOWN and right_type != Type.UNKNOWN:
                    raise SemanticError(
                        f"Type mismatch: Cannot compare incompatible types '{left_type.value}' and '{right_type.value}' using '{node.operator}'.",
                        node.line,
                        node.column,
                        node=node,
                        suggestion=f"Both operands of '{node.operator}' must be of the same type (both 'number' or both 'boolean')",
                    )
                node.inferred_type = Type.BOOLEAN.value
                return Type.BOOLEAN

            # Logical operators: &&, ||
            if node.operator in ("&&", "||"):
                if left_type != Type.BOOLEAN or right_type != Type.BOOLEAN:
                    raise SemanticError(
                        f"Type mismatch: Logical operator '{node.operator}' requires boolean operands, but received '{left_type.value}' and '{right_type.value}'.",
                        node.line,
                        node.column,
                        node=node,
                        suggestion=f"Ensure both operands of '{node.operator}' are boolean expressions (e.g. comparisons) or boolean variables",
                    )
                node.inferred_type = Type.BOOLEAN.value
                return Type.BOOLEAN

        # Fallback
        node.inferred_type = Type.UNKNOWN.value
        return Type.UNKNOWN

    def evaluate(self, node: ASTNode) -> Dict[str, Any]:
        """
        Safely evaluates AST using sample values in the symbol table.
        Does not use eval() or exec().
        """
        # First verify if all referenced variables have assigned sample values
        missing_values = []
        for var_name, var_info in self.used_variables.items():
            sym = self.symbol_table.lookup(var_name)
            if sym is None or sym.value is None:
                missing_values.append(var_name)

        if missing_values:
            return {
                "computed": False,
                "result": None,
                "status": "Missing Sample Values",
                "message": f"Cannot evaluate: sample values are missing for variables: {', '.join(missing_values)}. Assign sample values in the Symbol Table to evaluate.",
                "missing_variables": missing_values,
            }

        try:
            val = self._eval_node(node)
            return {
                "computed": True,
                "result": val,
                "result_str": "true" if val is True else ("false" if val is False else str(val)),
                "status": "Evaluated Successfully",
                "message": f"Expression evaluated to: {'true' if val is True else ('false' if val is False else str(val))}",
            }
        except Exception as e:
            return {
                "computed": False,
                "result": None,
                "status": "Evaluation Error",
                "message": str(e),
            }

    def _eval_node(self, node: ASTNode) -> Any:
        if isinstance(node, NumberNode):
            return node.value

        if isinstance(node, BooleanNode):
            return node.value

        if isinstance(node, IdentifierNode):
            sym = self.symbol_table.lookup(node.name)
            if sym is None or sym.value is None:
                raise ValueError(f"Variable '{node.name}' has no value assigned.")
            return sym.value

        if isinstance(node, UnaryOpNode):
            if node.operator == "!":
                sub_val = self._eval_node(node.operand)
                if not isinstance(sub_val, bool):
                    raise ValueError(f"Cannot apply '!' to non-boolean value '{sub_val}'")
                return not sub_val

        if isinstance(node, BinaryOpNode):
            left_val = self._eval_node(node.left)
            right_val = self._eval_node(node.right)

            if node.operator == ">":
                return left_val > right_val
            elif node.operator == "<":
                return left_val < right_val
            elif node.operator == "==":
                return left_val == right_val
            elif node.operator == "!=":
                return left_val != right_val
            elif node.operator == "&&":
                return bool(left_val and right_val)
            elif node.operator == "||":
                return bool(left_val or right_val)

        raise ValueError(f"Unsupported node type during evaluation: {type(node)}")
