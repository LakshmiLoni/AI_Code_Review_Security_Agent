"""Tests: Language Detection Suite."""
import unittest
from analysis.language_detector import detect_language, UnsupportedLanguageError


class TestLanguageDetection(unittest.TestCase):
    """Test automatic language detection for Python and Java."""

    def test_detect_python_by_extension(self):
        lang, conf, _ = detect_language("x = 1", filename="script.py")
        self.assertEqual(lang, "python")
        self.assertEqual(conf, 1.0)

    def test_detect_java_by_extension(self):
        lang, conf, _ = detect_language("int x = 1;", filename="App.java")
        self.assertEqual(lang, "java")
        self.assertEqual(conf, 1.0)

    def test_detect_pasted_python_code(self):
        code = "def calculate_sum(a, b):\n    return a + b\n"
        lang, conf, _ = detect_language(code)
        self.assertEqual(lang, "python")
        self.assertGreaterEqual(conf, 0.7)

    def test_detect_pasted_java_code(self):
        code = (
            "package com.example;\n"
            "public class Calculator {\n"
            "    public int add(int a, int b) {\n"
            "        return a + b;\n"
            "    }\n"
            "}\n"
        )
        lang, conf, _ = detect_language(code)
        self.assertEqual(lang, "java")
        self.assertGreaterEqual(conf, 0.7)

    def test_empty_code_raises_error(self):
        with self.assertRaises(UnsupportedLanguageError):
            detect_language("   ")

    def test_reject_unsupported_extension(self):
        with self.assertRaises(UnsupportedLanguageError):
            detect_language("cout << 1;", filename="main.cpp")


if __name__ == "__main__":
    unittest.main()
