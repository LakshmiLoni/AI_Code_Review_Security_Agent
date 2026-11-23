"""Utils: UI Helpers for Streamlit Application.

Provides unified layout styling, custom CSS injection, application header rendering,
sidebar metadata, cross-page review state synchronization, and resilient table/dataframe rendering.
"""
import os
import streamlit as st
from typing import Optional, Dict, Any, List, Union
from database.review_repository import ReviewRepository
from config import Config

STYLE_CSS_PATH = os.path.join(Config.PROJECT_ROOT, "assets", "style.css")


def get_safe_dataframe(data: Union[List[Dict[str, Any]], Dict[str, Any]], columns: Optional[List[str]] = None):
    """Construct a pandas DataFrame from tabular data (list of dicts, records, or dictionary)."""
    import pandas as pd
    if not data:
        return pd.DataFrame(columns=columns or [])
    if columns and isinstance(data, list) and data and isinstance(data[0], (list, tuple)):
        return pd.DataFrame(data, columns=columns)
    return pd.DataFrame(data)


def display_table(data: Union[List[Dict[str, Any]], Dict[str, Any]], columns: Optional[List[str]] = None):
    """Display tabular data as a clean Streamlit dataframe with full container width."""
    df = get_safe_dataframe(data, columns=columns)
    st.dataframe(df, use_container_width=True)


def apply_custom_theme():
    """Inject custom CSS for cream/warm-white and sage green professional theme."""
    if os.path.exists(STYLE_CSS_PATH):
        try:
            with open(STYLE_CSS_PATH, "r", encoding="utf-8") as f:
                css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        except Exception:
            pass


def render_header(title: str, subtitle: str = ""):
    """Render professional application header."""
    apply_custom_theme()
    sub_html = f"<div class='app-subtitle'>{subtitle}</div>" if subtitle else ""
    st.markdown(
        f"""
        <div class="app-header">
            <div class="app-title">
                <span>🛡️</span>
                <span>{title}</span>
            </div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_info():
    """Render project metadata and active session state in the Streamlit sidebar."""
    with st.sidebar:
        st.markdown("### 🛡️ AI Code Review")
        st.caption("Static Analysis & Security Audit Platform")
        st.markdown("---")

        active_review = get_active_review()
        if active_review:
            st.markdown("**Active Review Session**")
            rev_id = active_review.get("review_id", "N/A")
            fname = active_review.get("filename", "N/A")
            lang = str(active_review.get("detected_language", "N/A")).capitalize()
            score = active_review.get("health_score", 100)
            status = active_review.get("pr_status", "APPROVED")

            st.text(f"ID: {rev_id[:16]}...")
            st.text(f"File: {fname} ({lang})")
            st.text(f"Score: {score}/100")
            render_status_badge(status)
        else:
            st.info("No active review. Submit code in 'New Code Review'.")

        st.markdown("---")
        st.markdown(
            """
            <div class="sidebar-note">
                <b>Core Engine:</b> Python 3.11, AST Parser, SQLite, ChromaDB, RAG, Gemini 2.5 Flash.<br/>
                <b>Architecture:</b> 5 Autonomous Analysis Agents.
            </div>
            """,
            unsafe_allow_html=True,
        )


def get_active_review() -> Optional[Dict[str, Any]]:
    """Retrieve active review from session state or fallback to latest from SQLite DB."""
    if "current_review" in st.session_state and st.session_state["current_review"]:
        return st.session_state["current_review"]

    repo = ReviewRepository()
    all_reviews = repo.get_all_reviews(limit=1)
    if all_reviews:
        full_rev = repo.get_review_by_id(all_reviews[0]["review_id"])
        st.session_state["current_review"] = full_rev
        return full_rev
    return None


def set_active_review(review_data: Dict[str, Any]):
    """Set active review in Streamlit session state."""
    st.session_state["current_review"] = review_data


def render_severity_badge(severity: str) -> str:
    """Return HTML for a clean severity badge."""
    sev = str(severity).upper()
    css_class = f"badge-{sev.lower()}"
    return f"<span class='badge {css_class}'>{sev}</span>"


def render_status_badge(status: str):
    """Display PR review verdict badge in Streamlit."""
    st_upper = str(status).upper()
    if "APPROV" in st_upper and "SUGGEST" not in st_upper:
        st.markdown("<span class='status-approved'>APPROVED</span>", unsafe_allow_html=True)
    elif "SUGGEST" in st_upper:
        st.markdown("<span class='status-suggestions'>APPROVED WITH SUGGESTIONS</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='status-changes'>CHANGES REQUESTED</span>", unsafe_allow_html=True)
