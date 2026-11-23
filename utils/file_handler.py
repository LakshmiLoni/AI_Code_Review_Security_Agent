"""Utils: File Handler.

Handles file reading, file size verification, extension validation,
and filename sanitization safely.
"""
import os
import re
from typing import Tuple, Optional
from config import Config

ALLOWED_EXTENSIONS = {".py", ".java"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


class FileHandler:
    """Safe file handler operations."""

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Strip dangerous path traversal characters and normalize filename."""
        base = os.path.basename(filename)
        clean = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", base)
        return clean or "submitted_code"

    @staticmethod
    def validate_file(filename: str, file_size: int) -> Tuple[bool, Optional[str]]:
        """Verify extension and size constraints."""
        _, ext = os.path.splitext(filename.lower())
        if ext not in ALLOWED_EXTENSIONS:
            return False, f"Unsupported file type '{ext}'. Only .py and .java files are supported."

        if file_size > MAX_FILE_SIZE:
            return False, f"File exceeds maximum size limit of 5 MB ({file_size / (1024*1024):.1f} MB provided)."

        return True, None

    @staticmethod
    def read_uploaded_file(uploaded_file) -> Tuple[str, str]:
        """Read text from a Streamlit or Flask uploaded file object.

        Returns:
            Tuple of (source_code_text, sanitized_filename)
        """
        filename = getattr(uploaded_file, "name", "snippet")
        clean_name = FileHandler.sanitize_filename(filename)

        if hasattr(uploaded_file, "read"):
            content = uploaded_file.read()
            if isinstance(content, bytes):
                text = content.decode("utf-8", errors="replace")
            else:
                text = str(content)
            # Reset seek if supported
            if hasattr(uploaded_file, "seek"):
                uploaded_file.seek(0)
            return text, clean_name

        return str(uploaded_file), clean_name
