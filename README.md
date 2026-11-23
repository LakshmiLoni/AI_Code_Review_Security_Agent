# AI Code Review & Security Analysis Agent

**Autonomous Multi-Agent Code Review & Security Analysis Platform**

An autonomous multi-agent AI system designed to review Python and Java source code, detect code quality anti-patterns, identify OWASP security vulnerabilities, generate prioritized remediation roadmaps, and provide an interactive RAG-grounded conversational assistant.

---

## 1. Project Introduction
**AI Code Review & Security Analysis Agent** (`AI_code_review`) is an end-to-end multi-agent static code analysis platform. The system operates on a zero-trust model: submitted source code is treated as untrusted input and is never compiled or executed on the host. Instead, it is inspected via Python Abstract Syntax Trees (AST), Java structural parsers, regex security heuristics, and a persistent Retrieval-Augmented Generation (RAG) vector pipeline.

The platform features a clean, responsive **Streamlit** user interface designed using a warm-white and cream background (`#FDFBF7`), white content cards (`#FFFFFF`), muted sage green (`#5F8670`) and teal (`#0D9488`) accents, and dark grey (`#2D3748`) typography.

---

## 2. Key Features
- **Automatic Language Detection**: Detects Python (`.py`) and Java (`.java`) from file extensions or syntactic pattern indicators without manual user selection.
- **Concurrent Multi-Agent Architecture**: Five specialized AI agents running concurrently via `ThreadPoolExecutor`:
  1. **Code Analysis Agent**: AST quality smells, PEP 8 / Java naming, function length, mutable defaults, and bare `except:` clauses.
  2. **Security Vulnerability Agent**: 14 OWASP vulnerability classes with line citations, risk explanations, and false-positive suppression.
  3. **Remediation Agent**: Prioritized fix roadmap and side-by-side corrected code diffs without modifying original source files.
  4. **PR Summary Agent**: GitHub-style merge readiness verdicts (`Approved`, `Approved with Suggestions`, `Changes Requested`) and Code Health Scores (0–100).
  5. **Conversational Assistant Agent**: Interactive RAG chatbot grounded in 20 secure coding guidelines, powered by Gemini 2.5 Flash with an offline local vector fallback.
- **Strict Privacy in Reports**: Exported A4 PDF and JSON reports strictly omit raw source code, corrected code snippets, and raw secrets, presenting recommendations in a formal priority table (`Priority | Recommendation | Reason | Suggested Action`).
- **Sample Test Scenarios**: 8 pre-configured test scenarios across 3 sample project folders for demonstration.
- **Automated Verification**: Comprehensive test suite covering 28 automated tests with a 100% pass rate.

---

## 3. Technologies Used

### Frontend & UI
- **Streamlit**: Primary user interface framework.
- **Custom CSS**: Warm white (`#FDFBF7`), sage green (`#5F8670`), and teal (`#0D9488`) theme.
- **Pandas**: Structured dataframes for recommendations and review history.

### Backend & Core Analysis
- **Python 3.10–3.12**: Core runtime environment.
- **Python AST (`ast` module)**: Native AST parsing for deep Python structural inspection.
- **SQLAlchemy & SQLite**: Relational persistence for reviews, findings, and conversation logs.
- **Concurrent Futures (`ThreadPoolExecutor`)**: Parallel execution of analysis agents.

### AI and RAG Pipeline
- **Google Gemini API (`gemini-2.5-flash`)**: High-speed conversational reasoning and LLM generation.
- **ChromaDB**: Persistent vector database storing chunk embeddings.
- **Sentence Transformers (`all-MiniLM-L6-v2`)**: Dense semantic text embeddings.
- **Deterministic CRC32 Fallback Vectorizer**: Zero-dependency offline embedding generator ensuring 100% test reliability without external model downloads.
- **Secure Coding Knowledge Base**: 20 curated Markdown documents totaling 1,119 lines.

### Report Generation
- **ReportLab Platypus / Pure-Python A4 Generator**: Standards-compliant PDF generator with running headers, footers, and page numbers.
- **JSON Generator**: Machine-readable audit exporter enforcing zero-code privacy.

---

## 4. Project Structure

