"""Glue for the Code Submission Module: read -> detect -> validate.

Keeps ``app.py`` thin and makes the whole flow unit-testable.
"""
from __future__ import annotations

from typing import Optional

from models.submitted_code import SubmittedCode, ValidationResult
from submission.code_validator import validate_code
from submission.file_handler import check_text, read_uploaded_file
from submission.language_detector import detect_for_file, detect_language


def _finish(sub: SubmittedCode, detection) -> SubmittedCode:
    sub.language = detection.language
    sub.detection_confidence = detection.confidence
    sub.detection_notes = [detection.message] + detection.reasons[:6] if detection.message else detection.reasons[:6]
    if sub.language is None:
        sub.errors.append(detection.message or "The programming language could not be detected.")
        sub.validation = ValidationResult("skipped", None, "none", "Validation skipped: language not detected.")
    else:
        sub.validation = validate_code(sub.code, sub.language)
    return sub


def submit_pasted_code(text: Optional[str]) -> SubmittedCode:
    """Process code pasted into the text area."""
    sub = SubmittedCode(code=text or "", source_type="paste")
    checked = check_text(text)
    if not checked.ok:
        sub.errors.append(checked.error or "Invalid input.")
        sub.validation = ValidationResult("skipped", None, "none", "Validation skipped.")
        return sub
    return _finish(sub, detect_language(checked.text))


def submit_uploaded_file(filename: str, data: bytes) -> SubmittedCode:
    """Process an uploaded ``.py`` / ``.java`` file."""
    sub = SubmittedCode(code="", source_type="upload", filename=filename)
    read = read_uploaded_file(filename, data)
    if not read.ok:
        sub.errors.append(read.error or "The file could not be read.")
        sub.validation = ValidationResult("skipped", None, "none", "Validation skipped.")
        return sub
    sub.code = read.text
    return _finish(sub, detect_for_file(read.text, filename))
