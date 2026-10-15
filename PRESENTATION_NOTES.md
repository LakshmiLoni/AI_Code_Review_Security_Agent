# Milestone 1 - Short Explanation for the Project Guide

## One-minute summary
"My project is an AI Code Review & Security Analysis Agent for Python and Java. It will accept code, find security and quality problems, explain the fixes using a trusted knowledge base, and write a pull-request-style review. In Milestone 1 I built the **foundation**: a secure-coding knowledge base, the full system design, a safe code-submission module, and the retrieval half of a RAG pipeline."

## What I built (4 parts)
1. **Knowledge base** - 11 concise Markdown documents (OWASP Top 10:2025, SQL injection, XSS, CSRF, secrets, authentication, access control, secure Python/Java, code smells, RAG). Each has a definition, risk, vulnerable example, prevention and official source links.
2. **Architecture** - diagrams and documents for the whole system: five agents (Code Analysis, Security Vulnerability, Remediation, PR Summary, Conversational Assistant), an orchestrator that runs them in order, shared data models, and the RAG pipeline.
3. **Code Submission Module** - paste or upload code; the language is detected **automatically** with a confidence score (no dropdown); Python is checked with `ast`, Java with `javac`; errors show line numbers; edge cases (empty, wrong type, bad encoding, too large) are handled.
4. **RAG retrieval** - documents → clean → chunk (overlapping) → local embeddings → ChromaDB (persistent) → retrieval that returns text plus source file and URLs.

## Key design decisions (good viva answers)
- **Why never execute code?** Running unknown code is itself a security risk. `ast.parse` only builds a syntax tree; `javac` only compiles, with annotation processing off, in a temp folder.
- **How does language detection work?** Weighted pattern scoring (e.g. `def`, `elif`, `self` vs `public class`, `;`, `System.out`). Confidence reflects how one-sided the evidence is and how much there is; if too low, the user is asked for a clearer sample. For files, the extension is a hint that is cross-checked with the content.
- **Why RAG instead of only an LLM?** Answers can be grounded in official sources and cited, the knowledge is updatable without retraining, and it reduces hallucination.
- **Why local embeddings and ChromaDB?** Free, no API key, works offline after the first model download, and the index persists between runs.
- **Why chunk with overlap?** Pieces must be small enough to be specific but overlap preserves context that crosses a boundary.
- **How is the index kept efficient?** Each document's SHA-256 hash is stored; refresh only re-embeds new or changed documents.
- **Why OWASP 2025?** It is the current edition (released January 2026); I note the 2021 numbering for comparison.
- **Honest limits:** language detection is heuristic (it asks for help when unsure); `javac` also reports semantic errors such as missing libraries; retrieval quality depends on document quality; no LLM generation yet.

## Demo script (3 minutes)
1. Paste `sample_vulnerable.py` → Python detected, valid.
2. Paste `sample_invalid.py` → syntax errors with line numbers.
3. Upload `SampleInvalid.java` → `';' expected` on line 3 (or the JDK warning).
4. Paste `hello` → asks for a clearer sample.
5. Knowledge Base tab → search "How do I prevent SQL injection in Java?" → show text, source file and URLs.
6. Show `architecture/system_architecture.md` diagrams and `python -m pytest` passing.

## What comes next
| Milestone | Work |
|-----------|------|
| 2 | Code Analysis Agent + Security Vulnerability Agent (rule-based + RAG-backed) |
| 3 | Remediation Agent + orchestrator |
| 4 | PR Summary Agent + report export |
| 5 | Conversational Code Assistant, evaluation and polish |
