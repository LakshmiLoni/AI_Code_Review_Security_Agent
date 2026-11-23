# APPLICATION DEMONSTRATION & USER GUIDE
## AI Code Review & Security Analysis Agent
**System:** AI Code Review & Security Analysis Agent  
**Target Audience:** Security Engineers, Developers, and Technical Auditors

---

## 1. Quick Startup Instructions

### Step 1: Open the Project Directory
```bash
cd C:\Users\Lakshmi\.gemini\antigravity\scratch\AI_code_review
```

### Step 2: Launch the Streamlit Application
```bash
python -m streamlit run app.py
```
*(The browser will automatically open at `http://localhost:8501`)*

### Step 3: Run the Automated Verification Suite
In a separate terminal:
```bash
python tests/run_all_tests.py
```
*(Runs all 28 automated tests; demonstrates 100% pass rate).*

---

## 2. Step-by-Step Demonstration Walkthrough

### Phase 1: Dashboard Overview (`1_Dashboard.py`)
1. Point out that all displayed numbers (Total Reviews, Average Health Score, Critical Findings) are **computed directly from the SQLite database** (`database/ai_code_review.db`), with zero hardcoded or fabricated statistics.
2. Show the **Findings by Severity** bar chart (Critical, High, Medium, Low).
3. Show the **Analyzed Languages** distribution (Python vs. Java).
4. Review the **Recent Review Sessions** table.

### Phase 2: Live Code Review (`2_New_Code_Review.py`)
1. Navigate to **2. New Code Review** in the sidebar.
2. Select **"Load Sample Project"** from the radio buttons.
3. Choose: `Python Basic (User Service - SQLi & Anti-Patterns)`.
4. Click **"🚀 Run Multi-Agent Review"**.
5. Watch the spinner as Agents 1 & 2 run in parallel via `ThreadPoolExecutor(2)`.
6. Explain the resulting summary metrics:
   - Code Health Score: Dropped due to Critical SQLi and High bare-except / mutable default.
   - PR Status: `Changes Requested`.

### Phase 3: Inspecting Review Results & Observations (`3_Review_Results.py`)
1. Navigate to **3. Review Results**.
2. Show the **Executive Summary** written in clear engineering prose.
3. Highlight the separate **Security Observations** vs. **Quality Observations**.

### Phase 4: Security Vulnerabilities & Line Citations (`4_Security_Findings.py`)
1. Navigate to **4. Security Findings**.
2. Filter by `CRITICAL` severity.
3. Expand finding `#1: SQL Injection via Dynamic Query Formatting`.
4. Show:
   - Line citation: Line 18 in `user_service.py`.
   - OWASP Category: `OWASP A03:2021 - Injection`.
   - Risk Explanation & Evidence Snippet.
   - Practical remediation recommendation.

### Phase 5: Code Quality & AST Smells (`5_Code_Quality.py`)
1. Navigate to **5. Code Quality**.
2. Point out the AST visitor findings:
   - Mutable Default Argument in `GetUserRecords(filters=[])`.
   - Bare `except:` clause masking `BaseException`.
   - Function naming convention violation (`GetUserRecords` vs. PEP 8 `get_user_records`).

### Phase 6: Remediation & Secure Diffs (`6_Remediation.py`)
1. Navigate to **6. Remediation**.
2. Show the **Prioritized Remediation Roadmap** (Critical steps first).
3. Expand the side-by-side comparison:
   - Left: Flagged original dynamic SQL query string.
   - Right: Safe parameterized query with placeholder binding (`cursor.execute("... %s", (username,))`).
4. Reiterate the safety rule: **"The platform never silently modifies source files in place."**

### Phase 7: RAG Interactive Assistant (`7_AI_Assistant.py`)
1. Navigate to **7. AI Assistant**.
2. Click the quick query button: `"How to fix SQL injection?"`.
3. Highlight the RAG response:
   - Explains parameterized queries.
   - Grounds explanation in retrieved knowledge base documents.
   - **Cites source documents** (e.g. `sql_injection_prevention.md`, `owasp_top10.md`).
