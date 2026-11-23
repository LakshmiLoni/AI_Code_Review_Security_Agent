# Python Secure Coding Standard and Defensive Guidelines

## 1. Overview
Python is a dynamically-typed, highly productive language widely used in backend development, data engineering, and machine learning. However, dynamic execution features like eval, exec, pickle, and implicit string conversions introduce substantial security challenges if unconstrained.

## 2. Common Security Pitfalls in Python
- Using eval or exec with untrusted input to parse data.
- Unsafe object deserialization using pickle.loads.
- Unsanitized subprocess calls using subprocess.Popen with shell=True.
- Using hashlib.md5 or hashlib.sha1 for password hashing or integrity verification.
- Formatting raw strings into database cursors (cursor.execute with f-strings).
- Permitting arbitrary file uploads without filename normalization and extension whitelisting.

## 3. Vulnerable vs Secure Code Implementations

### A. Dynamic Code Execution
```python
# VULNERABLE: Arbitrary code execution via eval
def calculate_expression(user_input: str):
    return eval(user_input)  # Attacker submits: __import__('os').system('rm -rf /')

# SECURE: Safe math expression evaluation using ast.literal_eval or math parser
import ast

def safe_calculate(user_input: str):
    # Only allow safe mathematical literals, no calls or imports
    try:
        node = ast.parse(user_input, mode='eval')
        for subnode in ast.walk(node):
            if isinstance(subnode, (ast.Call, ast.Attribute, ast.Import, ast.ImportFrom)):
                raise ValueError("Unauthorized dynamic construct detected.")
        return eval(compile(node, '<string>', 'eval'), {"__builtins__": {}}, {})
    except Exception as exc:
        raise ValueError("Invalid mathematical expression") from exc
```

### B. Command Execution
```python
# VULNERABLE: Shell injection vulnerability
import subprocess

def ping_host(hostname: str):
    return subprocess.check_output(f"ping -c 1 {hostname}", shell=True)

# SECURE: Direct argument vector execution without shell
def ping_host_secure(hostname: str):
    import re
    # Validate hostname strictly
    if not re.match(r"^[a-zA-Z0-9.-]+$", hostname):
        raise ValueError("Invalid hostname format")
    return subprocess.check_output(["ping", "-c", "1", hostname], shell=False)
```

## 4. Best Practices for Python Developers
- Run static security analyzers like Bandit and SonarQube in CI pipelines.
- Use secrets module instead of random for cryptographic tokens, salts, and keys.
- Store sensitive configurations in environment variables via python-dotenv or cloud secrets managers.
- Always validate incoming payloads using schema validators like Pydantic or Marshmallow.
