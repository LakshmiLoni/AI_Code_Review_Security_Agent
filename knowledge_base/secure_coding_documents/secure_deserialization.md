# Insecure Deserialization Vulnerabilities & Safe Parsing

## 1. Description and Mechanism
Serialization converts complex object graphs in memory into byte streams or text formats for storage or transmission. Deserialization reconstructs the objects. Insecure deserialization occurs when an application deserializes untrusted data without verification, allowing an attacker to instantiate arbitrary classes, tamper with application state, or execute arbitrary code via gadget chains.

- **CWE Identifier**: CWE-502 (Deserialization of Untrusted Data)
- **OWASP Category**: A08:2021 - Software and Data Integrity Failures
- **Severity**: Critical (CVSS 9.0 - 10.0)

## 2. Vulnerable vs Secure Code Examples

### Python Pickle Vulnerability
```python
# VULNERABLE: Deserializing untrusted pickle byte stream
import pickle

def load_user_session(cookie_data: bytes):
    return pickle.loads(cookie_data)

# SECURE: Use safe, standard data formats like JSON or cryptographic signatures
import json
from itsdangerous import URLSafeTimedSerializer

SECRET_KEY = "my-secure-application-secret"
serializer = URLSafeTimedSerializer(SECRET_KEY)

def dump_session_secure(data: dict) -> str:
    return serializer.dumps(data)

def load_session_secure(token: str, max_age_seconds: int = 3600) -> dict:
    return serializer.loads(token, max_age=max_age_seconds)
```

### Python PyYAML Safety
```python
# VULNERABLE: PyYAML default load executes arbitrary python tags
import yaml
config = yaml.load(user_input)

# SECURE: Always use SafeLoader
config = yaml.safe_load(user_input)
```

### Java ObjectInputStream Hardening
```java
// VULNERABLE: Direct Java native deserialization
ObjectInputStream ois = new ObjectInputStream(inputStream);
Object obj = ois.readObject();

// SECURE: Restricting allowed classes using ObjectInputFilter (Java 9+)
import java.io.ObjectInputFilter;

ObjectInputStream ois = new ObjectInputStream(inputStream);
ObjectInputFilter filter = ObjectInputFilter.Config.createFilter(
    "com.mycompany.model.SafeData;!*"
);
ois.setObjectInputFilter(filter);
Object obj = ois.readObject();
```

## 3. Recommendations
- Avoid binary serialization formats across untrusted boundaries.
- Migrate to standard formats: JSON, Protocol Buffers, or CBOR.
- If native deserialization cannot be avoided, implement strict class whitelisting.
