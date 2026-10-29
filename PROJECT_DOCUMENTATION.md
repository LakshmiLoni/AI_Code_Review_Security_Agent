# SentinelAI: AI Code Review & Security Analysis Agent
## Comprehensive Project Documentation & Technical Viva Guide

**Academic Track**: Fourth-Year Bachelor of Technology (B.Tech) in Artificial Intelligence & Machine Learning (AIML)  
**Project Title**: Explainable Multi-Agent AI Code Review and Security Analysis Agent  
**Domain**: Software Security, Static Analysis, Natural Language Processing, Retrieval-Augmented Generation (RAG)

---

## 1. Problem Statement and Motivation

Modern software engineering teams face an overwhelming velocity of code changes, often pushing multiple releases per day. Despite advances in continuous integration, security code review remains a critical bottleneck:

1. **Human Reviewer Bottleneck**: Experienced application security engineers are scarce. Senior developers reviewing pull requests focus primarily on business logic and feature delivery, inadvertently allowing critical vulnerabilities (such as SQL injection, unvalidated deserialization, or hardcoded secrets) to slip into production.
2. **Shortcomings of Traditional Scanners**: Commercial Static Application Security Testing (SAST) tools generate voluminous, noisy reports with high false-positive rates. They tell developers *what* is wrong in obscure jargon, but rarely explain *why* the issue matters or provide verified, contextual drop-in code fixes.
3. **Black-Box LLM Risks**: Developers pasting proprietary source code into public cloud LLMs risk exposing intellectual property. Furthermore, LLMs frequently "hallucinate" incorrect security APIs or non-existent syntax.

### Project Objective
To engineer a functional, transparent, and explainable **Multi-Agent AI Code Review Platform** that:
- Never executes uploaded source code, guaranteeing 100% execution safety.
- Utilizes deterministic AST parsing and pattern matching for reliable vulnerability detection.
- Employs a Retrieval-Augmented Generation (RAG) system with a verified 1,900+ line security knowledge base.
- Generates side-by-side remediations with clear rationale.
- Operates fully offline without paid APIs, while supporting optional cloud generative AI (Google Gemini).

---

## 2. Existing System vs. Proposed System

| Dimension | Traditional SAST / Manual Review | Proposed Multi-Agent System |
|---|---|---|
| **Execution Safety** | Often requires compiling or executing partial builds. | Pure static AST analysis; zero execution of user code. |
| **Explanation Clarity** | Cryptic CWE codes and generic descriptions. | Natural-language rationale, educational impact analysis. |
| **Remediation Quality** | Generic textual advice; no concrete diff. | Side-by-side original vs. remediated code snippets. |
| **Knowledge Base** | Proprietary, closed-source rule dictionaries. | 1,900+ line transparent, verifiable Markdown knowledge base. |
| **Offline Viability** | Cloud-tethered subscription services. | Local TF-IDF + Cosine Similarity fallback with zero cloud costs. |
| **Interactive Mentoring**| Static PDF or HTML report without interaction. | Conversational AI assistant for student questions. |

---

## 3. System Architecture & Data Flow

```text
                        [ User / Student Interface ]
                        (Web Browser: HTML/CSS/JS)
                                     │
           ┌─────────────────────────┴────────────────────────┐
           ▼                                                  ▼
   [ Code Submission ]                                [ Chat Assistant ]
   (Paste or File Upload)                            (Conversational Q&A)
           │                                                  │
           ▼                                                  │
 ┌───────────────────────┐                                    │
 │  Code Parser Service  │                                    │
 │ (Python AST / Java)   │                                    │
 └─────────┬─────────────┘                                    │
           │                                                  │
           ├────────────────────────┬──────────────────────┐  │
           ▼                        ▼                      │  │
 ┌────────────────────┐   ┌────────────────────┐           │  │
 │ Quality Agent      │   │ Security Agent     │           │  │
 │ (Smells, Length,   │   │ (OWASP Top 10,     │           │  │
 │  Complexity, Imps) │   │  SQLi, Cmd, RCE)   │           │  │
 └─────────┬──────────┘   └─────────┬──────────┘           │  │
           │                        │                      │  │
           └───────────┬────────────┘                      │  │
                       ▼                                   │  │
           ┌────────────────────────┐                      │  │
           │  Remediation Agent     │                      │  │
           │ (Side-by-Side Patches) │                      │  │
           └───────────┬────────────┘                      │  │
                       ▼                                   │  │
           ┌────────────────────────┐                      │  │
           │  Summary Agent         │                      │  │
           │ (Scores, Risks, Stats) │                      │  │
           └───────────┬────────────┘                      │  │
                       │                                   │  │
                       ▼                                   ▼  ▼
           ┌────────────────────────┐            ┌────────────────────────┐
           │   SQLite Database      │            │  RAG Knowledge Base    │
           │ (reviews.db)           │            │ (1,971 lines, 216 chk) │
           └────────────────────────┘            └────────────────────────┘
```

