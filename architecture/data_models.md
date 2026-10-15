# Data Models

The dataclasses live in `models/`. `SubmittedCode` and `ValidationResult` are **used in Milestone 1**; `Finding`, `Remediation` and `ReviewResult` are **defined now as the contract for later milestones** (no component produces them yet).

```mermaid
classDiagram
    class SubmittedCode {
        +str code
        +str source_type
        +str filename
        +str language
        +float detection_confidence
        +list detection_notes
        +ValidationResult validation
        +list errors
        +str submitted_at
        +line_count() int
        +accepted() bool
    }
    class ValidationResult {
        +str status
        +str language
        +str tool
        +str message
        +list~SyntaxIssue~ issues
        +list~str~ warnings
    }
    class SyntaxIssue {
        +str message
        +int line
        +int column
        +str source_line
    }
    class Finding {
        +str finding_id
        +str title
        +str category
        +Severity severity
        +str description
        +int line_start
        +int line_end
        +str code_snippet
        +str cwe_id
        +float confidence
        +str detected_by
        +list~str~ references
    }
    class Remediation {
        +str finding_id
        +str summary
        +str explanation
        +str secure_code_example
        +str effort
        +list~str~ references
    }
    class ReviewResult {
        +SubmittedCode submission
        +list~Finding~ findings
        +list~Remediation~ remediations
        +str pr_summary
        +float quality_score
        +str created_at
    }
    class Severity {
        <<enumeration>>
        INFO
        LOW
        MEDIUM
        HIGH
        CRITICAL
    }
    SubmittedCode "1" --> "0..1" ValidationResult
    ValidationResult "1" --> "*" SyntaxIssue
    ReviewResult "1" --> "1" SubmittedCode
    ReviewResult "1" --> "*" Finding
    ReviewResult "1" --> "*" Remediation
    Finding --> Severity
    Remediation ..> Finding : finding_id
```

## Field notes
| Model | Purpose | Milestone |
|-------|---------|-----------|
| `SubmittedCode` | The code plus how it was received, detected and validated | ✅ 1 |
| `ValidationResult` / `SyntaxIssue` | Syntax check outcome with line information | ✅ 1 |
| `Finding` | One vulnerability or quality problem; links to OWASP/CWE and KB sources | 🕒 2 |
| `Remediation` | Fix explanation and secure code example for one finding | 🕒 3 |
| `ReviewResult` | Everything about one review, ready for the UI, the PR summary and export | 🕒 3-4 |

## Knowledge-base records (implemented)
Each indexed chunk in ChromaDB stores its text plus this metadata:

| Field | Meaning |
|-------|---------|
| `source_file` | Document name, e.g. `sql_injection.md` |
| `title` | Document title |
| `section` | Nearest Markdown heading |
| `chunk_index` | Position of the chunk within the document |
| `source_urls` | Official source URLs (joined with `\|`) |
| `content_hash` | SHA-256 of the document, used to skip unchanged files on refresh |

`Retriever.search()` returns `RetrievedChunk(text, source_file, title, section, source_urls, score, chunk_index)`.

## Design notes
- Plain `dataclasses` keep the models dependency-free and easy to serialise (`to_dict()`).
- `Finding.references` carries knowledge-base URLs so every claim can be traced to an official source.
- `ValidationResult.status` distinguishes *invalid code* from *validator unavailable*, so a missing JDK is never reported as a code error.
