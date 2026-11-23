# Cross-Site Scripting (XSS) Prevention & Mitigation

## 1. Description and Mechanism
Cross-Site Scripting (XSS) occurs when an application includes untrusted data in an HTTP response rendered in the user's browser without appropriate validation or context-aware encoding. Attackers can execute arbitrary JavaScript within the context of the victim's session, enabling credential theft, cookie hijacking, session impersonation, and DOM defacement.

- **CWE Identifier**: CWE-79 (Improper Neutralization of Input During Web Page Generation)
- **OWASP Category**: A03:2021 - Injection
- **Types**: Stored XSS, Reflected XSS, DOM-based XSS

## 2. Vulnerable vs Secure Code Implementations

### Python Flask Example
```python
# VULNERABLE: Direct HTML string concatenation or rendering raw HTML
from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route('/greet')
def greet():
    name = request.args.get('name', '')
    # Vulnerable to Reflected XSS:
    return f"<h1>Welcome, {name}!</h1>"

# SECURE: Context-aware HTML escaping using Jinja2 templates or markupsafe
from markupsafe import escape

@app.route('/greet_secure')
def greet_secure():
    name = request.args.get('name', '')
    safe_name = escape(name)
    return f"<h1>Welcome, {safe_name}!</h1>"
```

### Java Spring Boot Example
```java
// VULNERABLE: Writing raw parameter directly to HttpServletResponse
@GetMapping("/search")
public void search(@RequestParam("q") String query, HttpServletResponse response) throws IOException {
    response.setContentType("text/html");
    PrintWriter out = response.getWriter();
    out.println("<div>Results for: " + query + "</div>"); // Reflected XSS
}

// SECURE: Encoding output using OWASP Java HTML Sanitizer / HtmlUtils
import org.springframework.web.util.HtmlUtils;

@GetMapping("/search_secure")
public void searchSecure(@RequestParam("q") String query, HttpServletResponse response) throws IOException {
    response.setContentType("text/html; charset=UTF-8");
    PrintWriter out = response.getWriter();
    String sanitized = HtmlUtils.htmlEscape(query);
    out.println("<div>Results for: " + sanitized + "</div>");
}
```

## 3. Defense-in-Depth Measures
- **Content Security Policy (CSP)**: Deploy a strict CSP header: `Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none';`.
- **HttpOnly Cookies**: Protect session tokens by flagging cookies as `HttpOnly`, preventing JavaScript access via `document.cookie`.
- **Framework Auto-Escaping**: Utilize modern UI frameworks that auto-escape interpolated variables by default.
