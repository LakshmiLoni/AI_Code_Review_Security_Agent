"""Basic Python Project: User Management Service.

Demonstrates common Python security vulnerabilities and code quality smells:
1. SQL Injection (OWASP A03)
2. Command Injection (OWASP A03)
3. Mutable default argument anti-pattern
4. Bare except: error handling smell
5. PEP 8 function naming violation
"""
import os
import sqlite3


def GetUserRecords(db_path, username, filters=[]):  # Quality: Naming + Mutable default
    """Retrieve user record from SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # VULNERABILITY: SQL Injection via f-string dynamic formatting
    query = f"SELECT id, username, email FROM users WHERE username = '{username}'"
    cursor.execute(query)
    record = cursor.fetchone()
    conn.close()
    return record


def ping_user_host(host_address):
    """Check connectivity to client host."""
    # VULNERABILITY: OS Command Injection via os.system
    status = os.system("ping -c 1 " + host_address)
    return status == 0


def process_user_data(data_payload):
    """Parse user payload with unsafe exception handling."""
    try:
        val = int(data_payload)
        return val * 2
    except:  # Quality: Bare except catches all BaseExceptions
        return None
