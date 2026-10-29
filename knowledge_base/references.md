# Authoritative Security References and Standards

This document compiles the formal industry, academic, and governmental references utilized by the **AI Code Review & Security Analysis Agent** and indexed into its Retrieval-Augmented Generation (RAG) knowledge engine.

---

## 1. OWASP (Open Web Application Security Project) Standards
- **OWASP Top 10 Web Application Security Risks (2021)**:
  - Official URL: [https://owasp.org/Top10/](https://owasp.org/Top10/)
  - Focus: Core taxonomy of critical web vulnerabilities (A01:2021 through A10:2021).
- **OWASP API Security Top 10 (2023)**:
  - Official URL: [https://owasp.org/www-project-api-security/](https://owasp.org/www-project-api-security/)
  - Focus: Modern API threat vectors including BOLA, Broken Authentication, and Mass Assignment.
- **OWASP Cheat Sheet Series**:
  - SQL Injection Prevention Cheat Sheet: [https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
  - Cross-Site Scripting (XSS) Prevention Cheat Sheet: [https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
  - Cryptographic Storage Cheat Sheet: [https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
  - Password Storage Cheat Sheet: [https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
  - File Upload Cheat Sheet: [https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
  - Deserialization Cheat Sheet: [https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html)

---

## 2. MITRE Common Weakness Enumeration (CWE)
- **CWE/SANS Top 25 Most Dangerous Software Weaknesses**:
  - Official URL: [https://cwe.mitre.org/top25/](https://cwe.mitre.org/top25/)
- Key CWEs Tracked:
  - **CWE-89**: Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')
  - **CWE-78**: Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')
  - **CWE-79**: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')
  - **CWE-22**: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')
  - **CWE-502**: Deserialization of Untrusted Data
  - **CWE-798**: Use of Hard-coded Credentials
  - **CWE-327**: Use of a Broken or Risky Cryptographic Algorithm
  - **CWE-338**: Use of Cryptographically Weak Pseudo-Random Number Generator (PRNG)
  - **CWE-209**: Generation of Error Message Containing Sensitive Information
  - **CWE-117**: Improper Output Handling for Logs
  - **CWE-287**: Improper Authentication
  - **CWE-285**: Improper Authorization

---

## 3. Python Security Documentation & PEPs
- **Python Security Considerations in standard library**:
  - `secrets` — Generate secure tokens: [https://docs.python.org/3/library/secrets.html](https://docs.python.org/3/library/secrets.html)
  - `subprocess` — Subprocess management and security considerations: [https://docs.python.org/3/library/subprocess.html#security-considerations](https://docs.python.org/3/library/subprocess.html#security-considerations)
  - `pickle` — Restricting and avoiding pickle on untrusted data: [https://docs.python.org/3/library/pickle.html](https://docs.python.org/3/library/pickle.html)
  - `xml` — XML vulnerabilities and defusedxml: [https://docs.python.org/3/library/xml.html#xml-vulnerabilities](https://docs.python.org/3/library/xml.html#xml-vulnerabilities)
- **Python Enhancement Proposals**:
  - PEP 506: Adding A Secrets Module to The Standard Library
  - PEP 8: Style Guide for Python Code

---

## 4. Java SE and Jakarta EE Security Standards
- **SEI CERT Oracle Coding Standard for Java**:
  - Official URL: [https://wiki.sei.cmu.edu/confluence/display/java/SEI+CERT+Oracle+Coding+Standard+for+Java](https://wiki.sei.cmu.edu/confluence/display/java/SEI+CERT+Oracle+Coding+Standard+for+Java)
  - Rule IDS00-J: Prevent SQL injection
  - Rule IDS01-J: Normalize strings before validating them
  - Rule IDS07-J: Do not pass untrusted, unsanitized data to the Execution Shell
  - Rule SER00-J: Enable serialization filtering during ObjectInputStream
  - Rule MSC02-J: Generate strong random numbers using java.security.SecureRandom
- **Java Cryptography Architecture (JCA) Reference Guide**:
  - Official URL: [https://docs.oracle.com/en/java/javase/21/security/java-cryptography-architecture-jca-reference-guide.html](https://docs.oracle.com/en/java/javase/21/security/java-cryptography-architecture-jca-reference-guide.html)

---

## 5. National Institute of Standards and Technology (NIST)
- **NIST SP 800-53 Rev. 5**: Security and Privacy Controls for Information Systems and Organizations.
- **NIST SP 800-63B**: Digital Identity Guidelines — Authentication and Lifecycle Management.
- **NIST SP 800-132**: Recommendation for Password-Based Key Derivation (PBKDF2).

---

## 6. Academic and Theoretical Foundations
- **Rice's Theorem**: Rice, H. G. (1953). "Classes of recursively enumerable sets and their decision problems". Transactions of the American Mathematical Society. Proof of undecidability in static program properties.
- **Saltzer and Schroeder**: Saltzer, J. H., & Schroeder, M. D. (1975). "The protection of information in computer systems". Proceedings of the IEEE. Foundational principles of least privilege, fail-safe defaults, and economy of mechanism.
