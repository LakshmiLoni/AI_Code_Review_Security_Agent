"""Streamlit Page 2: New Code Review.

Allows pasting source code, uploading .py or .java files, or loading predefined
sample test scenarios for instant multi-agent analysis.
"""
import os
import streamlit as st
from utils.ui_helpers import render_header, render_sidebar_info, set_active_review
from utils.file_handler import FileHandler
from utils.language_detector import detect_language, UnsupportedLanguageError
from services.review_service import ReviewService
from config import Config

st.set_page_config(
    page_title="New Code Review | AI Code Review",
    page_icon="🔍",
    layout="wide"
)

render_sidebar_info()
render_header("New Code Review", "Submit Python or Java source code for static analysis")

review_service = ReviewService()

# Predefined Sample Test Scenarios
SAMPLE_PROJECTS = {
    "-- Select a sample project to inspect --": None,
    "Python Basic (User Service - SQLi & Anti-Patterns)": "sample_projects/python_basic/user_service.py",
    "Python Basic (Safe Calculator - Clean Code)": "sample_projects/python_basic/safe_calculator.py",
    "Python Basic (Broken Syntax - Error Test)": "sample_projects/python_basic/broken_syntax.py",
    "Java Intermediate (Order Controller - SQLi, XSS, Leaks)": "sample_projects/java_intermediate/OrderController.java",
    "Java Intermediate (Secure Auth Service - Parameterized)": "sample_projects/java_intermediate/SecureAuthService.java",
    "Java Intermediate (Broken Delimiter - Syntax Test)": "sample_projects/java_intermediate/BrokenOrder.java",
    "Advanced Project (Payment Gateway - Deserialization, AWS Key, MD5)": "sample_projects/advanced_project/PaymentGateway.py",
    "Advanced Project (Secure Token Validator - HMAC-SHA256)": "sample_projects/advanced_project/SecureTokenValidator.py",
}

# Input mode selection
input_mode = st.radio(
    "Choose Input Method:",
    ["Paste Code Directly", "Upload Source File", "Load Sample Project"],
    horizontal=True
)

code_content = ""
source_filename = ""

if input_mode == "Paste Code Directly":
    code_content = st.text_area(
        "Paste Source Code:",
        height=320,
        placeholder="Paste your Python or Java source code here...",
        key="paste_code_area"
    )
    if code_content.strip():
        try:
            detected_lang, conf, reason = detect_language(code_content)
            st.caption(f"Detected Language: **{detected_lang.capitalize()}** ({conf*100:.0f}% confidence) — {reason}")
        except Exception:
            pass

elif input_mode == "Upload Source File":
    uploaded_file = st.file_uploader(
        "Upload Source File (.py or .java):",
        type=["py", "java"],
        help="Maximum file size: 5 MB"
    )
    if uploaded_file is not None:
        code_content, source_filename = FileHandler.read_uploaded_file(uploaded_file)
        st.caption(f"Loaded: `{source_filename}` ({len(code_content.splitlines())} lines)")
        st.code(code_content[:1500] + ("\n... [truncated for display]" if len(code_content) > 1500 else ""), language="python" if source_filename.endswith(".py") else "java")

elif input_mode == "Load Sample Project":
    selected_sample = st.selectbox("Select Test Scenario:", list(SAMPLE_PROJECTS.keys()))
    if selected_sample and SAMPLE_PROJECTS[selected_sample]:
        rel_path = SAMPLE_PROJECTS[selected_sample]
        abs_path = os.path.join(Config.PROJECT_ROOT, rel_path)
        if os.path.exists(abs_path):
            with open(abs_path, "r", encoding="utf-8") as f:
                code_content = f.read()
            source_filename = os.path.basename(abs_path)
            st.caption(f"Loaded Sample: `{source_filename}` from `{rel_path}`")
            st.code(code_content, language="python" if source_filename.endswith(".py") else "java")
        else:
            st.error(f"Sample file not found at: {abs_path}")

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# Run Analysis Button
if st.button("🚀 Run Multi-Agent Review", type="primary", use_container_width=True):
    clean_code = (code_content or "").strip()
    if not clean_code:
        st.error("Source code is empty. Please paste code, upload a file, or select a sample project.")
    else:
        with st.spinner("Executing parallel multi-agent analysis (AST & OWASP Rules)..."):
            review_result = review_service.submit_and_review(
                code=clean_code,
                filename=source_filename or None
            )

        if not review_result.get("success"):
            st.error(f"Analysis Failed: {review_result.get('error', 'Unknown validation or parsing error')}")
            if review_result.get("line_number"):
                st.warning(f"Error occurred at line {review_result['line_number']}.")
        else:
            set_active_review(review_result)
            st.success(f"Review completed successfully! Review ID: `{review_result['review_id']}`")

            # Quick Results Card
            st.markdown("---")
            st.markdown("#### Review Summary")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Health Score", f"{review_result['health_score']}/100", f"Grade {review_result['letter_grade']}")
            with c2:
                st.metric("PR Status", review_result["pr_status"])
            with c3:
                st.metric("Critical Findings", review_result["critical_count"])
            with c4:
                st.metric("Total Findings", review_result["total_findings"])

            st.info("Navigate through the sidebar pages (Results, Findings, Quality, Remediation, AI Assistant, Reports) to explore detailed agent findings.")