---

## 4. Multi-Agent System Roles and Responsibilities

1. **Review Orchestrator**: The master controller coordinating the analysis pipeline, tracking execution time, and passing parsed data sequentially between specialized agents.
2. **Code Parser (`code_parser.py`)**:
   - For Python: Parses the source code into an Abstract Syntax Tree using `ast.parse()`. Measures lines of code, extracts function and class definitions, and calculates cyclomatic complexity based on decision nodes (`If`, `For`, `While`, `ExceptHandler`, `BoolOp`).
   - For Java: Inspects curly brace balance, extracts imports and class declarations, and detects method signatures and parameter lists.
3. **Code Quality Agent (`code_quality_agent.py`)**:
   - Identifies code smells that degrade maintainability and auditability.
   - Detects monolithic functions exceeding 35 lines.
   - Detects high cyclomatic complexity (>10 decision branches).
   - Identifies unused imports by cross-referencing imported identifiers against AST `Name` and `Attribute` usage.
   - Catches silent exception swallowing (`except Exception: pass`) and bare `except:` clauses.
4. **Security Vulnerability Detection Agent (`security_agent.py`)**:
   - Inspects AST nodes and regex signatures for critical security flaws.
   - Checks for dynamic query formatting in SQL database operations.
   - Identifies operating system command execution (`os.system`, `subprocess(shell=True)`, `Runtime.getRuntime().exec`).
   - Flags dangerous dynamic evaluation (`eval`, `exec`).
   - Detects unauthenticated deserialization (`pickle.loads`, `yaml.load`, `ObjectInputStream`).
   - Scans for hardcoded credentials, AWS access keys, and static password assignments.
   - Detects deprecated cryptographic primitives (MD5, SHA-1, ECB mode) and predictable PRNGs.
5. **Remediation Agent (`remediation_agent.py`)**:
   - Generates concrete, side-by-side corrected replacement code.
   - Explains the architectural reason why the fix mitigates the vulnerability.
   - Attaches mandatory human verification labels to all generated suggestions.
6. **Review Summary Agent (`review_summary_agent.py`)**:
   - Formulates composite Security (0–100) and Quality (0–100) scores.
   - Assigns normalized review status tags.
   - Details remaining risks and highlights static analysis limitations.
7. **Assistant Agent (`assistant_agent.py`)**:
   - Bridges the web chat interface with the knowledge retrieval engine.
   - Retrieves top-k matching knowledge base passages and synthesizes structured answers to student questions.

---

## 5. Retrieval-Augmented Generation (RAG) Architecture

The RAG subsystem enables grounded, verifiable security guidance without relying on cloud API connections:

1. **Document Loading**: `DocumentLoader` scans `knowledge_base/` for markdown documents and the JSON manifest.
2. **Semantic Chunking**: `MarkdownChunker` divides documents along logical level-2 (`##`) and level-3 (`###`) header boundaries, preserving topic IDs, headings, and context windows.
3. **Vector Store & Indexing**:
   - **Primary Engine**: ChromaDB persistent vector database (when installed).
   - **Fallback Engine**: Scikit-learn's `TfidfVectorizer` paired with `cosine_similarity`. It constructs a TF-IDF matrix across all 216 knowledge chunks and computes pairwise cosine similarity in milliseconds on any standard machine.
4. **Query & Citation**: Given a user query or finding rule ID, `retriever.py` queries the index, retrieves the top-k chunks, and returns cited file locations and relevance scores.

