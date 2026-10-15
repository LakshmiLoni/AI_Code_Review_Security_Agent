# AI Code Review & Security Analysis Agent — Milestone 1

Milestone 1 (Weeks 1–2) of the major project delivers four requirements:

1. **Secure-coding knowledge base:** 11 Markdown documents with source URLs.
2. **System architecture:** Agent responsibilities, orchestration, data models, and RAG diagram.
3. **Code Submission Module:** Paste or upload code, automatically detect the language, and validate syntax using Python `ast` or Java `javac`.
4. **RAG pipeline:** Load, clean, chunk, embed, store in ChromaDB, and retrieve relevant knowledge-base content through a search interface.

**Not implemented in Milestone 1:** The five analysis agents, automated vulnerability scanning, AI-generated fixes, conversational LLM assistant, pull-request summaries, and report export. These are design elements for later milestones.

**Safety:** Submitted code is never executed. Python is parsed with `ast`. Java is compiled using `javac` with annotation processing disabled; the resulting code is never run.

## Project Structure

```text
AI_Code_Review_Security_Agent/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── pytest.ini
├── .streamlit/
│   └── config.toml
├── config/
│   └── settings.py
├── submission/
├── knowledge_base/
│   └── documents/
├── models/
├── architecture/
├── tests/
├── sample_code/
├── MILESTONE1_CHECKLIST.md
└── PRESENTATION_NOTES.md
```

The `vector_store/` directory is generated when the knowledge-base index is built and is excluded from Git.

## Setup on Windows

### 1. Open the project

Open the project folder in VS Code and start a terminal from the project root.

### 2. Create a virtual environment

Python 3.10, 3.11, or 3.12 is recommended.

```powershell
python --version
python -m venv .venv
```

### 3. Activate the environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run the following for the current terminal session only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 5. Check Java availability

```powershell
java -version
javac -version
```

A JDK is required for Java syntax validation. Python validation does not require Java.

### 6. Build the knowledge-base index

```powershell
python -m knowledge_base.build_index
```

The first run downloads the embedding model and creates the index. An offline hashing backend is also available:

```powershell
python -m knowledge_base.build_index --backend hashing --force
```

### 7. Run the application

```powershell
python -m streamlit run app.py
```

Open http://localhost:8501 in your browser.

### 8. Test code submission

Use the Code Submission tab to test the sample files in `sample_code/`.

- `sample_vulnerable.py`: Python syntax validation.
- `sample_invalid.py`: Python syntax errors.
- `SampleVulnerable.java`: Java syntax validation.
- `SampleInvalid.java`: Java syntax errors.

Milestone 1 checks syntax; it does not yet perform automated vulnerability analysis.

### 9. Search the knowledge base

Try questions such as:

- How do I prevent SQL injection in Java?
- Why is MD5 unsafe for passwords?
- What is chunking in RAG?

Search results include relevant text and source information.

### 10. Run tests

```powershell
python -m pytest
```

Some optional tests may be skipped when the embedding model or JDK is unavailable.

## How It Works

**Language detection:** The application evaluates code patterns and file extensions to identify Python or Java and flag likely mismatches.

**Validation:** Python uses `ast.parse`. Java uses `javac` with annotation processing disabled in a temporary directory.

**Retrieval-Augmented Generation (RAG):** Knowledge documents are cleaned and divided into overlapping chunks, embedded using `all-MiniLM-L6-v2`, and stored in ChromaDB with source metadata. Queries use the same embedding model for retrieval.

## Configuration

Copy `.env.example` to `.env` to configure supported settings. Never commit actual API keys, passwords, or other secrets.

## Source Documents

The knowledge-base documents contain concise summaries and references to official OWASP, Python, and Oracle resources. Verify the source links before project submission.

## License and Usage

This project is intended for educational use. Sample files contain intentionally insecure code and must not be deployed.

See the [MIT License](LICENSE) for licensing terms.