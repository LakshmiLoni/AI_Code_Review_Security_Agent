"""Streamlit Page 8: Review History.

Displays historical review sessions persisted in SQLite, enabling selection,
inspection, and reloading of past audits.
"""
import streamlit as st
from utils.ui_helpers import (
    render_header, 
    render_sidebar_info, 
    set_active_review,
    display_table
)
from database.review_repository import ReviewRepository

st.set_page_config(
    page_title="Review History | AI Code Review",
    page_icon="📜",
    layout="wide"
)

render_sidebar_info()
render_header("Review History", "Archived code reviews and past session audit logs")

repo = ReviewRepository()
all_reviews = repo.get_all_reviews(limit=100)

if not all_reviews:
    st.info("No reviews stored in database yet. Navigate to 'New Code Review' to submit code.")
else:
    # Search / Filter
    search_q = st.text_input("Search Reviews by Filename or Review ID:", placeholder="e.g. user_service or REV-...")

    filtered = all_reviews
    if search_q.strip():
        q = search_q.strip().lower()
        filtered = [r for r in filtered if q in r["filename"].lower() or q in r["review_id"].lower()]

    st.caption(f"Showing **{len(filtered)}** reviews.")

    # Table view using resilient display_table helper
    table_data = []
    for r in filtered:
        table_data.append({
            "Review ID": r["review_id"],
            "Target File": r["filename"],
            "Language": str(r["detected_language"]).capitalize(),
            "Score": f"{r['health_score']}/100",
            "Grade": r["letter_grade"],
            "PR Verdict": r["pr_status"],
            "Date": r.get("timestamp", "N/A"),
        })

    display_table(table_data)

    st.markdown("---")
    st.markdown("##### Select Review to Activate")

    review_options = {f"{r['filename']} ({r['review_id'][:14]}...) - {r['pr_status']}": r['review_id'] for r in filtered}
    selected_label = st.selectbox("Choose a past review to inspect:", list(review_options.keys()))

    if st.button("Load Selected Review into Active Session", type="primary"):
        chosen_id = review_options[selected_label]
        full_data = repo.get_review_by_id(chosen_id)
        if full_data:
            set_active_review(full_data)
            st.success(f"Review `{chosen_id}` is now active! You can view its findings, quality, and reports in other tabs.")
            st.rerun()
