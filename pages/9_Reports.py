"""Streamlit Page 9: Reports.

Dedicated report generation and download portal for PDF and JSON technical audit reports.
Supports newly completed reviews and previously saved historical reviews.
Strictly excludes submitted source code, corrected code snippets, and raw secrets.
"""
import os
import streamlit as st
from utils.ui_helpers import (
    render_header, 
    render_sidebar_info, 
    get_active_review, 
    set_active_review,
    display_table
)
from database.review_repository import ReviewRepository
from reports.pdf_generator import PDFReportGenerator
from reports.json_generator import JSONReportGenerator
from reports.recommendation_formatter import RecommendationFormatter

st.set_page_config(
    page_title="Reports | AI Code Review",
    page_icon="📑",
    layout="wide"
)

render_sidebar_info()
render_header("Report Generation Portal", "Export formal PDF and JSON technical review reports")

repo = ReviewRepository()
pdf_gen = PDFReportGenerator()
json_gen = JSONReportGenerator()

all_reviews = repo.get_all_reviews(limit=100)

if not all_reviews:
    st.info("No reviews available to generate reports. Please submit code in 'New Code Review'.")
else:
    # 1. Review Selector
    review_map = {
        f"{r['filename']} ({r['review_id'][:14]}...) — {r['pr_status']} [{r.get('timestamp', '')[:10]}]": r["review_id"]
        for r in all_reviews
    }

    # Default to current active review if present
    active = get_active_review()
    default_idx = 0
    if active:
        target_id = active.get("review_id")
        for idx, (label, rid) in enumerate(review_map.items()):
            if rid == target_id:
                default_idx = idx
                break

    selected_label = st.selectbox("Select Review to Generate Reports For:", list(review_map.keys()), index=default_idx)
    selected_review_id = review_map[selected_label]

    # Fetch complete review record including findings
    review_data = repo.get_review_by_id(selected_review_id)

    if not review_data:
        st.error("Selected review record could not be loaded.")
    else:
        # Sync with active review state
        set_active_review(review_data)

        st.markdown(
            f"""
            <div class="content-card">
                <b>Target File:</b> <code>{review_data.get('filename')}</code> &nbsp;|&nbsp; 
                <b>Language:</b> {str(review_data.get('detected_language')).capitalize()} &nbsp;|&nbsp; 
                <b>Health Score:</b> {review_data.get('health_score')}/100 &nbsp;|&nbsp; 
                <b>Status:</b> <b>{review_data.get('pr_status')}</b> &nbsp;|&nbsp; 
                <b>Findings:</b> {review_data.get('total_findings', 0)} ({review_data.get('critical_count', 0)} Critical, {review_data.get('high_count', 0)} High)
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.info(
            "🔒 **Privacy & Data Security Policy:** "
            "Exported PDF and JSON reports contain analytical findings, severity classifications, "
            "impact explanations, and recommendations. Raw submitted source code, corrected code snippets, "
            "and sensitive secrets are strictly excluded."
        )

        # 2. Recommendations Table Preview using resilient display_table
        st.markdown("##### Recommendations for Improvement (Report Table Preview)")
        findings = review_data.get("findings", [])
        rec_table = RecommendationFormatter.format_recommendations_table(findings)

        if rec_table:
            display_table(rec_table)
        else:
            st.caption("No recommendations required for this review.")

        st.markdown("---")

        # 3. Download Controls
        st.markdown("##### Download Generated Reports")
        col_pdf, col_json = st.columns(2)

        # Generate fresh files on demand
        pdf_path = pdf_gen.generate(review_data)
        json_path = json_gen.generate(review_data)

        with col_pdf:
            st.markdown("###### 📄 Formal A4 PDF Technical Report")
            st.caption("Formal technical compliance and code quality audit report.")
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as pf:
                    pdf_bytes = pf.read()
                st.download_button(
                    label="⬇️ Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"{review_data.get('review_id')}.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True,
                )
            else:
                st.error("PDF generation failed.")

        with col_json:
            st.markdown("###### 📦 Structured JSON Audit Report")
            st.caption("Machine-readable finding classifications, metrics, and metadata.")
            if os.path.exists(json_path):
                with open(json_path, "rb") as jf:
                    json_bytes = jf.read()
                st.download_button(
                    label="⬇️ Download JSON Report",
                    data=json_bytes,
                    file_name=f"{review_data.get('review_id')}.json",
                    mime="application/json",
                    use_container_width=True,
                )
            else:
                st.error("JSON generation failed.")
