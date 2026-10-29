"""Security and sanitization utilities."""

import os
import re
import html
import uuid
from pathlib import Path


def get_safe_filename(original_name: str) -> str:
    """Generate a safe, sanitized filename preserving only extension and alphanumeric chars."""
    if not original_name:
        return f"submission_{uuid.uuid4().hex[:8]}.py"

    base_name, ext = os.path.splitext(os.path.basename(original_name))
    clean_base = re.sub(r"[^a-zA-Z0-9_\-]", "_", base_name)[:50]
    clean_ext = ext.lower() if ext.lower() in [".py", ".java"] else ".txt"

    if not clean_base:
        clean_base = f"file_{uuid.uuid4().hex[:8]}"

    return f"{clean_base}_{uuid.uuid4().hex[:6]}{clean_ext}"


def ensure_safe_path(base_dir: Path, requested_path: str) -> Path:
    """Ensure requested_path resolves strictly within base_dir, preventing path traversal."""
    base = Path(base_dir).resolve()
    target = (base / requested_path).resolve()

    if not target.is_relative_to(base):
        raise PermissionError(f"Security Violation: Path traversal attempt outside {base}")

    return target


def sanitize_text(text: str) -> str:
    """Escape HTML characters to prevent XSS reflection."""
    if not text:
        return ""
    return html.escape(str(text))
