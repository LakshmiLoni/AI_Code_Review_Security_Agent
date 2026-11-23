"""Analysis: Language Detector.

Automatically identifies programming language (Python or Java) from
file extensions or syntactic and heuristic pattern analysis.
"""
import os
import re
import ast
from typing import Tuple


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
    r";\s*$",
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
    r"^\s*#[^!].*",
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
        UnsupportedLanguageError: If the extension or code is unsupported.
    """
    if filename:
        _, ext = os.path.splitext(filename.lower())
        if ext in SUPPORTED_EXTENSIONS:
            lang = SUPPORTED_EXTENSIONS[ext]
            return lang, 1.0, f"Identified as {lang.capitalize()} based on file extension '{ext}'."
        elif ext:
            raise UnsupportedLanguageError(
                f"Unsupported file format '{ext}'. Only Python (.py) and Java (.java) source files are accepted."
            )

    code_stripped = code.strip()
    if not code_stripped:
        raise UnsupportedLanguageError("Submitted code is empty. Please provide valid source code.")

    is_valid_python_ast = False
    try:
        ast.parse(code_stripped)
        is_valid_python_ast = True
    except (SyntaxError, ValueError):
        is_valid_python_ast = False

    python_matches = sum(1 for pat in PYTHON_KEYWORDS if re.search(pat, code_stripped, re.MULTILINE))
    java_matches = sum(1 for pat in JAVA_KEYWORDS if re.search(pat, code_stripped, re.MULTILINE))

    if is_valid_python_ast and python_matches >= java_matches:
        conf = min(0.98, 0.7 + (python_matches * 0.05))
        return "python", conf, "Identified as Python via AST syntax parse and keyword indicators."

    if java_matches > python_matches:
        conf = min(0.95, 0.6 + (java_matches * 0.05))
        return "java", conf, f"Identified as Java via structural keywords ({java_matches} Java indicators matched)."

    if python_matches > 0:
        return "python", 0.75, "Identified as Python via heuristic keyword matching."

    if "{" in code_stripped and ";" in code_stripped:
        return "java", 0.60, "Identified as Java via C-style block delimiters and statement semicolons."

    return "python", 0.50, "Defaulted to Python syntax analysis."


__all__ = ["detect_language", "UnsupportedLanguageError", "SUPPORTED_EXTENSIONS"]
