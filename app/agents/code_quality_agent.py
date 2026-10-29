"""Code Quality Analysis Agent.

Evaluates maintainability, complexity, naming conventions, docstrings,
unused imports, and error handling for Python and Java code.
"""

import ast
import re
from typing import Dict, List, Any
from ..services.code_parser import ParsedCode


class CodeQualityAgent:
    """Performs static code quality and maintainability inspections."""

    def analyze(self, parsed: ParsedCode) -> List[Dict[str, Any]]:
        findings = []

        # 1. Syntax Error Check
        if parsed.has_syntax_error and parsed.syntax_error_details:
            err = parsed.syntax_error_details
            findings.append({
                "finding_type": "quality",
                "rule_id": "QUAL-SYNTAX-01",
                "title": "Syntax Error Detected",
                "severity": "Critical",
                "line_number": err.get("line", 1),
                "code_snippet": err.get("text", "").strip() or "(line contains syntax error)",
                "explanation": f"The source code failed parsing with error: {err.get('message')}.",
                "why_it_matters": "Code containing syntax errors cannot execute or be reliably analyzed by automated security tools.",
                "remediation": "Correct the syntax error according to language grammar rules.",
                "remediated_code": "# Corrected syntax\n",
                "kb_reference": "Section 21: Code Smells and Maintainability",
                "cwe_id": "CWE-1078",
                "owasp_category": "Code Quality & Correctness"
            })
            # Return early if syntax error renders further AST analysis impossible
            if parsed.language == "python" and not parsed.ast_tree:
                return findings

        if parsed.language == "python":
            findings.extend(self._analyze_python(parsed))
        elif parsed.language == "java":
            findings.extend(self._analyze_java(parsed))

        # Common checks across all languages
        findings.extend(self._analyze_general(parsed))

        return findings

    def _analyze_python(self, parsed: ParsedCode) -> List[Dict[str, Any]]:
        findings = []
        lines = parsed.lines
        tree = parsed.ast_tree

        if not tree:
            return findings

        # A. Function Length & Complexity
        for fn in parsed.functions:
            name = fn["name"]
            length = fn.get("length", 1)
            complexity = fn.get("complexity", 1)
            line_no = fn["line"]
            fn_node = fn.get("node")

            if length > 35:
                snippet = lines[line_no - 1].strip() if line_no <= len(lines) else f"def {name}():"
                findings.append({
                    "finding_type": "quality",
                    "rule_id": "QUAL-LEN-01",
                    "title": f"Function '{name}' is excessively long ({length} lines)",
                    "severity": "Low",
                    "line_number": line_no,
                    "code_snippet": snippet,
                    "explanation": f"Function '{name}' spans {length} lines (recommended maximum is 35 lines).",
                    "why_it_matters": "Monolithic functions violate the Single Responsibility Principle and increase the likelihood of overlooking subtle security flaws.",
                    "remediation": f"Decompose '{name}' into smaller, focused helper functions with clear parameter boundaries.",
                    "remediated_code": f"# Decompose into focused functions\ndef {name}_helper():\n    pass",
                    "kb_reference": "Section 21: Code Smells and Maintainability",
                    "cwe_id": "CWE-1078",
                    "owasp_category": "Maintainability"
                })

            if complexity > 10:
                snippet = lines[line_no - 1].strip() if line_no <= len(lines) else f"def {name}():"
                findings.append({
                    "finding_type": "quality",
                    "rule_id": "QUAL-COMP-01",
                    "title": f"High Cyclomatic Complexity in '{name}' (Score: {complexity})",
                    "severity": "Medium",
                    "line_number": line_no,
                    "code_snippet": snippet,
                    "explanation": f"Function '{name}' has a cyclomatic complexity of {complexity} (threshold is 10).",
                    "why_it_matters": "High complexity implies numerous branching paths and nested conditions, making thorough testing and security auditing difficult.",
                    "remediation": "Simplify decision trees by extracting guard clauses, early returns, or strategy pattern handlers.",
                    "remediated_code": "# Use early return guard clauses\nif not precondition:\n    return False",
                    "kb_reference": "Section 21: Code Smells and Maintainability",
                    "cwe_id": "CWE-1078",
                    "owasp_category": "Maintainability"
                })

            # Check for non-snake_case function names
            if not re.match(r"^[a-z_][a-z0-9_]*$", name) and not name.startswith("__"):
                snippet = lines[line_no - 1].strip() if line_no <= len(lines) else f"def {name}():"
                clean_name = re.sub(r"([A-Z])", r"_\1", name).lower().strip("_")
                findings.append({
                    "finding_type": "quality",
                    "rule_id": "QUAL-NAME-01",
                    "title": f"Non-standard function name '{name}'",
                    "severity": "Low",
                    "line_number": line_no,
                    "code_snippet": snippet,
                    "explanation": f"Function name '{name}' does not follow Python PEP 8 snake_case conventions.",
                    "why_it_matters": "Consistent naming conventions improve codebase readability and lower maintenance overhead.",
                    "remediation": "Rename function to lowercase snake_case.",
                    "remediated_code": f"def {clean_name}():",
                    "kb_reference": "Section 21: Code Smells and Maintainability",
                    "cwe_id": "CWE-1078",
                    "owasp_category": "Code Quality"
                })

        # B. Unused Imports Detection
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                used_names.add(node.attr)

        for imp in parsed.imports:
            full_name = imp["name"]
            asname = imp.get("asname")
            target_name = asname if asname else full_name.split(".")[-1]
            line_no = imp["line"]

            # If target name never appears as a Name or Attribute elsewhere in the AST
            if target_name not in used_names and full_name not in ["__future__"]:
                # Check that it only occurs once in source code
                snippet = lines[line_no - 1].strip() if line_no <= len(lines) else f"import {full_name}"
                findings.append({
                    "finding_type": "quality",
                    "rule_id": "QUAL-IMP-01",
                    "title": f"Unused Import: '{target_name}'",
                    "severity": "Low",
                    "line_number": line_no,
                    "code_snippet": snippet,
                    "explanation": f"The module or symbol '{target_name}' is imported on line {line_no} but never referenced.",
                    "why_it_matters": "Unused imports clutter the namespace, slow module loading, and increase cognitive burden during security reviews.",
                    "remediation": f"Remove the unused import statement '{snippet}'.",
                    "remediated_code": "# Remove unused import",
                    "kb_reference": "Section 21: Code Smells and Maintainability",
                    "cwe_id": "CWE-1078",
                    "owasp_category": "Clean Architecture"
                })

        # C. Broad Exception Handling
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                line_no = node.lineno
                snippet = lines[line_no - 1].strip() if line_no <= len(lines) else "except:"
                if node.type is None:
                    findings.append({
                        "finding_type": "quality",
                        "rule_id": "QUAL-ERR-01",
                        "title": "Bare 'except:' Clause Detected",
                        "severity": "Medium",
                        "line_number": line_no,
                        "code_snippet": snippet,
                        "explanation": "A bare 'except:' catches all exceptions, including SystemExit, KeyboardInterrupt, and MemoryError.",
                        "why_it_matters": "Masking critical system signals and unhandled errors prevents graceful shutdown and obscures security-critical bugs.",
                        "remediation": "Catch specific exception types (e.g., except (ValueError, KeyError) as e:).",
                        "remediated_code": "except (ValueError, KeyError) as e:\n    logger.error('Expected error: %s', e)",
                        "kb_reference": "Section 17: Error Handling and Logging",
                        "cwe_id": "CWE-396",
                        "owasp_category": "Error Handling"
                    })
                elif isinstance(node.type, ast.Name) and node.type.id in ["Exception", "BaseException"]:
                    # Check if body is just pass
                    if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                        findings.append({
                            "finding_type": "quality",
                            "rule_id": "QUAL-ERR-02",
                            "title": "Silent Exception Swallowing ('except Exception: pass')",
                            "severity": "Medium",
                            "line_number": line_no,
                            "code_snippet": snippet,
                            "explanation": "Exceptions are captured and silently discarded with 'pass' without logging or handling.",
                            "why_it_matters": "Swallowing exceptions fails closed security checks and hides unauthorized access attempts or system crashes.",
                            "remediation": "Log the exception with appropriate contextual detail or re-raise.",
                            "remediated_code": "except Exception as e:\n    logger.warning('Operation failed: %s', e)\n    raise",
                            "kb_reference": "Section 17: Error Handling and Logging",
                            "cwe_id": "CWE-391",
                            "owasp_category": "Error Handling"
                        })

        return findings

    def _analyze_java(self, parsed: ParsedCode) -> List[Dict[str, Any]]:
        findings = []
        lines = parsed.lines

        # Check empty catch blocks in Java
        empty_catch_pattern = re.compile(r"catch\s*\([^)]+\)\s*\{\s*\}")
        for idx, line in enumerate(lines, start=1):
            if empty_catch_pattern.search(line):
                findings.append({
                    "finding_type": "quality",
                    "rule_id": "QUAL-JAVA-ERR-01",
                    "title": "Empty Catch Block in Java",
                    "severity": "Medium",
                    "line_number": idx,
                    "code_snippet": line.strip(),
                    "explanation": "The catch block suppresses exceptions without logging or re-throwing.",
                    "why_it_matters": "Ignoring exceptions in Java leads to corrupted system state and silently bypassed security policies.",
                    "remediation": "Log the caught exception using a logging framework like SLF4J/Logback.",
                    "remediated_code": "catch (Exception e) {\n    logger.error(\"Operation failed: {}\", e.getMessage(), e);\n}",
                    "kb_reference": "Section 17: Error Handling and Logging",
                    "cwe_id": "CWE-391",
                    "owasp_category": "Error Handling"
                })

        # Check high parameter counts in Java methods
        for fn in parsed.functions:
            if fn.get("args_count", 0) > 4:
                line_no = fn["line"]
                findings.append({
                    "finding_type": "quality",
                    "rule_id": "QUAL-JAVA-PARAM-01",
                    "title": f"Excessive Parameters in Method '{fn['name']}' ({fn['args_count']} parameters)",
                    "severity": "Low",
                    "line_number": line_no,
                    "code_snippet": lines[line_no - 1].strip() if line_no <= len(lines) else "",
                    "explanation": f"Method '{fn['name']}' takes {fn['args_count']} parameters (recommended maximum is 4).",
                    "why_it_matters": "Methods with many parameters are error-prone and encourage parameter transposition bugs.",
                    "remediation": "Introduce a Parameter Object or Builder pattern.",
                    "remediated_code": f"public void {fn['name']}({fn['name'].capitalize()}Context context) {{",
                    "kb_reference": "Section 21: Code Smells and Maintainability",
                    "cwe_id": "CWE-1078",
                    "owasp_category": "Code Quality"
                })

        return findings

    def _analyze_general(self, parsed: ParsedCode) -> List[Dict[str, Any]]:
        findings = []
        lines = parsed.lines

        # Deep nesting check (> 4 indent levels, i.e., 16 spaces or 4 tabs)
        for idx, line in enumerate(lines, start=1):
            stripped = line.lstrip()
            if not stripped or stripped.startswith(("#", "//", "/*", "*")):
                continue
            indent = len(line) - len(stripped)
            # Assuming 4 spaces per indent level
            if indent >= 20:  # 5+ levels of indentation
                findings.append({
                    "finding_type": "quality",
                    "rule_id": "QUAL-NEST-01",
                    "title": f"Deeply Nested Code Block (Indentation Level {indent // 4})",
                    "severity": "Low",
                    "line_number": idx,
                    "code_snippet": stripped[:80],
                    "explanation": f"Line {idx} has an indentation depth of {indent // 4} levels.",
                    "why_it_matters": "Deep nesting impairs human code comprehension and obscures edge-case security vulnerabilities.",
                    "remediation": "Refactor nested if/loop structures using guard clauses and early returns.",
                    "remediated_code": "// Use early exit guard clause\nif (!condition) return;",
                    "kb_reference": "Section 21: Code Smells and Maintainability",
                    "cwe_id": "CWE-1078",
                    "owasp_category": "Maintainability"
                })
                break  # Flag first occurrence to avoid alert fatigue

        return findings
