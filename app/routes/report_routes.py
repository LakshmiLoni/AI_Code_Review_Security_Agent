"""Report export and download routes."""

from flask import Blueprint, Response, abort, current_app
from ..extensions import services

report_bp = Blueprint("reports", __name__)


@report_bp.route("/download/<string:review_uuid>/json")
def download_json_report(review_uuid):
    """Download review findings as a formatted JSON document."""
    review = services.analysis_service.get_review(review_uuid)
    if not review:
        abort(404)

    json_content = services.report_service.generate_json_report(review)
    filename = f"security_report_{review['filename']}_{review_uuid[:8]}.json"

    return Response(
        json_content,
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )


@report_bp.route("/download/<string:review_uuid>/markdown")
def download_markdown_report(review_uuid):
    """Download review findings as a comprehensive Markdown report."""
    review = services.analysis_service.get_review(review_uuid)
    if not review:
        abort(404)

    md_content = services.report_service.generate_markdown_report(review)
    filename = f"security_report_{review['filename']}_{review_uuid[:8]}.md"

    return Response(
        md_content,
        mimetype="text/markdown",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )
