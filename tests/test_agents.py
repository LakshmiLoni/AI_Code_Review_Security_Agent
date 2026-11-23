"""Tests: Multi-Agent Integration Suite."""
import unittest
from agents.code_analysis_agent import CodeAnalysisAgent
from agents.security_agent import SecurityAgent
from agents.remediation_agent import RemediationAgent
from agents.pr_summary_agent import PRSummaryAgent
from agents.code_assistant_agent import CodeAssistantAgent
from services.agent_orchestrator import AgentOrchestrator


class TestAgents(unittest.TestCase):
    """Test all five specialized AI agents and their orchestration."""

    def test_remediation_agent_prioritization(self):
        agent = RemediationAgent()
        sample_findings = [
            {"title": "Low style smell", "severity": "LOW", "line_number": 5},
            {"title": "Critical SQL Injection", "severity": "CRITICAL", "line_number": 12},
            {"title": "Medium smell", "severity": "MEDIUM", "line_number": 8},
            {"title": "High hardcoded secret", "severity": "HIGH", "line_number": 3},
        ]
        result = agent.generate_remediation_plan(sample_findings, detected_language="python")
        roadmap = result["prioritized_roadmap"]
        self.assertEqual(len(roadmap), 4)
        self.assertEqual(roadmap[0]["severity"], "CRITICAL")
        self.assertEqual(roadmap[1]["severity"], "HIGH")

    def test_pr_summary_agent_verdicts(self):
        agent = PRSummaryAgent()

        # Critical findings -> Changes Requested
        crit_health = {"health_score": 45.0, "critical_count": 1, "grade": "F"}
        rev_crit = agent.generate_review([], "python", crit_health, {})
        self.assertEqual(rev_crit["pr_status"], "Changes Requested")

        # Clean code -> Approved
        clean_health = {"health_score": 98.0, "critical_count": 0, "grade": "A"}
        rev_clean = agent.generate_review([], "python", clean_health, {})
        self.assertEqual(rev_clean["pr_status"], "Approved")

    def test_code_assistant_agent_fallback(self):
        agent = CodeAssistantAgent()
        resp = agent.ask("How to prevent SQL injection in Python?")
        self.assertIn("answer", resp)
        self.assertIn("citations", resp)
        self.assertTrue(len(resp["answer"]) > 50)

    def test_orchestrator_end_to_end_python(self):
        orchestrator = AgentOrchestrator()
        code = (
            "import os\n"
            "def run_cmd(user_arg):\n"
            "    os.system('cat ' + user_arg)\n"
        )
        res = orchestrator.run_review(code, filename="test_runner.py")
        self.assertTrue(res["success"])
        self.assertEqual(res["detected_language"], "python")
        self.assertGreaterEqual(res["critical_count"], 1)
        self.assertEqual(res["pr_status"], "Changes Requested")


if __name__ == "__main__":
    unittest.main()
