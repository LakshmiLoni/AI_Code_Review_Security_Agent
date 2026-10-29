"""LLM Integration Service with Google Gemini and Local RAG Fallback."""

import os
from typing import Optional, Dict, Any, List

# Check google-genai availability
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class LLMService:
    """Manages interactions with Google Gemini and handles offline/missing key fallbacks."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "").strip()
        self.model_name = model_name
        self.client = None

        if self.api_key and GENAI_AVAILABLE:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[LLMService] Could not initialize Gemini client: {e}")
                self.client = None

    def is_configured(self) -> bool:
        """Check if Gemini API is configured and operational."""
        return bool(self.client and self.api_key)

    def generate_chat_response(
        self,
        user_message: str,
        retrieved_context: List[Dict[str, Any]],
        review_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate response via Gemini or intelligent local RAG synthesizer."""
        citations = []
        context_blocks = []
        for c in retrieved_context:
            title = c.get("title", "KB Doc")
            fn = c.get("filename", "")
            citations.append({"title": title, "filename": fn, "score": c.get("score", 0.0)})
            context_blocks.append(f"--- Context from {title} ({fn}) ---\n{c.get('content', '')}")

        context_str = "\n\n".join(context_blocks)

        review_info_str = ""
        if review_context:
            review_info_str = (
                f"Active Code Review Context:\n"
                f"- File: {review_context.get('filename')}\n"
                f"- Language: {review_context.get('language')}\n"
                f"- Status: {review_context.get('status')}\n"
                f"- Total Findings: {review_context.get('total_findings')}\n"
                f"- Critical Issues: {review_context.get('critical_count')}, High: {review_context.get('high_count')}\n"
            )

        # 1. Attempt Gemini Call if configured
        if self.is_configured():
            try:
                prompt = (
                    "You are an expert AI Code Review & Cybersecurity Assistant mentoring an AIML engineering student.\n"
                    "Provide clear, accurate, practical explanations with vulnerable and secure code examples where appropriate.\n\n"
                    f"{review_info_str}\n\n"
                    f"Knowledge Base Documentation:\n{context_str}\n\n"
                    f"Student Question: {user_message}\n\n"
                    "Response:"
                )

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                if response and hasattr(response, "text") and response.text:
                    return {
                        "response": response.text.strip(),
                        "mode": "Gemini AI (Cloud)",
                        "model": self.model_name,
                        "citations": citations
                    }
            except Exception as e:
                print(f"[LLMService] Gemini call failed ({e}). Proceeding to Local RAG fallback.")

        # 2. Local RAG Fallback Synthesis (No API key or offline mode)
        local_response = self._synthesize_local_response(user_message, retrieved_context, review_context)
        return {
            "response": local_response,
            "mode": "Local RAG Knowledge Engine (Offline Mode)",
            "model": "Knowledge Base Semantic Matcher",
            "citations": citations
        }

    def _synthesize_local_response(
        self,
        query: str,
        retrieved_context: List[Dict[str, Any]],
        review_context: Optional[Dict[str, Any]] = None
    ) -> str:
        q_lower = query.lower()
        parts = []

        # Check common student question patterns
        if "sql injection" in q_lower or "sqli" in q_lower:
            parts.append(
                "### Understanding SQL Injection (CWE-89)\n\n"
                "**SQL Injection** occurs when untrusted user input is directly concatenated, formatted, or interpolated "
                "into dynamic SQL queries instead of being safely bound as parameters.\n\n"
                "#### How it happens:\n"
                "When an attacker inputs characters like `' OR '1'='1` into a login form or query parameter, "
                "the database SQL parser treats that data as executable SQL commands, altering query logic.\n\n"
                "#### The Fix (Parameterized Queries):\n"
                "Always separate the query structure from the data using parameter placeholders (`?` in SQLite/JDBC, `%s` in psycopg2):\n"
                "```python\n# SECURE\ncursor.execute('SELECT * FROM users WHERE email = ?', (email,))\n```"
            )
        elif "fix" in q_lower or "remediat" in q_lower or "first" in q_lower:
            parts.append(
                "### Recommended Vulnerability Remediation Priority\n\n"
                "In application security, vulnerabilities should always be triaged and fixed according to CVSS severity:\n\n"
                "1. **Critical Severity (Fix Immediately - Within 24 Hours)**:\n"
                "   - *Remote Code Execution (`eval`, `exec`)*\n"
                "   - *SQL Injection*\n"
                "   - *Unsafe Deserialization (`pickle.loads`)*\n"
                "   - *Command Injection (`os.system`)*\n"
                "2. **High Severity (Fix Within 7 Days)**:\n"
                "   - *Hardcoded Credentials & API Keys*\n"
                "   - *Path Traversal*\n"
                "   - *Stored Cross-Site Scripting (XSS)*\n"
                "3. **Medium Severity (Fix Within 30 Days)**:\n"
                "   - *Weak Cryptography (MD5/SHA1)*\n"
                "   - *Insecure PRNG for security tokens*\n"
                "4. **Low Severity (Quality / Hygiene Review)**:\n"
                "   - *Unused imports, monolithic function lengths, naming conventions*."
            )
        elif "explain" in q_lower or "simple" in q_lower or "review" in q_lower:
            if review_context:
                total = review_context.get("total_findings", 0)
                crit = review_context.get("critical_count", 0)
                high = review_context.get("high_count", 0)
                status = review_context.get("status", "Pending")
                parts.append(
                    f"### Summary of Code Review for `{review_context.get('filename')}`\n\n"
                    f"- **Current Review Status**: {status}\n"
                    f"- **Total Detected Findings**: {total}\n"
                    f"- **Critical Vulnerabilities**: {crit}\n"
                    f"- **High Severity Vulnerabilities**: {high}\n\n"
                    "**Key Takeaway**: "
                )
                if crit > 0 or high > 0:
                    parts.append(
                        "Your code contains high-risk security flaws that an external attacker could exploit. "
                        "Check the Findings tab to see the exact line numbers and the suggested side-by-side replacements."
                    )
                else:
                    parts.append(
                        "No critical security vulnerabilities were discovered by the static analyzer! "
                        "Ensure you still write unit tests and adhere to code maintainability best practices."
                    )
            else:
                parts.append(
                    "### Code Review Educational Overview\n\n"
                    "Automated code review inspects code using Static Application Security Testing (SAST). "
                    "It scans source files for structural code smells, maintainability issues, and security vulnerabilities "
                    "like injection, unvalidated deserialization, and hardcoded credentials before code is deployed."
                )
        else:
            parts.append(
                f"### Analysis Guidance for: \"{query}\"\n\n"
                "Based on the Secure Coding Knowledge Base, here are the most relevant principles and standards:"
            )

        # Incorporate retrieved knowledge base chunks
        if retrieved_context:
            parts.append("\n\n#### Knowledge Base Reference Highlights:")
            for idx, chunk in enumerate(retrieved_context[:2], 1):
                title = chunk.get("title", f"Section {idx}")
                content = chunk.get("content", "").strip()
                # Extract first 400 characters
                preview = content[:400].replace("\n\n", "\n")
                parts.append(f"\n**{title}**:\n> {preview}...\n")

        parts.append(
            "\n\n*(Note: Running with Local RAG Knowledge Base. To enable cloud generative explanations, "
            "set `GEMINI_API_KEY` in your environment or `.env` file.)*"
        )

        return "\n".join(parts)
