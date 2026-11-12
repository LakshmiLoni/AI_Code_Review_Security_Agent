# OWASP Top 10 Security Vulnerabilities & Mitigations Guide

## 1. Overview and Purpose
The Open Web Application Security Project (OWASP) Top 10 represents the standard awareness document for developers and web application security. It provides a consensus of the most critical security risks facing modern web applications, APIs, and microservices. Understanding these vulnerabilities enables engineering teams to design, code, and test defensive mechanisms effectively.

## 2. OWASP Top 10 (2021) Categories
1. **A01:2021 - Broken Access Control**: Failures in enforcing access restrictions, permitting users to view or modify unauthorized resources.
2. **A02:2021 - Cryptographic Failures**: Flaws related to cryptography exposing sensitive data (formerly Sensitive Data Exposure).
3. **A03:2021 - Injection**: SQL, NoSQL, OS Command, and ORM injection resulting from untrusted input passed to interpreters.
4. **A04:2021 - Insecure Design**: Flaws in software architectural design and threat modeling before implementation.
5. **A05:2021 - Security Misconfiguration**: Default credentials, verbose error messages, open cloud storage, and unhardened servers.
6. **A06:2021 - Vulnerable and Outdated Components**: Using dependencies with known CVEs without active monitoring or patching.
7. **A07:2021 - Identification and Authentication Failures**: Weak authentication, session fixation, credential stuffing, and missing brute-force defense.
8. **A08:2021 - Software and Data Integrity Failures**: Insecure CI/CD pipelines, auto-update mechanisms without verification, and unsafe deserialization.
9. **A09:2021 - Security Logging and Monitoring Failures**: Insufficient audit logs, unmonitored anomalies, and slow incident detection.
10. **A10:2021 - Server-Side Request Forgery (SSRF)**: Web applications fetching remote resources without validating the target URI.

## 3. Real-World Risk & Attack Scenarios
- **Scenario A**: An e-commerce platform passes `order_id` in a GET parameter. An attacker changes `order_id=1001` to `order_id=1002` and reads another customer's invoice (Broken Access Control / IDOR).
- **Scenario B**: A user search query is concatenated into an SQL string: `SELECT * FROM users WHERE name = '` + input + `'`. An attacker enters `' OR '1'='1` and dumps the entire user database.
- **Scenario C**: An application logs user session tokens and payment card data in plaintext to central log files, accessible to unauthorized engineers.

## 4. Defense-in-Depth Implementation Checklist
- Implement least-privilege role-based access control (RBAC) enforced server-side.
- Always use parameterized queries (PreparedStatement in Java, bound parameters in Python).
- Enforce TLS 1.3 for all transit and AES-256-GCM for sensitive data at rest.
- Maintain an active Software Bill of Materials (SBOM) and run automated SCA (Software Composition Analysis).
- Enable structured audit logging while strictly masking Personally Identifiable Information (PII).

## 5. References and Further Reading
- OWASP Top 10: https://owasp.org/Top10/
- OWASP Application Security Verification Standard (ASVS) 4.0
- NIST Special Publication 800-53: Security and Privacy Controls
