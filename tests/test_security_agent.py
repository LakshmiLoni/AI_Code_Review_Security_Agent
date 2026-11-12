"""Tests for agents/security_agent.py."""
from agents.security_agent import SecurityAgent


def test_python_sql_injection_detection():
    agent = SecurityAgent()
    code = """
def get_user(cursor, username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    return cursor.fetchone()
"""
    findings = agent.analyze(code, language="python", filename="db.py")
    sqli = [f for f in findings if "SQL Injection" in f["title"]]
    assert len(sqli) >= 1
    assert sqli[0]["severity"] == "CRITICAL"
    assert "A03:2021" in sqli[0]["category"]


def test_python_command_injection():
    agent = SecurityAgent()
    code = """
import os

def backup(folder):
    os.system(f"tar -czf backup.tar.gz {folder}")
"""
    findings = agent.analyze(code, language="python", filename="backup.py")
    cmdi = [f for f in findings if "Command Injection" in f["title"]]
    assert len(cmdi) >= 1
    assert cmdi[0]["severity"] == "CRITICAL"


def test_python_insecure_deserialization():
    agent = SecurityAgent()
    code = """
import pickle

def parse_session(token):
    return pickle.loads(token)
"""
    findings = agent.analyze(code, language="python", filename="auth.py")
    deserial = [f for f in findings if "Deserialization" in f["title"]]
    assert len(deserial) >= 1
    assert deserial[0]["severity"] == "CRITICAL"


def test_java_sql_injection():
    agent = SecurityAgent()
    code = """
import java.sql.*;

public class UserAuth {
    public void queryUser(Connection conn, String user) throws SQLException {
        Statement stmt = conn.createStatement();
        String sql = "SELECT * FROM accounts WHERE name = '" + user + "'";
        ResultSet rs = stmt.executeQuery(sql);
    }
}
"""
    findings = agent.analyze(code, language="java", filename="UserAuth.java")
    sqli = [f for f in findings if "SQL Injection" in f["title"]]
    assert len(sqli) >= 1
    assert sqli[0]["severity"] == "CRITICAL"


def test_hardcoded_aws_secret():
    agent = SecurityAgent()
    code = """
AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
"""
    findings = agent.analyze(code, language="python", filename="cloud.py")
    secrets = [f for f in findings if "AWS Access Key" in f["title"]]
    assert len(secrets) >= 1
    assert secrets[0]["severity"] == "CRITICAL"


def test_secure_parameterized_query_avoids_false_positive():
    agent = SecurityAgent()
    code = """
def get_user_secure(cursor, username):
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    return cursor.fetchone()
"""
    findings = agent.analyze(code, language="python", filename="secure_db.py")
    sqli = [f for f in findings if "SQL Injection" in f["title"]]
    assert len(sqli) == 0
