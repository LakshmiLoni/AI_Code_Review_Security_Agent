"""Tests: Security Analysis Suite."""
import unittest
from agents.security_agent import SecurityAgent


class TestSecurityAnalysis(unittest.TestCase):
    """Test OWASP security vulnerability detection and false positive suppression."""

    def setUp(self):
        self.agent = SecurityAgent()

    def test_python_sql_injection(self):
        code = 'query = f"SELECT * FROM users WHERE id = {user_id}"\ncursor.execute(query)'
        findings = self.agent.analyze(code, language="python", filename="auth.py")
        sqli = [f for f in findings if "SQL Injection" in f["title"]]
        self.assertGreaterEqual(len(sqli), 1)
        self.assertEqual(sqli[0]["severity"], "CRITICAL")
        self.assertTrue(sqli[0]["is_confirmed_pattern"])

    def test_parameterized_query_avoids_false_positive(self):
        code = 'cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))'
        findings = self.agent.analyze(code, language="python", filename="safe_auth.py")
        sqli = [f for f in findings if "SQL Injection" in f["title"]]
        self.assertEqual(len(sqli), 0)

    def test_python_command_injection(self):
        code = 'os.system("ping -c 1 " + host)'
        findings = self.agent.analyze(code, language="python", filename="net.py")
        cmd_inj = [f for f in findings if "Command Injection" in f["title"]]
        self.assertGreaterEqual(len(cmd_inj), 1)
        self.assertEqual(cmd_inj[0]["severity"], "CRITICAL")

    def test_python_insecure_deserialization(self):
        code = 'data = pickle.loads(untrusted_payload)'
        findings = self.agent.analyze(code, language="python", filename="cache.py")
        deser = [f for f in findings if "Insecure Deserialization" in f["title"]]
        self.assertGreaterEqual(len(deser), 1)
        self.assertEqual(deser[0]["severity"], "CRITICAL")

    def test_hardcoded_aws_secret(self):
        code = 'AWS_KEY = "AKIAIOSFODNN7EXAMPLE"'
        findings = self.agent.analyze(code, language="python", filename="creds.py")
        secrets = [f for f in findings if "AWS Access Key" in f["title"]]
        self.assertGreaterEqual(len(secrets), 1)
        self.assertEqual(secrets[0]["severity"], "CRITICAL")
        # Ensure evidence does not expose full key
        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", secrets[0]["evidence_snippet"])

    def test_java_sql_injection(self):
        code = (
            "String sql = \"SELECT * FROM users WHERE name = '\" + username + \"'\";\n"
            "Statement stmt = conn.createStatement();\n"
            "ResultSet rs = stmt.executeQuery(sql);"
        )
        findings = self.agent.analyze(code, language="java", filename="UserDao.java")
        sqli = [f for f in findings if "SQL Injection" in f["title"]]
        self.assertGreaterEqual(len(sqli), 1)
        self.assertEqual(sqli[0]["severity"], "CRITICAL")


if __name__ == "__main__":
    unittest.main()
