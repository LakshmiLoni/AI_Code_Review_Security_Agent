"""Syntax validation for Python (``ast``) and Java (``javac``).

SAFETY: submitted code is never executed.
* Python: ``ast.parse`` only builds a syntax tree.
* Java: ``javac`` only compiles to ``.class`` files in a temporary directory;
  the resulting classes are never loaded or run, and annotation processing is
  disabled (``-proc:none``) so compilation cannot trigger user-supplied code.
"""
from __future__ import annotations

import ast
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional

from config import settings
from models.submitted_code import SyntaxIssue, ValidationResult

JDK_HELP = (
    "Java syntax checking needs a JDK (not just a JRE) with 'javac' on PATH. "
    "Install a JDK (e.g. Temurin/OpenJDK 17 or 21), restart the terminal, and confirm with 'javac -version'."
)


# --------------------------------------------------------------------------- Python
def validate_python(code: str) -> ValidationResult:
    """Check Python syntax with the ``ast`` module (no execution)."""
    try:
        ast.parse(code, filename="<submitted>", mode="exec")
    except SyntaxError as exc:  # IndentationError / TabError are subclasses
        message = exc.msg or "invalid syntax"
        if isinstance(exc, IndentationError):
            message = f"Indentation problem: {message}"
        issue = SyntaxIssue(
            message=message,
            line=exc.lineno,
            column=exc.offset,
            source_line=(exc.text or "").rstrip("\n") or None,
        )
        return ValidationResult("invalid", "python", "ast", f"Python syntax error on line {exc.lineno}.", [issue])
    except (ValueError, RecursionError, MemoryError) as exc:
        # e.g. null bytes in source or pathologically nested expressions
        issue = SyntaxIssue(message=f"The code could not be parsed: {exc}")
        return ValidationResult("invalid", "python", "ast", "Python code could not be parsed.", [issue])
    return ValidationResult("valid", "python", "ast", "Python syntax is valid.")


# --------------------------------------------------------------------------- Java
def find_javac() -> Optional[str]:
    """Locate ``javac`` on PATH or under JAVA_HOME. Returns None if unavailable."""
    found = shutil.which("javac")
    if found:
        return found
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        for name in ("javac.exe", "javac"):
            candidate = Path(java_home) / "bin" / name
            if candidate.is_file():
                return str(candidate)
    return None


_PUBLIC_TYPE = re.compile(
    r"\bpublic\s+(?:(?:static|final|abstract|sealed|strictfp)\s+)*(?:class|interface|enum|record|@interface)\s+(\w+)"
)
_JAVAC_ERROR = re.compile(r"^(?P<file>[^\n:]*\.java):(?P<line>\d+):\s*(?P<kind>error|warning):\s*(?P<msg>.*)$")


def _java_file_name(code: str) -> str:
    match = _PUBLIC_TYPE.search(code)
    return f"{match.group(1)}.java" if match else "Main.java"


def _parse_javac_output(output: str) -> List[SyntaxIssue]:
    issues: List[SyntaxIssue] = []
    lines = output.splitlines()
    index = 0
    while index < len(lines):
        match = _JAVAC_ERROR.match(lines[index])
        if match and match.group("kind") == "error":
            source_line = lines[index + 1] if index + 1 < len(lines) else None
            caret = lines[index + 2] if index + 2 < len(lines) else ""
            column = caret.find("^") + 1 if "^" in caret else None
            issues.append(SyntaxIssue(match.group("msg").strip(), int(match.group("line")), column,
                                      source_line.strip() if source_line else None))
            index += 3
        else:
            index += 1
    return issues


def _basic_bracket_check(code: str) -> List[str]:
    """Very rough structural check used only when javac is unavailable.

    Ignores strings, char literals and comments. This is NOT a compiler.
    """
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: List[tuple] = []
    i, line, n = 0, 1, len(code)
    while i < n:
        ch = code[i]
        if ch == "\n":
            line += 1
        elif code.startswith("//", i):
            while i < n and code[i] != "\n":
                i += 1
            continue
        elif code.startswith("/*", i):
            end = code.find("*/", i + 2)
            end = n if end == -1 else end + 2
            line += code.count("\n", i, end)
            i = end
            continue
        elif ch in "\"'":
            quote = ch
            i += 1
            while i < n and code[i] != quote and code[i] != "\n":
                i += 2 if code[i] == "\\" else 1
        elif ch in "([{":
            stack.append((ch, line))
        elif ch in pairs:
            if not stack or stack[-1][0] != pairs[ch]:
                return [f"Unmatched '{ch}' near line {line}."]
            stack.pop()
        i += 1
    if stack:
        opener, opened_line = stack[-1]
        return [f"Unclosed '{opener}' opened on line {opened_line}."]
    return []


def validate_java(code: str, javac_path: Optional[str] = None, timeout: Optional[int] = None) -> ValidationResult:
    """Check Java syntax by invoking ``javac`` (compile only, never run).

    ``javac_path`` may be given explicitly (used by tests); otherwise it is discovered.
    When no JDK is available a ``unavailable`` result with a helpful warning is
    returned instead of raising.
    """
    javac = javac_path if javac_path is not None else find_javac()
    if not javac:
        warnings = [JDK_HELP]
        structural = _basic_bracket_check(code)
        if structural:
            warnings.append("Basic bracket check (not a compiler): " + " ".join(structural))
        else:
            warnings.append("Basic bracket check (not a compiler) found no unbalanced brackets, "
                            "but this does NOT confirm the code compiles.")
        return ValidationResult("unavailable", "java", "none",
                                "Java syntax could not be verified because javac was not found.",
                                warnings=warnings)

    timeout = timeout or settings.JAVAC_TIMEOUT_SECONDS
    with tempfile.TemporaryDirectory(prefix="java_validate_") as workdir:
        source_path = Path(workdir) / _java_file_name(code)
        source_path.write_text(code, encoding="utf-8")
        command = [javac, "-proc:none", "-Xlint:none", "-encoding", "UTF-8", "-d", workdir, str(source_path)]
        try:
            completed = subprocess.run(command, capture_output=True, text=True, timeout=timeout,
                                       cwd=workdir, shell=False, check=False)
        except subprocess.TimeoutExpired:
            return ValidationResult("unavailable", "java", "javac",
                                    f"javac did not finish within {timeout} seconds.",
                                    warnings=["Validation timed out. Try a smaller file."])
        except (OSError, ValueError) as exc:
            return ValidationResult("unavailable", "java", "javac",
                                    "javac could not be started.",
                                    warnings=[f"{exc}. {JDK_HELP}"])

    if completed.returncode == 0:
        return ValidationResult("valid", "java", "javac", "Java code compiled without syntax errors.")

    output = (completed.stderr or "") + (completed.stdout or "")
    issues = _parse_javac_output(output)
    if not issues:
        issues = [SyntaxIssue(message=output.strip()[:500] or "javac reported an unknown error.")]
    notes = []
    if any("cannot find symbol" in i.message or "does not exist" in i.message for i in issues):
        notes.append("Errors such as 'cannot find symbol' or 'package does not exist' can mean a missing "
                     "library or class in this stand-alone check rather than a typing mistake.")
    return ValidationResult("invalid", "java", "javac",
                            f"javac reported {len(issues)} error(s).", issues, notes)


# --------------------------------------------------------------------------- dispatcher
def validate_code(code: str, language: Optional[str]) -> ValidationResult:
    """Validate code for a detected language (``python`` or ``java``)."""
    if language == "python":
        return validate_python(code)
    if language == "java":
        return validate_java(code)
    return ValidationResult("skipped", language, "none", "Validation skipped because the language is unknown.")
