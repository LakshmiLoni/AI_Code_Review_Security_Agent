"""Report generation service for JSON and Markdown security audit exports."""

import json
from typing import Dict, Any


class ReportService:
    """Exports review findings as standardized JSON and Markdown reports."""

    def generate_json_report(self, review: Dict[str, Any]) -> str:
        """Format review dictionary into formatted JSON string."""
        report_data = {
            "report_title": "AI Code Review & Security Analysis Report",
            "review_uuid": review.get("review_uuid"),
            "target_file": review.get("filename"),
            "language": review.get("language"),
            "created_at": review.get("created_at"),
            "status": review.get("status"),
            "scores": {
                "security_score": review.get("security_score"),
                "quality_score": review.get("quality_score")
            },
            "summary": review.get("summary_text"),
            "severity_breakdown": {
                "critical": review.get("critical_count", 0),
                "high": review.get("high_count", 0),
                "medium": review.get("medium_count", 0),
                "low": review.get("low_count", 0),
                "total_findings": review.get("total_findings", 0)
            },
            "security_findings": review.get("security_findings", []),
            "quality_findings": review.get("quality_findings", []),
            "disclaimer": review.get("metrics", {}).get(
                "disclaimer",
                "Static analysis results do not guarantee absolute security."
            )
        }
        return json.dumps(report_data, indent=2)

    def generate_markdown_report(self, review: Dict[str, Any]) -> str:
        """Format review into a complete, human-readable Markdown report."""
        lines = []
        lines.append("# AI Code Review & Security Analysis Report")
        lines.append("")
        lines.append(f"**Target File**: `{review.get('filename')}`  ")
        lines.append(f"**Language**: `{review.get('language')}`  ")
        lines.append(f"**Review Identifier**: `{review.get('review_uuid')}`  ")
        lines.append(f"**Generated On**: `{review.get('created_at')}`  ")
        lines.append(f"**Overall Status**: **{review.get('status')}**  ")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## Executive Summary")
        lines.append(f"- **Security Score**: **{review.get('security_score')}/100**")
        lines.append(f"- **Quality Score**: **{review.get('quality_score')}/100**")
        lines.append(f"- **Total Findings**: {review.get('total_findings')}")
        lines.append(f"- **Severity Counts**: Critical: {review.get('critical_count')}, High: {review.get('high_count')}, Medium: {review.get('medium_count')}, Low: {review.get('low_count')}")
        lines.append("")
        lines.append(f"> {review.get('summary_text')}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Security Findings
        sec_findings = review.get("security_findings", [])
        lines.append(f"## Security Findings ({len(sec_findings)})")
        lines.append("")
        if not sec_findings:
            lines.append("No security vulnerabilities detected by current static analysis rules.")
            lines.append("")
        else:
            for idx, f in enumerate(sec_findings, start=1):
                lines.append(f"### {idx}. [{f.get('severity')}] {f.get('title')}")
                lines.append(f"- **Rule ID**: `{f.get('rule_id')}`")
                lines.append(f"- **Line Number**: Line {f.get('line_number')}")
                lines.append(f"- **CWE**: {f.get('cwe_id', 'N/A')}")
                lines.append(f"- **OWASP**: {f.get('owasp_category', 'N/A')}")
                lines.append(f"- **KB Reference**: {f.get('kb_reference', 'N/A')}")
                lines.append("")
                lines.append(f"**Explanation**: {f.get('explanation')}")
                lines.append("")
                lines.append(f"**Why It Matters**: {f.get('why_it_matters')}")
                lines.append("")
                lines.append("**Vulnerable Code:**")
                lines.append(f"```{review.get('language')}")
                lines.append(f.get("code_snippet", ""))
                lines.append("```")
                lines.append("")
                lines.append("**Recommended Remediation:**")
                lines.append(f"{f.get('remediation')}")
                lines.append("")
                if f.get("remediated_code"):
                    lines.append(f"```{review.get('language')}")
                    lines.append(f.get("remediated_code"))
                    lines.append("```")
                    lines.append("")
                lines.append("---")
                lines.append("")

        # Quality Findings
        qual_findings = review.get("quality_findings", [])
        lines.append(f"## Code Quality Findings ({len(qual_findings)})")
        lines.append("")
        if not qual_findings:
            lines.append("No code quality defects detected.")
            lines.append("")
        else:
            for idx, q in enumerate(qual_findings, start=1):
                lines.append(f"### {idx}. [{q.get('severity')}] {q.get('title')}")
                lines.append(f"- **Rule ID**: `{q.get('rule_id')}` | **Line**: {q.get('line_number')}")
                lines.append(f"- **Explanation**: {q.get('explanation')}")
                lines.append(f"- **Remediation**: {q.get('remediation')}")
                lines.append("")

        lines.append("## Residual Risks & Disclaimer")
        lines.append("")
        lines.append(review.get("metrics", {}).get("disclaimer", "Static analysis does not guarantee complete security."))
        lines.append("")

        return "\n".join(lines)
