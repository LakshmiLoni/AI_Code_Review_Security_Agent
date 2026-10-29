"""Conversational Assistant routes."""

from flask import Blueprint, render_template, request, jsonify
from ..extensions import services

assistant_bp = Blueprint("assistant", __name__)


@assistant_bp.route("/")
def assistant_ui():
    """Render conversational assistant web interface."""
    recent_reviews = services.analysis_service.get_recent_reviews(limit=10)
    kb_stats = services.knowledge_service.get_stats()
    llm_configured = services.llm_service.is_configured()

    return render_template(
        "assistant.html",
        recent_reviews=recent_reviews,
        kb_stats=kb_stats,
        llm_configured=llm_configured
    )


@assistant_bp.route("/chat", methods=["POST"])
def assistant_chat():
    """Handle chat messages via JSON API with RAG context."""
    data = request.get_json() or {}
    question = data.get("question", "").strip()
    review_uuid = data.get("review_uuid", "").strip()

    if not question:
        return jsonify({"error": "Question cannot be empty."}), 400

    review_context = None
    if review_uuid:
        review_context = services.analysis_service.get_review(review_uuid)

    result = services.assistant_agent.answer_question(
        question=question,
        review_context=review_context
    )

    return jsonify(result)
