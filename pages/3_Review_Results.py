"""Streamlit Page 3: Review Results.

Displays the PR review summary, merge readiness assessment, executive summary,
and overall code health metrics.
"""
import streamlit as st
from utils.ui_helpers import render_header, render_sidebar_info, get_active_review, render_status_badge

st.set_page_config(
    page_title="Review Results | AI Code Review",
    page_icon="📋",
    layout="wide"
)

render_sidebar_info()
render_header("Review Results", "Executive summary and Pull Request merge assessment")

active = get_active_review()

if not active:
    st.warning("No active code review session found. Please submit code in 'New Code Review'.")
else:
    # 1. Overview Metadata
    col_meta1, col_meta2 = st.columns([2, 1])
    with col_meta1:
        st.markdown(f"**Target Artifact:** `{active.get('filename')}`  |  **Language:** {str(active.get('detected_language')).capitalize()}")
        st.caption(f"Review ID: `{active.get('review_id')}`")
    with col_meta2:
        render_status_badge(active.get("pr_status", "APPROVED"))

    st.markdown("---")

    # 2. Executive Summary
    st.markdown("##### Executive Summary")
    exec_summary = active.get("executive_summary") or "Analysis completed with no major issues detected."
    st.markdown(
        f"""
        <div class="content-card">
            {exec_summary}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Health & Severity Metrics
    st.markdown("##### Code Health & Finding Distribution")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Health Score", f"{active.get('health_score', 100)}/100", f"Grade {active.get('letter_grade', 'A')}")
    with c2:
        st.metric("Critical", active.get("critical_count", 0))
    with c3:
        st.metric("High", active.get("high_count", 0))
    with c4:
        st.metric("Medium", active.get("medium_count", 0))
    with c5:
        st.metric("Low", active.get("low_count", 0))

    st.markdown("---")

    # 4. PR Review Observations
    col_sec, col_qual = st.columns(2)
    with col_sec:
        st.markdown("##### 🔒 Security Observations")
        sec_obs = active.get("security_observations", [])
        if sec_obs:
            for obs in sec_obs:
                st.markdown(f"- {obs}")
        else:
            st.success("No security vulnerabilities flagged.")

    with col_qual:
        st.markdown("##### 🧹 Quality Observations")
        qual_obs = active.get("quality_observations", [])
        if qual_obs:
            for obs in qual_obs:
                st.markdown(f"- {obs}")
        else:
            st.success("No code quality smells flagged.")
