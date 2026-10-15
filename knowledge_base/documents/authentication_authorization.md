# Authentication and Authorization Weaknesses

## Definitions
- **Authentication** answers "who are you?" (login, tokens, sessions, MFA).
- **Authorization** answers "what are you allowed to do?" (roles, permissions, ownership).
Confusing the two is a classic source of vulnerabilities. In OWASP Top 10:2025, weak authentication is A07:2025 Authentication Failures; weak authorization is A01:2025 Broken Access Control (see `access_control.md`).

## Common authentication weaknesses
- Passwords stored in plain text or with fast hashes (MD5, SHA-1, unsalted SHA-256).
- No protection against brute force or credential stuffing (no rate limit, lockout or MFA).
- Weak or default passwords allowed; insecure password reset flows.
- Predictable or long-lived session IDs; session ID not regenerated after login; sessions not invalidated on logout.
- Tokens (JWT) accepted without signature verification (`alg: none`), without expiry, or signed with a weak/hardcoded key.
- Different error messages for "unknown user" and "wrong password" (account enumeration).

## Vulnerable example (Python)
```python
import hashlib

def register(db, username, password):
    digest = hashlib.md5(password.encode()).hexdigest()      # VULNERABLE: fast, unsalted hash
    db.save(username, digest)

def login(db, username, password):
    user = db.find(username)
    if user is None:
        return "No such user"                                # VULNERABLE: user enumeration
    return "ok" if user.password == password else "Wrong password"   # VULNERABLE: plain-text compare
```

## Vulnerable example (Java)
```java
String hash = MessageDigest.getInstance("MD5").digest(password.getBytes()).toString();  // VULNERABLE
```

## Recommended prevention
1. Hash passwords with a slow, salted, purpose-built algorithm: **Argon2id**, scrypt, bcrypt or PBKDF2 with a high iteration count. Never invent your own scheme.
2. Offer and encourage **multi-factor authentication**.
3. Rate-limit and monitor failed logins; use generic error messages ("invalid username or password").
4. Generate session IDs with a cryptographically secure random generator, regenerate after login, set `HttpOnly`, `Secure`, `SameSite`, and expire/invalidate on logout.
5. Verify JWT signatures and expiry with a maintained library; pin the allowed algorithms.
6. Compare secrets in constant time (`hmac.compare_digest`, `MessageDigest.isEqual`).

## Secure example (Python, standard library)
```python
import hashlib, hmac, os

def hash_password(password: str) -> bytes:
    salt = os.urandom(16)
    return salt + hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)

def verify_password(password: str, stored: bytes) -> bool:
    salt, expected = stored[:16], stored[16:]
    candidate = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return hmac.compare_digest(candidate, expected)
```

## Sources
- https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
- https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
- https://docs.python.org/3/library/hashlib.html
- https://docs.python.org/3/library/hmac.html
