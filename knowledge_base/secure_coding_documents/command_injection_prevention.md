# Command Injection Prevention & Safe Process Execution

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
