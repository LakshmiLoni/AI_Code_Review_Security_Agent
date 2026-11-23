"""Analysis: Code Quality & Health Assessment.

Calculates code health scores, maintainability metrics, and provides
standardized grading based on static review findings.
"""
from typing import List, Dict, Any, Tuple

SEVERITY_RANGES = {
    "CRITICAL": (9.0, 10.0),
    "HIGH": (7.0, 8.9),
    "MEDIUM": (4.0, 6.9),
    "LOW": (0.1, 3.9),
}

SEVERITY_PENALTIES = {
    "CRITICAL": 20.0,
    "HIGH": 10.0,
    "MEDIUM": 4.0,
    "LOW": 1.0,
}


def calculate_finding_score(
    severity: str,
    exploitability: float = 0.5,
    impact: float = 0.5
) -> float:
    """Calculate internal heuristic risk score (0.1 to 10.0)."""
    sev = severity.upper()
    if sev not in SEVERITY_RANGES:
        sev = "MEDIUM"

    low_bound, high_bound = SEVERITY_RANGES[sev]
    spread = high_bound - low_bound
    factor = max(0.0, min(1.0, (exploitability * 0.5) + (impact * 0.5)))
    score = low_bound + (spread * factor)
    return round(score, 1)


def get_severity_label(score: float) -> str:
    """Map a numerical risk score to its corresponding severity tier."""
    if score >= 9.0:
        return "CRITICAL"
    elif score >= 7.0:
        return "HIGH"
    elif score >= 4.0:
        return "MEDIUM"
    return "LOW"


def calculate_code_health_score(findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate the overall Code Health Score out of 100.

    Formula:
        Base Health = 100.0
        Total Penalty = Sum(Severity Count * Penalty Weight)
        Health Score = Max(0.0, Base Health - Total Penalty)
    """
    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for f in findings:
        sev = str(f.get("severity", "LOW")).upper()
        if sev in counts:
            counts[sev] += 1
        else:
            counts["LOW"] += 1

    total_penalty = (
        (counts["CRITICAL"] * SEVERITY_PENALTIES["CRITICAL"])
        + (counts["HIGH"] * SEVERITY_PENALTIES["HIGH"])
        + (counts["MEDIUM"] * SEVERITY_PENALTIES["MEDIUM"])
        + (counts["LOW"] * SEVERITY_PENALTIES["LOW"])
    )

    health_score = max(0.0, round(100.0 - total_penalty, 1))

    if health_score >= 90.0:
        grade = "A"
        grade_desc = "Excellent - Minimal or no security/quality findings detected."
    elif health_score >= 80.0:
        grade = "B"
        grade_desc = "Good - Minor quality smells or low-severity items found."
    elif health_score >= 70.0:
        grade = "C"
        grade_desc = "Acceptable - Moderate findings require remediation before release."
    elif health_score >= 50.0:
        grade = "D"
        grade_desc = "Poor - Significant security vulnerabilities or major anti-patterns."
    else:
        grade = "F"
        grade_desc = "Critical Risk - Multiple high/critical vulnerabilities detected."

    return {
        "health_score": health_score,
        "grade": grade,
        "grade_description": grade_desc,
        "total_penalty": total_penalty,
        "severity_counts": counts,
        "critical_count": counts["CRITICAL"],
        "high_count": counts["HIGH"],
        "medium_count": counts["MEDIUM"],
        "low_count": counts["LOW"],
        "total_findings": len(findings),
        "formula": "100 - (Critical*20 + High*10 + Medium*4 + Low*1)",
        "disclaimer": (
            "Code health scores are internal heuristic indicators and "
            "do not constitute an official security certification."
        ),
    }


__all__ = [
    "calculate_finding_score",
    "get_severity_label",
    "calculate_code_health_score",
    "SEVERITY_RANGES",
    "SEVERITY_PENALTIES",
]
