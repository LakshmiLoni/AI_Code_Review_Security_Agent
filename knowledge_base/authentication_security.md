# Authentication & Credential Management Security

## 1. Overview
Authentication verifies the identity of an actor (user, service, or device) attempting to access a system. Flaws in authentication mechanisms allow attackers to hijack accounts, bypass credentials, or compromise administrative privileges.

- **CWE Identifiers**: CWE-287 (Improper Authentication), CWE-307 (Improper Restriction of Excessive Authentication Attempts)
- **OWASP Category**: A07:2021 - Identification and Authentication Failures

## 2. Common Authentication Vulnerabilities
- Storing passwords in plaintext, reversible encryption, or weak hashes (MD5, SHA1).
- Missing rate-limiting or lockout mechanisms against brute-force attacks.
- Predictable session IDs or session tokens generated using pseudo-random seeds.
- Session fixation: failing to regenerate session IDs upon login.
- Weak password complexity policies.

## 3. Vulnerable vs Secure Code Implementations

### Python Password Hashing
```python
# VULNERABLE: Insecure password hashing using standard SHA256 or MD5
import hashlib

def hash_password_bad(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()

# SECURE: Adaptive hashing using bcrypt or argon2
import bcrypt

def hash_password_secure(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password_secure(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
```

### Java Password Security
```java
// SECURE: Using Spring Security BCryptPasswordEncoder
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

public class AuthService {
    private final BCryptPasswordEncoder encoder = new BCryptPasswordEncoder(12);

    public String hashUserPassword(String rawPassword) {
        return encoder.encode(rawPassword);
    }

    public boolean checkCredentials(String rawPassword, String encodedHash) {
        return encoder.matches(rawPassword, encodedHash);
    }
}
```

## 4. Architectural Best Practices
- Enforce Multi-Factor Authentication (MFA) via TOTP or FIDO2/WebAuthn.
- Implement progressive rate limiting and account throttling.
- Terminate inactive sessions after a defined idle timeout (e.g. 15-30 minutes).
- Always regenerate session identifiers immediately upon successful authentication.
