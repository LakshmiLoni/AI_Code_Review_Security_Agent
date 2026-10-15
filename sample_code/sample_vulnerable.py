"""Deliberately insecure sample for demonstrating the Code Submission Module.

DO NOT use this code in a real application. It is only ever parsed, never run.
"""
import hashlib
import os
import sqlite3

DB_PASSWORD = "Sup3rS3cret!"            # hardcoded credential
API_KEY = "sk_live_51H8xExampleKey"     # hardcoded secret


def get_user(conn, username):
    query = "SELECT * FROM users WHERE name = '" + username + "'"   # SQL injection
    return conn.execute(query).fetchall()


def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()               # weak hash


def run_ping(host):
    os.system("ping -c 1 " + host)                                  # command injection


def calculate(expression):
    return eval(expression)                                         # arbitrary code execution


def add_item(item, items=[]):                                       # mutable default argument
    items.append(item)
    return items


if __name__ == "__main__":
    connection = sqlite3.connect(":memory:")
    print(add_item("example"))
