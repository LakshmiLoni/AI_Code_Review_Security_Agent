"""Source Code Syntax Validation Module.

Performs static syntax verification for Python and Java code prior to agent processing.
"""
import ast
import re
from typing import Tuple, Optional, Dict, Any


def validate_python_syntax(code: str) -> Tuple[bool, Optional[str], Optional[int]]:
    """Validate Python syntax using Python's native AST parser."""
    try:
        ast.parse(code)
        return True, None, None
    except SyntaxError as exc:
        msg = f"Python Syntax Error: {exc.msg}"
        return False, msg, exc.lineno
    except Exception as exc:
        return False, f"Python Parsing Error: {str(exc)}", None


def validate_java_syntax(code: str) -> Tuple[bool, Optional[str], Optional[int]]:
    """Validate Java code structure by checking balanced delimiters and basic syntax."""
    lines = code.splitlines()
    stack = []
    pairs = {"{": "}", "(": ")", "[": "]"}

    in_block_comment = False
    in_string = False

    for line_idx, line in enumerate(lines, start=1):
        clean_line = line.strip()
        i = 0
        while i < len(clean_line):
            ch = clean_line[i]

            # Handle multi-line comments
            if not in_string and not in_block_comment and clean_line[i:i+2] == "/*":
                in_block_comment = True
                i += 2
                continue
            if in_block_comment and clean_line[i:i+2] == "*/":
                in_block_comment = False
                i += 2
                continue
            if in_block_comment:
                i += 1
                continue

            # Handle single-line comments
            if not in_string and clean_line[i:i+2] == "//":
                break

            # Handle strings
            if ch == '"' and (i == 0 or clean_line[i-1] != '\\'):
                in_string = not in_string
                i += 1
                continue

            if in_string:
                i += 1
                continue

            # Check brackets
            if ch in pairs:
                stack.append((ch, line_idx))
            elif ch in pairs.values():
                if not stack:
                    return False, f"Unmatched closing delimiter '{ch}'", line_idx
                last_ch, open_line = stack.pop()
                if pairs[last_ch] != ch:
                    return False, f"Mismatched delimiter: '{last_ch}' at line {open_line} closed by '{ch}'", line_idx

            i += 1

    if stack:
        unclosed_ch, open_line = stack[-1]
        return False, f"Unclosed delimiter '{unclosed_ch}' opened at line {open_line}", open_line

    if in_block_comment:
        return False, "Unterminated block comment (/* ... */)", len(lines)

    return True, None, None


def validate_syntax(code: str, language: str) -> Tuple[bool, Optional[str], Optional[int]]:
    """Universal syntax validator for supported languages.

    Args:
        code: Source code text.
        language: 'python' or 'java'.

    Returns:
        (is_valid, error_message, line_number)
    """
    lang = language.lower().strip()
    if lang == "python":
        return validate_python_syntax(code)
    elif lang == "java":
        return validate_java_syntax(code)
    else:
        return False, f"Unsupported language '{language}' for syntax validation.", None
