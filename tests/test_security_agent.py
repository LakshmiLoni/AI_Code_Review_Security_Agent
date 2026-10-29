"""Test suite for Security Vulnerability Detection Agent."""

import unittest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.code_parser import CodeParser
from app.agents.security_agent import SecurityAgent


class TestSecurityAgent(unittest.TestCase):
    def setUp(self):
        self.parser = CodeParser()
        self.agent = SecurityAgent()

    def test_sql_injection_detection(self):
        code = """
import sqlite3
def get_user(uid):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = '{uid}'")
"""
        parsed = self.parser.parse(code, language="python")
        findings = self.agent.analyze(parsed)
        rule_ids = [f["rule_id"] for f in findings]
        self.assertIn("SEC-SQL-01", rule_ids)
        self.assertEqual(findings[0]["severity"], "Critical")

    def test_command_injection_detection(self):
        code = """
import os
def ping(host):
    os.system("ping -c 1 " + host)
"""
        parsed = self.parser.parse(code, language="python")
        findings = self.agent.analyze(parsed)
        rule_ids = [f["rule_id"] for f in findings]
        self.assertIn("SEC-CMD-01", rule_ids)

    def test_eval_code_execution_detection(self):
        code = """
def run_math(user_expr):
    return eval(user_expr)
"""
        parsed = self.parser.parse(code, language="python")
        findings = self.agent.analyze(parsed)
        rule_ids = [f["rule_id"] for f in findings]
        self.assertIn("SEC-EVAL-01", rule_ids)

    def test_pickle_deserialization_detection(self):
        code = """
import pickle
def restore(b):
    return pickle.loads(b)
"""
        parsed = self.parser.parse(code, language="python")
        findings = self.agent.analyze(parsed)
        rule_ids = [f["rule_id"] for f in findings]
        self.assertIn("SEC-DESER-01", rule_ids)

    def test_hardcoded_secret_detection(self):
        code = """
AWS_ACCESS_KEY_ID = "YOUR_AWS_ACCESS_KEY_ID"
API_KEY = "YOUR_API_KEY"
"""
        parsed = self.parser.parse(code, language="python")
        findings = self.agent.analyze(parsed)
        rule_ids = [f["rule_id"] for f in findings]
        self.assertTrue(any("SECRET" in r for r in rule_ids))

    def test_weak_cryptography_md5(self):
        code = """
import hashlib
def hash_pass(pwd):
    return hashlib.md5(pwd.encode()).hexdigest()
"""
        parsed = self.parser.parse(code, language="python")
        findings = self.agent.analyze(parsed)
        rule_ids = [f["rule_id"] for f in findings]
        self.assertIn("SEC-CRYPTO-01", rule_ids)

    def test_insecure_randomness_token(self):
        code = """
import random
def generate_auth_token():
    return str(random.randint(100000, 999999))
"""
        parsed = self.parser.parse(code, language="python")
        findings = self.agent.analyze(parsed)
        rule_ids = [f["rule_id"] for f in findings]
        self.assertIn("SEC-RAND-01", rule_ids)

    def test_java_sql_injection(self):
        code = """
public class AccountDAO {
    public void query(Connection conn, String id) throws Exception {
        Statement stmt = conn.createStatement();
        stmt.executeQuery("SELECT * FROM accounts WHERE id = " + id);
    }
}
"""
        parsed = self.parser.parse(code, language="java")
        findings = self.agent.analyze(parsed)
        rule_ids = [f["rule_id"] for f in findings]
        self.assertIn("SEC-JAVA-SQL-01", rule_ids)


if __name__ == "__main__":
    unittest.main()
