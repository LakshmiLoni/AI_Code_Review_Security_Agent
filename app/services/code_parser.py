"""Static Code Parser supporting Python AST and Java structural extraction."""

import ast
import re
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class ParsedCode:
    """Represents normalized parsed structure of source code."""
    language: str
    source_code: str
    lines: List[str]
    has_syntax_error: bool = False
    syntax_error_details: Optional[Dict[str, Any]] = None
    ast_tree: Optional[ast.AST] = None  # Python AST
    functions: List[Dict[str, Any]] = field(default_factory=list)
    classes: List[Dict[str, Any]] = field(default_factory=list)
    imports: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


class CodeParser:
    """Parses Python and Java source code without ever executing it."""

    def parse(self, source_code: str, language: str = "python") -> ParsedCode:
        lines = source_code.splitlines()
        lang = language.lower()

        if lang == "python":
            return self._parse_python(source_code, lines)
        elif lang == "java":
            return self._parse_java(source_code, lines)
        else:
            return ParsedCode(
                language=lang,
                source_code=source_code,
                lines=lines,
                metrics={"total_lines": len(lines)}
            )

    def _parse_python(self, source_code: str, lines: List[str]) -> ParsedCode:
        parsed = ParsedCode(language="python", source_code=source_code, lines=lines)

        try:
            tree = ast.parse(source_code)
            parsed.ast_tree = tree

            # Extract imports, functions, classes
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            parsed.imports.append({"name": alias.name, "asname": alias.asname, "line": node.lineno})
                    else:
                        module = node.module or ""
                        for alias in node.names:
                            parsed.imports.append({"name": f"{module}.{alias.name}", "asname": alias.asname, "line": node.lineno})

                elif isinstance(node, ast.FunctionDef):
                    # Measure function span
                    start = node.lineno
                    end = getattr(node, "end_lineno", start + len(node.body))
                    length = end - start + 1
                    # Estimate complexity based on decision points
                    complexity = 1
                    for child in ast.walk(node):
                        if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With)):
                            complexity += 1
                        elif isinstance(child, ast.BoolOp):
                            complexity += len(child.values) - 1

                    parsed.functions.append({
                        "name": node.name,
                        "line": start,
                        "end_line": end,
                        "length": length,
                        "args_count": len(node.args.args),
                        "complexity": complexity,
                        "node": node
                    })

                elif isinstance(node, ast.ClassDef):
                    parsed.classes.append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods_count": sum(1 for item in node.body if isinstance(item, ast.FunctionDef))
                    })

            parsed.metrics = {
                "total_lines": len(lines),
                "blank_lines": sum(1 for line in lines if not line.strip()),
                "comment_lines": sum(1 for line in lines if line.strip().startswith("#")),
                "function_count": len(parsed.functions),
                "class_count": len(parsed.classes),
                "import_count": len(parsed.imports)
            }

        except SyntaxError as e:
            parsed.has_syntax_error = True
            parsed.syntax_error_details = {
                "line": e.lineno or 1,
                "column": e.offset or 1,
                "message": e.msg,
                "text": e.text or ""
            }
            parsed.metrics = {"total_lines": len(lines), "syntax_error": True}

        return parsed

    def _parse_java(self, source_code: str, lines: List[str]) -> ParsedCode:
        parsed = ParsedCode(language="java", source_code=source_code, lines=lines)

        # Check basic bracket balance for syntax validity
        open_braces = source_code.count("{")
        close_braces = source_code.count("}")
        if open_braces != close_braces:
            parsed.has_syntax_error = True
            parsed.syntax_error_details = {
                "line": len(lines),
                "column": 1,
                "message": f"Mismatched curly braces in Java file (open: {open_braces}, close: {close_braces}).",
                "text": lines[-1] if lines else ""
            }

        # Extract package and imports
        import_pattern = re.compile(r"^\s*import\s+([a-zA-Z0-9_.*]+);")
        class_pattern = re.compile(r"\b(?:public\s+|private\s+|protected\s+)?(?:static\s+)?class\s+([a-zA-Z0-9_]+)")
        method_pattern = re.compile(r"\b(?:public|private|protected)\s+(?:static\s+)?(?:[\w<>\[\]]+)\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)")

        for idx, line in enumerate(lines, start=1):
            imp_match = import_pattern.match(line)
            if imp_match:
                parsed.imports.append({"name": imp_match.group(1), "line": idx})

            cls_match = class_pattern.search(line)
            if cls_match:
                parsed.classes.append({"name": cls_match.group(1), "line": idx})

            m_match = method_pattern.search(line)
            if m_match and not any(kw in line for kw in ["if", "for", "while", "return", "new"]):
                method_name = m_match.group(1)
                args_str = m_match.group(2).strip()
                args_count = len(args_str.split(",")) if args_str else 0
                parsed.functions.append({
                    "name": method_name,
                    "line": idx,
                    "args_count": args_count,
                    "raw": line.strip()
                })

        parsed.metrics = {
            "total_lines": len(lines),
            "blank_lines": sum(1 for line in lines if not line.strip()),
            "comment_lines": sum(1 for line in lines if line.strip().startswith("//")),
            "function_count": len(parsed.functions),
            "class_count": len(parsed.classes),
            "import_count": len(parsed.imports)
        }

        return parsed
