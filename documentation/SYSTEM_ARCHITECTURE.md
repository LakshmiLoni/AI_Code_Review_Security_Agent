# SYSTEM ARCHITECTURE DOCUMENT
## AI Code Review & Security Analysis Agent
**Architecture Classification:** Multi-Agent Autonomous Static Analysis & Retrieval-Augmented Generation (RAG) System

---

## 1. High-Level Architectural Overview

The platform uses a layered architecture designed for static code analysis, OWASP vulnerability detection, and conversational guidance without executing submitted user code.

```
+-----------------------------------------------------------------------------------+
|                        PRESENTATION LAYER (STREAMLIT UI)                          |
|  Dashboard | New Review | Results | Security | Quality | Remediation | Chat | Reports  |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                            APPLICATION SERVICE LAYER                              |
|   ReviewService    |   AgentOrchestrator   |   HistoryService   |   LLMService    |
+-----------------------------------------------------------------------------------+
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   ▼                                           ▼
+-------------------------------------+     +---------------------------------------+
|          MULTI-AGENT ENGINE         |     |          RAG KNOWLEDGE ENGINE         |
|  Agent 1: AST Code Analysis         |     |  Document Processor & Chunker         |
|  Agent 2: OWASP Security Analysis   |     |  Embedding Manager (MiniLM / CRC32)   |
|  Agent 3: Remediation & Diffs       |     |  ChromaDB / Persistent Vector Index   |
|  Agent 4: PR Summary & Verdicts     |     |  Semantic Similarity Retriever        |
|  Agent 5: Conversational Assistant  |     |  20 Secure Coding Documents (>1k L)   |
+-------------------------------------+     +---------------------------------------+
                   │                                           │
                   └─────────────────────┬─────────────────────┘
                                         ▼
+-----------------------------------------------------------------------------------+
|                           STORAGE & PERSISTENCE LAYER                             |
|  SQLite DB (code_reviews, review_findings, chat_messages) | Reports (PDF & JSON)  |
+-----------------------------------------------------------------------------------+
```

---

## 2. Multi-Agent Pipeline Workflow

```
   [User Code / File (.py, .java)]
                 │
                 ▼
      [Language Detector] ─────────► Python / Java
                 │
                 ▼
      [Syntax Validator]  ─────────► Syntax Error? ──► [Halt & Report Line Number]
                 │ (Valid)
                 ▼
    ┌─────────────────────────┐
    │  ThreadPoolExecutor(2)  │
    ├─────────────────────────┤
    │ Agent 1: Code Analysis  │ ──► Structural Smells & AST Metrics
    │ Agent 2: Security Agent │ ──► OWASP Top 10 Vulnerability Detections
    └─────────────────────────┘
                 │
                 ▼
      [Findings Manager]  ─────────► Deduplicate by (line, title, category)
                 │
                 ▼
     [Severity Calculator] ────────► Health Score (0-100) & Grade (A-F)
                 │
                 ▼
    [Agent 3: Remediation] ────────► Prioritized Steps & Safe Code Examples
                 │
                 ▼
    [Agent 4: PR Summary]  ────────► PR Verdict (Approved / Changes Requested)
                 │
                 ▼
    [Database Repository]  ────────► Persist to SQLite (No raw code retained)
                 │
                 ▼
   [Report Gen (PDF/JSON)] ────────► Strict Privacy: Findings & Recommendations Table
```

---

## 3. RAG Pipeline Architecture

```
[20 Secure Coding Documents] (1,119 lines in knowledge_base/secure_coding_documents/)
                 │
                 ▼
      [Markdown Document Loader]
                 │
                 ▼
      [Heading-Aware Splitter] ────► 119 semantic chunks
                 │
                 ▼
      [Embedding Manager]     ────► Dense vector generation (384-d normalized)
                 │
                 ▼
     [Vector Store (ChromaDB)] ───► Persistent storage in storage/chroma_db/
                 │
    (Runtime User Query / Finding Context)
                 │
                 ▼
     [Semantic Retriever]     ────► Top-k Cosine Similarity Matching
                 │
                 ▼
   [Agent 5 / LLM Synthesis] ────► Grounded answer with document citations
```

---

## 4. Database Schema (Entity-Relationship)

```
┌─────────────────────────────────┐
│          code_reviews           │
├─────────────────────────────────┤
│ id (PK, Integer)                │
│ review_id (String(64), Indexed) │
│ filename (String(255))          │
│ detected_language (String(32))  │
│ timestamp (DateTime)            │
│ status (String(32))             │
│ health_score (Float)            │
│ letter_grade (String(8))        │
│ pr_status (String(64))          │
│ executive_summary (Text)        │
│ pr_summary_json (Text)          │
│ total_findings (Integer)        │
│ critical_count (Integer)        │
│ high_count (Integer)            │
│ medium_count (Integer)          │
│ low_count (Integer)             │
│ retained_source_code (Text)     │
└─────────────────────────────────┘
                 │
                 │ 1:N
                 ▼
┌─────────────────────────────────┐
│         review_findings         │
├─────────────────────────────────┤
│ id (PK, Integer)                │
│ review_id (FK -> code_reviews)  │
│ finding_type (String(32))       │
│ title (String(255))             │
│ category (String(128))          │
│ severity (String(16))           │
│ heuristic_score (Float)         │
│ line_number (Integer)           │
│ filename (String(255))          │
│ description (Text)              │
│ risk_explanation (Text)         │
│ evidence_snippet (Text)         │
│ remediation_recommendation (Text│
│ corrected_code (Text)           │
│ is_confirmed_pattern (Boolean)  │
└─────────────────────────────────┘
```

---

## 5. Strict Report Privacy Architecture

To comply with enterprise security auditing standards:
- **No Code Dumps:** Reports focus entirely on analytical findings, explanations, and actionable guidance.
- **Secret Masking:** All credentials detected in evidence snippets are masked (`AKIA****************`).
- **Tabular Recommendations:** Recommendations are formatted in a clean 4-column priority matrix:
  `Priority | Recommendation | Reason | Suggested Action`
- **Standard A4 Layout:** Exact $595.28 \times 841.89$ pt dimensions with headers and `Page X of Y` footers.
