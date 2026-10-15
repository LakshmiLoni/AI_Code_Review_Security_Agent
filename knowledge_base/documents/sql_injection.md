# SQL Injection (SQLi)

## Definition
SQL injection happens when untrusted input is concatenated into a SQL statement so that the database interprets part of the input as SQL code instead of data. It belongs to OWASP A05:2025 Injection (A03:2021) and is catalogued as CWE-89.

## Risk
An attacker can read data they should not see, bypass logins, modify or delete records, and in some configurations execute commands on the database server. A single vulnerable query can expose the whole database.

## Vulnerable example (Python)
```python
def get_user(conn, username):
    query = "SELECT * FROM users WHERE name = '" + username + "'"   # VULNERABLE
    return conn.execute(query).fetchall()
# username = "x' OR '1'='1" returns every user.
```

## Vulnerable example (Java)
```java
String sql = "SELECT * FROM users WHERE name = '" + username + "'";   // VULNERABLE
Statement st = connection.createStatement();
ResultSet rs = st.executeQuery(sql);
```

## Recommended prevention
1. **Parameterised queries / prepared statements** - the primary defence. The query structure is sent separately from the data, so input can never change the SQL logic.
2. Use an ORM or query builder carefully; avoid raw string interpolation even inside an ORM.
3. For parts that cannot be parameterised (table or column names, `ORDER BY` direction), validate against an allow-list.
4. Give the database account the least privilege it needs (no admin rights, no `DROP`).
5. Validate input type and length as defence in depth - validation alone is not enough.

## Secure example (Python, sqlite3 DB-API)
```python
def get_user(conn, username):
    return conn.execute("SELECT * FROM users WHERE name = ?", (username,)).fetchall()
```

## Secure example (Java, JDBC)
```java
String sql = "SELECT * FROM users WHERE name = ?";
try (PreparedStatement ps = connection.prepareStatement(sql)) {
    ps.setString(1, username);
    try (ResultSet rs = ps.executeQuery()) { /* read rows */ }
}
```

## What a reviewer looks for
`execute(` / `executeQuery(` called with `+`, f-strings, `%` formatting, `.format()` or `String.format` building the SQL.

## Sources
- https://owasp.org/www-community/attacks/SQL_Injection
- https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
- https://cheatsheetseries.owasp.org/cheatsheets/Query_Parameterization_Cheat_Sheet.html
- https://docs.python.org/3/library/sqlite3.html
- https://docs.oracle.com/javase/tutorial/jdbc/basics/prepared.html
- https://cwe.mitre.org/data/definitions/89.html
