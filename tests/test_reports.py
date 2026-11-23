"""Tests: Reports Generation & Strict Privacy Suite."""
import os
import json
import unittest
import uuid
from reports.pdf_generator import PDFReportGenerator
from reports.json_generator import JSONReportGenerator
from reports.recommendation_formatter import RecommendationFormatter


class TestReports(unittest.TestCase):
    """Test report generation, table formatting, and privacy guarantees."""

    def setUp(self):
        self.pdf_gen = PDFReportGenerator()
        self.json_gen = JSONReportGenerator()
        self.test_review_id = f"TEST-REP-{uuid.uuid4().hex[:6]}"
        self.sample_review = {
            "review_id": self.test_review_id,
            "filename": "database_service.py",
            "detected_language": "python",
            "health_score": 72.0,
            "letter_grade": "C",
            "pr_status": "CHANGES_REQUESTED",
            "executive_summary": "Security analysis found SQL injection and hardcoded passwords.",
            "total_findings": 2,
            "critical_count": 1,
            "high_count": 1,
            "medium_count": 0,
            "low_count": 0,
            "findings": [
                {
                    "finding_type": "SECURITY",
                    "title": "SQL Injection via Query Formatting",
                    "category": "OWASP A03:2021 - Injection",
                    "severity": "CRITICAL",
                    "heuristic_score": 9.8,
                    "line_number": 24,
                    "filename": "database_service.py",
                    "description": "Dynamic SQL query formatting allows arbitrary query manipulation.",
                    "risk_explanation": "Attacker can bypass auth or dump database records.",
                    "remediation_recommendation": "Use parameterized queries with placeholder binding.",
                    "evidence_snippet": "cursor.execute('SELECT * FROM users WHERE name=' + user)",
                    "corrected_code": "cursor.execute('SELECT * FROM users WHERE name=%s', (user,))",
                },
                {
                    "finding_type": "SECURITY",
                    "title": "Hardcoded Database Password",
                    "category": "OWASP A07:2021 - Identification and Authentication Failures",
                    "severity": "HIGH",
                    "heuristic_score": 8.5,
                    "line_number": 12,
                    "filename": "database_service.py",
                    "description": "Database credentials hardcoded directly into source code.",
                    "risk_explanation": "Unauthorized database compromise via source repository inspection.",
                    "remediation_recommendation": "Externalize credentials to environment variables.",
                    "evidence_snippet": "DB_PASSWORD = '****SecretKey123!'",
                    "corrected_code": "DB_PASSWORD = os.environ.get('DB_PASSWORD')",
                }
            ],
            "roadmap": [
                {"step": 1, "title": "Fix SQL injection", "severity": "CRITICAL"},
                {"step": 2, "title": "Extract password to env", "severity": "HIGH"},
            ]
        }

    def tearDown(self):
        reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
        for ext in (".pdf", ".json"):
            fpath = os.path.join(reports_dir, f"{self.test_review_id}{ext}")
            if os.path.exists(fpath):
                try:
                    os.remove(fpath)
                except Exception:
                    pass

    def test_recommendation_formatter(self):
        rec_rows = RecommendationFormatter.format_recommendations_table(self.sample_review["findings"])
        self.assertEqual(len(rec_rows), 2)
        # Verify columns exist
        for r in rec_rows:
            self.assertIn("priority", r)
            self.assertIn("recommendation", r)
            self.assertIn("reason", r)
            self.assertIn("suggested_action", r)
        # Verify high priority first
        self.assertEqual(rec_rows[0]["priority"], "High")

    def test_generate_json_report_and_strict_privacy(self):
        json_path = self.json_gen.generate(self.sample_review)
        self.assertTrue(os.path.exists(json_path))

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Verify required report sections
        self.assertIn("report_information", data)
        self.assertIn("review_summary", data)
        self.assertIn("security_findings", data)
        self.assertIn("code_quality_assessment", data)
        self.assertIn("recommendations_for_improvement", data)
        self.assertIn("final_review_summary", data)

        # STRICT PRIVACY RESTRICTIONS:
        # Check that NO raw source code or corrected code blocks leaked into the JSON report
        serialized = json.dumps(data)
        self.assertNotIn("cursor.execute('SELECT * FROM users WHERE name=%s'", serialized)
        self.assertNotIn("SecretKey123!", serialized)

    def test_generate_pdf_report(self):
        pdf_path = self.pdf_gen.generate(self.sample_review)
        self.assertTrue(os.path.exists(pdf_path))
        self.assertGreater(os.path.getsize(pdf_path), 500)

        # Check PDF header
        with open(pdf_path, "rb") as f:
            header = f.read(8)
            self.assertTrue(header.startswith(b"%PDF-"))


if __name__ == "__main__":
    unittest.main()
