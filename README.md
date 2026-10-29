# AI Code Review & Security Analysis Agent (SentinelAI)

> **Final Year AIML Engineering Capstone Project**  
> An explainable, multi-agent static application security testing (SAST) and code review platform with an integrated 1,900+ line Retrieval-Augmented Generation (RAG) cybersecurity knowledge base.

---

## 1. Project Introduction & Overview

The **AI Code Review & Security Analysis Agent** is a full-featured, developer-friendly Python web application engineered to automate source code security inspections, detect maintainability code smells, produce side-by-side remediations, and mentor developers through an interactive AI assistant.

Built specifically for high-stakes academic reviews and technical interviews, it implements **100% explainable static analysis** using Python's Abstract Syntax Tree (`ast`) and Java structural heuristics, eliminating the "black box" unpredictability of raw prompt-based code reviewers while offering local RAG fallback when cloud AI APIs are unavailable.

---

## 2. Problem Statement & Motivation

- **Manual Code Review Bottlenecks**: Peer reviews are labor-intensive, subjective, and prone to human oversight—especially regarding subtle security defects like SQL injection, unsafe deserialization, or timing attacks.
- **Enterprise SAST Complexity**: Commercial security scanners (e.g., Fortify, Checkmarx) output hundreds of dense, overwhelming alerts with high false-positive rates and no developer-friendly remediation guidance.
- **Cloud LLM Hallucinations & Dependency**: Relying purely on cloud LLMs introduces unpredictable recommendations, privacy leaks of proprietary source code, and complete system failure when internet or paid API quotas expire.
- **The Proposed Solution**: A hybrid multi-agent architecture that performs deterministic static analysis on code trees, queries an authoritative local 1,900+ line security knowledge base via RAG, and produces explainable side-by-side corrected patterns.

---

## 3. Key Features

- **Code Submission Module**: Paste source code into the editor or upload `.py` and `.java` files (up to 2MB). Automatic language detection and strict sandbox safety (code is **never executed**).
- **Code Quality Analysis Agent**: AST-driven checks for syntax errors, monolithic functions (>35 lines), excessive cyclomatic complexity (>10), unused imports, non-standard naming, deep nesting, and silent exception swallowing.
- **Security Vulnerability Detection Agent**: Comprehensive checks mapped to CWE and OWASP Top 10:
  - *SQL Injection (CWE-89)*
  - *OS Command Injection (CWE-78)*
  - *Dynamic Code Execution via eval/exec (CWE-95)*
  - *Insecure Deserialization via pickle/Java ObjectInputStream (CWE-502)*
  - *Hardcoded Credentials, AWS Keys & Secrets (CWE-798)*
  - *Weak Cryptography (MD5/SHA1/ECB) (CWE-327/328)*
  - *Predictable PRNG for Security Tokens (CWE-338)*
  - *Path Traversal Indicators (CWE-22)*
- **AI Remediation Agent**: Suggests side-by-side drop-in replacement patterns, articulates why the fix is safer, and clearly labels output as recommendations requiring human verification.
- **Code Review Summary Agent**: Calculates composite security/quality scores (0–100), severity counts, executive narratives, and honest residual risk statements.
- **RAG Knowledge Base**: Over 1,900 meaningful non-blank lines indexed into ChromaDB with scikit-learn TF-IDF + cosine similarity fallback.
- **Conversational Code Assistant**: Mentors students on vulnerabilities ("Why is this vulnerable?", "How do I fix this?") using Google Gemini or the local RAG engine.
- **Dashboard & Audit Persistence**: SQLite review database tracking total reviews, findings by severity, and Chart.js issue distributions.
- **Downloadable Reports**: One-click exports in structured JSON and comprehensive GitHub Flavored Markdown.

---

## 4. Technology Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11, Flask 3.1.3, Jinja2 3.1.6, Werkzeug 3.1.8 |
| **Static Code Parsing** | Python `ast` (Abstract Syntax Tree), Regular Expressions |
| **Database** | SQLite 3 with parameterized queries and foreign keys |
| **Retrieval-Augmented Gen** | ChromaDB with local scikit-learn TF-IDF + Cosine Similarity fallback |
| **Generative AI** | Google Gemini API (via modern `google-genai` SDK) |
| **Frontend UI** | HTML5, CSS3 (Warm Cream & Gold theme), JavaScript, Chart.js |
| **Testing** | `unittest` and `pytest` |
| **Configuration** | `python-dotenv` |

