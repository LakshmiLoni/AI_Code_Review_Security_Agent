"""Tests for agents/remediation_agent.py and agents/pr_summary_agent.py."""
from agents.remediation_agent import RemediationAgent
from agents.pr_summary_agent import PRSummaryAgent
from utils.severity_scoring import calculate_code_health_score


def test_remediation_agent_prioritization():
    agent = RemediationAgent()
    mock_findings = [
        {
            "finding_type": "QUALITY",
            "title": "Non-Standard Naming",
            "severity": "LOW",
            "heuristic_score": 2.0,
            "line_number": 5,
            "description": "Naming smell",
            "evidence_snippet": "def MyFunc():",
            "corrected_code": "def my_func():",
            "remediation_recommendation": "Use snake_case",
        },
        {
            "finding_type": "SECURITY",
            "title": "SQL Injection",
            "severity": "CRITICAL",
            "heuristic_score": 9.8,
            "line_number": 12,
            "description": "Raw string formatting in SQL",
            "evidence_snippet": "cursor.execute(f'SELECT...')",
            "corrected_code": "cursor.execute('SELECT...', (val,))",
            "remediation_recommendation": "Use parameterized query",
        },
    ]

    plan = agent.generate_remediation_plan(mock_findings, detected_language="python")
    roadmap = plan["prioritized_roadmap"]

    assert len(roadmap) == 2
    # Critical should be first in prioritized roadmap
    assert roadmap[0]["severity"] == "CRITICAL"
    assert roadmap[0]["title"] == "SQL Injection"
    assert "remediation_code" in roadmap[0]
    assert len(plan["critical_actions"]) == 1


def test_pr_summary_agent_verdicts():
    agent = PRSummaryAgent()

    # Case 1: Critical finding -> Changes Requested
    crit_findings = [{"severity": "CRITICAL", "finding_type": "SECURITY", "title": "SQLi", "line_number": 10}]
    health_crit = calculate_code_health_score(crit_findings)
    review_crit = agent.generate_review(
        findings=crit_findings,
        detected_language="python",
        health_data=health_crit,
        remediation_data={"prioritized_roadmap": [], "critical_actions": ["Fix SQLi"]},
    )
    assert review_crit["pr_status"] == "Changes Requested"

    # Case 2: Clean code -> Approved
    clean_findings = []
    health_clean = calculate_code_health_score(clean_findings)
    review_clean = agent.generate_review(
        findings=clean_findings,
        detected_language="python",
        health_data=health_clean,
        remediation_data={"prioritized_roadmap": [], "critical_actions": []},
    )
    assert review_clean["pr_status"] == "Approved"
    assert review_clean["health_score"] == 100.0
