# Cross-Site Request Forgery (CSRF)

## Definition
CSRF tricks a logged-in user's browser into sending an unwanted state-changing request (change email, transfer money) to a site that trusts the browser's cookies. The server cannot tell the forged request from a genuine one because the browser attaches the session cookie automatically. CSRF is CWE-352 and is grouped under A01:2025 Broken Access Control.

## Risk
The attacker cannot read the response, but can make the victim perform any action the victim is allowed to do: change passwords, post content, make purchases, change settings.

## Vulnerable example (Python / Flask)
```python
@app.route("/transfer", methods=["POST"])
def transfer():
    # Relies only on the session cookie - no CSRF token is checked.
    move_money(session["user_id"], request.form["to"], request.form["amount"])
    return "done"
```
A malicious page can auto-submit a hidden form to `/transfer` while the victim is logged in.

## Vulnerable example (Java)
```java
// State change triggered by a GET request, no token, no origin check
@GetMapping("/deleteAccount")
public String delete(HttpSession session) { accountService.delete(session.getAttribute("user")); return "ok"; }
```

## Recommended prevention
1. **Synchroniser (anti-CSRF) tokens**: a random per-session (or per-request) token embedded in forms and verified server-side on every state-changing request. Use your framework's built-in protection (Flask-WTF `CSRFProtect`, Django's CSRF middleware, Spring Security CSRF).
2. **Never change state with GET** requests.
3. Set cookies with `SameSite=Lax` or `Strict` (defence in depth, not a replacement for tokens).
4. Verify `Origin` / `Referer` headers on sensitive requests.
5. Require re-authentication for high-risk actions.
6. Remember that XSS defeats CSRF defences - fix XSS too.

## Secure example (Python / Flask-WTF)
```python
from flask_wtf import CSRFProtect
csrf = CSRFProtect(app)            # rejects POSTs without a valid token
# In templates: <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```

## What a reviewer looks for
State-changing routes with CSRF protection disabled (`@csrf.exempt`, `http.csrf().disable()`), GET handlers that modify data, cookies without `SameSite`.

## Sources
- https://owasp.org/www-community/attacks/csrf
- https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
- https://cwe.mitre.org/data/definitions/352.html
