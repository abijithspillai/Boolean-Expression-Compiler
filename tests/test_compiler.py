"""
Comprehensive Automated Test Suite for Boolean Expression Compiler.
Includes:
- 10+ Valid syntax expressions
- 10+ Invalid syntax expressions
- Lexical error cases
- Semantic error cases (type mismatches, undeclared variables)
- Precedence & Associativity verification
- Safe AST Expression Evaluation verification
"""

import unittest
from backend.lexer import Lexer, TokenType, LexicalError
from backend.parser import Parser, ParseError
from backend.ast_nodes import BinaryOpNode, UnaryOpNode, NumberNode, IdentifierNode, BooleanNode
from backend.semantic_analyzer import SemanticAnalyzer, SemanticError, SymbolTable, Type
from backend.compiler import compile_expression


class TestLexer(unittest.TestCase):
    """Test tokenization, longest-match recognition, and lexical errors."""

    def test_basic_token_stream(self):
        lexer = Lexer("a > 10 && isValid == true")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens]
        self.assertEqual(types, [
            TokenType.IDENTIFIER,
            TokenType.GT,
            TokenType.NUMBER,
            TokenType.AND,
            TokenType.IDENTIFIER,
            TokenType.EQ,
            TokenType.BOOLEAN,
            TokenType.EOF,
        ])
        self.assertEqual(tokens[2].value, 10)
        self.assertEqual(tokens[6].value, True)

    def test_longest_match_operators(self):
        # == vs =, != vs !, && vs &, || vs |
        lexer = Lexer("== != && || ! > <")
        tokens = lexer.tokenize()
        types = [t.type for t in tokens[:-1]]
        self.assertEqual(types, [
            TokenType.EQ,
            TokenType.NEQ,
            TokenType.AND,
            TokenType.OR,
            TokenType.NOT,
            TokenType.GT,
            TokenType.LT,
        ])

    def test_single_ampersand_rejected(self):
        lexer = Lexer("a & b")
        with self.assertRaises(LexicalError) as ctx:
            lexer.tokenize()
        self.assertIn("Single '&' is not supported", ctx.exception.message)

    def test_single_pipe_rejected(self):
        lexer = Lexer("a | b")
        with self.assertRaises(LexicalError) as ctx:
            lexer.tokenize()
        self.assertIn("Single '|' is not supported", ctx.exception.message)

    def test_single_equal_rejected(self):
        lexer = Lexer("a = b")
        with self.assertRaises(LexicalError) as ctx:
            lexer.tokenize()
        self.assertIn("Single '=' is assignment", ctx.exception.message)

    def test_decimal_numbers(self):
        lexer = Lexer("3.14 0.5 42")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].value, 3.14)
        self.assertEqual(tokens[1].value, 0.5)
        self.assertEqual(tokens[2].value, 42)

    def test_malformed_number_multiple_dots(self):
        lexer = Lexer("10.20.30")
        with self.assertRaises(LexicalError):
            lexer.tokenize()

    def test_unsupported_character(self):
        lexer = Lexer("a @ b")
        with self.assertRaises(LexicalError) as ctx:
            lexer.tokenize()
        self.assertIn("Unexpected character '@'", ctx.exception.message)


