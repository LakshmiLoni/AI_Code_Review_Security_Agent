"""Aggregate result of a full review.

DESIGN ONLY IN MILESTONE 1: produced by the orchestrator in Milestone 3+.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from models.finding import Finding, Remediation
from models.submitted_code import SubmittedCode


@dataclass
class ReviewResult:
    submission: SubmittedCode
    findings: List[Finding] = field(default_factory=list)
    remediations: List[Remediation] = field(default_factory=list)
    pr_summary: str = ""
    quality_score: Optional[float] = None  # 0-100, defined in a later milestone
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def findings_by_severity(self) -> Dict[str, List[Finding]]:
        grouped: Dict[str, List[Finding]] = {}
        for finding in self.findings:
            grouped.setdefault(finding.severity.value, []).append(finding)
        return grouped

    def to_dict(self) -> Dict[str, Any]:
        return {
            "submission": self.submission.to_dict(),
            "findings": [f.to_dict() for f in self.findings],
            "remediations": [r.to_dict() for r in self.remediations],
            "pr_summary": self.pr_summary,
            "quality_score": self.quality_score,
            "created_at": self.created_at,
        }
