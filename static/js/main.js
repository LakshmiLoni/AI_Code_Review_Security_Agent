/**
 * AI Code Review & Security Analysis Agent - Frontend JavaScript
 */

document.addEventListener("DOMContentLoaded", () => {
    // 1. Sample Code Insertion for Demonstration
    const samplePythonBtn = document.getElementById("load-sample-py");
    const sampleJavaBtn = document.getElementById("load-sample-java");
    const sampleCleanBtn = document.getElementById("load-sample-clean");
    const codeTextarea = document.getElementById("source-code-input");
    const filenameInput = document.getElementById("filename-input");
    const languageSelect = document.getElementById("language-select");

    const SAMPLES = {
        python_vuln: `# Vulnerable Python Web Handler Demonstration
import os
import sqlite3
import pickle
import hashlib
import random

DATABASE_URI = "sqlite:///users.db"
ADMIN_KEY = "YOUR_ADMIN_KEY"  # Hardcoded secret

def authenticate_user(username, raw_password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # SQL Injection via f-string string interpolation
    query = f"SELECT id, role FROM accounts WHERE user = '{username}'"
    cursor.execute(query)
    record = cursor.fetchone()
    # Weak MD5 hash for password verification
    hashed = hashlib.md5(raw_password.encode()).hexdigest()
    return record

def restore_user_session(cookie_payload):
    # Insecure deserialization via pickle
    session_data = pickle.loads(cookie_payload)
    return session_data

def run_network_diagnostic(target_host):
    # Command injection via os.system
    os.system("ping -c 1 " + target_host)

def generate_reset_token():
    # Insecure pseudo-random generator
    return str(random.randint(100000, 999999))
`,
        java_vuln: `// Vulnerable Enterprise Java Demonstration
package com.security.demo;

import java.sql.*;
import java.io.*;
import java.util.Random;
import java.security.MessageDigest;

public class UserAccountManager {
    public static final String DB_PASSWORD = "HardcodedSuperAdminPass2026!";

    public ResultSet searchUser(Connection conn, String userSearch) throws SQLException {
        Statement stmt = conn.createStatement();
        // SQL Injection via concatenation
        String sql = "SELECT * FROM users WHERE name = '" + userSearch + "'";
        return stmt.executeQuery(sql);
    }

    public void runTrace(String host) throws Exception {
        // Command injection via Runtime.exec
        Runtime.getRuntime().exec("traceroute " + host);
    }

    public Object readSession(byte[] bytes) throws Exception {
        // Unsafe Java deserialization
        ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(bytes));
        return ois.readObject();
    }
}
`,
        clean_code: `# Secure Python Architecture
import os
import sqlite3
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path

DB_PATH = Path(os.environ.get("DATABASE_PATH", "secure.db")).resolve()

def get_user_account_secure(username: str, cursor: sqlite3.Cursor):
    """Safely fetch user account using parameterized bind variables."""
    query = "SELECT id, password_hash, role FROM accounts WHERE username = ?"
    cursor.execute(query, (username,))
    return cursor.fetchone()

def create_secure_reset_token() -> str:
    """Generate a 256-bit cryptographically secure URL-safe token."""
    return secrets.token_urlsafe(32)

def hash_new_password(password: str) -> str:
    """Hash credential using memory-hard scrypt KDF."""
    return generate_password_hash(password, method="scrypt")
`
    };

    if (samplePythonBtn && codeTextarea) {
        samplePythonBtn.addEventListener("click", () => {
            codeTextarea.value = SAMPLES.python_vuln;
            if (filenameInput) filenameInput.value = "vulnerable_service.py";
            if (languageSelect) languageSelect.value = "python";
        });
    }

    if (sampleJavaBtn && codeTextarea) {
        sampleJavaBtn.addEventListener("click", () => {
            codeTextarea.value = SAMPLES.java_vuln;
            if (filenameInput) filenameInput.value = "UserAccountManager.java";
            if (languageSelect) languageSelect.value = "java";
        });
    }

    if (sampleCleanBtn && codeTextarea) {
        sampleCleanBtn.addEventListener("click", () => {
            codeTextarea.value = SAMPLES.clean_code;
            if (filenameInput) filenameInput.value = "secure_service.py";
            if (languageSelect) languageSelect.value = "python";
        });
    }

    // 2. Chat Assistant Integration
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const chatMessages = document.getElementById("chat-messages");
    const reviewSelector = document.getElementById("chat-review-select");

    if (chatForm && chatInput && chatMessages) {
        chatForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const question = chatInput.value.trim();
            if (!question) return;

            // Append User message bubble
            appendMessage(question, "user");
            chatInput.value = "";

            // Append Loading indicator
            const loadingId = "msg-loading-" + Date.now();
            appendLoading(loadingId);

            try {
                const reviewUuid = reviewSelector ? reviewSelector.value : "";
                const response = await fetch("/assistant/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ question, review_uuid: reviewUuid })
                });

                removeElement(loadingId);

                if (!response.ok) {
                    throw new Error("Assistant service returned an error.");
                }

                const data = await response.json();
                appendAssistantMessage(data.response, data.citations, data.mode);
            } catch (err) {
                removeElement(loadingId);
                appendMessage("Sorry, an error occurred while processing your query. Please try again.", "assistant");
            }
        });
    }

    function appendMessage(text, sender) {
        const div = document.createElement("div");
        div.className = `chat-bubble bubble-${sender}`;
        div.textContent = text;
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendLoading(id) {
        const div = document.createElement("div");
        div.id = id;
        div.className = "chat-bubble bubble-assistant";
        div.innerHTML = "<em>Analyzing knowledge base and formulating explanation...</em>";
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function removeElement(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function appendAssistantMessage(text, citations, mode) {
        const div = document.createElement("div");
        div.className = "chat-bubble bubble-assistant";

        // Convert basic markdown backticks and headings to HTML
        let formatted = escapeHtml(text)
            .replace(/### (.*?)\n/g, "<h4 style='margin: 0.5rem 0; color: #111827;'>$1</h4>")
            .replace(/#### (.*?)\n/g, "<h5 style='margin: 0.4rem 0; color: #4b5563;'>$1</h5>")
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/\*(.*?)\*/g, "<em>$1</em>")
            .replace(/```([a-z]*)\n([\s\S]*?)```/g, "<pre style='background:#f1f5f9; padding:0.5rem; border-radius:4px; font-size:0.85rem; overflow-x:auto;'><code>$2</code></pre>")
            .replace(/`([^`]+)`/g, "<code style='background:#f1f5f9; padding:2px 4px; border-radius:3px;'>$1</code>")
            .replace(/\n/g, "<br>");

        div.innerHTML = formatted;

        if (citations && citations.length > 0) {
            const citBox = document.createElement("div");
            citBox.className = "chat-citations";
            let citHtml = `<strong>References Used (${mode || 'Local RAG'}):</strong><ul>`;
            citations.forEach(c => {
                citHtml += `<li>${c.title} <span style="color:#6b7280;">(${c.filename})</span></li>`;
            });
            citHtml += "</ul>";
            citBox.innerHTML = citHtml;
            div.appendChild(citBox);
        }

        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function escapeHtml(str) {
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // 3. Quick Prompt Buttons
    const promptButtons = document.querySelectorAll(".quick-prompt-btn");
    promptButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            if (chatInput) {
                chatInput.value = btn.getAttribute("data-prompt");
                if (chatForm) chatForm.dispatchEvent(new Event("submit"));
            }
        });
    });
});
