"""
Flask Web Application for Boolean Expression Compiler.
Serves modern web UI and REST API endpoints:
- GET  /            -> Frontend Web Application
- GET  /api/health  -> Health check and compiler status
- POST /api/compile -> Compiles expression and returns tokens, AST, semantics, phases, and evaluation
"""

import os
import sys
from flask import Flask, render_template, request, jsonify
from backend.compiler import compile_expression

app = Flask(__name__)


@app.route("/")
def index():
    """Serves the compiler interactive workbench."""
    return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health():
    """Returns backend system status and compiler capability metadata."""
    return jsonify({
        "status": "online",
        "service": "Boolean Expression Compiler",
        "version": "1.0.0",
        "python_version": sys.version.split()[0],
        "features": [
            "Lexical Analysis (Longest-match)",
            "Recursive-Descent Parsing (CFG)",
            "Dynamic AST Generation",
            "Static Semantic Type Checking",
            "Interactive Symbol Table",
            "Safe Expression Evaluation",
        ],
    })


@app.route("/api/compile", methods=["POST"])
def compile_api():
    """
    Compiles a Boolean expression submitted via JSON.
    Request body:
    {
        "expression": "a > b && c != d",
        "symbols": [
            {"name": "a", "type": "number", "value": 10},
            {"name": "b", "type": "number", "value": 5}
        ],
        "options": {
            "strict_mode": true,
            "evaluate": true
        }
    }
    """
    if not request.is_json:
        return jsonify({
            "success": False,
            "errors": [{
                "category": "API",
                "message": "Invalid request: Expected JSON body with Content-Type 'application/json'",
                "line": 1,
                "column": 1,
            }],
        }), 400

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({
            "success": False,
            "errors": [{
                "category": "API",
                "message": "Malformed JSON payload in request body",
                "line": 1,
                "column": 1,
            }],
        }), 400

    expression = data.get("expression", "")
    symbols = data.get("symbols", [])
    options = data.get("options", {})

    if not isinstance(symbols, list):
        symbols = []
    if not isinstance(options, dict):
        options = {}

    try:
        result = compile_expression(
            expression=expression,
            symbol_declarations=symbols,
            options=options,
        )
        return jsonify(result), 200
    except Exception as e:
        # Prevent stack trace leakage in production API
        return jsonify({
            "success": False,
            "expression": expression,
            "errors": [{
                "category": "Compiler",
                "message": f"Server processing error during compilation: {str(e)}",
                "line": 1,
                "column": 1,
            }],
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
