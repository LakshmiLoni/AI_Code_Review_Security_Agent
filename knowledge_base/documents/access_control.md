# Broken Access Control

## Definition
Access control enforces policy so that users cannot act outside their intended permissions. It is **broken** when those checks are missing, incomplete, or can be bypassed. It is ranked **A01:2025** (also #1 in 2021): OWASP's testing found some form of broken access control in every application tested. SSRF and CSRF-related weaknesses are now grouped with it.

## Risk
Unauthorised viewing, modification or deletion of other users' data; privilege escalation to administrator; exposure of internal functions and files.

## Common forms
- **IDOR (Insecure Direct Object Reference)**: changing `?invoice_id=1001` to `1002` shows someone else's invoice because ownership is never checked.
- **Missing function-level checks**: `/admin/...` URLs reachable by ordinary users; POST/PUT/DELETE endpoints without checks.
- **Privilege escalation**: user-controlled `role`/`is_admin` fields trusted from the request or a cookie.
- **Force browsing** to unlinked pages; **path traversal** (`../../etc/passwd`).
- Access control only in the front end (hiding buttons) rather than on the server.
- Misconfigured CORS or tampered JWT claims granting extra permission.

## Vulnerable example (Python / Flask)
```python
@app.route("/invoice/<int:invoice_id>")
@login_required
def get_invoice(invoice_id):
    return jsonify(Invoice.query.get_or_404(invoice_id).to_dict())   # VULNERABLE: any logged-in user
```

## Vulnerable example (Java / Spring)
```java
@GetMapping("/admin/users")
public List<User> allUsers() { return userRepository.findAll(); }     // VULNERABLE: no role check
```

## Recommended prevention
1. **Deny by default** - everything is forbidden unless explicitly allowed.
2. Enforce authorisation **on the server** for every request, centrally (middleware, decorators, `@PreAuthorize`) rather than ad hoc.
3. Check **ownership** of every object: query by both the object ID and the current user.
4. Never trust client-supplied roles, IDs of the acting user, or hidden fields; derive identity from the server-side session/token.
5. Use unpredictable identifiers (UUIDs) as defence in depth, not as the control itself.
6. Restrict file access to a safe base directory (resolve and verify paths).
7. Log access-control failures, alert on repeated ones, and include authorisation tests in unit/integration tests.

## Secure example (Python / Flask)
```python
@app.route("/invoice/<int:invoice_id>")
@login_required
def get_invoice(invoice_id):
    invoice = Invoice.query.filter_by(id=invoice_id, owner_id=current_user.id).first_or_404()
    return jsonify(invoice.to_dict())
```

## Secure example (Java / Spring)
```java
@PreAuthorize("hasRole('ADMIN')")
@GetMapping("/admin/users")
public List<User> allUsers() { return userRepository.findAll(); }
```

## Sources
- https://owasp.org/Top10/2025/A01_2025-Broken_Access_Control/
- https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
- https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html
- https://cwe.mitre.org/data/definitions/284.html