4. Show that if no Gemini API key is configured, the system uses its **rule-based offline vector fallback engine** without crashing.

### Phase 8: Strict Report Generation & Download (`9_Reports.py`)
1. Navigate to **9. Reports**.
2. Show the **Recommendations for Improvement Table**:
   - Organized by Priority (High first).
   - Columns: `Priority | Recommendation | Reason | Suggested Action`.
3. Click **"⬇️ Download PDF Report"**:
   - Open the generated PDF.
   - Point out: Clean A4 layout, headers, footers (`Page X of Y`), and **Strict Zero-Code Privacy** (no raw code or secrets exposed).
4. Click **"⬇️ Download JSON Report"**:
   - Inspect the clean, structured JSON audit file.

---

## 3. Sample Projects Reference Guide

| Project Directory | Target File | Demonstrated Concepts | Expected Verdict |
| :--- | :--- | :--- | :---: |
| `sample_projects/python_basic/` | `user_service.py` | SQL injection, os.system command injection, bare except, mutable default arguments | `Changes Requested` |
| `sample_projects/python_basic/` | `safe_calculator.py` | Type hints, specific exceptions, parameter range guards, clean PEP 8 design | `Approved` |
| `sample_projects/python_basic/` | `broken_syntax.py` | Deliberate unclosed parenthesis to test AST syntax error catcher | `Syntax Error (Line 7)` |
| `sample_projects/java_intermediate/` | `OrderController.java` | Statement SQLi, Reflected XSS, hardcoded DB password, empty catch, stack trace leak | `Changes Requested` |
| `sample_projects/java_intermediate/` | `SecureAuthService.java` | PreparedStatement binding, constant-time hash comparison, structured logging | `Approved` |
| `sample_projects/java_intermediate/` | `BrokenOrder.java` | Deliberate missing closing brace to test Java delimiter stack parser | `Delimiter Error (Line 8)` |
| `sample_projects/advanced_project/` | `PaymentGateway.py` | Insecure pickle deserialization, hardcoded AWS key, MD5 weak crypto, path traversal | `Changes Requested` |
| `sample_projects/advanced_project/` | `SecureTokenValidator.py` | HMAC-SHA256, cryptographically secure tokens (secrets), canonical path containment | `Approved` |

---

## 4. Technical Architecture FAQ

**Q1: Why did you choose Streamlit instead of a heavy frontend framework like React?**  
*Answer:* Streamlit provides a clean, reactive, Python-native environment ideal for applied AI and engineering workflows. It eliminates unnecessary boilerplate, connects directly to our multi-agent Python backend without brittle intermediate serialization, and enforces clean layout standards with our custom cream/sage-green palette.

**Q2: How does your system prevent code execution risks?**  
*Answer:* The platform operates under a strict **Zero-Code-Execution** model. Source code is never executed (`eval`, `exec`, or dynamic loading). Python code is parsed purely into an Abstract Syntax Tree (`ast.parse`), and Java code is tokenized using structural and lexical patterns.

**Q3: How is the RAG pipeline constructed and what happens when the Gemini API is offline?**  
*Answer:* Our knowledge base contains 20 curated Markdown documents (1,119 lines). Documents are chunked into 119 semantic units and indexed into ChromaDB with dense embeddings. When the Gemini API is offline, our `RAGPipeline` performs cosine similarity retrieval over the persistent vector store and synthesizes grounded answers using our deterministic rule engine, complete with document citations.

**Q4: How do you guarantee privacy in exported reports?**  
*Answer:* Reports are designed for compliance auditing. As enforced in `reports/pdf_generator.py` and `reports/json_generator.py`, raw source code and corrected code snippets are strictly stripped out. Hardcoded secrets are masked with asterisks (`AKIA****************`), and recommendations are presented in a structured tabular priority matrix.
