"""Advanced Project: Secure Token Validator.

Demonstrates secure, production-grade security engineering practices:
1. HMAC-SHA256 constant-time signature verification
2. Cryptographically secure random tokens (secrets module)
3. Canonical path containment verification
"""
import os
import hmac
import hashlib
import secrets


def generate_secure_session_token(token_byte_length: int = 32) -> str:
    """Generate cryptographically strong session token."""
    return secrets.token_hex(token_byte_length)


def verify_hmac_signature(key: bytes, message: bytes, expected_signature: bytes) -> bool:
    """Verify HMAC signature using constant-time comparison to prevent timing attacks."""
    computed_signature = hmac.new(key, message, hashlib.sha256).digest()
    return hmac.compare_digest(computed_signature, expected_signature)


def read_safe_file_within_boundary(base_directory: str, relative_path: str) -> str:
    """Read file only if canonical path is strictly contained within base directory."""
    base_canonical = os.path.realpath(base_directory)
    target_canonical = os.path.realpath(os.path.join(base_directory, relative_path))

    # Path traversal guard
    if not (target_canonical == base_canonical or target_canonical.startswith(base_canonical + os.sep)):
        raise PermissionError("Access denied: Target path resolves outside the permitted directory.")

    with open(target_canonical, "r", encoding="utf-8") as f:
        return f.read()