---

## 5. Folder Structure

```text
AI_Code_Review_Security_Agent/
├── app/
│   ├── __init__.py                # Flask application factory
│   ├── config.py                  # Environment & security configuration
│   ├── extensions.py              # Service container & dependency injection
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main_routes.py         # Home, dashboard, about, API stats
│   │   ├── review_routes.py       # Submit code, detail view, review history
│   │   ├── report_routes.py       # Download JSON & Markdown reports
│   │   └── assistant_routes.py    # Assistant UI & chat API endpoint
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── code_quality_agent.py  # AST maintainability & smell analyzer
│   │   ├── security_agent.py      # OWASP/CWE static vulnerability engine
│   │   ├── remediation_agent.py   # Side-by-side fix generator
│   │   ├── review_summary_agent.py# Score calculator & summary synthesizer
│   │   ├── assistant_agent.py     # Student mentor chatbot
│   │   └── orchestrator.py        # Multi-agent review pipeline coordinator
│   ├── services/
│   │   ├── __init__.py
│   │   ├── code_parser.py         # Python AST & Java structural parser
│   │   ├── analysis_service.py    # Facade for review workflows
│   │   ├── report_service.py      # JSON and Markdown report builder
│   │   ├── knowledge_service.py   # RAG bridge & line count verifier
│   │   └── llm_service.py         # Google Gemini & local heuristic engine
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── document_loader.py     # Knowledge base markdown loader
│   │   ├── chunker.py             # Section & header semantic chunker
│   │   ├── vector_store.py        # ChromaDB adapter & TF-IDF vectorizer
│   │   └── retriever.py           # Top-k query matching & citations
│   ├── models/
│   │   ├── __init__.py
│   │   └── review.py              # SQLite DatabaseManager & ReviewModel
│   └── utils/
│       ├── __init__.py
│       ├── validators.py          # Input size, syntax, language detection
│       └── security.py            # Filename sanitization & path guards
├── templates/
│   ├── base.html                  # Master layout with navbar & footer
│   ├── index.html                 # Hero landing page & quickstart
│   ├── dashboard.html             # Metrics, charts, KB status, recent reviews
│   ├── review.html                # Submission form with sample loaders
│   ├── review_detail.html         # Findings tabs, side-by-side diffs
│   ├── review_history.html        # Historical review audit table
│   ├── assistant.html             # Interactive mentor chat interface
│   ├── about.html                 # Architecture & college review doc
│   └── error.html                 # User-friendly error display
├── static/
│   ├── css/
│   │   └── style.css              # Warm cream & gold design system
│   └── js/
│       └── main.js                # Demo injectors, tab controls, chat handler
├── knowledge_base/
│   ├── secure_coding_knowledge_base.md # 1,900+ lines covering 25 topics
│   ├── references.md              # Authoritative CWE, OWASP, NIST links
│   └── manifest.json              # Document & topic metadata
├── tests/
│   ├── test_routes.py             # HTTP endpoint & status code tests
│   ├── test_code_quality.py       # AST complexity, smell & import tests
│   ├── test_security_agent.py     # SQLi, command injection, secret tests
│   ├── test_knowledge_base.py     # Line count (>=1200) & RAG retrieval tests
│   └── test_reports.py            # JSON & Markdown export tests
├── scripts/
│   ├── count_knowledge_lines.py   # Strict verification script (exits 1 if < 1200)
│   └── index_knowledge_base.py    # Rebuilds vector store index
├── data/                          # SQLite database directory
├── instance/                      # Instance overrides
├── uploads/                       # Safe temporary file upload staging
├── reports/                       # Generated report cache
├── chroma_db/                     # Persistent vector store index
├── .env.example                   # Environment variable template
├── .gitignore                     # Git exclusion rules
├── requirements.txt               # Pinned dependencies
├── run.py                         # Application entrypoint
├── README.md                      # Comprehensive guide
└── PROJECT_DOCUMENTATION.md       # Engineering capstone documentation
```

