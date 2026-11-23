# Secrets Management and API Key Protection

## 1. Problem Statement
Hardcoding credentials, API tokens, cryptographic private keys, database passwords, or JWT signing secrets directly into source code repositories is one of the most common causes of data breaches. Once committed, credentials can be harvested by scanners or leaked via version control backups.

- **CWE Identifier**: CWE-798 (Use of Hard-coded Credentials)
- **OWASP Category**: A05:2021 - Security Misconfiguration

## 2. Vulnerable vs Secure Code Examples

### Python Secrets Handling
```python
# VULNERABLE: Hardcoded API keys in source code
AWS_SECRET_KEY = "AKIAIOSFODNN7EXAMPLE" # Leaked in version control
DATABASE_URL = "postgres://root:p@ssword123@db.prod.internal/app"

# SECURE: Retrieving credentials from environment variables or AWS Secrets Manager
import os
from dotenv import load_dotenv

load_dotenv()

AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")

if not AWS_SECRET_KEY:
    raise RuntimeError("Missing required AWS_SECRET_KEY environment variable.")
```

### Java Secrets Management
```java
// SECURE: Injecting secrets via Spring Boot configuration properties from vault
@Component
public class PaymentGatewayClient {

    @Value("${payment.api.key}")
    private String apiKey;

    public void processPayment() {
        if (apiKey == null || apiKey.isBlank()) {
            throw new IllegalStateException("Payment API Key is unconfigured.");
        }
    }
}
```

## 3. Best Practices & Tooling
- Use centralized secret management solutions: HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, or GCP Secret Manager.
- Add .env, *.pem, *.key, id_rsa, and credential stores to .gitignore.
- Employ pre-commit git hooks to block commits containing high-entropy strings or known token regex patterns.
- Implement automated secret rotation policies every 90 days.
