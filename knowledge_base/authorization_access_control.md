# Authorization & Broken Access Control Prevention

## 1. Overview
Authorization determines what actions an authenticated principal is permitted to execute. Broken Access Control allows unauthorized information disclosure, data manipulation, or elevation of privilege. It ranks #1 in the OWASP Top 10 (A01:2021).

- **CWE Identifiers**: CWE-285 (Improper Authorization), CWE-639 (Insecure Direct Object Reference - IDOR)
- **OWASP Category**: A01:2021 - Broken Access Control
- **Severity**: High to Critical

## 2. Types of Access Control Failures
- **Vertical Privilege Escalation**: A standard user accesses an administrative URL or endpoint.
- **Horizontal Privilege Escalation (IDOR)**: A user accesses another user's private records by modifying an object reference.
- **Context-dependent Bypasses**: Skipping steps in a multi-step workflow.

## 3. Vulnerable vs Secure Code Implementations

### Python Flask IDOR Mitigation
```python
# VULNERABLE: Direct query without tenant or ownership verification
@app.route('/invoice/<int:invoice_id>')
def view_invoice(invoice_id):
    invoice = db.query("SELECT * FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
    return jsonify(invoice)

# SECURE: Explicit ownership check tied to authenticated principal
@app.route('/invoice_secure/<int:invoice_id>')
@login_required
def view_invoice_secure(invoice_id):
    invoice = db.query(
        "SELECT * FROM invoices WHERE id = ? AND user_id = ?",
        (invoice_id, current_user.id)
    ).fetchone()
    if not invoice:
        abort(404, description="Invoice not found or access denied")
    return jsonify(invoice)
```

### Java Method-Level Security
```java
// SECURE: Enforcing Role-Based Access Control via Spring Security annotations
@RestController
@RequestMapping("/api/admin")
public class AdminController {

    @PreAuthorize("hasRole('ADMIN')")
    @DeleteMapping("/users/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        userService.deleteUser(id);
        return ResponseEntity.noContent().build();
    }
}
```

## 4. Defensive Rules
- Default Deny: Deny access to all endpoints by default; explicitly declare public routes.
- Enforce authorization checks in the business logic layer, not merely in the presentation layer.
- Disable web server directory listing and ensure file metadata is protected.
