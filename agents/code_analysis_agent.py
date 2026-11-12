"""Agent 1: Code Analysis Agent.

Performs static code quality, structural, and maintainability analysis
for Python (using Python's native AST) and Java (using static structural tokenizer).
Identifies code smells, complexity issues, naming violations, anti-patterns,
and excessive nesting.
"""
import ast
import re
from typing import List, Dict, Any, Optional
from utils.severity_scoring import calculate_finding_score


class PythonASTQualityVisitor(ast.NodeVisitor):
    """AST Visitor that traverses Python code to detect code quality issues."""

    def __init__(self, filename: str, code_lines: List[str]):
        self.filename = filename
        self.code_lines = code_lines
        self.findings: List[Dict[str, Any]] = []
        self._current_nesting = 0
        self._defined_names = set()
        self._used_names = set()
        self._imported_modules = {}

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # 1. Check Function Length
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
                    "the recommended maximum of 35 lines. Long functions often violate "
                    "the Single Responsibility Principle."
                ),
                "risk_explanation": (
                    "Overly long functions increase cognitive complexity, make testing harder, "
                    "and often hide bugs or security vulnerabilities."
                ),
                "evidence_snippet": f"def {node.name}(...):  # spans lines {func_start}-{func_end}",
                "remediation_recommendation": (
                    "Decompose this function into smaller, cohesive helper functions that "
                    "each accomplish a single distinct task."
                ),
                "suggested_improvement": (
                    "Extract logical sub-steps (e.g. input validation, processing, and output formatting) "
                    "into private helper functions."
                ),
                "corrected_code": (
                    f"def {node.name}(...):\n"
                    "    # Refactored: Delegating responsibilities to concise helper methods\n"
                    "    data = _validate_and_parse_input(...)\n"
                    "    result = _process_core_logic(data)\n"
                    "    return _format_response(result)"
                ),
                "is_confirmed_pattern": True,
            })

        # 2. Check Naming Convention (Python functions should be snake_case)
        if not re.match(r"^_{0,2}[a-z][a-z0-9_]*_{0,2}$", node.name) and not (node.name.startswith("__") and node.name.endswith("__")):
            self.findings.append({
                "finding_type": "QUALITY",
                "title": f"Non-Standard Function Naming '{node.name}'",
                "category": "PEP 8 Style & Conventions",
                "severity": "LOW",
                "heuristic_score": 2.5,
                "line_number": node.lineno,
                "filename": self.filename,
                "description": (
                    f"Function '{node.name}' does not follow Python's PEP 8 snake_case "
                    "naming convention."
                ),
                "risk_explanation": "Inconsistent naming harms codebase readability and maintainability.",
                "evidence_snippet": f"def {node.name}(...):",
                "remediation_recommendation": f"Rename '{node.name}' using snake_case style.",
                "suggested_improvement": "Use lower_case_with_underscores for function and method names.",
                "corrected_code": f"def {self._to_snake_case(node.name)}(...):\n    pass",
                "is_confirmed_pattern": True,
            })

        # 3. Check Mutable Default Arguments
        for default in node.args.defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                type_name = type(default).__name__.lower()
                self.findings.append({
                    "finding_type": "QUALITY",
                    "title": f"Mutable Default Argument in '{node.name}'",
                    "category": "Python Anti-Patterns",
                    "severity": "HIGH",
                    "heuristic_score": 7.5,
                    "line_number": default.lineno,
                    "filename": self.filename,
                    "description": (
                        f"Function '{node.name}' uses a mutable {type_name} as a default argument. "
                        "Python default arguments are evaluated once at function definition time, "
                        "meaning modifications will persist across calls."
                    ),
                    "risk_explanation": (
                        "Leads to state pollution bugs and data leaks between different user invocations."
                    ),
                    "evidence_snippet": f"def {node.name}(..., param={ast.unparse(default) if hasattr(ast, 'unparse') else '[]'}):",
                    "remediation_recommendation": (
                        "Use None as the default value and initialize the mutable structure inside the body."
                    ),
                    "suggested_improvement": "def func(param=None):\n    if param is None:\n        param = []",
                    "corrected_code": (
                        f"def {node.name}(param=None):\n"
                        "    if param is None:\n"
                        "        param = []\n"
                        "    # proceed safely..."
                    ),
                    "is_confirmed_pattern": True,
                })

        # 4. Cyclomatic Complexity Heuristic
        complexity = 1
        for subnode in ast.walk(node):
            if isinstance(subnode, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.With)):
                complexity += 1
            elif isinstance(subnode, ast.BoolOp):
                complexity += len(subnode.values) - 1

        if complexity > 8:
            self.findings.append({
                "finding_type": "QUALITY",
                "title": f"High Cyclomatic Complexity ({complexity}) in '{node.name}'",
                "category": "Code Complexity",
                "severity": "HIGH" if complexity > 14 else "MEDIUM",
                "heuristic_score": 7.8 if complexity > 14 else 6.2,
                "line_number": node.lineno,
                "filename": self.filename,
                "description": (
                    f"Function '{node.name}' has a cyclomatic complexity of {complexity} "
                    "(recommended limit is <= 8)."
                ),
                "risk_explanation": (
                    "Functions with excessive execution paths are difficult to reason about, "
                    "prone to corner-case bugs, and difficult to test comprehensively."
                ),
                "evidence_snippet": f"def {node.name}(...):  # Complexity = {complexity}",
                "remediation_recommendation": (
                    "Simplify control flow using guard clauses, early returns, polymorphism, "
                    "or dictionary dispatch tables."
                ),
                "suggested_improvement": "Break nested conditionals into separate methods with early returns.",
                "corrected_code": (
                    f"def {node.name}(condition_a, condition_b):\n"
                    "    # Guard clause simplification\n"
                    "    if not condition_a:\n"
                    "        return None\n"
                    "    if not condition_b:\n"
                    "        return False\n"
                    "    return True"
                ),
                "is_confirmed_pattern": True,
            })

        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        # Detect wildcard imports
        for alias in node.names:
            if alias.name == "*":
                self.findings.append({
                    "finding_type": "QUALITY",
                    "title": f"Wildcard Import 'from {node.module} import *'",
                    "category": "Code Maintainability",
                    "severity": "LOW",
                    "heuristic_score": 3.0,
                    "line_number": node.lineno,
                    "filename": self.filename,
                    "description": (
                        f"Wildcard import 'from {node.module} import *' pollutes the global namespace "
                        "and masks the origin of variables and functions."
                    ),
                    "risk_explanation": (
                        "Namespace pollution can lead to accidental shadowing of built-ins and "
                        "unpredictable bugs."
                    ),
                    "evidence_snippet": f"from {node.module} import *",
                    "remediation_recommendation": "Explicitly import only the specific classes or functions needed.",
                    "suggested_improvement": f"from {node.module} import SpecificClass, specific_function",
                    "corrected_code": f"from {node.module} import SpecificClass, specific_function",
                    "is_confirmed_pattern": True,
                })
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        # Bare except: detection
        if node.type is None:
            self.findings.append({
                "finding_type": "QUALITY",
                "title": "Bare 'except:' Clause Detected",
                "category": "Exception Handling",
                "severity": "MEDIUM",
                "heuristic_score": 5.8,
                "line_number": node.lineno,
                "filename": self.filename,
                "description": (
                    "A bare 'except:' clause catches all exceptions, including KeyboardInterrupt, "
                    "SystemExit, and MemoryError, preventing normal termination."
                ),
                "risk_explanation": (
                    "Suppresses critical operational failures and masks syntax or logical errors."
                ),
                "evidence_snippet": "except:",
                "remediation_recommendation": (
                    "Catch specific exception types (e.g. ValueError, KeyError) or at least Exception."
                ),
                "suggested_improvement": "except Exception as exc:\n    logger.error('Error occurred: %s', exc)",
                "corrected_code": (
                    "except Exception as exc:\n"
                    "    logger.error('Operation failed: %s', exc)\n"
                    "    raise"
                ),
                "is_confirmed_pattern": True,
            })
        self.generic_visit(node)

    def visit_If(self, node: ast.If):
        self._check_nesting(node)
        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        self._check_nesting(node)
        self.generic_visit(node)

    def visit_While(self, node: ast.While):
        self._check_nesting(node)
        self.generic_visit(node)

    def _check_nesting(self, node: ast.AST):
        # Compute depth of nested blocks
        depth = 0
        parent = getattr(node, "_parent", None)
        while parent:
            if isinstance(parent, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                depth += 1
            parent = getattr(parent, "_parent", None)

        if depth >= 4:
            self.findings.append({
                "finding_type": "QUALITY",
                "title": f"Excessive Nesting Depth ({depth} levels)",
                "category": "Code Complexity",
                "severity": "MEDIUM",
                "heuristic_score": 6.0,
                "line_number": getattr(node, "lineno", 1),
                "filename": self.filename,
                "description": (
                    f"Code construct is nested {depth} levels deep. Deeply nested code is difficult "
                    "to trace and maintain."
                ),
                "risk_explanation": "Increased risk of logic bugs due to excessive cognitive branch tracking.",
                "evidence_snippet": f"Nested block at line {getattr(node, 'lineno', 1)}",
                "remediation_recommendation": "Invert conditions using guard clauses or extract nested logic into subroutines.",
                "suggested_improvement": "Use early return statements to flatten nested indentation.",
                "corrected_code": (
                    "# Flattened with guard clauses\n"
                    "if not condition:\n"
                    "    return\n"
                    "# Continue flat logic..."
                ),
                "is_confirmed_pattern": True,
            })

    def _to_snake_case(self, name: str) -> str:
        s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


class CodeAnalysisAgent:
    """Agent 1: Performs thorough code quality, structural, and smell analysis."""

    def __init__(self):
        self.agent_name = "Code Analysis Agent"

    def analyze(self, code: str, language: str, filename: str = "source_code") -> List[Dict[str, Any]]:
        """Execute code analysis based on detected language."""
        lang = language.lower().strip()
        if lang == "python":
            return self._analyze_python(code, filename)
        elif lang == "java":
            return self._analyze_java(code, filename)
        else:
            return []

    def _analyze_python(self, code: str, filename: str) -> List[Dict[str, Any]]:
        """Analyze Python code using AST and heuristic linters."""
        findings: List[Dict[str, Any]] = []
        code_lines = code.splitlines()

        try:
            tree = ast.parse(code)
            # Annotate parent nodes for nesting analysis
            for parent in ast.walk(tree):
                for child in ast.iter_child_nodes(parent):
                    child._parent = parent

            visitor = PythonASTQualityVisitor(filename, code_lines)
            visitor.visit(tree)
            findings.extend(visitor.findings)
        except Exception:
            pass

        # Text-based / Duplicate Code heuristics
        duplicate_findings = self._detect_duplicates(code_lines, filename)
        findings.extend(duplicate_findings)

        # Unused variable / Dead code regex heuristics
        unused_findings = self._detect_unused_python_elements(code, filename)
        findings.extend(unused_findings)

        return findings

    def _analyze_java(self, code: str, filename: str) -> List[Dict[str, Any]]:
        """Analyze Java code structure, naming conventions, and anti-patterns."""
        findings: List[Dict[str, Any]] = []
        lines = code.splitlines()

        # 1. Total Class Size (God Class smell)
        if len(lines) > 300:
            findings.append({
                "finding_type": "QUALITY",
                "title": f"Large Java Class File ({len(lines)} lines)",
                "category": "Clean Architecture & Modularity",
                "severity": "MEDIUM",
                "heuristic_score": 5.5,
                "line_number": 1,
                "filename": filename,
                "description": (
                    f"Java file has {len(lines)} lines. Consider decomposing into smaller, "
                    "single-responsibility components."
                ),
                "risk_explanation": "God classes become maintenance bottlenecks and violate SOLID principles.",
                "evidence_snippet": f"File length: {len(lines)} lines",
                "remediation_recommendation": "Split classes across cohesive service and repository abstractions.",
                "suggested_improvement": "Extract domain responsibilities into separate classes.",
                "corrected_code": "// Separate into UserService, UserRepository, and UserValidator",
                "is_confirmed_pattern": True,
            })

        # 2. Empty Catch Block detection
        empty_catch_regex = re.compile(r"catch\s*\([^)]+\)\s*\{\s*\}", re.MULTILINE)
        for match in empty_catch_regex.finditer(code):
            line_no = code[:match.start()].count("\n") + 1
            findings.append({
                "finding_type": "QUALITY",
                "title": "Empty Catch Block Detected",
                "category": "Error Handling Anti-Pattern",
                "severity": "HIGH",
                "heuristic_score": 7.0,
                "line_number": line_no,
                "filename": filename,
                "description": (
                    "Exception is caught but silently ignored with an empty body. "
                    "This suppresses operational failures and makes debugging impossible."
                ),
                "risk_explanation": "Failures fail silently, leaving the application in an indeterminate state.",
                "evidence_snippet": match.group(0),
                "remediation_recommendation": "Log the exception or re-throw a wrapped runtime exception.",
                "suggested_improvement": "catch (Exception e) { logger.error('Failure', e); }",
                "corrected_code": (
                    "catch (Exception e) {\n"
                    "    logger.error(\"Operation failed: \" + e.getMessage(), e);\n"
                    "    throw new ServiceException(\"Processing error\", e);\n"
                    "}"
                ),
                "is_confirmed_pattern": True,
            })

        # 3. Method Length and Parameter Count
        method_pattern = re.compile(
            r"(?:public|protected|private|static|\s)+[\w\<\>\[\]]+\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)\s*\{"
        )
        for match in method_pattern.finditer(code):
            method_name = match.group(1)
            params = match.group(2).strip()
            line_no = code[:match.start()].count("\n") + 1

            # Check parameter count
            if params:
                param_list = [p.strip() for p in params.split(",") if p.strip()]
                if len(param_list) > 4:
                    findings.append({
                        "finding_type": "QUALITY",
                        "title": f"Excessive Parameters ({len(param_list)}) in Method '{method_name}'",
                        "category": "Clean Code Principles",
                        "severity": "LOW",
                        "heuristic_score": 3.5,
                        "line_number": line_no,
                        "filename": filename,
                        "description": (
                            f"Method '{method_name}' takes {len(param_list)} parameters (recommended limit <= 4)."
                        ),
                        "risk_explanation": "Long parameter lists complicate unit testing and caller readability.",
                        "evidence_snippet": match.group(0),
                        "remediation_recommendation": "Encapsulate parameters into a Request DTO or Parameter Object.",
                        "suggested_improvement": "Use a Builder Pattern or Parameter DTO object.",
                        "corrected_code": f"public void {method_name}({method_name.capitalize()}Request request) {{ ... }}",
                        "is_confirmed_pattern": True,
                    })

            # Check method naming (Java methods should be lowerCamelCase)
            if method_name[0].isupper() and method_name != "main":
                findings.append({
                    "finding_type": "QUALITY",
                    "title": f"Non-Standard Java Method Naming '{method_name}'",
                    "category": "Java Naming Conventions",
                    "severity": "LOW",
                    "heuristic_score": 2.2,
                    "line_number": line_no,
                    "filename": filename,
                    "description": (
                        f"Method '{method_name}' starts with an uppercase letter. "
                        "Java methods must follow camelCase conventions."
                    ),
                    "risk_explanation": "Violates Java conventions, confusing developers with constructors or class names.",
                    "evidence_snippet": match.group(0),
                    "remediation_recommendation": f"Rename '{method_name}' to start with a lowercase letter.",
                    "suggested_improvement": f"Rename to '{method_name[0].lower() + method_name[1:]}'",
                    "corrected_code": f"public void {method_name[0].lower() + method_name[1:]}(...) {{ ... }}",
                    "is_confirmed_pattern": True,
                })

        # 4. Inefficient String Concatenation in Loops
        for i, line in enumerate(lines, 1):
            if re.search(r"\b(for|while)\b", line):
                # Look ahead for string += in the subsequent 6 lines
                for j in range(i, min(len(lines), i + 8)):
                    if "+=" in lines[j] and '"' in lines[j]:
                        findings.append({
                            "finding_type": "QUALITY",
                            "title": "Inefficient String Concatenation in Loop",
                            "category": "Performance & Resource Management",
                            "severity": "LOW",
                            "heuristic_score": 3.8,
                            "line_number": j + 1,
                            "filename": filename,
                            "description": (
                                "String concatenation (+ or +=) inside a loop creates new String objects "
                                "on every iteration, incurring O(N^2) memory and CPU overhead."
                            ),
                            "risk_explanation": "Causes excessive garbage collection and performance degradation on large loops.",
                            "evidence_snippet": lines[j].strip(),
                            "remediation_recommendation": "Use StringBuilder or StringBuffer for accumulating strings in loops.",
                            "suggested_improvement": "StringBuilder sb = new StringBuilder(); sb.append(...);",
                            "corrected_code": (
                                "StringBuilder sb = new StringBuilder();\n"
                                "for (String item : items) {\n"
                                "    sb.append(item);\n"
                                "}\n"
                                "String result = sb.toString();"
                            ),
                            "is_confirmed_pattern": True,
                        })
                        break

        # Check duplicates in Java
        findings.extend(self._detect_duplicates(lines, filename))
        return findings

    def _detect_duplicates(self, lines: List[str], filename: str) -> List[Dict[str, Any]]:
        """Detect identical or repeated multiline code blocks."""
        findings = []
        clean_lines = [line.strip() for line in lines]
        block_size = 4

        seen_blocks = {}
        for i in range(len(clean_lines) - block_size):
            block = tuple(clean_lines[i:i+block_size])
            # Skip empty or trivial blocks
            if any(len(l) < 5 or l in ("{", "}", ");", "pass") for l in block):
                continue
            if block in seen_blocks:
                orig_line = seen_blocks[block]
                findings.append({
                    "finding_type": "QUALITY",
                    "title": f"Duplicate Code Block ({block_size} identical lines)",
                    "category": "Don't Repeat Yourself (DRY)",
                    "severity": "LOW",
                    "heuristic_score": 3.2,
                    "line_number": i + 1,
                    "filename": filename,
                    "description": (
                        f"Found duplicate code block identical to lines {orig_line}-{orig_line+block_size-1}."
                    ),
                    "risk_explanation": (
                        "Duplicated code multiplies maintenance costs and bug fix oversights."
                    ),
                    "evidence_snippet": "\n".join(block[:2]) + "\n...",
                    "remediation_recommendation": "Extract common logic into a shared helper method.",
                    "suggested_improvement": "Refactor repetitive logic into a reusable method.",
                    "corrected_code": "// Extracted reusable method\nprivate void performCommonAction() { ... }",
                    "is_confirmed_pattern": True,
                })
                break
            else:
                seen_blocks[block] = i + 1
        return findings

    def _detect_unused_python_elements(self, code: str, filename: str) -> List[Dict[str, Any]]:
        """Identify potentially unused imports using static regex scan."""
        findings = []
        import_matches = re.finditer(r"^\s*import\s+([a-zA-Z0-9_]+)", code, re.MULTILINE)
        for match in import_matches:
            mod_name = match.group(1)
            line_no = code[:match.start()].count("\n") + 1
            # Count occurrences outside the import line
            occurrences = len(re.findall(r"\b" + re.escape(mod_name) + r"\b", code))
            if occurrences == 1:
                findings.append({
                    "finding_type": "QUALITY",
                    "title": f"Unused Import '{mod_name}'",
                    "category": "Dead Code Elimination",
                    "severity": "LOW",
                    "heuristic_score": 1.5,
                    "line_number": line_no,
                    "filename": filename,
                    "description": f"Module '{mod_name}' is imported but never referenced in the source file.",
                    "risk_explanation": "Dead imports increase module loading time and clutter source code.",
                    "evidence_snippet": match.group(0),
                    "remediation_recommendation": f"Remove the unused import 'import {mod_name}'.",
                    "suggested_improvement": f"Delete line {line_no}.",
                    "corrected_code": f"# Removed unused 'import {mod_name}'",
                    "is_confirmed_pattern": True,
                })
        return findings
