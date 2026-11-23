# Secure REST & GraphQL API Architecture Guidelines

## 1. API Security Overview
APIs serve as the foundational interface for modern web, mobile, and microservice architectures. Flaws in API design expose backend services directly to automated attacks, data scraping, and business logic abuse.

- **OWASP Reference**: OWASP API Security Top 10 (2023)
- **Top Risks**: Broken Object Level Authorization (BOLA), Broken Object Property Level Authorization (BOPLA), Unrestricted Resource Consumption.

## 2. Key API Security Controls

### A. Rate Limiting and Throttling
APIs must limit requests per client IP or authenticated user to prevent DoS, credential stuffing, and scraping.
```python
# SECURE: Flask-Limiter for API rate limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

@app.route("/api/v1/resource")
@limiter.limit("10 per minute")
def get_resource():
    return {"status": "ok"}
```

### B. Strict HTTP Method & Header Enforcement
- Reject unexpected HTTP verbs (e.g. only allow GET on retrieval endpoints).
- Set standard security headers on all responses:
  - Strict-Transport-Security: max-age=31536000; includeSubDomains
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - Cache-Control: no-store, max-age=0

### C. Mass Assignment Prevention
Avoid binding incoming request payloads directly to internal database entity models.
```python
# VULNERABLE: Direct dictionary update allows client to set isAdmin=True
def update_profile(user, data: dict):
    for key, value in data.items():
        setattr(user, key, value)

# SECURE: Whitelist allowable attributes
ALLOWED_FIELDS = {'first_name', 'last_name', 'bio'}
def update_profile_secure(user, data: dict):
    for key in ALLOWED_FIELDS:
        if key in data:
            setattr(user, key, data[key])
```

## 3. Best Practices
- Never transmit unencrypted tokens or credentials over HTTP; strictly enforce HTTPS/TLS.
- Implement API versioning in the URL path (/api/v1/) to manage breaking security changes cleanly.
- Use JWT tokens with short lifetimes (15 minutes) combined with revocable refresh tokens.
