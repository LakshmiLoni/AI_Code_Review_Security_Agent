"""Reports: JSON Report Generator.

Generates structured JSON reports containing metadata, summary metrics,
classified findings, and prioritized recommendations.
Strictly excludes raw submitted code, corrected code snippets, and sensitive secrets.
"""
import os
import json
import datetime
from typing import Dict, Any, List
from config import Config
from .recommendation_formatter import RecommendationFormatter


class JSONReportGenerator:
    """Generates sanitized, structured JSON review reports."""

    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or Config.REPORTS_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def generate(self, review_data: Dict[str, Any]) -> str:
        """Generate and save sanitized JSON report.

        Returns:
            Path to the saved JSON report file.
        """
        review_id = review_data.get("review_id", "REV-UNKNOWN")
        filename = review_data.get("filename", "unknown_file")
        raw_findings = review_data.get("findings", [])

        # Process and sanitize findings
        security_findings = []
        quality_findings = []

        for f in raw_findings:
            finding_type = f.get("finding_type", "SECURITY")
            sanitized_finding = {
                "title": f.get("title", ""),
                "category": f.get("category", ""),
                "severity": str(f.get("severity", "LOW")).upper(),
                "heuristic_score": f.get("heuristic_score", 1.0),
                "affected_location": f"Line {f.get('line_number', 1)} in {filename}",
                "description": f.get("description", ""),
                "potential_impact": f.get("risk_explanation", ""),
                "suggested_remediation": f.get("remediation_recommendation", "") or f.get("suggested_improvement", ""),
                "is_confirmed_pattern": f.get("is_confirmed_pattern", True),
            }

            if finding_type == "SECURITY":
                security_findings.append(sanitized_finding)
            else:
                quality_findings.append(sanitized_finding)

        # Generate structured recommendation table
        recommendations_table = RecommendationFormatter.format_recommendations_table(raw_findings)

        report_payload = {
            "report_information": {
                "project_name": "AI Code Review & Security Analysis Agent",
                "audit_type": "Static Security & Code Quality Audit",
                "review_id": review_id,
                "review_date_utc": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "filename": filename,
                "detected_language": str(review_data.get("detected_language", "Unknown")).capitalize(),
            },
            "review_summary": {
                "overall_status": review_data.get("pr_status", "APPROVED"),
                "executive_summary": review_data.get("executive_summary", ""),
                "code_health_assessment": {
                    "health_score": review_data.get("health_score", 100.0),
                    "letter_grade": review_data.get("letter_grade", "A"),
                },
                "total_findings_by_severity": {
                    "total": review_data.get("total_findings", len(raw_findings)),
                    "critical": review_data.get("critical_count", 0),
                    "high": review_data.get("high_count", 0),
                    "medium": review_data.get("medium_count", 0),
                    "low": review_data.get("low_count", 0),
                },
            },
            "security_findings": {
                "critical": [f for f in security_findings if f["severity"] == "CRITICAL"],
                "high": [f for f in security_findings if f["severity"] == "HIGH"],
                "medium": [f for f in security_findings if f["severity"] == "MEDIUM"],
                "low": [f for f in security_findings if f["severity"] == "LOW"],
            },
            "code_quality_assessment": {
                "total_quality_smells": len(quality_findings),
                "findings": quality_findings,
            },
            "recommendations_for_improvement": recommendations_table,
            "final_review_summary": (
                f"Review concluded with status {review_data.get('pr_status', 'APPROVED')}. "
                f"The target artifact contains {review_data.get('critical_count', 0)} critical and "
                f"{review_data.get('high_count', 0)} high severity security issues requiring immediate remediation."
            ),
        }

        # Write to primary reports directory
        filepath = os.path.join(self.output_dir, f"{review_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report_payload, f, indent=2)

        # Also write to legacy reports directory for cross-compatibility if different
        if Config.LEGACY_REPORTS_DIR and os.path.abspath(Config.LEGACY_REPORTS_DIR) != os.path.abspath(self.output_dir):
            try:
                legacy_file = os.path.join(Config.LEGACY_REPORTS_DIR, f"{review_id}.json")
                with open(legacy_file, "w", encoding="utf-8") as lf:
                    json.dump(report_payload, lf, indent=2)
            except Exception:
                pass

        return filepath