```text
AI_code_review/
├── app.py                             # Streamlit main application entry point
├── config.py                          # Unified configuration & environment manager
├── requirements.txt                   # Complete Python dependencies
├── README.md                          # Comprehensive project documentation
├── .env.example / .env                # Environment configuration
├── .gitignore                         # Version control exclusions
│
├── agents/                            # Five specialized AI Agents
│   ├── code_analysis_agent.py         # Agent 1: AST & structural code smells
│   ├── security_agent.py              # Agent 2: 14 OWASP vulnerability detectors
│   ├── remediation_agent.py           # Agent 3: Prioritized fix roadmap & diffs
│   ├── pr_summary_agent.py            # Agent 4: GitHub PR review & verdicts
│   ├── code_assistant_agent.py        # Agent 5: RAG conversational assistant
│   └── conversational_agent.py        # Alias / wrapper for Agent 5
│
├── analysis/                          # Modular Static Analysis Engine
│   ├── language_detector.py           # Python / Java automatic detection
│   ├── syntax_validator.py            # AST & delimiter syntax verification
│   ├── python_analyzer.py             # Modular Python AST analyzer
│   ├── java_analyzer.py               # Modular Java structural analyzer
│   ├── vulnerability_rules.py         # 14 OWASP vulnerability definitions
│   └── code_quality.py                # Health score & severity calculations
│
├── database/                          # SQLite & SQLAlchemy Database Models
│   ├── db.py                          # Scoped session lifecycle manager
│   ├── models.py                      # CodeReview & ReviewFinding models
│   ├── review_repository.py           # Repository query & persistence layer
│   └── ai_code_review.db              # Pre-seeded SQLite database
│
├── rag/                               # RAG Pipeline & ChromaDB Vector Store
│   ├── document_loader.py             # Markdown document parser
│   ├── text_splitter.py               # Section-aware markdown chunker
│   ├── embedding_manager.py           # MiniLM & deterministic CRC32 vectorizer
│   ├── vector_store.py                # ChromaDB & persistent JSON index
│   ├── retriever.py                   # Semantic similarity search
│   ├── rag_pipeline.py                # End-to-end RAG orchestrator
│   ├── embeddings.py                  # Module alias for EmbeddingManager
│   ├── knowledge_base.py              # Module alias for VectorStore
│   └── document_processor.py          # Unified loader and chunker
│
├── reports/                           # Strict Privacy Report Generation
│   ├── pdf_generator.py               # Formal A4 PDF generator (Page X of Y)
│   ├── json_generator.py              # Sanitized JSON report generator
│   └── recommendation_formatter.py    # Tabular recommendations formatter
│
├── services/                          # Application Service Layer
│   ├── review_service.py              # Primary review coordination facade
│   ├── agent_orchestrator.py          # Multi-agent ThreadPoolExecutor
│   ├── llm_service.py                 # Gemini client with fallback
│   └── history_service.py             # Historical review queries & stats
│
├── utils/                             # Utilities & Helpers
│   ├── file_handler.py                # Safe file upload, extension & size checks
│   ├── validators.py                  # Input string validation
│   ├── logger.py                      # Centralized logging configuration
│   ├── helpers.py                     # Review ID generation & text utilities
│   └── ui_helpers.py                  # Streamlit layout & custom theme helpers
│
├── pages/                             # Streamlit Multi-Page Interface
│   ├── 1_Dashboard.py                 # Authentic SQLite database metrics & charts
│   ├── 2_New_Code_Review.py           # Code paste, upload, & sample project loader
│   ├── 3_Review_Results.py            # PR summary verdict & executive review
│   ├── 4_Security_Findings.py         # OWASP finding inventory with line citations
│   ├── 5_Code_Quality.py              # AST code smells & maintainability metrics
│   ├── 6_Remediation.py               # Prioritized roadmap & side-by-side diffs
│   ├── 7_AI_Assistant.py              # Interactive RAG assistant with citations
│   ├── 8_Review_History.py            # Searchable audit archive with 1-click load
│   └── 9_Reports.py                   # Downloadable PDF & JSON report portal
│
├── assets/                            # Styling Assets
│   └── style.css                      # Custom warm-white & sage-green CSS
│
├── sample_projects/                   # Representative Test Cases for Demonstration
│   ├── python_basic/                  # user_service.py, safe_calculator.py, broken_syntax.py
│   ├── java_intermediate/             # OrderController.java, SecureAuthService.java, BrokenOrder.java
│   └── advanced_project/              # PaymentGateway.py, SecureTokenValidator.py
│
├── tests/                             # Comprehensive Automated Test Suite
│   ├── test_language_detection.py     # Language detection unit tests
│   ├── test_code_analysis.py          # AST & code smell tests
│   ├── test_security_analysis.py      # OWASP vulnerability detection tests
│   ├── test_agents.py                 # Agent coordination & PR verdict tests
│   ├── test_database.py               # SQLite persistence & query tests
│   ├── test_reports.py                # PDF/JSON generation & strict privacy tests
│   ├── test_knowledge_base.py         # KB line count (>1001) & retrieval tests
│   └── run_all_tests.py               # Standalone test runner (28 tests)
│
└── documentation/                     # System Documentation
    ├── MILESTONE_4_COMPLETION_REPORT.md
    ├── SYSTEM_ARCHITECTURE.md
    └── FINAL_DEMONSTRATION_GUIDE.md
```

---

## 5. Installation & Setup

### Prerequisites
- Python 3.10, 3.11, or 3.12 installed on your system.
- Git (optional).

### Step 1: Open the Project Directory
```bash
cd C:\Users\Lakshmi\.gemini\antigravity\scratch\AI_code_review
```

### Step 2: Set Up Virtual Environment (Recommended)
```bash
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```
*(Optional)* Add your Google Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```
> **Offline Note:** If `GEMINI_API_KEY` is omitted, the application runs using its built-in rule-based vector fallback engine without errors.

---

## 6. How to Run the Application

Execute the primary Streamlit interface:
```bash
python -m streamlit run app.py
```
*(Alternatively, execute `python app.py`, which will automatically invoke Streamlit).*

Open your browser at:
```
http://localhost:8501
```

---

## 7. How to Run Automated Tests

Run the complete test suite:
```bash
python tests/run_all_tests.py
```
*(Alternatively, run `pytest tests/`).*

Expected output:
```
=================================================================
TEST EXECUTION SUMMARY: 28 Passed, 0 Failed, 0 Errors (Total: 28)
=================================================================
[SUCCESS] All tests passed cleanly!
```

---

## 8. Technical Specifications & Security Summary
- **Zero-Code Execution:** Complete static analysis via AST and lexical parsing.
- **Knowledge Base Scale:** 20 documents, 1,119 verified lines (>1,001 requirement).
- **Report Integrity:** Formal A4 PDF generation with zero source code exposure and structured recommendation tables.
- **Testing:** 28 passing automated tests.
