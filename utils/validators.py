"""Utils: Validators.

Input validation helpers for submitted code, filenames, and parameters.
"""
from typing import Tuple, Optional
from analysis.syntax_validator import validate_syntax


class CodeValidator:
    """Validates source code inputs before pipeline execution."""

    @staticmethod
    def validate_code_input(code: str, language: str = None) -> Tuple[bool, Optional[str]]:
        """Verify code is not empty, does not exceed length bounds, and has valid syntax."""
        if not code or not code.strip():
            return False, "Source code cannot be empty. Please enter or upload valid code."

        if len(code) > 1_000_000:
            return False, "Source code exceeds maximum supported length (1,000,000 characters)."

        if language:
            is_valid, err_msg, line = validate_syntax(code, language)
            if not is_valid:
                return False, f"Syntax error at line {line}: {err_msg}"

        return True, None
