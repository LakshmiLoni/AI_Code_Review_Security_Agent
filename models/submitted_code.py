"""Data models for submitted source code and its validation outcome.

IMPLEMENTED IN MILESTONE 1 (used by the Code Submission Module).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class SyntaxIssue:
    """A single syntax / compile problem."""

    message: str
    line: Optional[int] = None
    column: Optional[int] = None
    source_line: Optional[str] = None


@dataclass
class ValidationResult:
    """Outcome of syntax validation.

    status:
        ``valid``       - syntax accepted by the parser/compiler
        ``invalid``     - syntax errors found (see ``issues``)
        ``unavailable`` - validator could not run (e.g. no JDK); see ``warnings``
        ``skipped``     - validation was not attempted (e.g. language unknown)
    """

    status: str
    language: Optional[str] = None
    tool: str = ""
    message: str = ""
    issues: List[SyntaxIssue] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return self.status == "valid"


@dataclass
class SubmittedCode:
    """A code submission after language detection and validation."""

    code: str
    source_type: str  # "paste" | "upload"
    filename: Optional[str] = None
    language: Optional[str] = None  # "python" | "java" | None
    detection_confidence: float = 0.0
    detection_notes: List[str] = field(default_factory=list)
    validation: Optional[ValidationResult] = None
    errors: List[str] = field(default_factory=list)  # blocking input problems
    submitted_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def line_count(self) -> int:
        return len(self.code.splitlines()) if self.code else 0

    @property
    def accepted(self) -> bool:
        """True when the input was usable (non-empty, readable, language known)."""
        return not self.errors and self.language is not None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
