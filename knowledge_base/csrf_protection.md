# Cross-Site Request Forgery (CSRF) Protection

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
