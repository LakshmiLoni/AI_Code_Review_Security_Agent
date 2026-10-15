"""Safe reading of uploaded files and pasted text.

Only reads bytes and decodes text. Nothing here ever runs the code.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from config import settings


@dataclass
class FileReadResult:
    ok: bool
    text: str = ""
    error: Optional[str] = None


def _format_size(num_bytes: int) -> str:
    return f"{num_bytes / 1024:.1f} KB"


def check_text(text: Optional[str]) -> FileReadResult:
    """Validate pasted text (empty / oversized)."""
    if text is None or not text.strip():
        return FileReadResult(False, error="The code input is empty. Paste some code or upload a .py / .java file.")
    if len(text.encode("utf-8", errors="ignore")) > settings.MAX_PASTE_CHARS:
        return FileReadResult(
            False,
            error=f"The pasted code is too large (limit {_format_size(settings.MAX_PASTE_CHARS)}). "
                  "Please submit a smaller sample.",
        )
    return FileReadResult(True, text=text)


def read_uploaded_file(filename: str, data: bytes) -> FileReadResult:
    """Validate and decode an uploaded file."""
    extension = os.path.splitext(filename or "")[1].lower()
    if extension not in settings.SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(settings.SUPPORTED_EXTENSIONS))
        shown = extension or "(none)"
        return FileReadResult(False, error=f"Unsupported file type '{shown}'. Supported types: {supported}.")

    if data is None or len(data) == 0:
        return FileReadResult(False, error=f"The file '{filename}' is empty.")

    if len(data) > settings.MAX_FILE_SIZE_BYTES:
        return FileReadResult(
            False,
            error=f"The file '{filename}' is {_format_size(len(data))}, which exceeds the "
                  f"{_format_size(settings.MAX_FILE_SIZE_BYTES)} limit.",
        )

    if b"\x00" in data:
        return FileReadResult(False, error=f"'{filename}' looks like a binary file, not source code.")

    try:
        text = data.decode("utf-8-sig")  # tolerates a UTF-8 BOM
    except UnicodeDecodeError as exc:
        return FileReadResult(
            False,
            error=f"'{filename}' could not be decoded as UTF-8 (invalid byte at position {exc.start}). "
                  "Please re-save the file with UTF-8 encoding and upload it again.",
        )

    if not text.strip():
        return FileReadResult(False, error=f"The file '{filename}' contains only whitespace.")
    return FileReadResult(True, text=text)
