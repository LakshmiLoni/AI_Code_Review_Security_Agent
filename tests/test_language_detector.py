"""Tests for utils/language_detector.py."""
from utils.language_detector import detect_language, UnsupportedLanguageError


def test_detect_python_by_extension():
    code = "x = 10"
    lang, conf, reason = detect_language(code, filename="main.py")
    assert lang == "python"
    assert conf == 1.0


def test_detect_java_by_extension():
    code = "int x = 10;"
    lang, conf, reason = detect_language(code, filename="App.java")
    assert lang == "java"
    assert conf == 1.0


def test_reject_unsupported_extension():
    raised = False
    try:
        detect_language("cout << 'hello';", filename="program.cpp")
    except UnsupportedLanguageError as exc:
        raised = True
        assert "Unsupported file format" in str(exc)
    assert raised, "Expected UnsupportedLanguageError was not raised"


def test_detect_pasted_python_code():
    code = """
def calculate_metrics(items):
    total = 0
    for item in items:
        total += item
    return total

if __name__ == '__main__':
    print(calculate_metrics([1, 2, 3]))
"""
    lang, conf, reason = detect_language(code)
    assert lang == "python"
    assert conf >= 0.70


def test_detect_pasted_java_code():
    code = """
package com.example.service;

import java.util.List;

public class MetricService {
    public int calculateMetrics(List<Integer> items) {
        int total = 0;
        for (int item : items) {
            total += item;
        }
        System.out.println("Total: " + total);
        return total;
    }
}
"""
    lang, conf, reason = detect_language(code)
    assert lang == "java"
    assert conf >= 0.70


def test_empty_code_raises_error():
    raised = False
    try:
        detect_language("   ")
    except UnsupportedLanguageError:
        raised = True
    assert raised, "Expected UnsupportedLanguageError on empty code"
