"""Analysis: Python Code Quality & AST Analyzer.

Analyzes Python source code using Python's native AST for structure,
complexity, code smells, naming conventions, and anti-patterns.
"""
import ast
import re
from typing import List, Dict, Any


class PythonASTVisitor(ast.NodeVisitor):
    """Traverses Python AST to identify code quality smells."""

    def __init__(self, filename: str, code_lines: List[str]):
        self.filename = filename
        self.code_lines = code_lines
        self.findings: List[Dict[str, Any]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # 1. Function Length
        func_start = node.lineno
        func_end = getattr(node, "end_lineno", func_start + len(node.body))
        func_length = func_end - func_start + 1

        if func_length > 35:
            self.findings.append({
                "finding_type": "QUALITY",
                "title": f"Overly Long Function '{node.name}' ({func_length} lines)",
                "category": "Code Structure & Modularity",
                "severity": "MEDIUM",
                "heuristic_score": 5.2,
                "line_number": node.lineno,
                "filename": self.filename,
                "description": (
                    f"Function '{node.name}' contains {func_length} lines, which exceeds "
                    "the recommended maximum of 35 lines. Long functions often violate SRP."
                ),
                "risk_explanation": "Increases cognitive complexity and makes unit testing harder.",
                "evidence_snippet": f"def {node.name}(...):  # {func_start}-{func_end}",
                "remediation_recommendation": (
                    "Decompose this function into smaller, cohesive helper functions."
                ),
                "is_confirmed_pattern": True,
            })

        # 2. Function Naming (PEP 8 snake_case)
        if not re.match(r"^_{0,2}[a-z][a-z0-9_]*_{0,2}$", node.name) and not (node.name.startswith("__") and node.name.endswith("__")):
            self.findings.append({
                "finding_type": "QUALITY",
                "title": f"Non-Standard Function Naming '{node.name}'",
                "category": "PEP 8 Style & Conventions",
                "severity": "LOW",
                "heuristic_score": 2.5,
                "line_number": node.lineno,
                "filename": self.filename,
                "description": f"Function '{node.name}' does not follow Python's PEP 8 snake_case convention.",
                "risk_explanation": "Inconsistent naming harms readability and team collaboration.",
                "evidence_snippet": f"def {node.name}(...):",
                "remediation_recommendation": f"Rename '{node.name}' using snake_case style.",
                "is_confirmed_pattern": True,
            })

        # 3. Mutable Default Arguments
        for default in node.args.defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self.findings.append({
                    "finding_type": "QUALITY",
                    "title": f"Mutable Default Argument in '{node.name}'",
                    "category": "Python Anti-Patterns",
                    "severity": "HIGH",
                    "heuristic_score": 7.5,
                    "line_number": default.lineno if hasattr(default, "lineno") else node.lineno,
                    "filename": self.filename,
                    "description": (
                        f"Function '{node.name}' uses a mutable default argument. "
                        "Python mutable defaults are bound once at function definition time "
                        "and shared across subsequent calls."
                    ),
                    "risk_explanation": "Leads to state bleeding bugs across independent invocations.",
                    "evidence_snippet": f"def {node.name}(..., param=[...]):",
                    "remediation_recommendation": "Use None as the default argument and initialize inside the function body.",
                    "is_confirmed_pattern": True,
                })

        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        # Bare except:
        if node.type is None:
            self.findings.append({
                "finding_type": "QUALITY",
                "title": "Bare 'except:' Clause Detected",
                "category": "Error Handling Best Practices",
                "severity": "HIGH",
                "heuristic_score": 7.0,
                "line_number": node.lineno,
                "filename": self.filename,
                "description": (
                    "A bare 'except:' clause catches all exceptions, including SystemExit, "
                    "KeyboardInterrupt, and MemoryError, masking critical runtime errors."
                ),
                "risk_explanation": "Prevents normal termination and obscures debugging stack traces.",
                "evidence_snippet": "except:  # catches BaseException",
                "remediation_recommendation": "Catch specific exceptions like Exception or ValueError.",
                "is_confirmed_pattern": True,
            })
        self.generic_visit(node)


class PythonAnalyzer:
    """Performs static code quality analysis on Python code."""

    def analyze(self, code: str, filename: str = "main.py") -> List[Dict[str, Any]]:
        findings = []
        lines = code.splitlines()

        # AST visitor
        try:
            tree = ast.parse(code)
            visitor = PythonASTVisitor(filename, lines)
            visitor.visit(tree)
            findings.extend(visitor.findings)
        except Exception:
            pass

        return findings
