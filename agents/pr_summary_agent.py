"""Agent 4: PR Summary Agent.

Generates a professional GitHub-style Pull Request review summary.
Evaluates overall merge readiness into:
- Approved
- Approved with Suggestions
- Changes Requested
Synthesizes security observations, code quality metrics, and a prioritized remediation roadmap.
"""
from typing import List, Dict, Any


class PRSummaryAgent:
    """Agent 4: Produces automated pull request reviews with executive summaries."""

    def __init__(self):
        self.agent_name = "PR Summary Agent"

    def generate_review(
        self,
        findings: List[Dict[str, Any]],
        detected_language: str,
        health_data: Dict[str, Any],
        remediation_data: Dict[str, Any],
        filename: str = "source_code"
    ) -> Dict[str, Any]:
        """Synthesize findings and metrics into an authoritative PR review."""
        counts = health_data.get("severity_counts", {})
        critical_count = health_data.get("critical_count", counts.get("CRITICAL", 0))
        high_count = health_data.get("high_count", counts.get("HIGH", 0))
        medium_count = health_data.get("medium_count", counts.get("MEDIUM", 0))
        low_count = health_data.get("low_count", counts.get("LOW", 0))
        total_findings = len(findings)
        health_score = health_data.get("health_score", 100.0)

        # Determine PR Status
        if critical_count > 0 or high_count > 1 or health_score < 70.0:
            pr_status = "Changes Requested"
            status_badge = "[CHANGES REQUESTED]"
            verdict_note = (
                "Critical or high-severity security vulnerabilities were identified that violate "
                "repository security policies. These must be resolved before merging."
            )
        elif high_count == 1 or medium_count > 2 or health_score < 90.0:
            pr_status = "Approved with Suggestions"
            status_badge = "[APPROVED WITH SUGGESTIONS]"
            verdict_note = (
                "The code is structurally sound but includes moderate quality or potential security "
                "improvements that should be addressed in this PR or a follow-up task."
            )
        else:
            pr_status = "Approved"
            status_badge = "[APPROVED]"
            verdict_note = "All security and quality checks passed cleanly. Ready to merge."

        # Split observations
        security_obs = []
        quality_obs = []

        for f in findings:
            title = f.get("title", "")
            line = f.get("line_number", 1)
            sev = f.get("severity", "LOW")
            ftype = f.get("finding_type", "SECURITY")

            obs_entry = f"[{sev}] Line {line}: {title}"
            if ftype == "SECURITY":
                security_obs.append(obs_entry)
            else:
                quality_obs.append(obs_entry)

        # Executive summary text
        exec_summary = (
            f"Automated Code Review for '{filename}' ({detected_language.capitalize()}). "
            f"Overall Code Health Score: {health_score}/100 (Grade {health_data.get('grade', 'A')}). "
            f"Identified {total_findings} finding(s): {critical_count} Critical, {high_count} High, "
            f"{medium_count} Medium, {low_count} Low. Verdict: {pr_status}."
        )

        recommended_fixes = remediation_data.get("critical_actions", [])
        if not recommended_fixes and total_findings > 0:
            recommended_fixes = [
                f"Address {f.get('title')} at line {f.get('line_number')}"
                for f in findings[:3]
            ]

        # Markdown representation for GitHub-style pull request comments
        markdown_review = self._build_markdown_review(
            status_badge=status_badge,
            filename=filename,
            language=detected_language,
            health_score=health_score,
            grade=health_data.get("grade", "A"),
            verdict_note=verdict_note,
            critical=critical_count,
            high=high_count,
            medium=medium_count,
            low=low_count,
            security_obs=security_obs,
            quality_obs=quality_obs,
            remediation_roadmap=remediation_data.get("prioritized_roadmap", [])
        )

        return {
            "pr_status": pr_status,
            "status_badge": status_badge,
            "executive_summary": exec_summary,
            "verdict_note": verdict_note,
            "detected_language": detected_language,
            "total_findings": total_findings,
            "critical_count": critical_count,
            "high_count": high_count,
            "medium_count": medium_count,
            "low_count": low_count,
            "health_score": health_score,
            "letter_grade": health_data.get("grade", "A"),
            "security_observations": security_obs,
            "quality_observations": quality_obs,
            "recommended_fixes": recommended_fixes,
            "roadmap": remediation_data.get("prioritized_roadmap", []),
            "markdown_summary": markdown_review,
        }

    def _build_markdown_review(
        self,
        status_badge: str,
        filename: str,
        language: str,
        health_score: float,
        grade: str,
        verdict_note: str,
        critical: int,
        high: int,
        medium: int,
        low: int,
        security_obs: List[str],
        quality_obs: List[str],
        remediation_roadmap: List[Dict[str, Any]]
    ) -> str:
        lines = [
            f"## {status_badge}",
            f"> **File Reviewed:** `{filename}` | **Language:** `{language.capitalize()}`",
            f"> **Code Health Score:** `{health_score}/100` (Grade **{grade}**)",
            "",
            f"**Review Assessment:** {verdict_note}",
            "",
            "### Findings Breakdown",
            f"- **Critical:** {critical}",
            f"- **High:** {high}",
            f"- **Medium:** {medium}",
            f"- **Low:** {low}",
            "",
        ]

        if security_obs:
            lines.append("### Security Observations")
            for obs in security_obs[:6]:
                lines.append(f"- {obs}")
            lines.append("")

        if quality_obs:
            lines.append("### Code Quality & Maintainability")
            for obs in quality_obs[:6]:
                lines.append(f"- {obs}")
            lines.append("")

        if remediation_roadmap:
            lines.append("### Prioritized Remediation Roadmap")
            for step in remediation_roadmap[:4]:
                lines.append(
                    f"1. **[{step['severity']}] Line {step['line_number']}**: {step['title']}  \n"
                    f"   *Action:* `{step['remediation_code'].splitlines()[0]}`"
                )
            lines.append("")

        lines.append("---")
        lines.append("*Generated by AI Code Review & Security Analysis Agent*")
        return "\n".join(lines)
