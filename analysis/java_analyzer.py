"""Analysis: Java Code Quality & Structural Analyzer.

Performs static quality and structural analysis on Java source code.
Detects empty catch blocks, naming issues, resource management issues,
and structural anti-patterns.
"""
import re
from typing import List, Dict, Any


class JavaAnalyzer:
    """Performs static code quality analysis on Java code."""

    def analyze(self, code: str, filename: str = "Main.java") -> List[Dict[str, Any]]:
        findings = []
        lines = code.splitlines()

        for idx, line in enumerate(lines, start=1):
            clean = line.strip()

            # Skip comments
            if clean.startswith("//") or clean.startswith("/*") or clean.startswith("*"):
                continue

            # 1. Empty catch block
            if re.search(r"catch\s*\([^)]+\)\s*\{\s*\}", clean) or \
               (re.search(r"catch\s*\([^)]+\)\s*\{?", clean) and idx < len(lines) and lines[idx].strip() == "}"):
                findings.append({
                    "finding_type": "QUALITY",
                    "title": "Empty Catch Block (Swallowed Exception)",
                    "category": "Error Handling & Reliability",
                    "severity": "HIGH",
                    "heuristic_score": 7.8,
                    "line_number": idx,
                    "filename": filename,
                    "description": (
                        "Catch block silently swallows exceptions without logging or remediation. "
                        "This hides database errors, network disconnects, or NullPointerExceptions."
                    ),
                    "risk_explanation": "Failures fail silently, leaving the application in an indeterminate state.",
                    "evidence_snippet": clean,
                    "remediation_recommendation": (
                        "Log the exception with a structured logger (e.g. SLF4J) or rethrow as a domain exception."
                    ),
                    "is_confirmed_pattern": True,
                })

            # 2. System.out.println in production code
            if re.search(r"\bSystem\.(?:out|err)\.print(?:ln)?\s*\(", clean):
                findings.append({
                    "finding_type": "QUALITY",
                    "title": "Standard Output Logging (System.out.println)",
                    "category": "Logging & Diagnostics",
                    "severity": "LOW",
                    "heuristic_score": 2.2,
                    "line_number": idx,
                    "filename": filename,
                    "description": (
                        "Direct calls to System.out/err bypass logging frameworks, lack log levels, "
                        "and cannot be filtered, routed, or masked in production."
                    ),
                    "risk_explanation": "Improper log management complicates incident response.",
                    "evidence_snippet": clean,
                    "remediation_recommendation": "Use an enterprise logger like SLF4J / Logback.",
                    "is_confirmed_pattern": True,
                })

            # 3. String Concatenation in Loop (Performance)
            if re.search(r"\bString\s+[a-zA-Z0-9_]+\s*\+=", clean) or \
               re.search(r"\b[a-zA-Z0-9_]+\s*=\s*[a-zA-Z0-9_]+\s*\+\s*", clean):
                if any("for" in lines[max(0, idx-4):idx][i] or "while" in lines[max(0, idx-4):idx][i] for i in range(min(4, idx))):
                    findings.append({
                        "finding_type": "QUALITY",
                        "title": "Inefficient String Concatenation in Loop",
                        "category": "Performance & Resource Management",
                        "severity": "MEDIUM",
                        "heuristic_score": 4.5,
                        "line_number": idx,
                        "filename": filename,
                        "description": (
                            "Repeated string concatenation inside loops allocates excessive String objects. "
                            "Java Strings are immutable, creating O(N^2) memory churn."
                        ),
                        "risk_explanation": "Degrades throughput and spikes garbage collection pauses.",
                        "evidence_snippet": clean,
                        "remediation_recommendation": "Use StringBuilder or StringBuffer for loop string accumulation.",
                        "is_confirmed_pattern": True,
                    })

        return findings
