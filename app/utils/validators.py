"""Input and file validation utilities."""

import os
import re
from typing import Tuple, Optional


ALLOWED_EXTENSIONS = {".py", ".java"}
MAX_CODE_LENGTH_CHARS = 500_000  # ~500KB source code limit
MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024  # 2MB upload limit


def validate_code_input(code_string: Optional[str]) -> Tuple[bool, str]:
    """Validate submitted source code text."""
    if not code_string or not code_string.strip():
        return False, "Submitted code cannot be empty."

    if len(code_string) > MAX_CODE_LENGTH_CHARS:
        return False, f"Submitted code exceeds maximum limit of {MAX_CODE_LENGTH_CHARS} characters."

    return True, ""


def detect_language(code_snippet: str, filename: Optional[str] = None) -> str:
    """Detect language ('python' or 'java') based on filename extension or content heuristics."""
    if filename:
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".py":
            return "python"
        elif ext == ".java":
            return "java"

    # Heuristic checks on content
    java_indicators = [
        r"\bpublic\s+class\b",
        r"\bpublic\s+static\s+void\s+main\b",
        r"\bSystem\.out\.println\b",
        r"\bpackage\s+[a-zA-Z0-9_.]+;",
        r"\bimport\s+java\.",
        r"\bpublic\s+interface\b",
        r"\bprivate\s+[A-Z][a-zA-Z0-9_]*\s+[a-z]",
    ]
    for pattern in java_indicators:
        if re.search(pattern, code_snippet):
            return "java"

    python_indicators = [
        r"^\s*def\s+[a-zA-Z0-9_]+\s*\(",
        r"^\s*import\s+[a-zA-Z0-9_]+",
        r"^\s*from\s+[a-zA-Z0-9_.]+\s+import\b",
        r"^\s*class\s+[a-zA-Z0-9_]+(\([a-zA-Z0-9_.]*\))?:",
        r"if\s+__name__\s*==\s*['\"]__main__['\"]:",
        r"\bprint\(",
    ]
    for pattern in python_indicators:
        if re.search(pattern, code_snippet, re.MULTILINE):
            return "python"

    return "python"  # Default fallback


def validate_file_upload(file_storage, max_size_bytes: int = MAX_FILE_SIZE_BYTES) -> Tuple[bool, str, str]:
    """Validate uploaded file storage object. Returns (is_valid, error_msg, detected_lang)."""
    if not file_storage or not getattr(file_storage, "filename", None):
        return False, "No file was selected for upload.", ""

    filename = file_storage.filename
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Disallowed file extension '{ext}'. Only .py and .java files are supported.", ""

    # Measure size
    file_storage.seek(0, os.SEEK_END)
    size = file_storage.tell()
    file_storage.seek(0)

    if size == 0:
        return False, "The uploaded file is empty.", ""

    if size > max_size_bytes:
        return False, f"File size ({round(size / 1024, 1)} KB) exceeds the limit of {round(max_size_bytes / 1024 / 1024, 1)} MB.", ""

    lang = "python" if ext == ".py" else "java"
    return True, "", lang
