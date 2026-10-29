"""Test suite for Flask Web Routes and Endpoints."""

import unittest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.config import Config


class TestWebRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Configure app in testing mode with temporary test database
        cls.test_config = Config()
        cls.test_config.DATABASE_PATH = PROJECT_ROOT / "data" / "test_reviews.db"
        cls.app = create_app(cls.test_config)
        cls.client = cls.app.test_client()

    def test_home_page(self):
        """Verify home page loads successfully with 200 OK."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AI Code Review", response.data)

    def test_dashboard_page(self):
        """Verify dashboard route loads with metrics and charts."""
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Security Operations Dashboard", response.data)

    def test_new_review_page(self):
        """Verify new review submission form loads."""
        response = self.client.get("/reviews/new")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Submit Code for Review", response.data)

    def test_code_submission_and_detail(self):
        """Verify submitting code creates a review and redirects to detail page."""
        test_code = """
import os
def run_command(cmd):
    os.system(cmd)
"""
        response = self.client.post("/reviews/submit", data={
            "source_code": test_code,
            "filename": "test_cmd.py",
            "language": "python"
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"test_cmd", response.data)
        self.assertIn(b"Command Injection Risk", response.data)

    def test_review_history_page(self):
        """Verify review history renders."""
        response = self.client.get("/reviews/history")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Review History", response.data)

    def test_assistant_chat_api(self):
        """Verify conversational assistant chat API responds properly."""
        payload = {"question": "What is SQL injection?", "review_uuid": ""}
        response = self.client.post("/assistant/chat", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("response", data)
        self.assertIn("SQL", data["response"])

    def test_api_kb_stats(self):
        """Verify /api/kb/stats endpoint returns line count >= 1200."""
        response = self.client.get("/api/kb/stats")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertGreaterEqual(data["nonblank_line_count"], 1200)
        self.assertTrue(data["meets_requirement"])


if __name__ == "__main__":
    unittest.main()
