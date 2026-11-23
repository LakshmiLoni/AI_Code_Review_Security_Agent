"""Streamlit Page 5: Code Quality.

Displays static AST quality findings, maintainability smells, style violations,
and clean code refactoring recommendations.
"""
import streamlit as st
from utils.ui_helpers import render_header, render_sidebar_info, get_active_review, render_severity_badge

st.set_page_config(
    page_title="Code Quality | AI Code Review",
    page_icon="🧹",
    layout="wide"
)

render_sidebar_info()
render_header("Code Quality & Maintainability", "AST structural analysis, complexity, and code smells")

active = get_active_review()

if not active:
    st.warning("No active code review session found. Please submit code in 'New Code Review'.")
else:
    findings = active.get("findings", [])
    qual_findings = [f for f in findings if f.get("finding_type") == "QUALITY"]

    if not qual_findings:
        st.success("No code quality or maintainability smells detected in the active code review.")
    else:
        # Overview Cards
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Quality Smells", len(qual_findings))
        with c2:
            st.metric("High/Medium Smells", sum(1 for f in qual_findings if f.get("severity") in ["HIGH", "MEDIUM"]))
        with c3:
            st.metric("Style Violations", sum(1 for f in qual_findings if "Style" in f.get("category", "") or "PEP" in f.get("category", "")))

        st.markdown("---")
        st.markdown("##### Detected Quality Issues")

        for idx, f in enumerate(qual_findings, start=1):
            sev = str(f.get("severity", "LOW")).upper()
            line = f.get("line_number", 1)
            title = f.get("title", "Untitled Smell")
            cat = f.get("category", "General Quality")

            badge_html = render_severity_badge(sev)
            expander_title = f"#{idx} [{sev}] {title} (Line {line})"

            with st.expander(expander_title, expanded=(idx <= 3)):
                st.markdown(f"**Category:** `{cat}`  |  **Line:** `{line}`  |  **Severity:** {badge_html}", unsafe_allow_html=True)
                st.markdown(f"**Observation:** {f.get('description')}")
                st.markdown(f"**Maintainability Impact:** {f.get('risk_explanation')}")

                if f.get("evidence_snippet"):
                    st.markdown("**Evidence Snippet:**")
                    st.code(f.get("evidence_snippet"), language="text")

                st.markdown(f"**Suggested Refactoring:** {f.get('remediation_recommendation')}")
