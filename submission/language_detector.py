"""Heuristic, confidence-based detection of Python vs Java source code.

The detector never executes code. It counts weighted "evidence" patterns for each
language and turns the balance into a confidence score between 0 and 1.

* Pasted code  -> :func:`detect_language`
* Uploaded file -> :func:`detect_for_file` (extension is a strong hint that is
  cross-checked against the content).
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from config import settings

_M = re.MULTILINE

# (regex, weight, description). Each pattern's match count is capped at _MAX_HITS.
_PYTHON_PATTERNS: List[Tuple[re.Pattern, int, str]] = [
    (re.compile(r"^\s*(async\s+)?def\s+\w+\s*\(", _M), 3, "'def name(' function definition"),
    (re.compile(r"^\s*class\s+\w+\s*(\([^)]*\))?\s*:\s*$", _M), 3, "'class Name:' definition"),
    (re.compile(r"^\s*from\s+[\w.]+\s+import\s+", _M), 3, "'from x import y'"),
    (re.compile(r"^\s*import\s+[\w.]+(\s+as\s+\w+)?\s*(,\s*[\w.]+\s*)*$", _M), 2, "import without semicolon"),
    (re.compile(r"^\s*elif\b", _M), 3, "'elif' keyword"),
    (re.compile(r"^\s*(except\b.*|finally|else|try)\s*:\s*$", _M), 2, "try/except/else block ending in ':'"),
    (re.compile(r"^\s*with\s+.+:\s*$", _M), 2, "'with ...:' block"),
    (re.compile(r"^\s*(if|for|while)\s+[^{;]*:\s*$", _M), 2, "control statement ending in ':'"),
    (re.compile(r"\bif\s+__name__\s*==", _M), 3, "'__name__ ==' guard"),
    (re.compile(r"\bself\.\w+"), 1, "'self.' attribute access"),
    (re.compile(r"(?<![.\w])print\s*\("), 1, "print() call"),
    (re.compile(r"\b(True|False|None)\b"), 1, "True/False/None literals"),
    (re.compile(r"^\s*#(?!\s*include)", _M), 1, "'#' comment"),
    (re.compile(r"\bf[\"'][^\"'\n]*\{[^}\n]+\}"), 1, "f-string"),
    (re.compile(r"\blambda\b[^:\n]*:"), 1, "lambda expression"),
    (re.compile(r"^\s*(return|pass|raise|yield)\b[^;{}\n]*$", _M), 1, "statement without ';'"),
]

_JAVA_PATTERNS: List[Tuple[re.Pattern, int, str]] = [
    (re.compile(r"\bpublic\s+(static\s+)?(final\s+)?(abstract\s+)?(class|interface|enum|record)\s+\w+"), 4, "'public class/interface' declaration"),
    (re.compile(r"\bpublic\s+static\s+void\s+main\s*\("), 4, "'public static void main('"),
    (re.compile(r"^\s*package\s+[\w.]+\s*;", _M), 3, "'package x;' declaration"),
    (re.compile(r"^\s*import\s+(static\s+)?[\w.]+(\.\*)?\s*;", _M), 3, "'import x.y;' with semicolon"),
    (re.compile(r"System\.(out|err)\.print"), 3, "System.out/err.print*"),
    (re.compile(r"\b(private|protected|public)\s+(static\s+)?(final\s+)?[\w<>\[\],.? ]+\s+\w+\s*\([^)]*\)\s*(throws\s+[\w., ]+)?\s*\{?"), 2, "method with access modifier"),
    (re.compile(r"\b(private|protected)\b"), 1, "'private/protected' modifier"),
    (re.compile(r"\b(String|int|boolean|double|long|float|char|byte)(\[\])?\s+\w+\s*(=|;|,|\))"), 1, "typed declaration (String x = ...)"),
    (re.compile(r"\bnew\s+[A-Z]\w*\s*(<[^>]*>)?\s*[(\[]"), 2, "'new ClassName(' instantiation"),
    (re.compile(r"@(Override|SuppressWarnings|Deprecated|FunctionalInterface|SafeVarargs)\b"), 2, "Java annotation"),
    (re.compile(r"\bthrows\s+\w+"), 2, "'throws' clause"),
    (re.compile(r"\b(extends|implements)\s+\w+"), 1, "'extends/implements'"),
    (re.compile(r"\bcatch\s*\(\s*[\w.| ]+\s+\w+\s*\)"), 2, "'catch (Type e)'"),
    (re.compile(r"\btry\s*(\([^)]*\))?\s*\{"), 2, "'try {' block"),
    (re.compile(r";\s*$", _M), 1, "lines ending in ';'"),
    (re.compile(r"\{\s*$", _M), 1, "lines ending in '{'"),
    (re.compile(r"^\s*\}\s*(else|catch|finally)?.*$", _M), 1, "closing brace line"),
]

_MAX_HITS = 3
_MIN_EVIDENCE = 3  # below this total score the sample is considered too small/ambiguous


@dataclass
class DetectionResult:
    """Outcome of language detection."""

    language: Optional[str]  # "python" | "java" | None
    confidence: float
    scores: Dict[str, int] = field(default_factory=dict)
    reasons: List[str] = field(default_factory=list)
    extension_language: Optional[str] = None
    mismatch: bool = False  # file extension contradicts the content
    message: str = ""

    @property
    def is_confident(self) -> bool:
        return self.language is not None and self.confidence >= settings.DETECTION_CONFIDENCE_THRESHOLD


def _score(code: str, patterns) -> Tuple[int, List[str]]:
    total = 0
    reasons: List[str] = []
    for regex, weight, description in patterns:
        hits = len(regex.findall(code))
        if hits:
            points = min(hits, _MAX_HITS) * weight
            total += points
            reasons.append(f"{description} (x{hits}, +{points})")
    return total, reasons


def detect_language(code: str) -> DetectionResult:
    """Detect the language of pasted code from its content alone."""
    if code is None or not code.strip():
        return DetectionResult(None, 0.0, message="No code to analyse.")

    py_score, py_reasons = _score(code, _PYTHON_PATTERNS)
    java_score, java_reasons = _score(code, _JAVA_PATTERNS)
    scores = {"python": py_score, "java": java_score}
    total = py_score + java_score

    if total < _MIN_EVIDENCE:
        return DetectionResult(
            None, 0.0, scores,
            message="Not enough language-specific syntax to decide. "
                    "Please submit a longer or clearer code sample, or upload a correctly named .py / .java file.",
        )

    language = "python" if py_score >= java_score else "java"
    winner, loser = max(py_score, java_score), min(py_score, java_score)
    share = winner / total
    evidence = min(1.0, total / 10.0)
    confidence = round(share * (0.6 + 0.4 * evidence), 3)
    reasons = py_reasons if language == "python" else java_reasons

    if share < 0.65 or winner == loser:
        return DetectionResult(
            None, confidence, scores, reasons=reasons,
            message="The code contains syntax typical of both Python and Java, so the language is ambiguous. "
                    "Please submit a clearer code sample or upload a correctly named .py / .java file.",
        )
    if confidence < settings.DETECTION_CONFIDENCE_THRESHOLD:
        return DetectionResult(
            None, confidence, scores, reasons=reasons,
            message=f"Best guess is {language.title()}, but confidence is too low "
                    f"({confidence:.0%}). Please submit a longer or clearer code sample, "
                    "or upload a correctly named source file.",
        )
    return DetectionResult(language, confidence, scores, reasons=reasons,
                           message=f"Detected {language.title()} from code characteristics.")


def extension_language(filename: Optional[str]) -> Optional[str]:
    if not filename:
        return None
    return settings.SUPPORTED_EXTENSIONS.get(os.path.splitext(filename)[1].lower())


def detect_for_file(code: str, filename: Optional[str]) -> DetectionResult:
    """Detect language for an uploaded file, using the extension as a strong hint.

    * Extension and content agree (or content is inconclusive) -> trust the extension.
    * Content strongly contradicts the extension -> ``mismatch=True`` and no language,
      so the user can upload a correctly named file.
    """
    ext_lang = extension_language(filename)
    content = detect_language(code)

    if ext_lang is None:
        content.message = content.message or "Unsupported file extension."
        return content

    if content.language == ext_lang:
        boosted = round(min(1.0, 0.85 + 0.15 * content.confidence), 3)
        return DetectionResult(ext_lang, boosted, content.scores, content.reasons, ext_lang, False,
                               f"File extension and content both indicate {ext_lang.title()}.")

    if content.language and content.language != ext_lang and content.confidence >= settings.EXTENSION_OVERRIDE_CONFIDENCE:
        return DetectionResult(
            None, content.confidence, content.scores, content.reasons, ext_lang, True,
            f"The file is named '{filename}' ({ext_lang.title()}) but its content looks like "
            f"{content.language.title()} ({content.confidence:.0%} confidence). "
            "Please upload a correctly named source file.",
        )

    # Content inconclusive or only weakly contradictory: trust the extension, but be honest.
    return DetectionResult(ext_lang, 0.8, content.scores, content.reasons, ext_lang, False,
                           f"Language taken from the '{os.path.splitext(filename)[1]}' extension; "
                           "content was too short to confirm it.")
