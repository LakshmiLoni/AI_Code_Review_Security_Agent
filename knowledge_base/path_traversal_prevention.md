# Path Traversal (Directory Traversal) Prevention

## 1. Description and Risks
Path Traversal vulnerabilities occur when user input is used to construct a file system path without proper sanitization. By supplying sequences like ../ or ..\\, an attacker can escape the intended directory and access sensitive files on the filesystem, such as /etc/passwd or application source code.

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