---

## 6. Database Design

The application utilizes a lightweight, ACID-compliant SQLite database stored in `data/reviews.db`:

### `reviews` Table
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | Auto-incrementing primary key |
| `review_uuid` | TEXT UNIQUE | 32-character hexadecimal UUID |
| `filename` | TEXT | Sanitized name of the analyzed source file |
| `language` | TEXT | 'python' or 'java' |
| `source_code` | TEXT | Submitted source code |
| `security_score` | REAL | Computed security rating (0.0 - 100.0) |
| `quality_score` | REAL | Computed code quality rating (0.0 - 100.0) |
| `status` | TEXT | Normalized risk status tag |
| `summary_text` | TEXT | Executive narrative summary |
| `critical_count` | INTEGER | Count of Critical findings |
| `high_count` | INTEGER | Count of High findings |
| `medium_count` | INTEGER | Count of Medium findings |
| `low_count` | INTEGER | Count of Low findings |
| `total_findings`| INTEGER | Total findings count |
| `metrics_json` | TEXT | JSON blob of parsed metrics and residual risks |
| `created_at` | TIMESTAMP | Creation timestamp |

### `findings` Table
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | Primary key |
| `review_id` | INTEGER FOREIGN KEY | Reference to `reviews.id` (ON DELETE CASCADE) |
| `finding_type` | TEXT | 'security' or 'quality' |
| `rule_id` | TEXT | Unique rule ID (e.g., SEC-SQL-01) |
| `title` | TEXT | Human-readable finding name |
| `severity` | TEXT | Critical, High, Medium, or Low |
| `line_number` | INTEGER | Line number in source code |
| `code_snippet` | TEXT | Exact code snippet flagged |
| `explanation` | TEXT | Technical explanation of the issue |
| `why_it_matters`| TEXT | Operational impact and risk analysis |
| `remediation` | TEXT | Recommended fix description |
| `remediated_code`| TEXT | Corrected replacement code pattern |
| `kb_reference` | TEXT | Cited knowledge base topic |
| `cwe_id` | TEXT | Common Weakness Enumeration ID |
| `owasp_category`| TEXT | OWASP Top 10 category |

---

## 7. Security Controls Implemented

- **Non-Execution Invariant**: Source code submitted by users is never executed or evaluated by the Python runtime.
- **Path Traversal Guards**: Filenames are sanitized through `get_safe_filename()`, and all path resolutions verify boundary containment via `Path.resolve()`.
- **Upload Constraints**: Enforces a strict 2MB file size ceiling and whitelists only `.py` and `.java` extensions.
- **SQL Injection Prevention**: All internal SQLite operations use parameterized bind placeholders (`?`), completely avoiding string interpolation in queries.
- **XSS Output Neutralization**: Templates employ Jinja2 auto-escaping, and text reflections are sanitized with `html.escape()`.
- **Secret Isolation**: Secrets and API keys are read from environment variables; `.env` is excluded in `.gitignore`.

---

## 8. Testing Strategy

The test suite consists of 5 modular test cases implemented using Python's standard `unittest` framework:
1. `test_routes.py`: Validates all HTTP endpoints, redirects, status codes, and JSON APIs.
2. `test_code_quality.py`: Tests syntax error handling, long function flags, cyclomatic complexity calculations, and unused import detection.
3. `test_security_agent.py`: Asserts correct detection and severity scoring for SQLi, Command Injection, `eval`, `pickle`, hardcoded secrets, and weak crypto.
4. `test_knowledge_base.py`: Formally asserts that `secure_coding_knowledge_base.md` contains at least 1,200 non-blank lines and validates RAG semantic retrieval.
5. `test_reports.py`: Validates JSON schema compliance and Markdown formatting for report generation.

---

## 9. Future Enhancements

- **Dynamic Taint Analysis Integration**: Incorporating symbolic execution engines (e.g., PyExZ3) to trace user inputs through complex call graphs.
- **Multi-Language Expansion**: Extending AST parsing support to C/C++, Go, and TypeScript.
- **Automated CI/CD Action**: Packaging SentinelAI into a GitHub Action that posts inline review comments on Pull Requests.
