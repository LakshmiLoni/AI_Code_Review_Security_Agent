"""Test suite for Report Generation Service."""

import unittest
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.report_service import ReportService


class TestReports(unittest.TestCase):
    def setUp(self):
        self.service = ReportService()
        self.mock_review = {
            "review_uuid": "test-uuid-123456",
            "filename": "demo_service.py",
            "language": "python",
            "created_at": "2026-10-27T12:00:00",
            "status": "Critical Risk - Immediate Action Required",
            "security_score": 45.0,
            "quality_score": 85.0,
            "critical_count": 1,
            "high_count": 1,
            "medium_count": 0,
            "low_count": 0,
            "total_findings": 2,
            "summary_text": "Demonstration review report with SQL injection and command injection.",
            "metrics": {
                "disclaimer": "Static analysis does not guarantee 100% security."
            },
            "security_findings": [
                {
                    "rule_id": "SEC-SQL-01",
                    "title": "SQL Injection Risk",
                    "severity": "Critical",
                    "line_number": 12,
                    "code_snippet": "cursor.execute(f'SELECT * FROM users WHERE id = {uid}')",
                    "explanation": "Dynamic query construction.",
                    "why_it_matters": "Exfiltrates records.",
                    "remediation": "Use parameter placeholders.",
                    "remediated_code": "cursor.execute('SELECT * FROM users WHERE id = ?', (uid,))",
                    "cwe_id": "CWE-89",
                    "owasp_category": "A03:2021"
                }
            ],
            "quality_findings": [
                {
                    "rule_id": "QUAL-IMP-01",
                    "title": "Unused Import: os",
                    "severity": "Low",
                    "line_number": 1,
                    "explanation": "os is imported but unused.",
                    "remediation": "Remove import os"
                }
            ]
        }

    def test_json_report_generation(self):
        json_output = self.service.generate_json_report(self.mock_review)
        parsed = json.loads(json_output)
        self.assertEqual(parsed["review_uuid"], "test-uuid-123456")
        self.assertEqual(parsed["target_file"], "demo_service.py")
        self.assertEqual(len(parsed["security_findings"]), 1)
        self.assertEqual(parsed["severity_breakdown"]["critical"], 1)

    def test_markdown_report_generation(self):
        md_output = self.service.generate_markdown_report(self.mock_review)
        self.assertIn("# AI Code Review & Security Analysis Report", md_output)
        self.assertIn("demo_service.py", md_output)
        self.assertIn("SQL Injection Risk", md_output)
        self.assertIn("CWE-89", md_output)
        self.assertIn("Static analysis does not guarantee", md_output)


if __name__ == "__main__":
    unittest.main()
