"""Streamlit Page 6: Remediation.

Provides prioritized remediation roadmaps, secure coding guidelines, and
side-by-side original vs corrected code comparisons.
"""
import streamlit as st
from utils.ui_helpers import render_header, render_sidebar_info, get_active_review, render_severity_badge

st.set_page_config(
    page_title="Remediation | AI Code Review",
    page_icon="🔧",
    layout="wide"
)

render_sidebar_info()
render_header("Remediation & Fix Guidance", "Prioritized roadmap and side-by-side corrected code")

active = get_active_review()

if not active:
    st.warning("No active code review session found. Please submit code in 'New Code Review'.")
else:
    findings = active.get("findings", [])
    roadmap = active.get("roadmap", [])

    st.info("💡 **Safety Policy:** The system generates advisory patches and recommendations. It never silently modifies your original source files.")

    # 1. Prioritized Action Roadmap
    st.markdown("##### 1. Prioritized Remediation Roadmap")
    if roadmap:
        for step in roadmap:
            st.markdown(f"- **Step {step.get('step', '-')}:** {step.get('title')} `[{step.get('severity')}]` — *{step.get('action')}*")
    else:
        st.caption("No pending remediation steps recorded.")

    st.markdown("---")

    # 2. Side-by-side Corrected Code Examples
    st.markdown("##### 2. Corrected Code Examples & Safety Rationales")
    findings_with_fixes = [f for f in findings if f.get("corrected_code")]

    if not findings_with_fixes:
        st.success("No code corrections required.")
    else:
        for idx, f in enumerate(findings_with_fixes, start=1):
            sev = f.get("severity", "LOW")
            line = f.get("line_number", 1)
            title = f.get("title", "")

            with st.expander(f"Fix #{idx}: [{sev}] {title} (Line {line})", expanded=(idx == 1)):
                st.markdown(f"**Why this is unsafe:** {f.get('risk_explanation')}")
                st.markdown(f"**Why the suggested fix is secure:** {f.get('remediation_recommendation')}")

                col_orig, col_fix = st.columns(2)
                with col_orig:
                    st.markdown("**Original Flagged Pattern:**")
                    snippet = f.get("evidence_snippet") or "# [Flagged code pattern]"
                    st.code(snippet, language="text")

                with col_fix:
                    st.markdown("**Secure Corrected Example:**")
                    st.code(f.get("corrected_code"), language="python" if active.get("detected_language") == "python" else "java")
