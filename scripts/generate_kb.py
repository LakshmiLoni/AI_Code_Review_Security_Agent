"""Generate the 20 comprehensive Markdown documents for the secure coding knowledge base."""
import os

BASE_DIR = r"C:\Users\Lakshmi\.gemini\antigravity\scratch\AI_code_review\knowledge_base"
os.makedirs(BASE_DIR, exist_ok=True)

docs = {
    "owasp_top10.md": """# OWASP Top 10 Security Vulnerabilities & Mitigations Guide

## 1. Overview and Purpose
The Open Web Application Security Project (OWASP) Top 10 represents the standard awareness document for developers and web application security. It provides a consensus of the most critical security risks facing modern web applications, APIs, and microservices. Understanding these vulnerabilities enables engineering teams to design, code, and test defensive mechanisms effectively.

## 2. OWASP Top 10 (2021) Categories
1. **A01:2021 - Broken Access Control**: Failures in enforcing access restrictions, permitting users to view or modify unauthorized resources.
2. **A02:2021 - Cryptographic Failures**: Flaws related to cryptography exposing sensitive data (formerly Sensitive Data Exposure).
3. **A03:2021 - Injection**: SQL, NoSQL, OS Command, and ORM injection resulting from untrusted input passed to interpreters.
4. **A04:2021 - Insecure Design**: Flaws in software architectural design and threat modeling before implementation.
5. **A05:2021 - Security Misconfiguration**: Default credentials, verbose error messages, open cloud storage, and unhardened servers.
6. **A06:2021 - Vulnerable and Outdated Components**: Using dependencies with known CVEs without active monitoring or patching.
7. **A07:2021 - Identification and Authentication Failures**: Weak authentication, session fixation, credential stuffing, and missing brute-force defense.
8. **A08:2021 - Software and Data Integrity Failures**: Insecure CI/CD pipelines, auto-update mechanisms without verification, and unsafe deserialization.
9. **A09:2021 - Security Logging and Monitoring Failures**: Insufficient audit logs, unmonitored anomalies, and slow incident detection.
10. **A10:2021 - Server-Side Request Forgery (SSRF)**: Web applications fetching remote resources without validating the target URI.

## 3. Real-World Risk & Attack Scenarios
- **Scenario A**: An e-commerce platform passes `order_id` in a GET parameter. An attacker changes `order_id=1001` to `order_id=1002` and reads another customer's invoice (Broken Access Control / IDOR).
- **Scenario B**: A user search query is concatenated into an SQL string: `SELECT * FROM users WHERE name = '` + input + `'`. An attacker enters `' OR '1'='1` and dumps the entire user database.
- **Scenario C**: An application logs user session tokens and payment card data in plaintext to central log files, accessible to unauthorized engineers.

## 4. Defense-in-Depth Implementation Checklist
- Implement least-privilege role-based access control (RBAC) enforced server-side.
- Always use parameterized queries (PreparedStatement in Java, bound parameters in Python).
- Enforce TLS 1.3 for all transit and AES-256-GCM for sensitive data at rest.
- Maintain an active Software Bill of Materials (SBOM) and run automated SCA (Software Composition Analysis).
- Enable structured audit logging while strictly masking Personally Identifiable Information (PII).

## 5. References and Further Reading
- OWASP Top 10: https://owasp.org/Top10/
- OWASP Application Security Verification Standard (ASVS) 4.0
- NIST Special Publication 800-53: Security and Privacy Controls
""",

    "python_secure_coding.md": """# Python Secure Coding Standard and Defensive Guidelines

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
""",

    "java_secure_coding.md": """# Java Enterprise Secure Coding Guidelines

## 1. Overview
Java Enterprise applications (Spring Boot, Jakarta EE, Quarkus) power mission-critical banking, healthcare, and enterprise software. Due to Java's strong typing and bytecode compilation, many low-level memory corruption bugs are avoided. However, architectural vulnerabilities such as deserialization, injection, and broken access controls remain prevalent.

## 2. Common Security Vulnerabilities in Java
- Unvalidated deserialization of ObjectInputStream leading to Remote Code Execution (RCE).
- Concatenation of parameters into SQL or HQL/JPQL statements.
- XML External Entity (XXE) injection via unhardened DocumentBuilderFactory or SAXParser.
- Insecure use of Runtime.getRuntime().exec() without command parameterization.
- Using weak random number generators (java.util.Random) for security-sensitive tokens.
- Exposing internal stack traces to end-users via uncaught exceptions in REST controllers.

## 3. Vulnerable vs Secure Code Examples

### A. XML External Entity (XXE) Prevention
```java
// VULNERABLE: Default DocumentBuilderFactory processes external DTD entities
DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
DocumentBuilder builder = factory.newDocumentBuilder();
Document doc = builder.parse(inputStream); // Attacker injects external entities

// SECURE: Disallow DOCTYPE declarations and external entities
DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
factory.setFeature("http://xml.org/sax/features/external-general-entities", false);
factory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
factory.setXIncludeAware(false);
factory.setExpandEntityReferences(false);
DocumentBuilder builder = factory.newDocumentBuilder();
Document doc = builder.parse(inputStream);
```

### B. Secure Random Number Generation
```java
// VULNERABLE: Pseudorandom generator is predictable
import java.util.Random;
Random rng = new Random();
String token = Long.toHexString(rng.nextLong());

// SECURE: Cryptographically Strong SecureRandom
import java.security.SecureRandom;
import java.util.Base64;
SecureRandom secureRng = new SecureRandom();
byte[] randomBytes = new byte[32];
secureRng.nextBytes(randomBytes);
String sessionToken = Base64.getUrlEncoder().withoutPadding().encodeToString(randomBytes);
```

## 4. Key Security Rules for Java Applications
- Disable Java native serialization for network transport; prefer strict JSON or Protobuf.
- Configure Spring Security with explicit CSRF protection, secure cookies (SameSite=Strict, HttpOnly), and CORS policies.
- Sanitize logging output to prevent Log Injection (CRLF injection in log records).
- Use PreparedStatement or JPA criteria builders exclusively for database operations.
""",

    "sql_injection_prevention.md": """# SQL Injection (SQLi) Prevention Standard

## 1. Description and Mechanism
SQL Injection occurs when untrusted user input is directly concatenated, interpolated, or formatted into a database SQL query string. The database interpreter cannot distinguish between the developer's SQL commands and data supplied by the attacker, allowing the attacker to alter the query logic, bypass authentication, exfiltrate confidential data, or execute operating system commands.

- **CWE Identifier**: CWE-89 (Improper Neutralization of Special Elements used in an SQL Command)
- **OWASP Category**: A03:2021 - Injection
- **Severity**: Critical (CVSS 9.0 - 10.0)

## 2. Vulnerable vs Secure Code Implementations

### Python SQLite / PostgreSQL Example
```python
# VULNERABLE: Direct string formatting into SQL query
def get_user_account(cursor, username: str):
    query = f"SELECT id, username, email FROM users WHERE username = '{username}'"
    cursor.execute(query) # Attacker submits: admin' --
    return cursor.fetchone()

# SECURE: Parameterized Query using bound parameter placeholder
def get_user_account_secure(cursor, username: str):
    query = "SELECT id, username, email FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    return cursor.fetchone()
```

### Java JDBC Example
```java
// VULNERABLE: Dynamic SQL string concatenation
public User authenticate(Connection conn, String user, String pass) throws SQLException {
    Statement stmt = conn.createStatement();
    String sql = "SELECT * FROM users WHERE username = '" + user + "' AND password = '" + pass + "'";
    ResultSet rs = stmt.executeQuery(sql); // Attacker passes: ' OR '1'='1
    return mapUser(rs);
}

// SECURE: Java PreparedStatement with parameter binding
public User authenticateSecure(Connection conn, String user, String pass) throws SQLException {
    String sql = "SELECT * FROM users WHERE username = ? AND password_hash = ?";
    try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
        pstmt.setString(1, user);
        pstmt.setString(2, hashPassword(pass));
        try (ResultSet rs = pstmt.executeQuery()) {
            return mapUser(rs);
        }
    }
}
```

## 3. Defense Techniques
1. **Parameterized Queries / Prepared Statements**: Completely decouples SQL code from data variables.
2. **Object-Relational Mapping (ORM)**: Use SQLAlchemy, Hibernate, or Spring Data JPA with bound entities.
3. **Stored Procedures with Parameters**: Parameterized stored procedures prevent structural query alteration.
4. **Principle of Least Privilege**: Ensure the database user account only has necessary permissions.
5. **Input Validation**: Enforce strict alphanumeric whitelisting on fields like identifiers and table names.
""",

    "xss_prevention.md": """# Cross-Site Scripting (XSS) Prevention & Mitigation

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
""",

    "csrf_protection.md": """# Cross-Site Request Forgery (CSRF) Protection

## 1. Description and Mechanism
Cross-Site Request Forgery (CSRF) is an attack that forces an authenticated end-user to execute unauthorized actions on a web application in which they are currently logged in. By tricking the browser into sending an HTTP request containing the victim's session cookies to the target application, the server assumes the legitimate user initiated the transaction.

- **CWE Identifier**: CWE-352 (Cross-Site Request Forgery)
- **OWASP Category**: A01:2021 - Broken Access Control
- **Severity**: High (CVSS 7.0 - 8.8)

## 2. Vulnerable vs Secure Patterns

### Python Flask Example
```python
# VULNERABLE: State-changing endpoint executed via GET without token verification
@app.route('/transfer', methods=['GET', 'POST'])
def transfer_money():
    recipient = request.args.get('to')
    amount = request.args.get('amount')
    db.execute("UPDATE accounts SET balance = balance - ? WHERE user = ?", (amount, current_user))
    return "Transferred successfully"

# SECURE: Flask-WTF CSRFProtect with Synchronizer Token Pattern
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

@app.route('/transfer_secure', methods=['POST'])
def transfer_secure():
    recipient = request.form['to']
    amount = request.form['amount']
    process_transfer(current_user, recipient, amount)
    return "Transfer complete"
```

### Java Spring Security Example
```java
// SECURE: Enabling CSRF tokens in Spring Security configuration
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf
                .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
            )
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/public/**").permitAll()
                .anyRequest().authenticated()
            );
        return http.build();
    }
}
```

## 3. Mitigation Strategies
- **Synchronizer Token Pattern**: Issue unique, cryptographically random CSRF tokens tied to user sessions. Validate token on every state-changing request.
- **SameSite Cookie Attribute**: Set SameSite=Strict or SameSite=Lax on all session cookies.
- **Double-Submit Cookie Pattern**: Used for stateless APIs where a pseudo-random value is sent both in a cookie and in a custom header.
""",

    "authentication_security.md": """# Authentication & Credential Management Security

## 1. Overview
Authentication verifies the identity of an actor (user, service, or device) attempting to access a system. Flaws in authentication mechanisms allow attackers to hijack accounts, bypass credentials, or compromise administrative privileges.

- **CWE Identifiers**: CWE-287 (Improper Authentication), CWE-307 (Improper Restriction of Excessive Authentication Attempts)
- **OWASP Category**: A07:2021 - Identification and Authentication Failures

## 2. Common Authentication Vulnerabilities
- Storing passwords in plaintext, reversible encryption, or weak hashes (MD5, SHA1).
- Missing rate-limiting or lockout mechanisms against brute-force attacks.
- Predictable session IDs or session tokens generated using pseudo-random seeds.
- Session fixation: failing to regenerate session IDs upon login.
- Weak password complexity policies.

## 3. Vulnerable vs Secure Code Implementations

### Python Password Hashing
```python
# VULNERABLE: Insecure password hashing using standard SHA256 or MD5
import hashlib

def hash_password_bad(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()

# SECURE: Adaptive hashing using bcrypt or argon2
import bcrypt

def hash_password_secure(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password_secure(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
```

### Java Password Security
```java
// SECURE: Using Spring Security BCryptPasswordEncoder
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

public class AuthService {
    private final BCryptPasswordEncoder encoder = new BCryptPasswordEncoder(12);

    public String hashUserPassword(String rawPassword) {
        return encoder.encode(rawPassword);
    }

    public boolean checkCredentials(String rawPassword, String encodedHash) {
        return encoder.matches(rawPassword, encodedHash);
    }
}
```

## 4. Architectural Best Practices
- Enforce Multi-Factor Authentication (MFA) via TOTP or FIDO2/WebAuthn.
- Implement progressive rate limiting and account throttling.
- Terminate inactive sessions after a defined idle timeout (e.g. 15-30 minutes).
- Always regenerate session identifiers immediately upon successful authentication.
""",

    "authorization_access_control.md": """# Authorization & Broken Access Control Prevention

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
""",

    "secrets_management.md": """# Secrets Management and API Key Protection

## 1. Problem Statement
Hardcoding credentials, API tokens, cryptographic private keys, database passwords, or JWT signing secrets directly into source code repositories is one of the most common causes of data breaches. Once committed, credentials can be harvested by scanners or leaked via version control backups.

- **CWE Identifier**: CWE-798 (Use of Hard-coded Credentials)
- **OWASP Category**: A05:2021 - Security Misconfiguration

## 2. Vulnerable vs Secure Code Examples

### Python Secrets Handling
```python
# VULNERABLE: Hardcoded API keys in source code
AWS_SECRET_KEY = "AKIAIOSFODNN7EXAMPLE" # Leaked in version control
DATABASE_URL = "postgres://root:p@ssword123@db.prod.internal/app"

# SECURE: Retrieving credentials from environment variables or AWS Secrets Manager
import os
from dotenv import load_dotenv

load_dotenv()

AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")

if not AWS_SECRET_KEY:
    raise RuntimeError("Missing required AWS_SECRET_KEY environment variable.")
```

### Java Secrets Management
```java
// SECURE: Injecting secrets via Spring Boot configuration properties from vault
@Component
public class PaymentGatewayClient {

    @Value("${payment.api.key}")
    private String apiKey;

    public void processPayment() {
        if (apiKey == null || apiKey.isBlank()) {
            throw new IllegalStateException("Payment API Key is unconfigured.");
        }
    }
}
```

## 3. Best Practices & Tooling
- Use centralized secret management solutions: HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, or GCP Secret Manager.
- Add .env, *.pem, *.key, id_rsa, and credential stores to .gitignore.
- Employ pre-commit git hooks to block commits containing high-entropy strings or known token regex patterns.
- Implement automated secret rotation policies every 90 days.
""",

    "input_validation.md": """# Input Validation & Defensive Boundary Enforcement

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
""",

    "output_encoding.md": """# Output Encoding & Context-Aware Data Sanitization

## 1. Purpose of Output Encoding
Output encoding transforms untrusted data before it is rendered or interpreted by a downstream parser (HTML renderer, JavaScript interpreter, CSS parser, URL resolver, XML parser). By converting special control characters into their safe, inert representations, the target interpreter treats the characters as literal display content rather than executable code.

- **CWE Identifier**: CWE-116 (Improper Encoding or Escaping of Output)
- **OWASP Category**: A03:2021 - Injection

## 2. Context-Specific Encoding Requirements
1. **HTML Body Context**: Convert & to &amp;, < to &lt;, > to &gt;, " to &quot;, ' to &#x27;.
2. **HTML Attribute Context**: Strictly quote all attributes and hex-encode alphanumeric characters.
3. **JavaScript Context**: Encode JSON using Unicode escape sequences (e.g. \\u003cscript\\u003e).
4. **URL Context**: Use percent-encoding (urllib.parse.quote in Python, URLEncoder.encode in Java).

## 3. Code Implementations

### Python Context Encoding
```python
import html
import urllib.parse
import json

def encode_for_html(untrusted: str) -> str:
    return html.escape(untrusted, quote=True)

def encode_for_url(untrusted: str) -> str:
    return urllib.parse.quote(untrusted, safe='')

def serialize_for_script_tag(data: dict) -> str:
    raw_json = json.dumps(data)
    return raw_json.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
```

### Java Output Encoding
```java
import org.owasp.encoder.Encode;

public class OutputSanitizer {
    public static String safeForHtml(String input) {
        return Encode.forHtml(input);
    }

    public static String safeForJavaScript(String input) {
        return Encode.forJavaScript(input);
    }

    public static String safeForUri(String input) {
        return Encode.forUriComponent(input);
    }
}
```

## 4. Architectural Guidelines
- Rely on automated template engines that support context-aware encoding.
- Do not mix raw string concatenation with HTML generation.
""",

    "cryptography_best_practices.md": """# Cryptographic Best Practices & Key Management

## 1. Overview
Cryptography provides confidentiality, data integrity, non-repudiation, and authentication. Implementing custom cryptographic algorithms or using obsolete primitives compromises application security entirely.

- **CWE Identifiers**: CWE-327 (Use of a Broken or Risky Cryptographic Algorithm), CWE-326 (Inadequate Encryption Strength)
- **OWASP Category**: A02:2021 - Cryptographic Failures

## 2. Prohibited vs Recommended Algorithms
- **Broken / Prohibited**:
  - Hashing: MD5, SHA-1
  - Symmetric Ciphers: DES, 3DES, RC4, Blowfish, AES in ECB mode
  - Asymmetric: RSA with keys < 2048 bits
- **Recommended**:
  - Hashing: SHA-256, SHA-384, SHA-512, SHA-3
  - Password Storage: Argon2id, bcrypt (work factor >= 12), PBKDF2 (>= 600,000 iterations)
  - Symmetric Encryption: AES-256-GCM (Authenticated Encryption with Associated Data - AEAD), ChaCha20-Poly1305
  - Asymmetric: RSA >= 3072 bits, ECDSA/Ed25519 with Curve25519

## 3. Vulnerable vs Secure Code Implementations

### Python Cryptography (AES-GCM)
```python
# VULNERABLE: AES in ECB mode without integrity verification or IV
from Crypto.Cipher import AES

def insecure_encrypt(key: bytes, data: bytes):
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(data)

# SECURE: AES-256 in GCM mode with random 96-bit nonce and authentication tag
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def secure_encrypt(key: bytes, plaintext: bytes, associated_data: bytes = b"") -> bytes:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
    return nonce + ciphertext

def secure_decrypt(key: bytes, payload: bytes, associated_data: bytes = b"") -> bytes:
    nonce = payload[:12]
    ciphertext = payload[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, associated_data)
```

### Java AES-GCM Implementation
```java
// SECURE: AES-GCM implementation in Java
import javax.crypto.Cipher;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import java.security.SecureRandom;

public class EncryptionUtil {
    private static final int GCM_TAG_LENGTH = 128;
    private static final int IV_LENGTH = 12;

    public static byte[] encrypt(SecretKey key, byte[] plaintext) throws Exception {
        byte[] iv = new byte[IV_LENGTH];
        new SecureRandom().nextBytes(iv);

        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        GCMParameterSpec spec = new GCMParameterSpec(GCM_TAG_LENGTH, iv);
        cipher.init(Cipher.ENCRYPT_MODE, key, spec);

        byte[] cipherText = cipher.doFinal(plaintext);
        byte[] combined = new byte[iv.length + cipherText.length];
        System.arraycopy(iv, 0, combined, 0, iv.length);
        System.arraycopy(cipherText, 0, combined, iv.length, cipherText.length);
        return combined;
    }
}
```

## 4. Key Rules
- Never reuse a Nonce/IV with the same secret key in GCM mode.
- Always use constant-time comparison (hmac.compare_digest in Python, MessageDigest.isEqual in Java).
""",

    "secure_file_handling.md": """# Secure File Handling & Upload Protection

## 1. Description and Risks
Accepting file uploads from untrusted users introduces critical risks, including arbitrary code execution, server compromise, cross-site scripting (via SVG or HTML files), server storage exhaustion, and malware dissemination.

- **CWE Identifier**: CWE-434 (Unrestricted Upload of File with Dangerous Type)
- **OWASP Category**: A04:2021 - Insecure Design / A01:2021 - Broken Access Control

## 2. Vulnerable vs Secure Code Implementations

### Python Secure File Upload
```python
# VULNERABLE: Direct file saving with user-supplied filename
from flask import request

@app.route('/upload', methods=['POST'])
def upload_file_vulnerable():
    file = request.files['file']
    file.save('/var/www/uploads/' + file.filename)
    return "Uploaded"

# SECURE: Secure filename handling, size limits, and extension whitelisting
import os
import uuid
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.pdf'}
UPLOAD_FOLDER = '/var/app/secure_storage'
MAX_SIZE = 5 * 1024 * 1024 # 5MB

def allowed_file(filename: str) -> bool:
    _, ext = os.path.splitext(filename)
    return ext.lower() in ALLOWED_EXTENSIONS

@app.route('/upload_secure', methods=['POST'])
def upload_file_secure():
    if 'file' not in request.files:
        abort(400, "No file provided")
    file = request.files['file']
    if not file.filename or not allowed_file(file.filename):
        abort(400, "Invalid file format")

    _, ext = os.path.splitext(secure_filename(file.filename))
    safe_name = f"{uuid.uuid4().hex}{ext.lower()}"
    destination = os.path.join(UPLOAD_FOLDER, safe_name)

    file.save(destination)
    return {"status": "success", "file_id": safe_name}
```

## 3. Defense Checklist
- Store uploaded files outside the public web root.
- Validate actual file content headers (Magic Bytes) using filetype or python-magic.
- Serve uploads with Content-Disposition: attachment and X-Content-Type-Options: nosniff.
- Scan uploaded files for malware using ClamAV or equivalent virus scanning engine.
""",

    "command_injection_prevention.md": """# Command Injection Prevention & Safe Process Execution

## 1. Description and Mechanism
Command injection occurs when an application passes unsanitized user data to an operating system system shell (sh, bash, cmd.exe). Attackers can append command separators (;, &&, |, `, $(...)) to execute arbitrary operating system commands with the privileges of the web application service.

- **CWE Identifier**: CWE-78 (Improper Neutralization of Special Elements used in an OS Command)
- **OWASP Category**: A03:2021 - Injection
- **Severity**: Critical (CVSS 9.0 - 10.0)

## 2. Vulnerable vs Secure Code Implementations

### Python Process Spawning
```python
# VULNERABLE: Invoking system shell with formatted string
import os

def generate_report(report_name: str):
    os.system(f"generate_pdf --name {report_name}") # Command injection

# SECURE: Use subprocess without shell, passing arguments as a sequence
import subprocess
import re

def generate_report_secure(report_name: str):
    if not re.match(r'^[a-zA-Z0-9_-]{1,64}$', report_name):
        raise ValueError("Invalid report name format")

    result = subprocess.run(
        ["generate_pdf", "--name", report_name],
        capture_output=True,
        text=True,
        check=True,
        shell=False
    )
    return result.stdout
```

### Java Process Execution
```java
// VULNERABLE: Concatenating input into shell command
public void runTool(String fileName) throws IOException {
    Runtime.getRuntime().exec("sh -c 'convert " + fileName + " output.png'");
}

// SECURE: ProcessBuilder with explicit token arguments
public void runToolSecure(String fileName) throws IOException, InterruptedException {
    if (!fileName.matches("^[a-zA-Z0-9._-]{1,100}$")) {
        throw new IllegalArgumentException("Invalid file name format");
    }

    ProcessBuilder pb = new ProcessBuilder("convert", fileName, "output.png");
    pb.redirectErrorStream(true);
    Process process = pb.start();
    int exitCode = process.waitFor();
    if (exitCode != 0) {
        throw new RuntimeException("Process failed with code " + exitCode);
    }
}
```

## 3. Core Mitigation Rules
- Avoid invoking OS commands altogether; use native language libraries.
- If system commands are mandatory, pass arguments as discrete array elements and set shell=False.
- Execute processes under low-privilege dedicated service accounts using sandboxing.
""",

    "path_traversal_prevention.md": """# Path Traversal (Directory Traversal) Prevention

## 1. Description and Risks
Path Traversal vulnerabilities occur when user input is used to construct a file system path without proper sanitization. By supplying sequences like ../ or ..\\\\, an attacker can escape the intended directory and access sensitive files on the filesystem, such as /etc/passwd or application source code.

- **CWE Identifier**: CWE-22 (Improper Limitation of a Pathname to a Restricted Directory)
- **OWASP Category**: A01:2021 - Broken Access Control
- **Severity**: High (CVSS 7.5 - 8.6)

## 2. Vulnerable vs Secure Code Implementations

### Python Path Resolution
```python
# VULNERABLE: Blindly joining user path
import os

def read_user_file(filename: str):
    base_dir = "/app/user_files"
    path = os.path.join(base_dir, filename)
    with open(path, 'r') as f:
        return f.read()

# SECURE: Resolving absolute path and verifying containment
from pathlib import Path

def read_user_file_secure(filename: str):
    base_dir = Path("/app/user_files").resolve()
    target_path = (base_dir / filename).resolve()

    if not target_path.is_relative_to(base_dir):
        raise PermissionError("Access denied: Path traversal attempt detected.")

    if not target_path.is_file():
        raise FileNotFoundError("Requested file does not exist.")

    return target_path.read_text(encoding='utf-8')
```

### Java Path Verification
```java
// SECURE: Normalizing path and verifying directory containment in Java
import java.io.File;
import java.io.IOException;

public class SafeFileReader {
    public static File getSafeFile(File baseDirectory, String requestedFilename) throws IOException {
        File targetFile = new File(baseDirectory, requestedFilename).getCanonicalFile();
        File canonicalBase = baseDirectory.getCanonicalFile();

        if (!targetFile.getPath().startsWith(canonicalBase.getPath() + File.separator)) {
            throw new SecurityException("Path traversal attempt detected: " + requestedFilename);
        }
        return targetFile;
    }
}
```

## 3. Best Practices
- Never use user-supplied input directly as a filesystem path.
- Store documents in object storage using opaque UUID keys instead of local paths.
- Strip path separators and strictly whitelist allowable filenames.
""",

    "secure_deserialization.md": """# Insecure Deserialization Vulnerabilities & Safe Parsing

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
""",

    "python_code_quality.md": """# Python Code Quality, Readability, and Anti-Patterns

## 1. Overview
High-quality code minimizes bugs, reduces cognitive load, improves maintainability, and prevents subtle security regressions. Adhering to Python standard conventions (PEP 8, PEP 257) ensures uniform codebase structure.

## 2. Common Code Smells in Python
- **Overly Long Functions**: Functions exceeding 40-50 lines usually violate the Single Responsibility Principle.
- **Deep Nesting**: Nesting conditional statements deeper than 3 levels impairs readability and increases cyclomatic complexity.
- **Bare Except Clauses**: Catching all exceptions with `except:` masks syntax errors, system exits, and memory errors.
- **Mutable Default Arguments**: Using `def append_to(item, target=[])` causes state to persist across function calls.
- **Wildcard Imports**: `from module import *` pollutes namespace and obscures variable origin.
- **Dead / Unused Code**: Unreferenced variables, imports, and functions add unnecessary clutter.

## 3. Refactoring Code Smells

### A. Mutable Default Argument Fix
```python
# CODE SMELL: Mutable list as default argument
def add_entry(entry: str, log: list = []):
    log.append(entry)
    return log

# CLEAN REFACTOR: Use None sentinel value
from typing import Optional, List

def add_entry_clean(entry: str, log: Optional[List[str]] = None) -> List[str]:
    if log is None:
        log = []
    log.append(entry)
    return log
```

### B. Guard Clauses to Reduce Nesting
```python
# CODE SMELL: Excessive nesting
def process_order(order):
    if order is not None:
        if order.is_paid:
            if order.items:
                if not order.is_shipped:
                    order.ship()
                    return "Shipped"

# CLEAN REFACTOR: Inverted guard clauses (Bouncer pattern)
def process_order_clean(order):
    if order is None:
        return "Invalid order"
    if not order.is_paid:
        return "Order unpaid"
    if not order.items:
        return "Empty order"
    if order.is_shipped:
        return "Already shipped"

    order.ship()
    return "Shipped"
```

## 4. Key Metrics
- Keep Cyclomatic Complexity under 10 per function.
- Enforce type hints (typing module) and run mypy in CI pipelines.
- Automate style enforcement with ruff, flake8, and black.
""",

    "java_code_quality.md": """# Java Code Quality Standards & Clean Architecture

## 1. Overview
In enterprise Java development, maintaining clean code principles and reducing complexity is critical for enterprise maintainability. Consistent adherence to Java naming conventions, SOLID design principles, and effective error handling prevents technical debt.

## 2. Common Java Code Quality Issues
- **God Classes**: Single classes containing thousands of lines and multiple unrelated responsibilities.
- **Empty Catch Blocks**: Catching exceptions and silently ignoring them: `catch (Exception e) {}`.
- **Excessive Parameter Lists**: Methods with more than 4-5 parameters make unit testing and invocation error-prone.
- **Primitive Obsession**: Using raw strings and integers instead of domain value objects.
- **NullPointerExceptions**: Improper null handling without Optional or annotations (@NonNull).
- **Resource Leaks**: Neglecting to close database connections or streams.

## 3. Refactoring Patterns

### A. Try-With-Resources for Safe Clean-up
```java
// CODE SMELL: Manual resource closing prone to leaks
FileInputStream fis = null;
try {
    fis = new FileInputStream("data.txt");
    fis.read();
} catch (IOException e) {
    logger.error("Read failed", e);
} finally {
    if (fis != null) {
        try { fis.close(); } catch (IOException ignore) {}
    }
}

// CLEAN REFACTOR: Try-with-resources statement (AutoCloseable)
try (FileInputStream fis = new FileInputStream("data.txt")) {
    fis.read();
} catch (IOException e) {
    logger.error("Read failed", e);
}
```

### B. Builder Pattern for Complex Constructors
```java
// CODE SMELL: Telescoping constructors with 8 arguments
public User(String id, String first, String last, String email, String phone, String address, boolean active, int role) { }

// CLEAN REFACTOR: Builder Pattern or Lombok @Builder
User user = User.builder()
    .id("USR-101")
    .firstName("Alice")
    .lastName("Smith")
    .email("alice@example.com")
    .active(true)
    .build();
```

## 4. Best Practices
- Avoid returning null from collections; return Collections.emptyList() or Optional.
- Keep methods focused on doing one thing well (Single Responsibility Principle).
- Employ SonarQube, SpotBugs, and Checkstyle in Maven/Gradle builds.
""",

    "clean_code_principles.md": """# Clean Code Principles & Architectural Guidelines

## 1. The Core Philosophy of Clean Code
Clean code is readable, simple, direct, and well-tested. As Robert C. Martin states, the ratio of time spent reading versus writing code is well over 10 to 1. Making code easy to read directly improves engineering velocity and software reliability.

## 2. The SOLID Principles
- **S - Single Responsibility Principle (SRP)**: A class or function should have one, and only one, reason to change.
- **O - Open/Closed Principle (OCP)**: Software entities should be open for extension, but closed for modification.
- **L - Liskov Substitution Principle (LSP)**: Subtypes must be substitutable for their base types without altering correctness.
- **I - Interface Segregation Principle (ISP)**: Clients should not be forced to depend on methods they do not use.
- **D - Dependency Inversion Principle (DIP)**: Depend upon abstractions, not concretions.

## 3. General Clean Coding Guidelines
1. **Meaningful Names**: Variable and method names should reveal intent. Avoid cryptic abbreviations.
2. **Small Functions**: Functions should hardly ever be 20 lines long. Each function should tell a cohesive story.
3. **Do One Thing (SRP)**: Functions should do one thing, and do it well.
4. **Don't Repeat Yourself (DRY)**: Duplicated code represents duplicated maintenance burden. Extract common abstractions.
5. **Fail Fast**: Check conditions at boundaries and throw expressive, typed exceptions immediately.
6. **Self-Documenting Code**: Well-written code with clear naming and structure reduces the need for redundant comments.

## 4. Code Review Checklist for Quality
- Is the purpose of each function obvious from its name and signature?
- Are boundary edge cases (null values, empty collections, extreme numbers) handled?
- Are resources (database handles, network sockets, file descriptors) properly managed?
- Are magic numbers replaced by named constants?
- Is there sufficient test coverage for critical business logic paths?
""",

    "secure_api_development.md": """# Secure REST & GraphQL API Architecture Guidelines

## 1. API Security Overview
APIs serve as the foundational interface for modern web, mobile, and microservice architectures. Flaws in API design expose backend services directly to automated attacks, data scraping, and business logic abuse.

- **OWASP Reference**: OWASP API Security Top 10 (2023)
- **Top Risks**: Broken Object Level Authorization (BOLA), Broken Object Property Level Authorization (BOPLA), Unrestricted Resource Consumption.

## 2. Key API Security Controls

### A. Rate Limiting and Throttling
APIs must limit requests per client IP or authenticated user to prevent DoS, credential stuffing, and scraping.
```python
# SECURE: Flask-Limiter for API rate limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

@app.route("/api/v1/resource")
@limiter.limit("10 per minute")
def get_resource():
    return {"status": "ok"}
```

### B. Strict HTTP Method & Header Enforcement
- Reject unexpected HTTP verbs (e.g. only allow GET on retrieval endpoints).
- Set standard security headers on all responses:
  - Strict-Transport-Security: max-age=31536000; includeSubDomains
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - Cache-Control: no-store, max-age=0

### C. Mass Assignment Prevention
Avoid binding incoming request payloads directly to internal database entity models.
```python
# VULNERABLE: Direct dictionary update allows client to set isAdmin=True
def update_profile(user, data: dict):
    for key, value in data.items():
        setattr(user, key, value)

# SECURE: Whitelist allowable attributes
ALLOWED_FIELDS = {'first_name', 'last_name', 'bio'}
def update_profile_secure(user, data: dict):
    for key in ALLOWED_FIELDS:
        if key in data:
            setattr(user, key, data[key])
```

## 3. Best Practices
- Never transmit unencrypted tokens or credentials over HTTP; strictly enforce HTTPS/TLS.
- Implement API versioning in the URL path (/api/v1/) to manage breaking security changes cleanly.
- Use JWT tokens with short lifetimes (15 minutes) combined with revocable refresh tokens.
"""
}

total_lines = 0
for filename, content in docs.items():
    filepath = os.path.join(BASE_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    lines = content.strip().count("\n") + 1
    total_lines += lines
    print(f"Created {filename}: {lines} lines")

print(f"\nTotal Knowledge Base Lines across {len(docs)} documents: {total_lines}")
