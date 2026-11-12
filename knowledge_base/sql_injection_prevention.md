# SQL Injection (SQLi) Prevention Standard

## 1. Description and Mechanism
SQL Injection occurs when untrusted user input is directly concatenated, interpolated, or formatted into a database SQL query string. The database interpreter cannot distinguish between the developer's SQL commands and data supplied by the attacker, allowing the attacker to alter the query logic, bypass authentication, exfiltrate confidential data, or execute operating system commands.

- **CWE Identifier**: CWE-89 (Improper Neutralization of Special Elements used in an SQL Command)
- **OWASP Category**: A03:2021 - Injection
- **Severity**: Critical (CVSS 9.0 - 10.0)

## 2. Vulnerable vs Secure Code Implementations

### Python SQLite / PostgreSQL Example
```python
# VULNERABLE: Direct string formatting into SQL query
def get_user_account(cursor, username: str):
    query = f"SELECT id, username, email FROM users WHERE username = '{username}'"
    cursor.execute(query) # Attacker submits: admin' --
    return cursor.fetchone()

# SECURE: Parameterized Query using bound parameter placeholder
def get_user_account_secure(cursor, username: str):
    query = "SELECT id, username, email FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    return cursor.fetchone()
```

### Java JDBC Example
```java
// VULNERABLE: Dynamic SQL string concatenation
public User authenticate(Connection conn, String user, String pass) throws SQLException {
    Statement stmt = conn.createStatement();
    String sql = "SELECT * FROM users WHERE username = '" + user + "' AND password = '" + pass + "'";
    ResultSet rs = stmt.executeQuery(sql); // Attacker passes: ' OR '1'='1
    return mapUser(rs);
}

// SECURE: Java PreparedStatement with parameter binding
public User authenticateSecure(Connection conn, String user, String pass) throws SQLException {
    String sql = "SELECT * FROM users WHERE username = ? AND password_hash = ?";
    try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
        pstmt.setString(1, user);
        pstmt.setString(2, hashPassword(pass));
        try (ResultSet rs = pstmt.executeQuery()) {
            return mapUser(rs);
        }
    }
}
```

## 3. Defense Techniques
1. **Parameterized Queries / Prepared Statements**: Completely decouples SQL code from data variables.
2. **Object-Relational Mapping (ORM)**: Use SQLAlchemy, Hibernate, or Spring Data JPA with bound entities.
3. **Stored Procedures with Parameters**: Parameterized stored procedures prevent structural query alteration.
4. **Principle of Least Privilege**: Ensure the database user account only has necessary permissions.
5. **Input Validation**: Enforce strict alphanumeric whitelisting on fields like identifiers and table names.
