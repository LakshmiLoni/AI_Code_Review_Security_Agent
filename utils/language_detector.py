"""Independent Language Detection Module.

Automatically detects whether submitted source code or uploaded files are
written in Python or Java based on file extensions and syntactic pattern heuristics.
Rejects unsupported file types and languages with explicit errors.
"""
import os
import re
import ast
from typing import Tuple, Dict, Any


class UnsupportedLanguageError(ValueError):
    """Raised when an uploaded file extension or code syntax is unsupported."""
    pass


SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".java": "java",
}


JAVA_KEYWORDS = [
    r"\bpublic\s+(?:class|interface|enum)\b",
    r"\bpackage\s+[a-zA-Z0-9_.]+\s*;",
    r"\bimport\s+java\.[a-zA-Z0-9_.*]+\s*;",
    r"\bimport\s+javax\.[a-zA-Z0-9_.*]+\s*;",
    r"\bimport\s+org\.[a-zA-Z0-9_.*]+\s*;",
    r"\bpublic\s+static\s+void\s+main\b",
    r"\bSystem\.(?:out|err)\.print(?:ln)?\b",
    r"@Override\b",
    r"@Autowired\b",
    r"@GetMapping\b",
    r"@PostMapping\b",
    r"\b(?:public|private|protected)\s+(?:static\s+)?(?:final\s+)?[a-zA-Z0-9_<>\[\]]+\s+[a-zA-Z0-9_]+\s*\(",
    r"\bnew\s+[A-Z][a-zA-Z0-9_]*\(",
    r";\s*$",  # Line ending with semicolon
]

PYTHON_KEYWORDS = [
    r"^\s*def\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(",
    r"^\s*class\s+[a-zA-Z_][a-zA-Z0-9_]*\s*(?:\([^)]*\))?\s*:",
    r"^\s*import\s+[a-zA-Z_][a-zA-Z0-9_.]*",
    r"^\s*from\s+[a-zA-Z_][a-zA-Z0-9_.]*\s+import\b",
    r"\bprint\s*\(",
    r"\bself\.[a-zA-Z_]",
    r"\b__init__\b",
    r"\belif\s+.*:",
    r"\bexcept\s*(?:[A-Za-z0-9_,\s()]+)?\s*:",
    r'if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:',
    r"^\s*#[^!].*",  # Python comment
]


def detect_language(code: str, filename: str = None) -> Tuple[str, float, str]:
    """Detect the programming language from file extension or source code patterns.

    Args:
        code: Source code string.
        filename: Optional filename or path.

    Returns:
        Tuple of (language_name, confidence_score, detection_reason)
        language_name is either 'python' or 'java'.

    Raises:
        UnsupportedLanguageError: If the extension or code is unsupported or cannot be determined.
    """
    # 1. Filename extension rule (highest authority when present)
    if filename:
        _, ext = os.path.splitext(filename.lower())
        if ext in SUPPORTED_EXTENSIONS:
            lang = SUPPORTED_EXTENSIONS[ext]
            return lang, 1.0, f"Identified as {lang.capitalize()} based on file extension '{ext}'."
        elif ext:
            raise UnsupportedLanguageError(
                f"Unsupported file format '{ext}'. Only Python (.py) and Java (.java) source files are accepted."
            )

    # 2. Direct code pattern heuristic analysis
    code_stripped = code.strip()
    if not code_stripped:
        raise UnsupportedLanguageError("Submitted code is empty. Please provide valid source code.")

    # Try Python AST parse first
    is_valid_python_ast = False
    try:
        ast.parse(code_stripped)
        is_valid_python_ast = True
    except (SyntaxError, ValueError):
        is_valid_python_ast = False

    # Count pattern occurrences
    python_matches = 0
    for pat in PYTHON_KEYWORDS:
        if re.search(pat, code_stripped, re.MULTILINE):
            python_matches += 1

    java_matches = 0
    for pat in JAVA_KEYWORDS:
        if re.search(pat, code_stripped, re.MULTILINE):
            java_matches += 1

    # Check for Java strong indicators (semicolons + braces)
    semicolon_count = len(re.findall(r";\s*$", code_stripped, re.MULTILINE))
    brace_open_count = code_stripped.count("{")
    brace_close_count = code_stripped.count("}")

    if brace_open_count > 0 and brace_close_count > 0 and semicolon_count >= 2:
        java_matches += 2

    # Weight decisions
    if is_valid_python_ast and java_matches == 0:
        confidence = min(0.99, 0.70 + (python_matches * 0.05))
        return "python", confidence, "Detected Python syntax structure (valid AST and keywords)."

    if java_matches > python_matches and not is_valid_python_ast:
        confidence = min(0.99, 0.65 + (java_matches * 0.05))
        return "java", confidence, f"Detected Java language constructs ({java_matches} Java syntactic patterns matched)."

    if is_valid_python_ast and python_matches >= java_matches:
        return "python", 0.90, "Identified as Python by AST syntax parsing and keyword matches."

    if java_matches > 0 and java_matches >= python_matches:
        return "java", 0.85, f"Identified as Java by {java_matches} class/package/method markers."

    if is_valid_python_ast:
        return "python", 0.75, "Parsed as valid Python syntax tree."

    # Could not determine with reasonable certainty
    raise UnsupportedLanguageError(
        "Could not automatically determine programming language. Please provide valid Python or Java source code."
    )
