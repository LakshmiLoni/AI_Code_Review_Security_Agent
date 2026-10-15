# Cross-Site Scripting (XSS)

## Definition
Cross-Site Scripting is an injection attack where untrusted data is included in a web page without proper handling, so the victim's browser runs attacker-supplied JavaScript in the context of the trusted site. In OWASP Top 10 it is part of A05:2025 Injection (CWE-79).

## Types
- **Reflected XSS** - the payload is in the request (e.g. a URL parameter) and echoed back immediately.
- **Stored XSS** - the payload is saved (comment, profile field) and served to every viewer.
- **DOM-based XSS** - client-side JavaScript writes untrusted data into the page (`innerHTML`, `document.write`).

## Risk
Session theft, account takeover, forged actions on behalf of the user, defacement, and malware delivery. Stored XSS can spread to many users.

## Vulnerable example (Python / Flask)
```python
@app.route("/greet")
def greet():
    name = request.args.get("name", "")
    return "<h1>Hello " + name + "</h1>"        # VULNERABLE: name=<script>...</script>
```

## Vulnerable example (Java servlet)
```java
String name = request.getParameter("name");
response.getWriter().println("<h1>Hello " + name + "</h1>");   // VULNERABLE
```

## Recommended prevention
1. **Output-encode by context** (HTML body, attribute, JavaScript, URL, CSS). Encoding is the main defence.
2. Use frameworks that auto-escape templates (Jinja2 with autoescape on, Thymeleaf, JSP with `<c:out>`); avoid "raw"/"safe" bypasses on untrusted data.
3. Never insert untrusted data with `innerHTML`; use `textContent`.
4. Add a restrictive **Content-Security-Policy** header as defence in depth.
5. Mark session cookies `HttpOnly` and `Secure`.
6. If rich HTML must be accepted, sanitise it with a maintained library using an allow-list.

## Secure example (Python)
```python
from html import escape

@app.route("/greet")
def greet():
    name = request.args.get("name", "")
    return "<h1>Hello " + escape(name) + "</h1>"
```
Better still, render with an auto-escaping template engine.

## What a reviewer looks for
Request data concatenated into HTML strings; templates using `|safe`, `Markup()`, `th:utext`, or `<%= %>` without escaping; `innerHTML` assignments.

## Sources
- https://owasp.org/www-community/attacks/xss/
- https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- https://docs.python.org/3/library/html.html
- https://cwe.mitre.org/data/definitions/79.html
