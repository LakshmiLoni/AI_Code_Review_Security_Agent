"""Code Review Summary Agent.

Synthesizes findings into executive summaries, risk scores, status tags,
and transparent assessments of residual security risk.
"""

from typing import Dict, List, Any


class ReviewSummaryAgent:
    """Generates comprehensive review metrics, summaries, and remaining risk assessments."""

    STATIC_ANALYSIS_DISCLAIMER = (
        "IMPORTANT SECURITY DISCLAIMER: Static Application Security Testing (SAST) "
        "inspects source code patterns without executing the program with live runtime inputs. "
        "A scan with zero reported findings does NOT guarantee that the application is "
        "completely secure or free of logical, authentication, or infrastructure vulnerabilities."
    )

    def generate_summary(
        self,
        quality_findings: List[Dict[str, Any]],
        security_findings: List[Dict[str, Any]],
        parsed_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        critical_count = sum(1 for f in security_findings if f.get("severity") == "Critical")
        high_count = sum(1 for f in security_findings if f.get("severity") == "High")
        medium_count = sum(1 for f in security_findings if f.get("severity") == "Medium")
        low_count = sum(1 for f in security_findings if f.get("severity") == "Low")

        total_findings = len(quality_findings) + len(security_findings)

        # Calculate Security Score (100 base, deductions for findings)
        sec_penalty = (critical_count * 35) + (high_count * 20) + (medium_count * 10) + (low_count * 3)
        security_score = max(0.0, min(100.0, 100.0 - sec_penalty))

        # Calculate Quality Score
        qual_penalty = len(quality_findings) * 8
        if parsed_metrics.get("syntax_error"):
            qual_penalty += 50
        quality_score = max(0.0, min(100.0, 100.0 - qual_penalty))

        # Determine Final Review Status
        if parsed_metrics.get("syntax_error"):
            status = "Syntax Error - Remediation Required"
        elif critical_count > 0:
            status = "Critical Risk - Immediate Action Required"
        elif high_count > 0:
            status = "High Risk - Action Required"
        elif medium_count > 0 or len(quality_findings) > 3:
            status = "Moderate Risk - Refactoring Recommended"
        elif total_findings > 0:
            status = "Low Risk - Minor Improvements"
        else:
            status = "No Static Issues Detected - Human Review Advised"

        # Formulate executive narrative
        summary_paragraphs = []
        if critical_count > 0 or high_count > 0:
            summary_paragraphs.append(
                f"Static analysis flagged {critical_count} Critical and {high_count} High severity security vulnerabilities. "
                "These issues pose immediate operational and compliance risks (such as remote code execution, injection, or credential exposure) "
                "and must be remediated prior to merging into production branches."
            )
        elif total_findings > 0:
            summary_paragraphs.append(
                f"The review completed with {total_findings} total findings ({len(security_findings)} security, {len(quality_findings)} quality). "
                "The code structure is generally functional, but defense-in-depth improvements and code smells require attention."
            )
        else:
            summary_paragraphs.append(
                "No heuristic security flaws or maintainability warnings were detected during this static scan. "
                "The code complies with standard baseline checks for supported patterns."
            )

        # Remaining risks and limitations
        remaining_risks = [
            "Business logic flaws: Flawed transaction flows or state-machine bugs cannot be proved safe via static heuristics.",
            "Runtime infrastructure security: Cloud IAM permissions, container isolation, and TLS certificate validation require environmental testing.",
            "Third-party package vulnerabilities: Transitive library CVEs should be continuously scanned using Software Composition Analysis (SCA)."
        ]

        # Prioritized action items
        recommended_fixes = []
        for f in security_findings[:3]:
            recommended_fixes.append(f"[{f.get('severity')}] {f.get('title')}: {f.get('remediation')}")
        for q in quality_findings[:2]:
            recommended_fixes.append(f"[Quality] {q.get('title')}: {q.get('remediation')}")

        return {
            "status": status,
            "security_score": round(security_score, 1),
            "quality_score": round(quality_score, 1),
            "critical_count": critical_count,
            "high_count": high_count,
            "medium_count": medium_count,
            "low_count": low_count,
            "total_findings": total_findings,
            "summary_text": " ".join(summary_paragraphs),
            "remaining_risks": remaining_risks,
            "recommended_fixes": recommended_fixes,
            "disclaimer": self.STATIC_ANALYSIS_DISCLAIMER
        }
