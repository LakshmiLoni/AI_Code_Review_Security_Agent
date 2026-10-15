# Hardcoded Credentials and Secrets

## Definition
A hardcoded secret is a password, API key, token, private key or connection string written directly in source code or committed configuration. It is catalogued as CWE-798 (Use of Hard-coded Credentials) and relates to OWASP A04:2025 Cryptographic Failures and A07:2025 Authentication Failures.

## Risk
Anyone with access to the repository, a build artifact, a decompiled binary or a leaked backup can use the secret. Secrets committed to version control remain in history even after deletion, and public-repository leaks are scanned by attackers within minutes. The same secret in every deployment cannot be rotated without redeploying.

## Vulnerable example (Python)
```python
DB_PASSWORD = "Sup3rS3cret!"                       # VULNERABLE
API_KEY = sk_test_YOUR_STRIPE_API_KEY_HERE    # VULNERABLE
conn = connect(host="db.internal", user="admin", password=DB_PASSWORD)
```

## Vulnerable example (Java)
```java
private static final String PASSWORD = "admin123";   // VULNERABLE: also visible in the .class file
Connection c = DriverManager.getConnection(url, "admin", PASSWORD);
```

## Recommended prevention
1. **Load secrets at runtime** from environment variables or a dedicated secret manager (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager).
2. Keep local `.env` files out of version control (`.gitignore`) and commit only a `.env.example` with placeholders.
3. Use **least-privilege**, short-lived credentials and rotate them regularly.
4. Run secret scanning (pre-commit hooks, CI scanners) to block commits that contain secrets.
5. **If a secret leaked, revoke and rotate it immediately** - deleting the commit is not enough.
6. Never log secrets or include them in error messages.

## Secure example (Python)
```python
import os

DB_PASSWORD = os.environ["DB_PASSWORD"]   # fails loudly if missing
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY is not configured")
```

## Secure example (Java)
```java
String password = System.getenv("DB_PASSWORD");
if (password == null || password.isEmpty()) {
    throw new IllegalStateException("DB_PASSWORD is not configured");
}
```

## What a reviewer looks for
Variables named `password`, `secret`, `token`, `api_key`, `private_key` assigned string literals; strings that look like keys (`AKIA...`, `sk_live_...`, `-----BEGIN PRIVATE KEY-----`); credentials inside connection URLs.

## Sources
- https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- https://cwe.mitre.org/data/definitions/798.html
- https://docs.python.org/3/library/os.html#os.environ
- https://docs.python.org/3/library/secrets.html
