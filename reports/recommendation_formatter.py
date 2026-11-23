"""Reports: Recommendation Formatter.

Extracts, prioritizes, deduplicates, and formats recommendations from review
findings into a structured tabular representation for PDF and JSON reports.
"""
from typing import List, Dict, Any


class RecommendationFormatter:
    """Formats actionable review recommendations into structured table rows."""

    SEVERITY_TO_PRIORITY = {
        "CRITICAL": "High",
        "HIGH": "High",
        "MEDIUM": "Medium",
        "LOW": "Low",
    }

    PRIORITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}

    @classmethod
    def format_recommendations_table(cls, findings: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Generate deduplicated, prioritized recommendation rows.

        Returns:
            List of dicts with keys:
            - priority: 'High', 'Medium', or 'Low'
            - recommendation: Concise action item
            - reason: Justification for why this matters
            - suggested_action: Concrete architectural or coding next step
        """
        seen_actions = set()
        table_rows = []

        # Sort findings by severity
        sev_rank = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        sorted_findings = sorted(
            findings,
            key=lambda f: (sev_rank.get(str(f.get("severity", "LOW")).upper(), 4), f.get("line_number", 1))
        )

        for f in sorted_findings:
            sev = str(f.get("severity", "LOW")).upper()
            priority = cls.SEVERITY_TO_PRIORITY.get(sev, "Low")
            title = f.get("title", "")
            category = f.get("category", "")
            raw_rec = f.get("remediation_recommendation", "") or f.get("suggested_improvement", "")
            risk = f.get("risk_explanation", "") or f.get("description", "")

            # Create a deduplication key based on title or category
            norm_key = title.lower().strip()
            if any(term in norm_key for term in ["sql injection", "sqli"]):
                dedup_key = "sql_injection"
                rec_title = "Implement Parameterized SQL Queries"
                reason = "Dynamic string concatenation allows unauthorized database access or extraction."
                action = "Replace query string formatting with bound parameter placeholders (%s, ?)."
            elif any(term in norm_key for term in ["command injection", "os command"]):
                dedup_key = "command_injection"
                rec_title = "Eliminate OS Shell Command Execution"
                reason = "Shell execution permits arbitrary host system takeover via untrusted input."
                action = "Use safe process execution with argument vectors and shell=False."
            elif any(term in norm_key for term in ["deserialization", "pickle"]):
                dedup_key = "deserialization"
                rec_title = "Replace Insecure Object Deserialization"
                reason = "Deserializing untrusted data can trigger arbitrary remote code execution."
                action = "Adopt strict schema serialization formats such as JSON or Protocol Buffers."
            elif any(term in norm_key for term in ["secret", "credential", "password", "aws"]):
                dedup_key = "secrets_management"
                rec_title = "Externalize Embedded Credentials"
                reason = "Hardcoded secrets in source control expose accounts to unauthorized compromise."
                action = "Store credentials in environment variables or an enterprise secrets vault."
            elif any(term in norm_key for term in ["xss", "cross-site scripting"]):
                dedup_key = "xss"
                rec_title = "Apply Context-Aware Output Encoding"
                reason = "Unescaped user input rendered in browser documents leads to script execution."
                action = "Enable template auto-escaping and encode dynamic values before output."
            elif any(term in norm_key for term in ["path traversal", "directory traversal"]):
                dedup_key = "path_traversal"
                rec_title = "Validate and Canonicalize File Paths"
                reason = "Relative directory navigation permits unauthorized access to sensitive files."
                action = "Resolve paths with realpath/getCanonicalPath and verify base directory containment."
            elif any(term in norm_key for term in ["cryptographic", "md5", "sha-1", "crypto"]):
                dedup_key = "cryptography"
                rec_title = "Upgrade to Modern Cryptographic Standards"
                reason = "Legacy algorithms (MD5, DES, ECB) suffer known collision and predictability attacks."
                action = "Use SHA-256 for data verification and AES-GCM or bcrypt for passwords."
            elif any(term in norm_key for term in ["bare 'except'", "bare except"]):
                dedup_key = "bare_except"
                rec_title = "Catch Specific Exception Types"
                reason = "Bare exception handlers mask system interrupts and unexpected fatal errors."
                action = "Catch specific error classes (e.g. ValueError, KeyError) instead of BaseException."
            elif any(term in norm_key for term in ["mutable default", "default argument"]):
                dedup_key = "mutable_default"
                rec_title = "Avoid Mutable Default Arguments"
                reason = "Default lists/dicts are shared across all calls, causing cross-call state leakage."
                action = "Set default parameter to None and initialize new collections inside the function."
            elif any(term in norm_key for term in ["empty catch"]):
                dedup_key = "empty_catch"
                rec_title = "Log or Handle Swallowed Exceptions"
                reason = "Empty catch blocks silence operational failures, hindering fault diagnosis."
                action = "Log exception stack details with an enterprise logger or propagate upward."
            elif any(term in norm_key for term in ["overly long", "long function"]):
                dedup_key = "long_function"
                rec_title = "Refactor Large Functions into Modules"
                reason = "Excessively long methods impair maintainability and complicate test coverage."
                action = "Decompose methods longer than 35 lines into focused single-responsibility helpers."
            else:
                dedup_key = title.lower()[:30]
                rec_title = title
                reason = (risk[:110] + "...") if len(risk) > 110 else risk
                action = (raw_rec[:110] + "...") if len(raw_rec) > 110 else raw_rec

            if dedup_key not in seen_actions:
                seen_actions.add(dedup_key)
                table_rows.append({
                    "priority": priority,
                    "recommendation": rec_title,
                    "reason": reason,
                    "suggested_action": action,
                })

        # Sort: High first, then Medium, then Low
        table_rows.sort(key=lambda r: cls.PRIORITY_ORDER.get(r["priority"], 3))
        return table_rows
