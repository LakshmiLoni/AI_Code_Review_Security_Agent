# OWASP Top 10 Web Application Security Risks

## Definition
The OWASP Top 10 is an awareness document published by the Open Web Application Security Project. It lists the ten most critical categories of web application security risk, based on vulnerability data and a community survey. It is a starting point for secure development, not a complete checklist. The current edition is **OWASP Top 10:2025** (final release January 2026); the previous edition is 2021.

## The 2025 list
| ID | Category | Short explanation |
|----|----------|-------------------|
| A01:2025 | Broken Access Control | Users can act outside their intended permissions (also now includes SSRF). |
| A02:2025 | Security Misconfiguration | Insecure defaults, open cloud storage, verbose errors, unneeded features enabled. |
| A03:2025 | Software Supply Chain Failures | Compromised or vulnerable dependencies, build systems and distribution channels. |
| A04:2025 | Cryptographic Failures | Weak or missing encryption, bad key management, weak hashing. |
| A05:2025 | Injection | Untrusted data interpreted as commands or queries (SQL injection, XSS, OS command injection). |
| A06:2025 | Insecure Design | Missing or flawed security controls at design level; cannot be fixed by perfect coding alone. |
| A07:2025 | Authentication Failures | Weak login, credential stuffing, bad session handling, weak password recovery. |
| A08:2025 | Software or Data Integrity Failures | Trusting unsigned updates, insecure deserialization, unverified CI/CD artifacts. |
| A09:2025 | Security Logging and Alerting Failures | Missing logs/alerts, so attacks go unnoticed. |
| A10:2025 | Mishandling of Exceptional Conditions | Poor error handling, failing open, leaking details in exceptions. |

## What changed from 2021
- Two new categories: Software Supply Chain Failures (broadens "Vulnerable and Outdated Components") and Mishandling of Exceptional Conditions.
- Server-Side Request Forgery (SSRF), a separate item in 2021, is folded into Broken Access Control.
- Security Misconfiguration rose to #2; Injection fell to #5; "Identification and Authentication Failures" is now "Authentication Failures".
- Many online tutorials still use the 2021 numbering (A01 Broken Access Control, A02 Cryptographic Failures, A03 Injection, A04 Insecure Design, A05 Security Misconfiguration, A06 Vulnerable and Outdated Components, A07 Identification and Authentication Failures, A08 Software and Data Integrity Failures, A09 Security Logging and Monitoring Failures, A10 SSRF). Always state which edition you cite.

## Why it matters for code review
Most categories map to concrete code patterns a reviewer can spot: string-built SQL (A05), missing ownership checks (A01), hardcoded keys (A04/A07), `pickle.loads` on untrusted data (A08), bare `except: pass` (A10). The knowledge base in this project is organised around these patterns.

## Prevention (general principles)
1. Enforce authorisation on the server for every request (deny by default).
2. Treat all external input as untrusted; validate it and use safe APIs (parameterised queries, output encoding).
3. Keep secrets out of source code; use well-vetted crypto libraries.
4. Pin, scan and update dependencies; verify the integrity of build artifacts.
5. Fail securely and log security-relevant events.

## Sources
- https://owasp.org/Top10/2025/
- https://owasp.org/Top10/2025/A01_2025-Broken_Access_Control/
- https://cheatsheetseries.owasp.org/
