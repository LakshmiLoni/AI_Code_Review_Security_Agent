# Java Enterprise Secure Coding Guidelines

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
