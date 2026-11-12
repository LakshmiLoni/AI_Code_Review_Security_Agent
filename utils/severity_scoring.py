"""Severity Scoring and Code Health Score Module.

Provides internal heuristic scoring inspired by CVSS v3.1 principles,
and calculates an overall repository Code Health Score out of 100.
All scores are internal analytical heuristics and not official security certifications.
"""
from typing import List, Dict, Any, Tuple


SEVERITY_RANGES = {
    "CRITICAL": (9.0, 10.0),
    "HIGH": (7.0, 8.9),
    "MEDIUM": (4.0, 6.9),
    "LOW": (0.1, 3.9),
}

# Penalty points deducted from 100 for each finding severity
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
    """Calculate internal CVSS-inspired heuristic score.

    Note: This is an internal heuristic risk score, not an official CVSS score.
    """
    sev = severity.upper()
    if sev not in SEVERITY_RANGES:
        sev = "MEDIUM"

    low_bound, high_bound = SEVERITY_RANGES[sev]
    spread = high_bound - low_bound

    # Interpolate based on exploitability and impact factors (0.0 - 1.0)
    factor = (exploitability * 0.5) + (impact * 0.5)
    factor = max(0.0, min(1.0, factor))

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
    else:
        return "LOW"


def calculate_code_health_score(findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate the overall Code Health Score out of 100.

    Formula:
        Base Health = 100.0
        Total Penalty = Sum(Severity Count * Penalty Weight)
        Health Score = Max(0.0, Base Health - Total Penalty)

    Weights:
        - Critical: 20 points
        - High: 10 points
        - Medium: 4 points
        - Low: 1 point

    Returns:
        Dictionary containing health_score, letter_grade, penalty_breakdown,
        severity_counts, and disclaimer.
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

    # Determine Letter Grade
    if health_score >= 90.0:
        grade = "A"
        grade_desc = "Excellent - Minimal or no security/quality findings detected."
    elif health_score >= 80.0:
        grade = "B"
        grade_desc = "Good - Minor quality smells or low-impact security concerns."
    elif health_score >= 70.0:
        grade = "C"
        grade_desc = "Fair - Moderate findings present; security remediation advised."
    elif health_score >= 60.0:
        grade = "D"
        grade_desc = "Poor - High-severity vulnerabilities detected; urgent attention required."
    else:
        grade = "F"
        grade_desc = "Critical - Multiple high/critical vulnerabilities compromising integrity."

    return {
        "health_score": health_score,
        "grade": grade,
        "grade_description": grade_desc,
        "total_penalty": total_penalty,
        "severity_counts": counts,
        "formula": "Score = max(0, 100 - (Critical*20 + High*10 + Medium*4 + Low*1))",
        "disclaimer": (
            "Notice: The Code Health Score is an automated internal heuristic metric "
            "designed to assist code review prioritization. It does not represent an "
            "official industry compliance certification or guarantee of complete security."
        ),
    }
