"""AI Code Review & Security Analysis Agent.

Primary Streamlit Application Entry Point.
Static Code Review & Vulnerability Analysis Platform.

Execution command:
    python -m streamlit run app.py
"""
import sys
import os

# If launched directly with `python app.py`, seamlessly delegate to Streamlit CLI
try:
    from streamlit.runtime import exists as _st_runtime_exists
    _in_streamlit = _st_runtime_exists()
except ImportError:
    _in_streamlit = False

if not _in_streamlit and __name__ == "__main__":
    import subprocess
    print("Launching Streamlit application...")
    cmd = [sys.executable, "-m", "streamlit", "run", os.path.abspath(__file__)]
    subprocess.run(cmd)
    sys.exit(0)

# =============================================================================
# STREAMLIT APPLICATION INTERFACE
# =============================================================================
import streamlit as st
from config import Config
from utils.ui_helpers import render_header, render_sidebar_info, get_active_review
from database.review_repository import ReviewRepository

# Page Configuration
st.set_page_config(
    page_title="AI Code Review & Security Analysis Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize runtime directories and database
Config.init_app()
repo = ReviewRepository()

# Sidebar
render_sidebar_info()

# Header
render_header(
    "AI Code Review & Security Analysis Agent",
    "Static Code Review & Vulnerability Analysis Platform"
)

# Overview Container
st.markdown(
    """
    <div class="content-card">
        <h4>System Overview</h4>
        <p style="color: #4a5568; line-height: 1.6;">
            An autonomous multi-agent platform designed for automated static code review,
            code quality smell detection, OWASP-aligned security vulnerability analysis,
            prioritized remediation roadmap generation, and RAG-grounded conversational assistance
            for <b>Python</b> and <b>Java</b> source code.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# System Architecture & Agent Workflow Grid
st.markdown("##### The Five Autonomous Agents")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        """
        <div class="metric-box health">
            <div class="metric-title">Agent 1: Code Analysis</div>
            <div style="font-size: 0.88rem; color: #4a5568; margin-top: 6px;">
                AST traversal, code smells, function length, PEP 8 / Java naming,
                mutable default arguments, bare except handlers, and complexity checks.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        """
        <div class="metric-box critical">
            <div class="metric-title">Agent 2: Security Agent</div>
            <div style="font-size: 0.88rem; color: #4a5568; margin-top: 6px;">
                OWASP Top 10 vulnerability scanning: SQL Injection, Command Injection,
                XSS, Path Traversal, Hardcoded Secrets, Deserialization, and Weak Cryptography.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        """
        <div class="metric-box high">
            <div class="metric-title">Agent 3: Remediation Agent</div>
            <div style="font-size: 0.88rem; color: #4a5568; margin-top: 6px;">
                Generates prioritized remediation roadmaps, explains safety rationales,
                and produces side-by-side secure code examples without modifying source files.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
c4, c5, c6 = st.columns(3)
with c4:
    st.markdown(
        """
        <div class="metric-box medium">
            <div class="metric-title">Agent 4: PR Summary Agent</div>
            <div style="font-size: 0.88rem; color: #4a5568; margin-top: 6px;">
                Produces GitHub-style pull request merge readiness verdicts (Approved,
                Approved with Suggestions, Changes Requested) and computes Code Health Scores.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c5:
    st.markdown(
        """
        <div class="metric-box low">
            <div class="metric-title">Agent 5: Conversational Assistant</div>
            <div style="font-size: 0.88rem; color: #4a5568; margin-top: 6px;">
                RAG-grounded conversational agent powered by 20 secure coding guidelines,
                Gemini 2.5 Flash, and an offline local vector retrieval fallback.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c6:
    st.markdown(
        """
        <div class="metric-box health">
            <div class="metric-title">Reports & Privacy</div>
            <div style="font-size: 0.88rem; color: #4a5568; margin-top: 6px;">
                Export formal A4 PDF and JSON reports. Zero-code leakage guarantee:
                reports strictly exclude raw submitted source code and secrets.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# Quick Navigation Section
st.markdown("##### Application Navigation")
st.markdown("Use the sidebar on the left or the quick links below to navigate:")

nav_col1, nav_col2, nav_col3 = st.columns(3)
with nav_col1:
    st.markdown(
        """
        - **1. Dashboard:** Visual overview of all analyzed reviews and severity statistics.
        - **2. New Code Review:** Paste code, upload files, or load sample projects for analysis.
        - **3. Review Results:** PR summary, merge verdict, and health score assessment.
        """
    )
with nav_col2:
    st.markdown(
        """
        - **4. Security Findings:** Detailed OWASP vulnerability detections and line evidence.
        - **5. Code Quality:** AST code smell detections and maintainability insights.
        - **6. Remediation:** Step-by-step fix roadmaps and side-by-side corrected code diffs.
        """
    )
with nav_col3:
    st.markdown(
        """
        - **7. AI Assistant:** Interactive RAG code assistant with secure guideline citations.
        - **8. Review History:** Searchable database table of all historical review sessions.
        - **9. Reports:** Download formal A4 PDF reports and structured JSON audit files.
        """
    )

st.markdown("---")

# Current Status Card
active = get_active_review()
if active:
    st.success(
        f"Active Session Loaded: `{active.get('filename')}` ({str(active.get('detected_language')).capitalize()}) — "
        f"Health Score: {active.get('health_score')}/100 | PR Status: {active.get('pr_status')}."
    )
else:
    st.info("💡 To start your first review, navigate to **2. New Code Review** in the sidebar.")
