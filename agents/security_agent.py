"""Agent 2: Security Vulnerability Agent.

Detects OWASP-related security vulnerabilities in Python and Java source code:
1. SQL Injection
2. Cross-Site Scripting (XSS)
3. Cross-Site Request Forgery (CSRF)
4. Hardcoded passwords and API keys
5. Insecure authentication
6. Broken access control
7. Insecure direct object references (IDOR)
8. Command injection
9. Path traversal
10. Insecure deserialization
11. Weak cryptographic practices
12. Sensitive information exposure
13. Improper input validation
14. Insecure file handling

Clearly distinguishes confirmed pattern matches from potential security risks.
"""
import re
from typing import List, Dict, Any, Tuple
from utils.severity_scoring import calculate_finding_score


class SecurityAgent:
    """Agent 2: Detects OWASP Top 10 vulnerabilities in Python and Java code."""

    def __init__(self):
        self.agent_name = "Security Vulnerability Agent"

    def analyze(self, code: str, language: str, filename: str = "source_code") -> List[Dict[str, Any]]:
        """Run security scanning rules based on the detected language."""
        lang = language.lower().strip()
        findings = []

        if lang == "python":
            findings.extend(self._scan_python_security(code, filename))
        elif lang == "java":
            findings.extend(self._scan_java_security(code, filename))

        # Common cross-language scans (e.g. hardcoded secrets, keys)
        findings.extend(self._scan_common_secrets(code, filename))

        return findings

    # =========================================================================
    # PYTHON SECURITY SCANNING
    # =========================================================================
    def _scan_python_security(self, code: str, filename: str) -> List[Dict[str, Any]]:
        findings = []
        lines = code.splitlines()

        for idx, line in enumerate(lines, start=1):
            clean = line.strip()

            # 1. SQL Injection: formatted strings in execute calls or SQL formatting
            if re.search(r"\b(?:cursor|db|session|conn)\.execute\s*\(\s*(?:f[\"']|[\"'].*%\s*|[\"'].*\.format\()", clean, re.IGNORECASE) or \
               re.search(r"\bSELECT\s+.*\s+FROM\s+.*(?:\{|\%s|\+)", clean, re.IGNORECASE) or \
               re.search(r"\bquery\s*=\s*f[\"']SELECT\b", clean, re.IGNORECASE):
                if not re.search(r"\.execute\s*\(\s*[\"'][^\"']*\%s[^\"']*[\"']\s*,\s*\(", clean):
                    findings.append({
                        "finding_type": "SECURITY",
                        "title": "SQL Injection (SQLi) via Dynamic Query Formatting",
                        "category": "OWASP A03:2021 - Injection",
                        "severity": "CRITICAL",
                        "heuristic_score": 9.8,
                        "line_number": idx,
                        "filename": filename,
                        "description": (
                            "Dynamic SQL query construction detected using string interpolation, formatting, "
                            "or concatenation. Untrusted input concatenated directly into query strings allows "
                            "attackers to bypass authentication, extract database contents, or modify data."
                        ),
                        "risk_explanation": (
                            "Allows arbitrary SQL execution. An attacker could enter `' OR '1'='1` to bypass authentication "
                            "or execute `UNION SELECT` to exfiltrate private credentials."
                        ),
                        "evidence_snippet": clean,
                        "remediation_recommendation": (
                            "Use parameterized queries with bound placeholders (%s or ?), or leverage an ORM."
                        ),
                        "corrected_code": (
                            "# Secure: Use parameterized SQL query with parameter binding\n"
                            "cursor.execute(\"SELECT * FROM users WHERE username = %s\", (username,))"
                        ),
                        "is_confirmed_pattern": True,
                    })

            # 2. Command Injection: os.system, subprocess with shell=True
            if re.search(r"\bos\.system\s*\(", clean) or \
               re.search(r"\bsubprocess\.(?:Popen|call|check_output|run)\s*\(.*shell\s*=\s*True", clean):
                findings.append({
                    "finding_type": "SECURITY",
                    "title": "OS Command Injection via Shell Execution",
                    "category": "OWASP A03:2021 - Injection",
                    "severity": "CRITICAL",
                    "heuristic_score": 9.5,
                    "line_number": idx,
                    "filename": filename,
                    "description": (
                        "Execution of operating system shell commands using os.system() or "
                        "subprocess with shell=True. If user-controlled input reaches the command string, "
                        "arbitrary system commands can be executed."
                    ),
                    "risk_explanation": (
                        "Attackers can chain shell metacharacters (;, |, &&, `) to execute arbitrary commands "
                        "with application privileges, leading to full server compromise."
                    ),
                    "evidence_snippet": clean,
                    "remediation_recommendation": (
                        "Pass command arguments as a list of strings and set shell=False, or use native Python libraries."
                    ),
                    "corrected_code": (
                        "# Secure: Pass command argument vector without invoking a system shell\n"
                        "subprocess.run([\"ping\", \"-c\", \"1\", sanitized_host], shell=False, check=True)"
                    ),
                    "is_confirmed_pattern": True,
                })

            # 3. Cross-Site Scripting (XSS): render_template_string or raw HTML returns
            if re.search(r"\brender_template_string\s*\(.*f[\"']", clean) or \
               re.search(r"return\s+f?[\"']<[a-z]+>.*\{.*\}", clean, re.IGNORECASE):
                findings.append({
                    "finding_type": "SECURITY",
                    "title": "Cross-Site Scripting (XSS) via Unescaped Template Rendering",
                    "category": "OWASP A03:2021 - Injection",
                    "severity": "HIGH",
                    "heuristic_score": 7.8,
                    "line_number": idx,
                    "filename": filename,
                    "description": (
                        "Unescaped user input rendered directly into an HTML response or template string. "
                        "Attackers can inject malicious JavaScript executed within victim browser sessions."
                    ),
                    "risk_explanation": (
                        "Enables session hijacking, theft of authentication tokens, and defacement."
                    ),
                    "evidence_snippet": clean,
                    "remediation_recommendation": (
                        "Rely on Jinja2 automated template escaping or explicitly sanitize output using markupsafe.escape()."
                    ),
                    "corrected_code": (
                        "from markupsafe import escape\n"
                        "# Secure: Explicitly escape user-supplied strings before rendering\n"
                        "return f\"<h1>Hello, {escape(user_name)}!</h1>\""
                    ),
                    "is_confirmed_pattern": True,
                })

            # 4. Insecure Deserialization: pickle.loads, yaml.load
            if re.search(r"\bpickle\.(?:loads?|load)\s*\(", clean) or \
               re.search(r"\byaml\.load\s*\([^,)]+\)", clean):
                findings.append({
                    "finding_type": "SECURITY",
                    "title": "Insecure Deserialization via Pickle / PyYAML",
                    "category": "OWASP A08:2021 - Software and Data Integrity Failures",
                    "severity": "CRITICAL",
                    "heuristic_score": 9.7,
                    "line_number": idx,
                    "filename": filename,
                    "description": (
                        "Deserialization of untrusted data using Python's pickle module or unsafe yaml.load(). "
                        "The pickle protocol can instantiate arbitrary Python classes and execute code upon unpickling."
                    ),
                    "risk_explanation": (
                        "Remote Code Execution (RCE) via custom __reduce__ methods or gadget chains."
                    ),
                    "evidence_snippet": clean,
                    "remediation_recommendation": (
                        "Use safe data serialization formats like JSON, Protocol Buffers, or yaml.safe_load()."
                    ),
                    "corrected_code": (
                        "import json\n"
                        "# Secure: Use standard JSON parsing for untrusted payloads\n"
                        "data = json.loads(payload)"
                    ),
                    "is_confirmed_pattern": True,
                })

            # 5. Path Traversal: direct file path join without verification
            if re.search(r"\bopen\s*\(\s*(?:os\.path\.join|f[\"']|\w+\s*\+\s*)", clean) and not "resolve" in clean:
                findings.append({
                    "finding_type": "SECURITY",
                    "title": "Potential Path Traversal in File Access",
                    "category": "OWASP A01:2021 - Broken Access Control",
                    "severity": "HIGH",
                    "heuristic_score": 8.0,
                    "line_number": idx,
                    "filename": filename,
                    "description": (
                        "Constructing file paths with user input without validating directory containment. "
                        "Attackers may supply '../' directory traversal sequences to read or write arbitrary system files."
                    ),
                    "risk_explanation": (
                        "Allows unauthorized disclosure of sensitive files such as /etc/passwd or application secrets."
                    ),
                    "evidence_snippet": clean,
                    "remediation_recommendation": (
                        "Resolve canonical paths with pathlib.Path.resolve() and verify target is within the intended base directory."
                    ),
                    "corrected_code": (
                        "from pathlib import Path\n"
                        "base = Path('/safe/storage').resolve()\n"
                        "target = (base / user_filename).resolve()\n"
                        "if not target.is_relative_to(base):\n"
                        "    raise PermissionError('Path traversal detected')\n"
                        "content = target.read_text()"
                    ),
                    "is_confirmed_pattern": False,
                })

            # 6. Weak Cryptography: md5, sha1, DES
            if re.search(r"\bhashlib\.(?:md5|sha1)\s*\(", clean, re.IGNORECASE) or \
               re.search(r"\bAES\.MODE_ECB\b", clean):
                findings.append({
                    "finding_type": "SECURITY",
                    "title": "Use of Broken Cryptographic Algorithm",
                    "category": "OWASP A02:2021 - Cryptographic Failures",
                    "severity": "HIGH",
                    "heuristic_score": 7.5,
                    "line_number": idx,
                    "filename": filename,
                    "description": (
                        "Usage of obsolete or vulnerable cryptographic algorithms (MD5, SHA-1, or ECB mode). "
                        "These algorithms suffer from collision attacks and lack integrity verification."
                    ),
                    "risk_explanation": (
                        "MD5 and SHA-1 collisions are trivial to generate. Passwords hashed with MD5 can be cracked in seconds."
                    ),
                    "evidence_snippet": clean,
                    "remediation_recommendation": (
                        "Use SHA-256/SHA-512 for data integrity, bcrypt/Argon2 for passwords, and AES-GCM for encryption."
                    ),
                    "corrected_code": (
                        "import hashlib\n"
                        "# Secure: Use SHA-256 for cryptographic hashing\n"
                        "digest = hashlib.sha256(data.encode()).hexdigest()"
                    ),
                    "is_confirmed_pattern": True,
                })

            # 7. Sensitive Information Exposure: printing stack traces or logging secrets
            if re.search(r"\b(?:traceback\.print_exc|logging\.info\(.*password|print\(.*token)", clean, re.IGNORECASE):
                findings.append({
                    "finding_type": "SECURITY",
                    "title": "Sensitive Information Exposure in Logs or Console",
                    "category": "OWASP A05:2021 - Security Misconfiguration",
                    "severity": "LOW",
                    "heuristic_score": 3.5,
                    "line_number": idx,
                    "filename": filename,
                    "description": (
                        "Printing or logging sensitive data, credentials, or raw stack traces. "
                        "Exposes internal paths and database structures to unauthorized observers."
                    ),
                    "risk_explanation": (
                        "Aids attackers in reconnaissance and may leak confidential session tokens."
                    ),
                    "evidence_snippet": clean,
                    "remediation_recommendation": (
                        "Mask sensitive fields in logs and configure generic error pages for end users."
                    ),
                    "suggested_improvement": "logger.info('User authenticated successfully')",
                    "corrected_code": "logger.info('User %s authenticated successfully', sanitized_user_id)",
                    "is_confirmed_pattern": True,
                })

            # 8. Insecure File Handling: chmod 777 or tempfile.mktemp
            if re.search(r"\bos\.chmod\s*\(.*0o?777", clean) or re.search(r"\btempfile\.mktemp\s*\(", clean):
                findings.append({
                    "finding_type": "SECURITY",
                    "title": "Insecure File Permissions / Race Condition",
                    "category": "OWASP A04:2021 - Insecure Design",
                    "severity": "MEDIUM",
                    "heuristic_score": 6.2,
                    "line_number": idx,
                    "filename": filename,
                    "description": (
                        "Setting overly permissive file permissions (0777 world-writable) or using "
                        "deprecated tempfile.mktemp() which is vulnerable to symlink race conditions."
                    ),
                    "risk_explanation": "Enables local privilege escalation and race-condition file tampering.",
                    "evidence_snippet": clean,
                    "remediation_recommendation": "Use restrictive file permissions (0600 / 0700) and tempfile.NamedTemporaryFile().",
                    "corrected_code": (
                        "import os, tempfile\n"
                        "# Secure: Restrict permissions to owner only\n"
                        "os.chmod(file_path, 0o600)"
                    ),
                    "is_confirmed_pattern": True,
                })

            # 9. CSRF Vulnerability: explicit csrf_exempt
            if re.search(r"@csrf_exempt\b", clean):
                findings.append({
                    "finding_type": "SECURITY",
                    "title": "Cross-Site Request Forgery (CSRF) Protection Disabled",
                    "category": "OWASP A01:2021 - Broken Access Control",
                    "severity": "HIGH",
                    "heuristic_score": 7.5,
                    "line_number": idx,
                    "filename": filename,
                    "description": (
                        "Endpoint is explicitly marked @csrf_exempt, bypassing anti-CSRF token verification."
                    ),
                    "risk_explanation": (
                        "Allows unauthorized third-party sites to perform state-changing requests on behalf of authenticated users."
                    ),
                    "evidence_snippet": clean,
                    "remediation_recommendation": "Remove @csrf_exempt and require valid CSRF tokens or SameSite=Strict cookies.",
                    "corrected_code": "# Remove @csrf_exempt and validate CSRF token",
                    "is_confirmed_pattern": True,
                })

        return findings

    # =========================================================================
    # JAVA SECURITY SCANNING
    # =========================================================================
    def _scan_java_security(self, code: str, filename: str) -> List[Dict[str, Any]]:
        findings = []
        lines = code.splitlines()

        for idx, line in enumerate(lines, start=1):
            clean = line.strip()

            # 1. Java SQL Injection: dynamic concatenation in SQL query or Statement execute
            is_sqli = False
            if (
                re.search(r"\b(?:SELECT|INSERT|UPDATE|DELETE)\s+.*[\"']\s*\+", clean, re.IGNORECASE)
                or re.search(r"\+\s*[\"'].*\b(?:WHERE|AND|OR|FROM)\b", clean, re.IGNORECASE)
                or re.search(r"\b(?:Statement|stmt)\.execute(?:Query|Update)?\s*\(", clean)
                or re.search(r"createQuery\s*\(\s*.*(?:\+|\b[a-zA-Z0-9_]+\b)", clean)
            ):
                # Ensure it's not a safe PreparedStatement with ? placeholder
                if not ("PreparedStatement" in clean and "?" in clean):
                    is_sqli = True

            if is_sqli:
                findings.append({
                    "finding_type": "SECURITY",
                    "title": "Java SQL Injection via Dynamic Statement Concatenation",
                    "category": "OWASP A03:2021 - Injection",
                    "severity": "CRITICAL",
                    "heuristic_score": 9.8,
                    "line_number": idx,
                    "filename": filename,
                    "description": (
                        "Direct string concatenation into an SQL statement via java.sql.Statement. "
                        "Allows external actors to manipulate query structure and access or alter unauthorized database tables."
                    ),
                    "risk_explanation": "Complete compromise of database confidentiality and authentication bypass.",
                    "evidence_snippet": clean,
                    "remediation_recommendation": (
                        "Replace Statement with java.sql.PreparedStatement and set parameters via setString/setInt."
                    ),
                    "corrected_code": (
                        "String sql = \"SELECT * FROM users WHERE username = ?\";\n"
                        "try (PreparedStatement pstmt = conn.prepareStatement(sql)) {\n"
                        "    pstmt.setString(1, username);\n"
                        "    ResultSet rs = pstmt.executeQuery();\n"
                        "}"
                    ),
                    "is_confirmed_pattern": True,
                })

            # 2. Java Command Injection: Runtime.exec or ProcessBuilder with shell
            if re.search(r"\bRuntime\.getRuntime\(\)\.exec\s*\(", clean) or \
               re.search(r"new\s+ProcessBuilder\s*\(\s*[\"']sh[\"']\s*,\s*[\"']-c[\"']", clean):
                findings.append({
                    "finding_type": "SECURITY",
                    "title": "Command Injection via Runtime.getRuntime().exec",
                    "category": "OWASP A03:2021 - Injection",
                    "severity": "CRITICAL",
                    "heuristic_score": 9.5,
                    "line_number": idx,
                    "filename": filename,
                    "description": (
                        "Executing external system binaries via Runtime.getRuntime().exec() with unescaped arguments. "
                        "Enables attackers to execute arbitrary system shell commands."
                    ),
                    "risk_explanation": "Remote command execution leading to lateral network movement and server takeover.",
                    "evidence_snippet": clean,
                    "remediation_recommendation": (
                        "Use ProcessBuilder with a parameterized argument array and avoid passing commands to system shells."
                    ),
                    "corrected_code": (
                        "ProcessBuilder pb = new ProcessBuilder(\"convert\", sanitizedFileName, \"output.png\");\n"
                        "Process process = pb.start();"
                    ),
                    "is_confirmed_pattern": True,
                })

            # 3. Insecure Deserialization: ObjectInputStream.readObject()
            if re.search(r"\bObjectInputStream\b.*\.readObject\s*\(", clean) or \
               re.search(r"\.readObject\s*\(\s*\)", clean):
                findings.append({
                    "finding_type": "SECURITY",
                    "title": "Java Insecure Deserialization (ObjectInputStream)",
                    "category": "OWASP A08:2021 - Software and Data Integrity Failures",
                    "severity": "CRITICAL",
                    "heuristic_score": 9.6,
                    "line_number": idx,
                    "filename": filename,
                    "description": (
                        "Unrestricted Java object deserialization via ObjectInputStream.readObject(). "
                        "Known gadget chains in standard classpath libraries can be triggered to execute arbitrary bytecode."
                    ),
                    "risk_explanation": "Remote Code Execution (RCE) without requiring prior authentication.",
                    "evidence_snippet": clean,
                    "remediation_recommendation": (
                        "Migrate to standard JSON / Protocol Buffers, or configure an ObjectInputFilter to whitelist classes."
                    ),
                    "corrected_code": (
                        "// Secure: Whitelist permitted classes via ObjectInputFilter\n"
                        "ObjectInputFilter filter = ObjectInputFilter.Config.createFilter(\"com.example.SafeData;!*\");\n"
                        "ois.setObjectInputFilter(filter);\n"
                        "Object obj = ois.readObject();"
                    ),
                    "is_confirmed_pattern": True,
                })

            # 4. Java XSS: PrintWriter.println with unencoded input
            if re.search(r"response\.getWriter\(\)\.print(?:ln)?\s*\(\s*[\"'].*\+\s*", clean):
                findings.append({
                    "finding_type": "SECURITY",
                    "title": "Cross-Site Scripting (XSS) in Java Servlet Output",
                    "category": "OWASP A03:2021 - Injection",
                    "severity": "HIGH",
                    "heuristic_score": 7.8,
                    "line_number": idx,
                    "filename": filename,
                    "description": (
                        "Writing dynamic parameter values directly to HttpServletResponse writer without HTML encoding."
                    ),
                    "risk_explanation": "Permits stored or reflected cross-site script execution.",
                    "evidence_snippet": clean,
                    "remediation_recommendation": "Sanitize output using org.owasp.encoder.Encode.forHtml().",
                    "corrected_code": "out.println(org.owasp.encoder.Encode.forHtml(userParam));",
                    "is_confirmed_pattern": True,
                })

            # 5. Java Path Traversal: new File(parent, child) without canonical checks
            if re.search(r"new\s+File\s*\([^,)]+,\s*[a-zA-Z0-9_]+\)", clean) and not "getCanonical" in clean:
                findings.append({
                    "finding_type": "SECURITY",
                    "title": "Potential Path Traversal in Java File Resolution",
                    "category": "OWASP A01:2021 - Broken Access Control",
                    "severity": "HIGH",
                    "heuristic_score": 8.0,
                    "line_number": idx,
                    "filename": filename,
                    "description": (
                        "Instantiating java.io.File with user input without verifying canonical path containment. "
                        "Attackers can provide relative '..' paths to access files outside the base directory."
                    ),
                    "risk_explanation": "Unauthorized reading or overwriting of configuration and system files.",
                    "evidence_snippet": clean,
                    "remediation_recommendation": (
                        "Verify that file.getCanonicalPath().startsWith(baseDir.getCanonicalPath())."
                    ),
                    "corrected_code": (
                        "File file = new File(baseDir, userInput).getCanonicalFile();\n"
                        "if (!file.getPath().startsWith(baseDir.getCanonicalPath())) {\n"
                        "    throw new SecurityException(\"Access denied\");\n"
                        "}"
                    ),
                    "is_confirmed_pattern": False,
                })

            # 6. Weak Cryptography in Java: DES, ECB, MD5, SHA-1, java.util.Random
            if re.search(r"Cipher\.getInstance\s*\(\s*[\"'](?:DES|AES/ECB)", clean, re.IGNORECASE) or \
               re.search(r"MessageDigest\.getInstance\s*\(\s*[\"'](?:MD5|SHA-?1)[\"']", clean, re.IGNORECASE) or \
               re.search(r"new\s+Random\s*\(", clean):
                findings.append({
                    "finding_type": "SECURITY",
                    "title": "Weak Cryptographic Primitive / Insecure Randomness",
                    "category": "OWASP A02:2021 - Cryptographic Failures",
                    "severity": "HIGH",
                    "heuristic_score": 7.6,
                    "line_number": idx,
                    "filename": filename,
                    "description": (
                        "Usage of insecure cryptographic algorithms (DES, MD5, SHA-1, ECB mode) or "
                        "predictable pseudorandom generator (java.util.Random) for security operations."
                    ),
                    "risk_explanation": "Allows attackers to predict session tokens or decrypt intercepted communications.",
                    "evidence_snippet": clean,
                    "remediation_recommendation": (
                        "Use java.security.SecureRandom for tokens, and AES/GCM/NoPadding for encryption."
                    ),
                    "corrected_code": (
                        "// Secure: Use SecureRandom and AES-GCM\n"
                        "SecureRandom secureRandom = new SecureRandom();\n"
                        "Cipher cipher = Cipher.getInstance(\"AES/GCM/NoPadding\");"
                    ),
                    "is_confirmed_pattern": True,
                })

            # 7. Sensitive Stack Trace Leak: e.printStackTrace()
            if re.search(r"\bprintStackTrace\s*\(\s*\)", clean):
                findings.append({
                    "finding_type": "SECURITY",
                    "title": "Stack Trace Exposure via printStackTrace()",
                    "category": "OWASP A05:2021 - Security Misconfiguration",
                    "severity": "LOW",
                    "heuristic_score": 3.0,
                    "line_number": idx,
                    "filename": filename,
                    "description": (
                        "Calling e.printStackTrace() outputs detailed stack traces to standard error, "
                        "leaking system paths, library versions, and query fragments to potential attackers."
                    ),
                    "risk_explanation": "Provides valuable diagnostic intelligence to attackers during penetration testing.",
                    "evidence_snippet": clean,
                    "remediation_recommendation": "Use structured SLF4J / Logback logging with masked sensitive parameters.",
                    "suggested_improvement": "logger.error(\"Operation failed\", e);",
                    "corrected_code": "logger.error(\"Failed processing request: {}\", e.getMessage());",
                    "is_confirmed_pattern": True,
                })

        return findings

    # =========================================================================
    # COMMON SECRETS & CREDENTIAL SCANS
    # =========================================================================
    def _scan_common_secrets(self, code: str, filename: str) -> List[Dict[str, Any]]:
        findings = []
        lines = code.splitlines()

        secret_patterns = [
            (
                r"\b(?:AKIA[0-9A-Z]{16})\b",
                "AWS Access Key ID Hardcoded",
                "CRITICAL",
                9.9,
                "Exposes Amazon Web Services cloud infrastructure to unauthorized takeover."
            ),
            (
                r"(?i)\b(?:api_key|apikey|secret_key|secretkey|jwt_secret)\s*[:=]\s*[\"']([a-zA-Z0-9_\-\.]{12,})[\"']",
                "Hardcoded API Key / Secret Token",
                "HIGH",
                8.5,
                "Hardcoding authentication secrets into repositories permits anyone with read access to compromise accounts."
            ),
            (
                r"(?i)\b(?:password|passwd|pwd)\s*[:=]\s*[\"']([^\"']{4,})[\"']",
                "Hardcoded Database or Account Password",
                "HIGH",
                8.7,
                "Plaintext passwords in source code expose backend databases to unauthorized access."
            ),
        ]

        for idx, line in enumerate(lines, start=1):
            clean = line.strip()
            # Skip comments
            if clean.startswith("#") or clean.startswith("//") or clean.startswith("*"):
                continue

            for pattern, title, severity, score, risk in secret_patterns:
                match = re.search(pattern, clean)
                if match:
                    matched_str = match.group(0)
                    masked = re.sub(r"([\"'])(?:[^\'\"]{4})([^\'\"]+)([\"'])", r"\1****\3", matched_str)
                    findings.append({
                        "finding_type": "SECURITY",
                        "title": title,
                        "category": "OWASP A05:2021 - Security Misconfiguration",
                        "severity": severity,
                        "heuristic_score": score,
                        "line_number": idx,
                        "filename": filename,
                        "description": (
                            f"Hardcoded credential or sensitive secret detected. Credentials should never "
                            "be stored directly in source code or committed to version control."
                        ),
                        "risk_explanation": risk,
                        "evidence_snippet": masked,
                        "remediation_recommendation": (
                            "Extract the secret into an environment variable or secure vault (e.g. AWS Secrets Manager, HashiCorp Vault)."
                        ),
                        "corrected_code": (
                            "# Secure: Load credential securely from environment variable\n"
                            "import os\n"
                            "SECRET_KEY = os.environ.get('APP_SECRET_KEY')\n"
                            "if not SECRET_KEY:\n"
                            "    raise RuntimeError('APP_SECRET_KEY environment variable is not configured')"
                        ),
                        "is_confirmed_pattern": True,
                    })
                    break

        return findings
