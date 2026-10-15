# Secure Java Coding Practices

## Definition
Secure Java coding applies the guidance in Oracle's *Secure Coding Guidelines for Java SE* and OWASP's Java cheat sheets. Java's type safety removes some bug classes (buffer overflows), but injection, unsafe deserialization, weak crypto and information leaks still occur.

## 1. Validate input and prevent injection
Validate all external input (length, type, range, allow-list). Use `PreparedStatement` for SQL (see `sql_injection.md`) and encode output for HTML (see `xss_prevention.md`). Never build OS commands from user input:
```java
Runtime.getRuntime().exec("ping " + host);                       // VULNERABLE
new ProcessBuilder("ping", "-c", "1", host).start();              // better: separate arguments + validated host
```

## 2. Avoid unsafe deserialization
Deserialising untrusted data with `ObjectInputStream` can lead to remote code execution through "gadget chains".
```java
ObjectInputStream in = new ObjectInputStream(socket.getInputStream());
Object obj = in.readObject();                                    // VULNERABLE
```
Prefer data-only formats (JSON with a strict schema). If Java serialization is unavoidable, apply a **deserialization filter** (`ObjectInputFilter`) with an allow-list of classes.

## 3. Use strong cryptography correctly
- Use `java.security.SecureRandom` for tokens and keys, not `java.util.Random`.
- Use AES-GCM for encryption; avoid DES, 3DES, RC4, ECB mode and MD5/SHA-1 for security purposes.
- Hash passwords with BCrypt/Argon2/PBKDF2 (`PBKDF2WithHmacSHA256`) with a unique salt.
- Never hardcode keys or passwords (see `secrets_management.md`).
```java
SecureRandom rnd = new SecureRandom();
byte[] token = new byte[32];
rnd.nextBytes(token);
```

## 4. Handle exceptions and resources safely
- Do not swallow exceptions (`catch (Exception e) {}`) and do not leak stack traces or internal paths to users; log details server-side.
- Use **try-with-resources** so streams, connections and statements are always closed.
- Do not log passwords, tokens or personal data.

## 5. Limit access and mutability
Make fields `private` and classes `final` where inheritance is not intended; prefer immutable objects; avoid public mutable static fields; defensively copy mutable arguments and return values.

## 6. Protect against path traversal and XXE
Normalise and verify file paths stay inside an allowed base directory (`Path.normalize()`, `startsWith(base)`). Disable external entities and DTDs in XML parsers (`XMLConstants.FEATURE_SECURE_PROCESSING`, `disallow-doctype-decl`).

## 7. Keep dependencies and the JDK updated
Use dependency scanners (OWASP Dependency-Check), prefer supported JDK releases with security updates, and avoid known-vulnerable libraries.

## 8. Web-layer reminders (Spring/Servlet)
Keep CSRF protection enabled, set secure cookie flags, enforce authorisation with `@PreAuthorize`/filters, and send security headers.

## Sources
- https://www.oracle.com/java/technologies/javase/seccodeguide.html
- https://docs.oracle.com/javase/tutorial/jdbc/basics/prepared.html
- https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/security/SecureRandom.html
- https://docs.oracle.com/en/java/javase/17/core/serialization-filtering1.html
- https://cheatsheetseries.owasp.org/cheatsheets/Java_Security_Cheat_Sheet.html
- https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html