---

## 6. Installation & Setup Guide (Windows)

### Prerequisites
- Python 3.10+ (Python 3.11 recommended) installed and added to system `PATH`.
- Visual Studio Code installed.

### Step 1: Open the Project in VS Code
Open PowerShell or Windows Command Prompt and navigate to the project directory:
```powershell
cd "C:\Users\Lakshmi\.gemini\antigravity\scratch\AI_Code_Review_Security_Agent"
code .
```

### Step 2: Create and Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If PowerShell blocks script execution, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

### Step 3: Install Dependencies
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy the example environment file:
```powershell
Copy-Item .env.example .env
```
Open `.env` in VS Code. To enable cloud Gemini responses, set your API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```
*(Note: If you leave `GEMINI_API_KEY` blank, the application will automatically run in **Local RAG Offline Mode** with zero paid API requirements!)*

---

## 7. Running the Application

### Start the Flask Server
Run the entrypoint script:
```powershell
python run.py
```
Output:
```text
[*] Starting AI Code Review & Security Analysis Agent on http://127.0.0.1:5000
 * Serving Flask app 'run'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```
Open your web browser and navigate to:
**[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 8. Verifying Knowledge Base & Running Tests

### Strict Knowledge Base Line-Count Verification
Verify that the knowledge base strictly satisfies the 1,200+ non-blank line requirement:
```powershell
python scripts\count_knowledge_lines.py
```
Expected output:
```text
[KB Verifier] Target file: ...\knowledge_base\secure_coding_knowledge_base.md
[KB Verifier] Non-blank line count: 1971
[KB Verifier] Minimum required: 1200
[KB Verifier] SUCCESS: Knowledge base meets the line count requirement (1971 >= 1200).
```

### Re-indexing the Knowledge Base
To index or re-index the knowledge base into the vector store:
```powershell
python scripts\index_knowledge_base.py
```

### Running the Test Suite
Run all unit and integration tests using Python's built-in test runner or pytest:
```powershell
python -m unittest discover tests
```
or with pytest:
```powershell
pytest
```

---

## 9. How to Use the Application

1. **Dashboard (`/dashboard`)**:
   - Inspect total reviews, vulnerability distribution charts, and the live line count of the Knowledge Base.
2. **Submit a Review (`/reviews/new`)**:
   - Click one of the demo sample buttons (**Vulnerable Python**, **Vulnerable Java**, or **Clean Code**).
   - Alternatively, upload a `.py` or `.java` source file.
   - Click **Execute Multi-Agent Analysis**.
3. **Inspect Findings (`/reviews/<uuid>`)**:
   - View composite **Security** and **Quality** scores.
   - Switch between **Security Findings**, **Code Quality**, and **Full Source Code** tabs.
   - Compare the **Insecure Code** against the **Suggested Remediation Pattern** side by side.
4. **Download Reports**:
   - Click **Export JSON** or **Export Markdown** to download the audit record.
5. **Ask AI Assistant (`/assistant/`)**:
   - Select the active review from the context dropdown.
   - Ask questions like: *"Why is this code vulnerable?"* or *"What is SQL injection?"*
   - Review cited knowledge base sections and educational remediation advice.

---

## 10. Troubleshooting

- **Port 5000 in use**:
  - In PowerShell, run: `Stop-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess -Force` or set `FLASK_PORT=5001` in `.env`.
- **ChromaDB is not installed**:
  - The application automatically falls back to its built-in scikit-learn TF-IDF + Cosine Similarity engine with zero configuration.
- **Gemini API Key missing**:
  - The assistant automatically switches to **Local RAG Knowledge Engine Mode**, synthesizing high-accuracy explanations directly from the 1,900+ line knowledge base.

---

## 11. Known Limitations

1. **Static Analysis Boundaries**: The analyzer inspects syntax patterns without executing code. It cannot detect dynamic business logic bypasses (e.g., deducting $5 instead of $50).
2. **Complex Reflection**: Heavy runtime reflection in enterprise Java frameworks may cause certain taint chains to be missed.
3. **Heuristic Disclaimers**: All generated fixes are recommendations that require verification by human software engineers prior to production deployment.
