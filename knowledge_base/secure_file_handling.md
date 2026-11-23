# Secure File Handling & Upload Protection

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
