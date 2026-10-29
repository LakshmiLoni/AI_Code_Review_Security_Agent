"""Test suite for Code Quality Agent."""

import unittest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.code_parser import CodeParser
from app.agents.code_quality_agent import CodeQualityAgent


class TestCodeQualityAgent(unittest.TestCase):
    def setUp(self):
        self.parser = CodeParser()
        self.agent = CodeQualityAgent()

    def test_syntax_error_detection(self):
        code = "def broken_syntax(:\n    return 42"
        parsed = self.parser.parse(code, language="python")
        findings = self.agent.analyze(parsed)
        rule_ids = [f["rule_id"] for f in findings]
        self.assertIn("QUAL-SYNTAX-01", rule_ids)

    def test_unused_import_detection(self):
        code = """
import math
import sys

def calculate_square(x):
    return x * x
"""
        parsed = self.parser.parse(code, language="python")
        findings = self.agent.analyze(parsed)
        rule_ids = [f["rule_id"] for f in findings]
        self.assertIn("QUAL-IMP-01", rule_ids)

    def test_bare_except_detection(self):
        code = """
def fetch_data():
    try:
        do_something()
    except:
        pass
"""
        parsed = self.parser.parse(code, language="python")
        findings = self.agent.analyze(parsed)
        rule_ids = [f["rule_id"] for f in findings]
        self.assertIn("QUAL-ERR-01", rule_ids)

    def test_long_function_detection(self):
        body = "\n".join([f"    x_{i} = {i}" for i in range(40)])
        code = f"def monolithic_function():\n{body}\n    return x_0\n"
        parsed = self.parser.parse(code, language="python")
        findings = self.agent.analyze(parsed)
        rule_ids = [f["rule_id"] for f in findings]
        self.assertIn("QUAL-LEN-01", rule_ids)

    def test_java_empty_catch_detection(self):
        code = """
public class SafeHandler {
    public void execute() {
        try {
            int a = 1 / 0;
        } catch (Exception e) {}
    }
}
"""
        parsed = self.parser.parse(code, language="java")
        findings = self.agent.analyze(parsed)
        rule_ids = [f["rule_id"] for f in findings]
        self.assertIn("QUAL-JAVA-ERR-01", rule_ids)


if __name__ == "__main__":
    unittest.main()
