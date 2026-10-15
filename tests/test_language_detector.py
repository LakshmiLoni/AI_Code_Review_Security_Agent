import pytest

from submission.language_detector import detect_for_file, detect_language

PYTHON_SNIPPET = '''
import os

def greet(name):
    if name:
        print(f"Hello {name}")
    else:
        print("Hello")

class Greeter:
    def __init__(self):
        self.count = 0
'''

JAVA_SNIPPET = '''
package demo;

import java.util.List;

public class Hello {
    private int count = 0;

    public static void main(String[] args) {
        System.out.println("Hello");
    }
}
'''


def test_detects_python():
    result = detect_language(PYTHON_SNIPPET)
    assert result.language == "python"
    assert result.is_confident
    assert result.confidence >= 0.65


def test_detects_java():
    result = detect_language(JAVA_SNIPPET)
    assert result.language == "java"
    assert result.is_confident


def test_short_python_function_detected():
    assert detect_language("def add(a, b):\n    return a + b\n").language == "python"


def test_short_java_statement_detected():
    code = 'public class A {\n    void f() {\n        System.out.println("x");\n    }\n}\n'
    assert detect_language(code).language == "java"


def test_invalid_python_still_detected_as_python():
    assert detect_language("def broken(name\n    print('x')\n").language == "python"


@pytest.mark.parametrize("text", ["", "   ", "\n\n\t"])
def test_empty_input_not_detected(text):
    result = detect_language(text)
    assert result.language is None
    assert result.confidence == 0.0


@pytest.mark.parametrize("text", ["hello world", "x = 1", "just some plain english sentence here", "42"])
def test_ambiguous_input_not_detected(text):
    result = detect_language(text)
    assert result.language is None
    assert "clearer" in result.message or "No code" in result.message


def test_mixed_code_is_ambiguous():
    mixed = "def f():\n    pass\n" + "public class A {\n}\nSystem.out.println(1);\n"
    result = detect_language(mixed)
    # Either clearly one language or refuses; must never claim high confidence for a coin-flip.
    assert result.language is None or result.confidence < 0.9


def test_extension_confirms_content():
    result = detect_for_file(PYTHON_SNIPPET, "tool.py")
    assert result.language == "python"
    assert not result.mismatch
    assert result.confidence >= 0.85


def test_extension_trusted_for_short_content():
    result = detect_for_file("x = 1\n", "tiny.py")
    assert result.language == "python"


def test_extension_mismatch_detected():
    result = detect_for_file(JAVA_SNIPPET, "script.py")
    assert result.mismatch
    assert result.language is None
    assert "Java" in result.message


def test_unknown_extension_falls_back_to_content():
    result = detect_for_file(JAVA_SNIPPET, "notes.txt")
    assert result.language == "java"
