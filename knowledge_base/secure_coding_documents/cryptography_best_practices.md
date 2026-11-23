# Cryptographic Best Practices & Key Management

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
