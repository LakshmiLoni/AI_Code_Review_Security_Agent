"""Main Flask Application Entry Point.

AI Code Review & Security Analysis Agent Developer Portal.
Implements web routes, REST APIs, report downloads, and multi-agent orchestration.
"""
import os
import sys
import json
import logging
from flask import (
    Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, abort
)

# Ensure project root is in path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import Config
from orchestrator.agent_orchestrator import AgentOrchestrator
from database.db import init_db, get_db_session
from database.models import CodeReview, ReviewFinding, ChatMessage
from utils.language_detector import detect_language, UnsupportedLanguageError
from modules.findings_manager import FindingsManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    """Application factory for Flask."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    Config.init_app(app)

    # Enable CORS
    try:
        from flask_cors import CORS
        CORS(app)
    except ImportError:
        @app.after_request
        def add_cors_headers(response):
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
            response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
            return response

    # Initialize SQLite database
    init_db()

    orchestrator = AgentOrchestrator()

    # -------------------------------------------------------------------------
    # WEB ROUTES
    # -------------------------------------------------------------------------
    @app.route("/")
    def index():
        """Landing Page."""
        return render_template("index.html")

    @app.route("/dashboard")
    def dashboard():
        """Analytics Dashboard."""
        session = get_db_session()
        try:
            reviews = session.query(CodeReview).order_by(CodeReview.id.desc()).all()
            total_reviews = len(reviews)
            total_critical = sum(r.critical_count for r in reviews)
            total_high = sum(r.high_count for r in reviews)
            total_medium = sum(r.medium_count for r in reviews)
            total_low = sum(r.low_count for r in reviews)
            total_vulnerabilities = total_critical + total_high + total_medium + total_low

            avg_health = 100.0
            if total_reviews > 0:
                avg_health = round(sum(r.health_score for r in reviews) / total_reviews, 1)

            recent_reviews = [r.to_dict() for r in reviews[:8]]

            return render_template(
                "dashboard.html",
                total_reviews=total_reviews,
                total_critical=total_critical,
                total_high=total_high,
                total_medium=total_medium,
                total_low=total_low,
                total_vulnerabilities=total_vulnerabilities,
                avg_health_score=avg_health,
                recent_reviews=recent_reviews,
            )
        finally:
            session.close()

    @app.route("/submit", methods=["GET", "POST"])
    def submit():
        """Code Submission Page."""
        if request.method == "GET":
            return render_template("submission.html")

        submission_type = request.form.get("submission_type", "paste")

        if submission_type == "upload":
            file = request.files.get("code_file")
            if not file or not file.filename:
                flash("Please choose a valid .py or .java file to upload.", "error")
                return redirect(url_for("submit"))

            sub_handler = orchestrator.submission_handler
            prep_res = sub_handler.handle_uploaded_file(file)
            if not prep_res.get("success"):
                flash(prep_res.get("error", "Upload processing failed."), "error")
                return redirect(url_for("submit"))

            code = prep_res["code"]
            filename = prep_res["filename"]
            language = prep_res["detected_language"]

        else:
            code = request.form.get("code_content", "")
            filename = None
            language = None

        # Execute multi-agent analysis workflow
        review_result = orchestrator.run_review(
            code=code,
            filename=filename,
            detected_language=language,
        )

        if not review_result.get("success"):
            flash(review_result.get("error", "Code review analysis failed."), "error")
            return redirect(url_for("submit"))

        flash(f"Analysis completed successfully for {review_result['filename']}!", "success")
        return redirect(url_for("results", review_id=review_result["review_id"]))

    @app.route("/results/<review_id>")
    def results(review_id):
        """Pull Request Review Summary."""
        session = get_db_session()
        try:
            review = session.query(CodeReview).filter_by(review_id=review_id).first()
            if not review:
                flash(f"Review ID '{review_id}' was not found.", "error")
                return redirect(url_for("history"))

            review_dict = review.to_dict()
            findings = [f.to_dict() for f in review.findings]
            review_dict["findings"] = findings

            # Reconstruct remediation roadmap from JSON
            roadmap = review_dict.get("pr_summary", [])
            review_dict["roadmap"] = roadmap

            return render_template("results.html", review=review_dict)
        finally:
            session.close()

    @app.route("/findings/<review_id>")
    def findings_view(review_id):
        """Detailed Findings View with Category / Severity Filtering."""
        finding_type = request.args.get("type", "").lower()
        severity_filter = request.args.get("severity", "").upper()

        session = get_db_session()
        try:
            review = session.query(CodeReview).filter_by(review_id=review_id).first()
            if not review:
                flash(f"Review ID '{review_id}' was not found.", "error")
                return redirect(url_for("history"))

            all_findings = [f.to_dict() for f in review.findings]
            security_count = sum(1 for f in all_findings if f["finding_type"] == "SECURITY")
            quality_count = sum(1 for f in all_findings if f["finding_type"] == "QUALITY")

            filtered = FindingsManager.filter_findings(
                findings=all_findings,
                finding_type=finding_type if finding_type else None,
                severity=severity_filter if severity_filter else None,
            )

            return render_template(
                "findings.html",
                review=review.to_dict(),
                findings=filtered,
                current_type=finding_type,
                current_severity=severity_filter,
                security_count=security_count,
                quality_count=quality_count,
            )
        finally:
            session.close()

    @app.route("/remediation/<review_id>")
    def remediation_view(review_id):
        """Prioritized Remediation Guide and Code Corrections."""
        session = get_db_session()
        try:
            review = session.query(CodeReview).filter_by(review_id=review_id).first()
            if not review:
                flash(f"Review ID '{review_id}' was not found.", "error")
                return redirect(url_for("history"))

            review_dict = review.to_dict()
            roadmap = review_dict.get("pr_summary", [])
            return render_template("remediation.html", review=review_dict, roadmap=roadmap)
        finally:
            session.close()

    @app.route("/assistant")
    @app.route("/assistant/<review_id>")
    def assistant(review_id=None):
        """Conversational AI Code Assistant Interface."""
        active_review = None
        chat_history = []

        session = get_db_session()
        try:
            if review_id:
                review = session.query(CodeReview).filter_by(review_id=review_id).first()
                if review:
                    active_review = review.to_dict()
                    active_review["findings"] = [f.to_dict() for f in review.findings]

                # Load chat messages for this review
                messages = (
                    session.query(ChatMessage)
                    .filter_by(review_id=review_id)
                    .order_by(ChatMessage.id.asc())
                    .all()
                )
                chat_history = [m.to_dict() for m in messages]

            return render_template(
                "assistant.html",
                active_review=active_review,
                chat_history=chat_history,
            )
        finally:
            session.close()

    @app.route("/history")
    def history():
        """Review History Audit Table."""
        session = get_db_session()
        try:
            reviews = session.query(CodeReview).order_by(CodeReview.id.desc()).all()
            review_list = [r.to_dict() for r in reviews]
            return render_template("history.html", reviews=review_list)
        finally:
            session.close()

    @app.route("/export/<review_id>/<format>")
    def export_report(review_id, format):
        """Download Generated PDF or JSON Review Report."""
        format_lower = format.lower()
        if format_lower not in ("pdf", "json"):
            abort(400, "Invalid export format. Only 'pdf' and 'json' are supported.")

        filename = f"{review_id}.{format_lower}"
        filepath = os.path.join(Config.REPORTS_DIR, filename)

        if not os.path.exists(filepath):
            # Attempt to re-generate from database
            session = get_db_session()
            try:
                review = session.query(CodeReview).filter_by(review_id=review_id).first()
                if not review:
                    abort(404, "Report not found.")
                review_dict = review.to_dict()
                review_dict["findings"] = [f.to_dict() for f in review.findings]
                review_dict["roadmap"] = review_dict.get("pr_summary", [])

                if format_lower == "pdf":
                    filepath = orchestrator.report_generator.generate_pdf_report(review_dict)
                else:
                    filepath = orchestrator.report_generator.generate_json_report(review_dict)
            finally:
                session.close()

        return send_file(
            filepath,
            as_attachment=True,
            download_name=f"{review_id}_Report.{format_lower}"
        )

    # -------------------------------------------------------------------------
    # REST API ENDPOINTS
    # -------------------------------------------------------------------------
    @app.route("/api/detect-language", methods=["POST"])
    def api_detect_language():
        """Live language detection API for editor preview."""
        data = request.get_json() or {}
        code = data.get("code", "")
        if not code.strip():
            return jsonify({"success": False, "error": "Empty code payload"})

        try:
            lang, confidence, reason = detect_language(code)
            return jsonify({
                "success": True,
                "language": lang,
                "confidence": confidence,
                "reason": reason,
            })
        except UnsupportedLanguageError as exc:
            return jsonify({"success": False, "error": str(exc)})

    @app.route("/api/chat", methods=["POST"])
    def api_chat():
        """Process question via RAG Conversational Assistant."""
        data = request.get_json() or {}
        question = data.get("question", "").strip()
        review_id = data.get("review_id", "").strip()

        if not question:
            return jsonify({"success": False, "error": "Question cannot be empty."}), 400

        review_context = None
        session = get_db_session()
        try:
            if review_id:
                review = session.query(CodeReview).filter_by(review_id=review_id).first()
                if review:
                    review_context = review.to_dict()
                    review_context["findings"] = [f.to_dict() for f in review.findings]

            # Query Assistant Agent
            res = orchestrator.code_assistant_agent.ask(
                question=question,
                review_context=review_context,
            )

            # Persist chat history to database
            user_msg = ChatMessage(
                review_id=review_id if review_id else None,
                role="user",
                message=question,
            )
            assistant_msg = ChatMessage(
                review_id=review_id if review_id else None,
                role="assistant",
                message=res.get("answer", ""),
                citations_json=json.dumps(res.get("citations", [])),
            )
            session.add(user_msg)
            session.add(assistant_msg)
            session.commit()

            return jsonify({
                "success": True,
                "answer": res.get("answer", ""),
                "citations": res.get("citations", []),
                "model_used": res.get("model_used", "Rule Engine"),
            })
        except Exception as exc:
            session.rollback()
            logger.error("Chat API error: %s", exc)
            return jsonify({"success": False, "error": str(exc)}), 500
        finally:
            session.close()

    @app.route("/api/chat/clear", methods=["POST"])
    def api_chat_clear():
        """Clear chat messages."""
        data = request.get_json() or {}
        review_id = data.get("review_id", "").strip()

        session = get_db_session()
        try:
            if review_id:
                session.query(ChatMessage).filter_by(review_id=review_id).delete()
            else:
                session.query(ChatMessage).filter(ChatMessage.review_id.is_(None)).delete()
            session.commit()
            return jsonify({"success": True, "message": "Chat history cleared."})
        except Exception as exc:
            session.rollback()
            return jsonify({"success": False, "error": str(exc)}), 500
        finally:
            session.close()

    @app.errorhandler(413)
    def file_too_large(e):
        flash("The uploaded file exceeds the 5 MB limit. Please upload a smaller file.", "error")
        return redirect(url_for("submit")), 413

    @app.errorhandler(404)
    def not_found(e):
        return render_template("base.html", content="<div class='text-center py-5'><h3>404 - Page Not Found</h3><a href='/'>Return to Home</a></div>"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("base.html", content="<div class='text-center py-5'><h3>500 - Internal Server Error</h3><a href='/'>Return to Home</a></div>"), 500

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\nAI Code Review Platform running at: http://127.0.0.1:{port}\n")
    app.run(host="127.0.0.1", port=port, debug=False)
