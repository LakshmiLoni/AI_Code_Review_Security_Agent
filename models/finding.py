"""Data models for security findings and remediation recommendations.

DESIGN ONLY IN MILESTONE 1: these dataclasses define the contract that the
Security Vulnerability Agent and Remediation Agent will use in later
milestones. No component produces them yet.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Finding:
    """One detected issue (security vulnerability or code-quality problem)."""

    finding_id: str
    title: str
    category: str  # e.g. "A05:2025 Injection" or "Code Smell"
    severity: Severity
    description: str
    line_start: int
    line_end: Optional[int] = None
    code_snippet: str = ""
    cwe_id: Optional[str] = None  # e.g. "CWE-89"
    confidence: float = 0.0  # 0-1
    detected_by: str = ""  # agent name
    references: List[str] = field(default_factory=list)  # knowledge-base source URLs

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["severity"] = self.severity.value
        return data


@dataclass
class Remediation:
    """A recommended fix for one finding."""

    finding_id: str
    summary: str
    explanation: str
    secure_code_example: str = ""
    effort: str = "low"  # "low" | "medium" | "high"
    references: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
