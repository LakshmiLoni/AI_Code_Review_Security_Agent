
import sqlite3

def get_user(username):
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()

    # Vulnerability: SQL Injection
    query = "SELECT * FROM users WHERE username = '" + username + "'"

    cursor.execute(query)
    result = cursor.fetchall()

    conn.close()
    return result


def login(password):
    # Vulnerability: Hardcoded password
    admin_password = "admin123"

    if password == admin_password:
        print("Login successful")
    else:
        print("Invalid password")


username = input("Enter username: ")
password = input("Enter password: ")

print(get_user(username))
login(password)
