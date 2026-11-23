"""Streamlit Page 1: Dashboard.

Displays authentic review statistics, language distributions, and recent audit activity
calculated directly from the SQLite database.
"""
import streamlit as st
from utils.ui_helpers import (
    render_header, 
    render_sidebar_info, 
    display_table,
    get_safe_dataframe
)
from services.history_service import HistoryService

st.set_page_config(
    page_title="Dashboard | AI Code Review",
    page_icon="📊",
    layout="wide"
)

render_sidebar_info()
render_header("Security & Quality Dashboard", "Review metrics and historical analysis trends")

service = HistoryService()
metrics = service.get_dashboard_metrics()

total_reviews = metrics.get("total_reviews", 0)

if total_reviews == 0:
    st.info("No reviews recorded yet. Navigate to 'New Code Review' to submit Python or Java source code.")
else:
    # 1. Summary Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
            <div class="metric-box health">
                <div class="metric-title">Total Reviews</div>
                <div class="metric-value">{metrics['total_reviews']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="metric-box health">
                <div class="metric-title">Avg Health Score</div>
                <div class="metric-value">{metrics['avg_health_score']}<span style="font-size: 0.9rem; color:#718096;">/100</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
            <div class="metric-box critical">
                <div class="metric-title">Critical Findings</div>
                <div class="metric-value">{metrics['critical_count']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""
            <div class="metric-box high">
                <div class="metric-title">Total Findings</div>
                <div class="metric-value">{metrics['total_findings']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 2. Charts / Distributions (Native Streamlit chart dicts - 100% resilient)
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("##### Findings by Severity")
        sev_dict = {
            "Critical": metrics["critical_count"],
            "High": metrics["high_count"],
            "Medium": metrics["medium_count"],
            "Low": metrics["low_count"],
        }
        st.bar_chart(sev_dict, color="#5F8670")

    with col_right:
        st.markdown("##### Analyzed Languages")
        lang_data = metrics.get("languages", {})
        if lang_data:
            st.bar_chart(lang_data, color="#0D9488")
        else:
            st.caption("No language statistics available.")

    st.markdown("---")

    # 3. Recent Review Sessions
    st.markdown("##### Recent Review Sessions")
    recent = metrics.get("recent_reviews", [])
    if recent:
        table_rows = []
        for r in recent:
            table_rows.append({
                "Review ID": r["review_id"][:16] + "...",
                "Filename": r["filename"],
                "Language": str(r["detected_language"]).capitalize(),
                "Health Score": f"{r['health_score']}/100 ({r['letter_grade']})",
                "PR Status": r["pr_status"],
                "Timestamp": r.get("timestamp", "N/A"),
            })
        display_table(table_rows)
    else:
        st.caption("No recent sessions found.")
