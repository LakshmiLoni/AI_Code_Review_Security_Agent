"""Tests for orchestrator/agent_orchestrator.py."""
import os
from orchestrator.agent_orchestrator import AgentOrchestrator
from database.db import get_db_session
from database.models import CodeReview


def test_orchestrator_end_to_end_python():
    code = """
import os
import hashlib

def login_user(username, password):
    query = f"SELECT * FROM users WHERE user='{username}'"
    pwd_hash = hashlib.md5(password.encode()).hexdigest()
    os.system(f"echo Logged in: {username}")
    return True
"""
    orch = AgentOrchestrator()
    result = orch.run_review(code, filename="auth_service.py")

    assert result["success"] is True
    assert result["detected_language"] == "python"
    assert result["review_id"].startswith("REV-")
    assert result["health_score"] < 70.0
    assert result["pr_status"] == "Changes Requested"
    assert result["critical_count"] >= 1

    # Verify JSON report was created on disk
    assert "json_report_path" in result
    assert os.path.exists(result["json_report_path"])

    # Verify PDF report was created on disk
    assert "pdf_report_path" in result
    assert os.path.exists(result["pdf_report_path"])

    # Verify database persistence
    session = get_db_session()
    db_review = session.query(CodeReview).filter_by(review_id=result["review_id"]).first()
    assert db_review is not None
    assert db_review.filename == "auth_service.py"
    session.close()


def test_orchestrator_end_to_end_java():
    code = """
package com.test;
import java.sql.*;

public class AccountDao {
    public void findAccount(Connection conn, String accountId) throws SQLException {
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery("SELECT * FROM accounts WHERE id = '" + accountId + "'");
    }
}
"""
    orch = AgentOrchestrator()
    result = orch.run_review(code, filename="AccountDao.java")

    assert result["success"] is True
    assert result["detected_language"] == "java"
    assert result["critical_count"] >= 1
    assert result["pr_status"] == "Changes Requested"