class TestValidSyntax(unittest.TestCase):
    """Test 10+ required valid syntax expressions."""

    def setUp(self):
        # Standard test symbols
        self.symbols = [
            {"name": "a", "type": "number", "value": 15},
            {"name": "b", "type": "number", "value": 10},
            {"name": "c", "type": "number", "value": 20},
            {"name": "d", "type": "number", "value": 30},
            {"name": "x1", "type": "number", "value": 50},
            {"name": "isValid", "type": "boolean", "value": True},
        ]

    def _assert_valid(self, expr: str):
        res = compile_expression(expr, self.symbols)
        self.assertTrue(res["success"], f"Expected valid syntax for '{expr}', got errors: {res['errors']}")
        self.assertIsNotNone(res["ast"])
        self.assertEqual(len(res["errors"]), 0)

    # 10 Required Valid Cases
    def test_valid_01_greater_than(self):
        self._assert_valid("a > b")

    def test_valid_02_less_than(self):
        self._assert_valid("a < b")

    def test_valid_03_equal_to(self):
        self._assert_valid("a == b")

    def test_valid_04_not_equal_to(self):
        self._assert_valid("a != b")

    def test_valid_05_and_expression(self):
        self._assert_valid("a > b && c < d")

    def test_valid_06_or_expression(self):
        self._assert_valid("a > b || c < d")

    def test_valid_07_unary_not_identifier(self):
        self._assert_valid("!isValid")

    def test_valid_08_unary_not_parentheses(self):
        self._assert_valid("!(a > b)")

    def test_valid_09_grouped_and_expressions(self):
        self._assert_valid("(a > b) && (c != d)")

    def test_valid_10_mixed_precedence(self):
        self._assert_valid("a > b || c < d && !isValid")

    # Additional Valid Cases
    def test_valid_11_bounded_range(self):
        self._assert_valid("(x1 > 10) && (x1 < 100)")

    def test_valid_12_nested_parentheses(self):
        self._assert_valid("!((a > b) || ((c < d) && isValid))")

    def test_valid_13_boolean_literals(self):
        self._assert_valid("true && false || (a > 5)")


class TestInvalidSyntax(unittest.TestCase):
    """Test 10+ required invalid syntax expressions."""

    def _assert_invalid_syntax(self, expr: str):
        res = compile_expression(expr)
        self.assertFalse(res["success"], f"Expected expression '{expr}' to fail syntax check")
        has_syntax_or_lex_error = any(e["category"] in ("Syntax", "Lexical", "Input") for e in res["errors"])
        self.assertTrue(has_syntax_or_lex_error, f"Expected Syntax or Lexical error in {res['errors']}")

    # 10 Required Invalid Cases
    def test_invalid_01_trailing_operator(self):
        self._assert_invalid_syntax("a >")

    def test_invalid_02_leading_and(self):
        self._assert_invalid_syntax("&& a")

    def test_invalid_03_double_and(self):
        self._assert_invalid_syntax("a && && b")

    def test_invalid_04_unclosed_parenthesis(self):
        self._assert_invalid_syntax("(a > b")

    def test_invalid_05_unmatched_closing_parenthesis(self):
        self._assert_invalid_syntax("a > b)")

    def test_invalid_06_missing_operator(self):
        self._assert_invalid_syntax("a b")

    def test_invalid_07_consecutive_comparison_operators(self):
        self._assert_invalid_syntax("a < < b")

    def test_invalid_08_dangling_not(self):
        self._assert_invalid_syntax("!")

    def test_invalid_09_single_ampersand(self):
        self._assert_invalid_syntax("a & b")

    def test_invalid_10_trailing_or(self):
        self._assert_invalid_syntax("a > b ||")

    # Additional Invalid Cases
    def test_invalid_11_chained_comparisons(self):
        # Must explicitly reject a < b < c
        res = compile_expression("a < b < c")
        self.assertFalse(res["success"])
        self.assertTrue(any("Chained comparisons" in e["message"] for e in res["errors"]))

    def test_invalid_12_empty_expression(self):
        res = compile_expression("   ")
        self.assertFalse(res["success"])
        self.assertEqual(res["errors"][0]["category"], "Input")


