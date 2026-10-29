"""Code review submission, detail inspection, and history routes."""

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from ..extensions import services
from ..utils.validators import validate_code_input, detect_language, validate_file_upload
from ..utils.security import get_safe_filename

review_bp = Blueprint("reviews", __name__)


@review_bp.route("/new", methods=["GET"])
def new_review():
    """Form to submit code via text editor or file upload."""
    return render_template("review.html")


@review_bp.route("/submit", methods=["POST"])
def submit_review():
    """Handle paste submission or file upload, run multi-agent review, and redirect."""
    source_code = ""
    filename = "submission.py"
    language = "python"

    # Check for file upload first
    if "code_file" in request.files and request.files["code_file"].filename:
        uploaded_file = request.files["code_file"]
        is_valid, err_msg, detected_lang = validate_file_upload(uploaded_file)
        if not is_valid:
            flash(err_msg, "danger")
            return redirect(url_for("reviews.new_review"))

        try:
            raw_bytes = uploaded_file.read()
            source_code = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            flash("The uploaded file could not be decoded as UTF-8 text.", "danger")
            return redirect(url_for("reviews.new_review"))

        filename = get_safe_filename(uploaded_file.filename)
        language = detected_lang

    else:
        # Code pasted in textarea
        source_code = request.form.get("source_code", "")
        pasted_lang = request.form.get("language", "auto")
        filename_input = request.form.get("filename", "").strip()

        is_valid, err_msg = validate_code_input(source_code)
        if not is_valid:
            flash(err_msg, "danger")
            return redirect(url_for("reviews.new_review"))

        if pasted_lang == "auto" or not pasted_lang:
            language = detect_language(source_code, filename_input)
        else:
            language = pasted_lang.lower()

        if filename_input:
            filename = get_safe_filename(filename_input)
        else:
            ext = ".py" if language == "python" else ".java"
            filename = f"snippet_{language}{ext}"

    # Execute review via multi-agent orchestrator
    try:
        review_record = services.analysis_service.review_code(
            source_code=source_code,
            filename=filename,
            language=language
        )
        flash("Code analysis completed successfully!", "success")
        return redirect(url_for("reviews.review_detail", review_uuid=review_record["review_uuid"]))
    except Exception as e:
        flash(f"An error occurred during analysis: {str(e)}", "danger")
        return redirect(url_for("reviews.new_review"))


@review_bp.route("/<string:review_uuid>")
def review_detail(review_uuid):
    """Display comprehensive review findings, side-by-side fixes, and summary."""
    review = services.analysis_service.get_review(review_uuid)
    if not review:
        abort(404)
    return render_template("review_detail.html", review=review)


@review_bp.route("/history")
def review_history():
    """List historical reviews."""
    reviews = services.analysis_service.get_recent_reviews(limit=100)
    return render_template("review_history.html", reviews=reviews)


@review_bp.route("/<string:review_uuid>/delete", methods=["POST"])
def delete_review(review_uuid):
    """Delete a review from history."""
    success = services.analysis_service.delete_review(review_uuid)
    if success:
        flash("Review record deleted successfully.", "info")
    else:
        flash("Could not find the specified review to delete.", "warning")
    return redirect(url_for("reviews.review_history"))
