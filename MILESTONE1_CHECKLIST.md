# Milestone 1 Completion Checklist

✅ = implemented and tested · 🕒 = intentionally left for later milestones

## Requirement 1 - Secure coding knowledge base
- [x] 11 Markdown documents in `knowledge_base/documents/`
- [x] OWASP Top 10 (2025 edition, with 2021 comparison)
- [x] SQL Injection, XSS, CSRF
- [x] Hardcoded credentials and secrets
- [x] Authentication/authorization weaknesses and broken access control (separate documents)
- [x] Secure Python coding, secure Java coding
- [x] Code smells, maintainability, common mistakes
- [x] Introduction to RAG
- [x] Each document has definition, risk, vulnerable example (where relevant), prevention and a **Sources** section with URLs
- [x] Original concise summaries (no copied pages)

## Requirement 2 - System architecture
- [x] System architecture diagram (Mermaid) - `architecture/system_architecture.md`
- [x] Responsibilities of all five future agents - `agent_responsibilities.md`
- [x] Orchestration flow (sequence + error flow diagrams) - `orchestration_flow.md`
- [x] Data models: submitted code, findings, remediation, review result - `data_models.md` + `models/*.py`
- [x] RAG pipeline diagram (load → clean → chunk → embed → vector store → retrieval)
- [x] Implemented vs planned clearly marked (✅ / 🕒)
- [x] All 6 Mermaid diagrams syntax-checked with the Mermaid parser

## Requirement 3 - Code Submission Module
- [x] Paste code in a text area
- [x] Upload `.py` and `.java` files
- [x] Automatic language detection with confidence; **no** language dropdown (asserted by a test)
- [x] Detected language and validation status displayed
- [x] Python syntax via `ast` (never executed - test proves a side-effect file is not created)
- [x] Java syntax via `javac`; helpful warning when no JDK (no crash)
- [x] Syntax errors with line (and column) information
- [x] Empty input, unsupported file type, encoding errors, oversized files, binary files handled
- [x] Ambiguous code → asks for a clearer sample / correctly named file
- [x] Extension cross-checked against content (mismatch message)
- [x] View submitted code and validation results
- [x] Light, simple theme

## Requirement 4 - Knowledge base + RAG pipeline
- [x] Separate files: loader, cleaner, chunker, embedding service, vector store, retriever
- [x] Overlapping chunks
- [x] Local embeddings (Sentence-Transformers `all-MiniLM-L6-v2`; no API key)
- [x] Persistent ChromaDB index in `vector_store/`
- [x] Source metadata on every chunk; results return source file names and URLs
- [x] Index is **not** rebuilt per search; incremental refresh skips unchanged documents; force rebuild available
- [x] Build/refresh via CLI and via the UI
- [x] Streamlit search page showing retrieved text and sources
- [x] Troubleshooting text for model-download failures; offline fallback backend
- [x] A failed model load cannot destroy an existing index (regression test)

## Testing and documentation
- [x] Tests: Python detection, Java detection, ambiguous/empty, valid/invalid Python, Java with javac, javac-unavailable, loading, chunking, persistent indexing and retrieval, UI smoke tests
- [x] README with step-by-step Windows/PowerShell/VS Code setup and troubleshooting
- [x] `requirements.txt`, `.env.example`, `.gitignore`

## Deliberately NOT implemented (later milestones) 🕒
- [ ] Code Analysis / Security Vulnerability / Remediation / PR Summary agents
- [ ] Automated OWASP scanning of submitted code
- [ ] AI-generated fixes
- [ ] Conversational LLM assistant
- [ ] Final review report and export