class TestSemanticAnalysis(unittest.TestCase):
    """Test type checking, symbol resolution, and semantic error reporting."""

    def setUp(self):
        self.symbols = [
            {"name": "numA", "type": "number", "value": 10},
            {"name": "numB", "type": "number", "value": 20},
            {"name": "flagA", "type": "boolean", "value": True},
            {"name": "flagB", "type": "boolean", "value": False},
        ]

    def test_number_with_logical_and(self):
        # 10 && flagA should fail semantic check
        res = compile_expression("numA && flagA", self.symbols)
        self.assertFalse(res["success"])
        self.assertTrue(any(e["category"] == "Semantic" and "requires boolean operands" in e["message"] for e in res["errors"]))

    def test_not_applied_to_number(self):
        # !numA should fail semantic check
        res = compile_expression("!numA", self.symbols)
        self.assertFalse(res["success"])
        self.assertTrue(any(e["category"] == "Semantic" and "cannot be applied to numeric operand" in e["message"] for e in res["errors"]))

    def test_incompatible_comparison_equality(self):
        # numA == flagA should fail
        res = compile_expression("numA == flagA", self.symbols)
        self.assertFalse(res["success"])
        self.assertTrue(any(e["category"] == "Semantic" and "Cannot compare incompatible types" in e["message"] for e in res["errors"]))

    def test_relational_with_boolean(self):
        # flagA > 5 should fail
        res = compile_expression("flagA > 5", self.symbols)
        self.assertFalse(res["success"])
        self.assertTrue(any(e["category"] == "Semantic" and "requires numeric operands" in e["message"] for e in res["errors"]))

    def test_undeclared_variable_strict_mode(self):
        res = compile_expression("undeclaredVar > 10", self.symbols, options={"strict_mode": True})
        self.assertFalse(res["success"])
        self.assertTrue(any(e["category"] == "Semantic" and "Undeclared identifier" in e["message"] for e in res["errors"]))

    def test_undeclared_variable_lenient_mode(self):
        res = compile_expression("undeclaredVar > 10", self.symbols, options={"strict_mode": False})
        # In lenient mode, warning is generated instead of stopping
        self.assertTrue(len(res["warnings"]) > 0)
        self.assertIn("undeclaredVar", res["warnings"][0]["message"])


class TestPrecedenceAndEvaluation(unittest.TestCase):
    """Verify operator precedence and safe expression evaluation."""

    def test_precedence_and_over_or(self):
        # a || b && c should parse as: a || (b && c)
        # With a=false, b=true, c=false => false || (true && false) => false
        symbols = [
            {"name": "a", "type": "boolean", "value": False},
            {"name": "b", "type": "boolean", "value": True},
            {"name": "c", "type": "boolean", "value": False},
        ]
        res = compile_expression("a || b && c", symbols)
        self.assertTrue(res["success"])
        self.assertFalse(res["evaluation"]["result"])
        # Check AST root is OR, and right child is AND
        self.assertEqual(res["ast"]["operator"], "||")
        self.assertEqual(res["ast"]["right"]["operator"], "&&")

    def test_precedence_not_over_and(self):
        # !a && b should parse as (!a) && b
        symbols = [
            {"name": "a", "type": "boolean", "value": True},
            {"name": "b", "type": "boolean", "value": True},
        ]
        res = compile_expression("!a && b", symbols)
        self.assertTrue(res["success"])
        # (!true) && true => false && true => false
        self.assertFalse(res["evaluation"]["result"])
        self.assertEqual(res["ast"]["operator"], "&&")
        self.assertEqual(res["ast"]["left"]["node_type"], "UnaryOpNode")

    def test_precedence_comparison_over_and(self):
        # 10 > 5 && 20 < 30 => (10 > 5) && (20 < 30) => true && true => true
        res = compile_expression("10 > 5 && 20 < 30")
        self.assertTrue(res["success"])
        self.assertTrue(res["evaluation"]["result"])
        self.assertEqual(res["ast"]["operator"], "&&")
        self.assertEqual(res["ast"]["left"]["operator"], ">")
        self.assertEqual(res["ast"]["right"]["operator"], "<")

    def test_evaluation_missing_sample_value(self):
        # Symbol declared but value is None
        symbols = [
            {"name": "x", "type": "number", "value": None},
        ]
        res = compile_expression("x > 10", symbols)
        self.assertTrue(res["success"])
        # Should gracefully skip evaluation
        self.assertFalse(res["evaluation"]["computed"])
        self.assertIn("missing", res["evaluation"]["status"].lower())


if __name__ == "__main__":
    unittest.main()
