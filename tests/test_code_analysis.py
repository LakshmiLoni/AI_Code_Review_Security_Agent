"""Tests for agents/code_analysis_agent.py."""
import unittest
from agents.code_analysis_agent import CodeAnalysisAgent


class TestCodeAnalysis(unittest.TestCase):
    """Test AST code analysis and smell detection for Python and Java."""

    def setUp(self):
        self.agent = CodeAnalysisAgent()

    def test_python_mutable_default_argument(self):
        code = """
def add_user(user, user_list=[]):
    user_list.append(user)
    return user_list
"""
        findings = self.agent.analyze(code, language="python", filename="user_service.py")
        mutable_findings = [f for f in findings if "Mutable Default" in f["title"]]
        self.assertGreaterEqual(len(mutable_findings), 1)
        self.assertEqual(mutable_findings[0]["severity"], "HIGH")

    def test_python_bare_except(self):
        code = """
def load_data():
    try:
        val = 1 / 0
    except:
        return None
"""
        findings = self.agent.analyze(code, language="python", filename="loader.py")
        bare_except = [f for f in findings if "Bare 'except:'" in f["title"]]
        self.assertGreaterEqual(len(bare_except), 1)

    def test_python_naming_convention(self):
        code = """
def ProcessUserData(data):
    return data
"""
        findings = self.agent.analyze(code, language="python", filename="processor.py")
        naming = [f for f in findings if "Non-Standard" in f["title"]]
        self.assertGreaterEqual(len(naming), 1)

    def test_java_empty_catch_block(self):
        code = """
public class DataProcessor {
    public void process() {
        try {
            int x = 10 / 0;
        } catch (Exception e) {
        }
    }
}
"""
        findings = self.agent.analyze(code, language="java", filename="DataProcessor.java")
        empty_catch = [f for f in findings if "Empty Catch Block" in f["title"]]
        self.assertGreaterEqual(len(empty_catch), 1)
        self.assertEqual(empty_catch[0]["severity"], "HIGH")

    def test_clean_python_code_has_no_high_smells(self):
        clean_code = """
def compute_area(width: float, height: float) -> float:
    \"\"\"Compute area of rectangle cleanly.\"\"\"
    if width <= 0 or height <= 0:
        raise ValueError("Dimensions must be positive")
    return width * height
"""
        findings = self.agent.analyze(clean_code, language="python", filename="geometry.py")
        high_issues = [f for f in findings if f["severity"] in ("CRITICAL", "HIGH")]
        self.assertEqual(len(high_issues), 0)


if __name__ == "__main__":
    unittest.main()
