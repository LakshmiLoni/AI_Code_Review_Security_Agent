"""Module: Findings Manager.

Consolidates, deduplicates, sorts, filters, and formats findings from both
the Code Analysis and Security Vulnerability agents. Computes Code Health Scores
and groups findings for developer portal display.
"""
from typing import List, Dict, Any, Tuple
from utils.severity_scoring import calculate_code_health_score, calculate_finding_score


class FindingsManager:
    """Consolidates and manages code review findings."""

    SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}

    @classmethod
    def consolidate_findings(
        cls,
        quality_findings: List[Dict[str, Any]],
        security_findings: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Merge findings from both agents, eliminate duplicates, and sort by severity."""
        raw_list = []
        raw_list.extend(security_findings or [])
        raw_list.extend(quality_findings or [])

        # Deduplicate based on (line_number, title)
        seen = set()
        deduped = []
        for item in raw_list:
            key = (item.get("line_number", 1), item.get("title", ""))
            if key not in seen:
                seen.add(key)
                sev = str(item.get("severity", "LOW")).upper()
                if "heuristic_score" not in item:
                    item["heuristic_score"] = calculate_finding_score(sev)
                deduped.append(item)

        # Sort: Critical first, then High, Medium, Low, then by line number
        deduped.sort(
            key=lambda x: (
                cls.SEVERITY_ORDER.get(str(x.get("severity", "LOW")).upper(), 4),
                -x.get("heuristic_score", 0),
                x.get("line_number", 1),
            )
        )
        return deduped

    @classmethod
    def compute_summary_metrics(cls, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute health score and finding counts."""
        health_data = calculate_code_health_score(findings)
        counts = health_data["severity_counts"]

        security_count = sum(1 for f in findings if f.get("finding_type") == "SECURITY")
        quality_count = sum(1 for f in findings if f.get("finding_type") == "QUALITY")

        return {
            "total_findings": len(findings),
            "security_findings_count": security_count,
            "quality_findings_count": quality_count,
            "severity_counts": counts,
            "critical_count": counts.get("CRITICAL", 0),
            "high_count": counts.get("HIGH", 0),
            "medium_count": counts.get("MEDIUM", 0),
            "low_count": counts.get("LOW", 0),
            "health_score": health_data["health_score"],
            "grade": health_data["grade"],
            "grade_description": health_data["grade_description"],
            "total_penalty": health_data["total_penalty"],
            "formula": health_data["formula"],
            "disclaimer": health_data["disclaimer"],
        }

    @classmethod
    def filter_findings(
        cls,
        findings: List[Dict[str, Any]],
        finding_type: str = None,
        severity: str = None,
    ) -> List[Dict[str, Any]]:
        """Filter findings by type (SECURITY/QUALITY) or severity tier."""
        results = findings
        if finding_type:
            ft = finding_type.upper().strip()
            results = [f for f in results if f.get("finding_type", "").upper() == ft]
        if severity:
            sev = severity.upper().strip()
            results = [f for f in results if f.get("severity", "").upper() == sev]
        return results
