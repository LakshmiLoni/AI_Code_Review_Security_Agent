"""Tests: Database & Review Repository Suite."""
import unittest
import uuid
from database.review_repository import ReviewRepository
from database.models import CodeReview


class TestDatabase(unittest.TestCase):
    """Test SQLite database operations and ReviewRepository."""

    def setUp(self):
        self.repo = ReviewRepository()
        self.test_review_id = f"TEST-REV-{uuid.uuid4().hex[:8]}"

    def test_save_and_retrieve_review(self):
        review_data = {
            "review_id": self.test_review_id,
            "filename": "unit_test.py",
            "detected_language": "python",
            "health_score": 85.0,
            "letter_grade": "B",
            "pr_status": "APPROVED_WITH_SUGGESTIONS",
            "executive_summary": "Test executive summary for unit test.",
            "total_findings": 1,
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 1,
            "low_count": 0,
            "findings": [
                {
                    "finding_type": "SECURITY",
                    "title": "Medium severity test finding",
                    "category": "Test Category",
                    "severity": "MEDIUM",
                    "heuristic_score": 5.0,
                    "line_number": 10,
                    "filename": "unit_test.py",
                    "description": "Test finding description",
                    "risk_explanation": "Test risk",
                    "remediation_recommendation": "Test remediation",
                }
            ],
            "roadmap": [{"step": 1, "title": "Fix medium smell", "severity": "MEDIUM"}],
        }

        # 1. Save
        saved = self.repo.save_review(review_data)
        self.assertTrue(saved)

        # 2. Retrieve
        retrieved = self.repo.get_review_by_id(self.test_review_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["filename"], "unit_test.py")
        self.assertEqual(retrieved["health_score"], 85.0)
        self.assertEqual(len(retrieved["findings"]), 1)

        # 3. Clean up
        deleted = self.repo.delete_review(self.test_review_id)
        self.assertTrue(deleted)
        self.assertIsNone(self.repo.get_review_by_id(self.test_review_id))

    def test_get_dashboard_metrics(self):
        metrics = self.repo.get_dashboard_metrics()
        self.assertIn("total_reviews", metrics)
        self.assertIn("avg_health_score", metrics)
        self.assertIn("critical_count", metrics)
        self.assertIn("languages", metrics)


if __name__ == "__main__":
    unittest.main()
