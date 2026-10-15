import pytest

from submission.code_validator import (
    find_javac,
    validate_code,
    validate_java,
    validate_python,
)

JAVAC_AVAILABLE = find_javac() is not None
needs_javac = pytest.mark.skipif(not JAVAC_AVAILABLE, reason="javac (JDK) not installed")

VALID_JAVA = """public class Hello {
    public static void main(String[] args) {
        System.out.println("hi");
    }
}
"""

INVALID_JAVA = """public class Broken {
    public static void main(String[] args) {
        int x = 5
        System.out.println(x);
    }
}
"""


# ----------------------------------------------------------------- Python
def test_valid_python():
    result = validate_python("def f(x):\n    return x * 2\n")
    assert result.status == "valid"
    assert result.is_valid
    assert result.tool == "ast"


def test_invalid_python_reports_line():
    result = validate_python("x = 1\ndef broken(:\n    pass\n")
    assert result.status == "invalid"
    assert result.issues[0].line == 2
    assert result.issues[0].message


def test_indentation_error_is_explained():
    result = validate_python("def f():\nreturn 1\n")
    assert result.status == "invalid"
    assert "ndent" in result.issues[0].message


def test_python_validation_never_executes_code(tmp_path):
    marker = tmp_path / "executed.txt"
    code = f"open(r'{marker}', 'w').write('boom')\nraise SystemExit(1)\n"
    result = validate_python(code)
    assert result.status == "valid"      # parsed only
    assert not marker.exists()


def test_python_null_bytes_handled():
    result = validate_python("x = 1\x00")
    assert result.status == "invalid"


def test_dispatcher_unknown_language_skipped():
    assert validate_code("whatever", None).status == "skipped"


# ----------------------------------------------------------------- Java
@needs_javac
def test_valid_java_compiles():
    result = validate_java(VALID_JAVA)
    assert result.status == "valid"
    assert result.tool == "javac"


@needs_javac
def test_invalid_java_reports_line():
    result = validate_java(INVALID_JAVA)
    assert result.status == "invalid"
    assert result.issues[0].line == 3
    assert "';'" in result.issues[0].message


@needs_javac
def test_java_never_executes_code(tmp_path):
    marker = tmp_path / "executed.txt"
    code = (
        "public class Evil {\n"
        "    static { try { new java.io.FileWriter(\"" + str(marker).replace("\\", "\\\\") + "\").close(); } catch (Exception e) {} }\n"
        "    public static void main(String[] a) {}\n"
        "}\n"
    )
    assert validate_java(code).status == "valid"
    assert not marker.exists()


@needs_javac
def test_non_public_class_name_does_not_break_validation():
    assert validate_java("class Helper { int f() { return 1; } }").status == "valid"


def test_java_unavailable_is_graceful(monkeypatch):
    monkeypatch.setattr("submission.code_validator.find_javac", lambda: None)
    result = validate_java(VALID_JAVA)
    assert result.status == "unavailable"
    assert any("JDK" in w for w in result.warnings)
    assert not result.issues


def test_java_unavailable_bracket_hint(monkeypatch):
    monkeypatch.setattr("submission.code_validator.find_javac", lambda: None)
    result = validate_java("public class A {\n void f() {\n")
    assert result.status == "unavailable"
    assert any("Unclosed" in w for w in result.warnings)


def test_java_bad_javac_path_is_graceful():
    result = validate_java(VALID_JAVA, javac_path="/definitely/not/javac")
    assert result.status == "unavailable"
    assert result.warnings
