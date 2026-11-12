"""Tests for agents/code_analysis_agent.py."""
from agents.code_analysis_agent import CodeAnalysisAgent


def test_python_mutable_default_argument():
    agent = CodeAnalysisAgent()
    code = """
def add_user(user, user_list=[]):
    user_list.append(user)
    return user_list
"""
    findings = agent.analyze(code, language="python", filename="user_service.py")
    mutable_findings = [f for f in findings if "Mutable Default" in f["title"]]
    assert len(mutable_findings) >= 1
    assert mutable_findings[0]["severity"] == "HIGH"


def test_python_bare_except():
    agent = CodeAnalysisAgent()
    code = """
def load_data():
    try:
        val = 1 / 0
    except:
        return None
"""
    findings = agent.analyze(code, language="python", filename="loader.py")
    bare_except = [f for f in findings if "Bare 'except:'" in f["title"]]
    assert len(bare_except) >= 1


def test_python_naming_convention():
    agent = CodeAnalysisAgent()
    code = """
def ProcessUserData(data):
    return data
"""
    findings = agent.analyze(code, language="python", filename="processor.py")
    naming = [f for f in findings if "Non-Standard" in f["title"]]
    assert len(naming) >= 1


def test_java_empty_catch_block():
    agent = CodeAnalysisAgent()
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
    findings = agent.analyze(code, language="java", filename="DataProcessor.java")
    empty_catch = [f for f in findings if "Empty Catch Block" in f["title"]]
    assert len(empty_catch) >= 1
    assert empty_catch[0]["severity"] == "HIGH"


def test_clean_python_code_has_no_high_smells():
    agent = CodeAnalysisAgent()
    clean_code = """
def compute_area(width: float, height: float) -> float:
    \"\"\"Compute area of rectangle cleanly.\"\"\"
    if width <= 0 or height <= 0:
        raise ValueError("Dimensions must be positive")
    return width * height
"""
    findings = agent.analyze(clean_code, language="python", filename="geometry.py")
    high_issues = [f for f in findings if f["severity"] in ("CRITICAL", "HIGH")]
    assert len(high_issues) == 0
