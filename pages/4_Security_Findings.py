"""Streamlit Page 4: Security Findings.

Displays OWASP-aligned security vulnerability findings with line numbers,
severity ratings, risk explanations, and targeted remediations.
"""
import streamlit as st
from utils.ui_helpers import render_header, render_sidebar_info, get_active_review, render_severity_badge

st.set_page_config(
    page_title="Security Findings | AI Code Review",
    page_icon="🛡️",
    layout="wide"
)

render_sidebar_info()
render_header("Security Findings", "Static OWASP vulnerability detections and risk explanations")

active = get_active_review()

if not active:
    st.warning("No active code review session found. Please submit code in 'New Code Review'.")
else:
    findings = active.get("findings", [])
    sec_findings = [f for f in findings if f.get("finding_type") == "SECURITY"]

    if not sec_findings:
        st.success("No security vulnerabilities were identified in the active code review.")
    else:
        # Filters
        c_filter1, c_filter2 = st.columns([1, 2])
        with c_filter1:
            sev_filter = st.selectbox(
                "Filter by Severity:",
                ["All Severities", "CRITICAL", "HIGH", "MEDIUM", "LOW"]
            )
        with c_filter2:
            categories = sorted(list({f.get("category", "General") for f in sec_findings}))
            cat_filter = st.selectbox("Filter by OWASP Category:", ["All Categories"] + categories)

        # Filter logic
        filtered = sec_findings
        if sev_filter != "All Severities":
            filtered = [f for f in filtered if str(f.get("severity", "")).upper() == sev_filter]
        if cat_filter != "All Categories":
            filtered = [f for f in filtered if f.get("category") == cat_filter]

        st.caption(f"Showing **{len(filtered)}** security findings matching filters.")

        for idx, f in enumerate(filtered, start=1):
            sev = str(f.get("severity", "LOW")).upper()
            line = f.get("line_number", 1)
            title = f.get("title", "Untitled")
            cat = f.get("category", "General")

            badge_html = render_severity_badge(sev)
            expander_title = f"#{idx} [{sev}] {title} (Line {line})"

            with st.expander(expander_title, expanded=(sev in ["CRITICAL", "HIGH"])):
                st.markdown(f"**Category:** `{cat}`  |  **Line:** `{line}`  |  **Severity:** {badge_html}", unsafe_allow_html=True)
                st.markdown(f"**Description:** {f.get('description')}")
                st.markdown(f"**Potential Impact / Risk:** {f.get('risk_explanation')}")

                if f.get("evidence_snippet"):
                    st.markdown("**Evidence Snippet:**")
                    st.code(f.get("evidence_snippet"), language="text")

                st.markdown(f"**Remediation Recommendation:** {f.get('remediation_recommendation')}")
