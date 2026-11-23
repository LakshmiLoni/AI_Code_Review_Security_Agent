# Input Validation & Defensive Boundary Enforcement

## 1. Overview
All data arriving across a trust boundary (HTTP parameters, JSON request bodies, file uploads, headers, environment flags, database reads) must be treated as untrusted input. Input validation ensures that data conforms to strict syntax, length, character set, and semantic rules before processing.

- **CWE Identifier**: CWE-20 (Improper Input Validation)
- **OWASP Category**: A03:2021 - Injection / A04:2021 - Insecure Design

## 2. Validation Strategies
- **Positive / Whitelist Validation (Recommended)**: Explicitly permit only known safe characters and formats.
- **Negative / Blacklist Validation (Fragile)**: Rejecting specific keywords is easily bypassed via obfuscation or encoding variations.

## 3. Vulnerable vs Secure Code Examples

### Python Pydantic Input Validation
```python
# VULNERABLE: Processing raw, unvalidated JSON dictionary
def register_user(payload: dict):
    age = int(payload['age']) # May cause unhandled exception or integer overflow
    email = payload['email'] # Could be anything

# SECURE: Strict schema validation using Pydantic
from pydantic import BaseModel, EmailStr, Field

class UserRegistrationSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, pattern=r'^[a-zA-Z0-9_]+$')
    email: EmailStr
    age: int = Field(..., ge=18, le=120)

def register_user_secure(raw_data: dict):
    validated_user = UserRegistrationSchema(**raw_data)
    return validated_user
```

### Java Jakarta Bean Validation
```java
// SECURE: Validating DTOs with Jakarta / Hibernate Validator
public class UserCreateRequest {

    @NotBlank(message = "Username cannot be blank")
    @Size(min = 4, max = 25)
    @Pattern(regexp = "^[A-Za-z0-9_-]+$")
    private String username;

    @Email(message = "Invalid email format")
    @NotBlank
    private String email;

    @Min(18)
    @Max(120)
    private int age;
}
```

## 4. Key Rules
- Perform validation on the server side; client-side validation is solely for user convenience and easily bypassed.
- Enforce length limits on strings to prevent Denial of Service (ReDoS) and memory exhaustion.
