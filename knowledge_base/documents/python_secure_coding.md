# Secure Python Coding Practices

## Definition
Secure Python coding means using the language and standard library in ways that avoid common vulnerability patterns. Python's dynamic features (`eval`, `pickle`, `subprocess`, `yaml.load`) are powerful but dangerous with untrusted input.

## 1. Never evaluate untrusted input
```python
result = eval(user_input)            # VULNERABLE: arbitrary code execution
```
Use `ast.literal_eval` for literals only, or parse explicitly (`int()`, `json.loads`). Avoid `exec`, `eval` and `compile` on external data.

## 2. Avoid shell injection
```python
import os
os.system("ping " + host)                         # VULNERABLE
subprocess.run("ping " + host, shell=True)        # VULNERABLE
```
Pass a list of arguments and keep `shell=False` (the default):
```python
subprocess.run(["ping", "-c", "1", host], check=True, capture_output=True, timeout=10)
```
Validate `host` against an allow-list or pattern first.

## 3. Do not unpickle untrusted data
`pickle`, `marshal` and `shelve` can execute code while loading. Use JSON (or another data-only format) for data crossing a trust boundary. For YAML use `yaml.safe_load`, never `yaml.load` without a safe loader.

## 4. Use secure randomness and hashing
- Tokens, password-reset codes, session IDs: use the `secrets` module (`secrets.token_urlsafe(32)`), not `random`.
- Do not use MD5 or SHA-1 for security. Store passwords with scrypt/Argon2/bcrypt (see `authentication_authorization.md`).
- Compare secrets with `hmac.compare_digest`.

## 5. Parameterise database queries
Use placeholders (`?`, `%s`, named parameters) and pass values separately (see `sql_injection.md`).

## 6. Handle files and paths safely
```python
from pathlib import Path
BASE = Path("/srv/uploads").resolve()
target = (BASE / user_filename).resolve()
if BASE not in target.parents:
    raise PermissionError("path traversal attempt")      # prevents ../../ escapes
```
Use `tempfile` (not predictable names in `/tmp`) and close files with `with`.

## 7. Network and TLS
Never disable certificate verification (`requests.get(url, verify=False)`). Set timeouts on network calls. Do not run Flask/Django with `debug=True` in production.

## 8. Validate input and handle errors deliberately
Validate type, length, range and format at the boundary. Catch specific exceptions, do not use bare `except: pass`, and do not return stack traces to users. Use `assert` only for developer checks - assertions are removed with `python -O`.

## 9. Manage dependencies
Pin versions in `requirements.txt`, scan with `pip-audit`, use virtual environments, and install only trusted packages (beware typosquatting).

## 10. Keep secrets out of code
Read them from environment variables or a secret manager (see `secrets_management.md`).

## Sources
- https://docs.python.org/3/library/security_warnings.html
- https://docs.python.org/3/library/subprocess.html#security-considerations
- https://docs.python.org/3/library/pickle.html
- https://docs.python.org/3/library/secrets.html
- https://docs.python.org/3/library/hashlib.html
- https://docs.python.org/3/library/ast.html#ast.literal_eval
- https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html
