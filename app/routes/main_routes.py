"""Main navigation and dashboard routes."""

from flask import Blueprint, render_template, jsonify
from ..extensions import services

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Home / Landing page."""
    kb_stats = services.knowledge_service.get_stats()
    db_metrics = services.analysis_service.get_dashboard_summary()
    return render_template("index.html", kb_stats=kb_stats, db_metrics=db_metrics)


@main_bp.route("/dashboard")
def dashboard():
    """Comprehensive metrics dashboard."""
    kb_stats = services.knowledge_service.get_stats()
    metrics = services.analysis_service.get_dashboard_summary()
    recent_reviews = services.analysis_service.get_recent_reviews(limit=10)
    llm_configured = services.llm_service.is_configured()

    return render_template(
        "dashboard.html",
        kb_stats=kb_stats,
        metrics=metrics,
        recent_reviews=recent_reviews,
        llm_configured=llm_configured
    )


@main_bp.route("/about")
def about():
    """Project architecture and overview page."""
    kb_stats = services.knowledge_service.get_stats()
    return render_template("about.html", kb_stats=kb_stats)


@main_bp.route("/api/kb/stats")
def api_kb_stats():
    """JSON API returning knowledge base metrics and line counts."""
    return jsonify(services.knowledge_service.get_stats())
