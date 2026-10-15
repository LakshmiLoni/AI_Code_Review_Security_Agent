# Orchestration Flow (Planned)

> **Milestone 1 status:** only the first two steps (submission and validation) and the standalone knowledge-base search are implemented. The orchestrator itself is designed here and built in a later milestone.

## 1. End-to-end sequence

```mermaid
sequenceDiagram
    actor U as User
    participant UI as Streamlit UI ✅
    participant SM as Submission Module ✅
    participant O as Orchestrator 🕒
    participant A1 as Code Analysis 🕒
    participant A2 as Security Agent 🕒
    participant KB as Knowledge Base / RAG ✅
    participant A3 as Remediation 🕒
    participant A4 as PR Summary 🕒
    participant A5 as Chat Assistant 🕒

    U->>UI: paste code or upload .py/.java
    UI->>SM: raw text / file bytes
    SM->>SM: size, encoding, extension checks
    SM->>SM: detect language (confidence)
    SM->>SM: syntax check (ast / javac) - no execution
    SM-->>UI: SubmittedCode + validation result
    UI-->>U: show language and validation status
    Note over UI,O: Milestone 1 ends here
    UI->>O: validated SubmittedCode
    O->>A1: analyse structure & quality
    A1-->>O: quality findings
    O->>A2: scan for vulnerabilities
    A2->>KB: retrieve OWASP guidance
    KB-->>A2: chunks + sources
    A2-->>O: security findings
    O->>A3: remediate findings
    A3->>KB: retrieve secure patterns
    KB-->>A3: chunks + sources
    A3-->>O: remediations
    O->>A4: summarise review
    A4-->>O: PR summary
    O-->>UI: ReviewResult
    U->>A5: "Why is this dangerous?"
    A5->>KB: retrieve context
    A5-->>U: grounded answer with sources
```

## 2. Step-by-step description
1. **Submit** - the user provides code (paste or upload).
2. **Pre-checks** - empty, unsupported type, bad encoding and oversized inputs are rejected with clear messages.
3. **Detect** - the language is inferred (no dropdown). If it is unclear, the user is asked for a clearer sample.
4. **Validate** - Python via `ast`, Java via `javac`. Code that does not parse is reported with line numbers; later agents are not run on it (or run in a "best effort" mode - a decision for Milestone 2).
5. **Analyse** - Code Analysis Agent produces structure and quality findings.
6. **Secure** - Security Vulnerability Agent produces security findings, backed by retrieved OWASP guidance.
7. **Fix** - Remediation Agent explains and demonstrates fixes.
8. **Summarise** - PR Summary Agent writes the review.
9. **Discuss** - Conversational Code Assistant answers follow-up questions about the `ReviewResult`.

## 3. Orchestrator design
- A simple, deterministic **pipeline controller** (not free-form agent chat) so results are repeatable and easy to explain.
- Each stage receives and returns typed objects from `models/`.
- A failing agent is recorded in the result and the pipeline continues where possible (graceful degradation).
- Stages that need an LLM check that an API key/model is configured and otherwise fall back to rule-based output.

## 4. Error-handling flow (implemented for submission)

```mermaid
flowchart TD
    In[Input received] --> E{Empty?}
    E -- yes --> M1[Show 'input is empty']
    E -- no --> T{"Supported type<br/>and size OK?"}
    T -- no --> M2[Show type / size error]
    T -- yes --> D{"Decodable<br/>as UTF-8?"}
    D -- no --> M3[Show encoding error]
    D -- yes --> L{"Language<br/>confident?"}
    L -- no --> M4[Ask for clearer sample / correctly named file]
    L -- yes --> V{Validator available?}
    V -- "no (no JDK)" --> M5[Warn: Java not verified]
    V -- yes --> R[Show valid / errors with line numbers]
```
