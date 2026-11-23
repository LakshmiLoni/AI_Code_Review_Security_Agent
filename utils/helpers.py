"""Helper utility functions."""
import uuid
import datetime
import json
from typing import Optional, Any


def generate_review_id(prefix: str = "REV") -> str:
    """Generate a readable unique review identifier."""
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M")
    unique_suffix = uuid.uuid4().hex[:6].upper()
    return f"{prefix}-{timestamp}-{unique_suffix}"


def format_timestamp(dt: Optional[datetime.datetime] = None) -> str:
    """Format datetime into standard ISO 8601 string."""
    if dt is None:
        dt = datetime.datetime.utcnow()
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def safe_json_loads(data: str, default: Any = None) -> Any:
    """Safely parse JSON string, returning default if invalid."""
    if not data:
        return default
    try:
        return json.loads(data)
    except Exception:
        return default


def sanitize_evidence(evidence: str, max_length: int = 400) -> str:
    """Sanitize and limit length of evidence code snippets."""
    if not evidence:
        return ""
    clean = evidence.strip()
    if len(clean) > max_length:
        return clean[:max_length] + " ... [truncated]"
    return clean


def extract_code_snippet(code: str, line_number: int, context: int = 2) -> str:
    """Extract code lines surrounding a specific line number with line prefixes."""
    if not code or line_number <= 0:
        return ""
    lines = code.splitlines()
    start = max(0, line_number - 1 - context)
    end = min(len(lines), line_number + context)

    snippet_lines = []
    for idx in range(start, end):
        curr_line = idx + 1
        marker = ">> " if curr_line == line_number else "   "
        line_content = lines[idx]
        snippet_lines.append(f"{marker}{curr_line:4d} | {line_content}")

    return "\n".join(snippet_lines)
