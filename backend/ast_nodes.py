"""
Abstract Syntax Tree (AST) Node definitions for Boolean Expressions.
Each node retains source line/column positions, operands, and inferred types.
Includes JSON serialization and tree visualization methods.
"""

from typing import Any, Dict, List, Optional, Union


# Human-friendly operator naming for AST visualization
OP_DISPLAY_NAMES = {
    ">": "GREATER_THAN",
    "<": "LESS_THAN",
    "==": "EQUAL_TO",
    "!=": "NOT_EQUAL",
    "&&": "AND",
    "||": "OR",
    "!": "NOT",
}


class ASTNode:
    """Base class for all Abstract Syntax Tree nodes."""

    def __init__(self, line: int, column: int):
        self.line = line
        self.column = column
        self.inferred_type: Optional[str] = None  # Populated during semantic analysis ("number", "boolean")

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to JSON-serializable dictionary."""
        raise NotImplementedError

    def to_tree_str(self, prefix: str = "", is_last: bool = True) -> str:
        """Render node as readable ASCII tree with connectors."""
        raise NotImplementedError

    def get_children(self) -> List["ASTNode"]:
        """Return list of child AST nodes."""
        return []


class NumberNode(ASTNode):
    """Represents a numeric literal (integer or float)."""

    def __init__(self, value: Union[int, float], line: int, column: int):
        super().__init__(line, column)
        self.value = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "NumberNode",
            "value": self.value,
            "line": self.line,
            "column": self.column,
            "inferred_type": self.inferred_type or "number",
        }

    def to_tree_str(self, prefix: str = "", is_last: bool = True) -> str:
        connector = "└── " if is_last else "├── "
        return f"{prefix}{connector}Number({self.value})\n"

    def __repr__(self) -> str:
        return f"NumberNode({self.value})"


class BooleanNode(ASTNode):
    """Represents a Boolean literal (true or false)."""

    def __init__(self, value: bool, line: int, column: int):
        super().__init__(line, column)
        self.value = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "BooleanNode",
            "value": self.value,
            "line": self.line,
            "column": self.column,
            "inferred_type": self.inferred_type or "boolean",
        }

    def to_tree_str(self, prefix: str = "", is_last: bool = True) -> str:
        connector = "└── " if is_last else "├── "
        return f"{prefix}{connector}Boolean({'true' if self.value else 'false'})\n"

    def __repr__(self) -> str:
        return f"BooleanNode({'true' if self.value else 'false'})"


class IdentifierNode(ASTNode):
    """Represents an identifier / variable."""

    def __init__(self, name: str, line: int, column: int):
        super().__init__(line, column)
        self.name = name

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "IdentifierNode",
            "name": self.name,
            "line": self.line,
            "column": self.column,
            "inferred_type": self.inferred_type,
        }

    def to_tree_str(self, prefix: str = "", is_last: bool = True) -> str:
        connector = "└── " if is_last else "├── "
        type_annot = f": {self.inferred_type}" if self.inferred_type else ""
        return f"{prefix}{connector}Identifier({self.name}{type_annot})\n"

    def __repr__(self) -> str:
        return f"IdentifierNode({self.name})"


class UnaryOpNode(ASTNode):
    """Represents a unary operator expression (e.g. !operand)."""

    def __init__(self, operator: str, operand: ASTNode, line: int, column: int):
        super().__init__(line, column)
        self.operator = operator
        self.operand = operand

    def get_children(self) -> List[ASTNode]:
        return [self.operand]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "UnaryOpNode",
            "operator": self.operator,
            "operator_name": OP_DISPLAY_NAMES.get(self.operator, self.operator),
            "line": self.line,
            "column": self.column,
            "inferred_type": self.inferred_type,
            "operand": self.operand.to_dict(),
        }

    def to_tree_str(self, prefix: str = "", is_last: bool = True, is_root: bool = False) -> str:
        op_name = OP_DISPLAY_NAMES.get(self.operator, self.operator)
        if is_root:
            res = f"{op_name}\n"
            child_prefix = ""
        else:
            connector = "└── " if is_last else "├── "
            res = f"{prefix}{connector}{op_name}\n"
            child_prefix = prefix + ("    " if is_last else "│   ")

        res += self.operand.to_tree_str(child_prefix, is_last=True)
        return res

    def __repr__(self) -> str:
        return f"UnaryOpNode({self.operator}, {self.operand})"


class BinaryOpNode(ASTNode):
    """Represents a binary operator expression (left op right)."""

    def __init__(self, operator: str, left: ASTNode, right: ASTNode, line: int, column: int):
        super().__init__(line, column)
        self.operator = operator
        self.left = left
        self.right = right

    def get_children(self) -> List[ASTNode]:
        return [self.left, self.right]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "BinaryOpNode",
            "operator": self.operator,
            "operator_name": OP_DISPLAY_NAMES.get(self.operator, self.operator),
            "line": self.line,
            "column": self.column,
            "inferred_type": self.inferred_type,
            "left": self.left.to_dict(),
            "right": self.right.to_dict(),
        }

    def to_tree_str(self, prefix: str = "", is_last: bool = True, is_root: bool = False) -> str:
        op_name = OP_DISPLAY_NAMES.get(self.operator, self.operator)
        if is_root:
            res = f"{op_name}\n"
            child_prefix = ""
        else:
            connector = "└── " if is_last else "├── "
            res = f"{prefix}{connector}{op_name}\n"
            child_prefix = prefix + ("    " if is_last else "│   ")

        res += self.left.to_tree_str(child_prefix, is_last=False)
        res += self.right.to_tree_str(child_prefix, is_last=True)
        return res

    def __repr__(self) -> str:
        return f"BinaryOpNode({self.left} {self.operator} {self.right})"


def render_ast_tree(node: ASTNode) -> str:
    """Render full AST tree from root node."""
    if isinstance(node, (BinaryOpNode, UnaryOpNode)):
        return node.to_tree_str(is_root=True).rstrip()
    elif isinstance(node, (NumberNode, BooleanNode, IdentifierNode)):
        # Single node tree
        return node.to_tree_str(is_last=True).lstrip("└── ").rstrip()
    return str(node)
