"""Services: Review Service.

High-level application service that coordinates code intake, language detection,
syntax verification, multi-agent review orchestration, report generation,
and database persistence.
"""
from typing import Dict, Any, Optional
from orchestrator.agent_orchestrator import AgentOrchestrator
from database.review_repository import ReviewRepository
from reports.pdf_generator import PDFReportGenerator
from reports.json_generator import JSONReportGenerator
from analysis.language_detector import detect_language


class ReviewService:
    """Primary review service coordinating execution and persistence."""

    def __init__(self):
        self.orchestrator = AgentOrchestrator()
        self.repository = ReviewRepository()
        self.pdf_generator = PDFReportGenerator()
        self.json_generator = JSONReportGenerator()

    def submit_and_review(
        self,
        code: str,
        filename: Optional[str] = None,
        detected_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute end-to-end multi-agent review for submitted source code."""
        result = self.orchestrator.run_review(
            code=code,
            filename=filename,
            detected_language=detected_language
        )

        if result.get("success"):
            # Ensure saved in repository
            self.repository.save_review(result)
            # Ensure reports exist
            if not result.get("pdf_report_path"):
                result["pdf_report_path"] = self.pdf_generator.generate(result)
            if not result.get("json_report_path"):
                result["json_report_path"] = self.json_generator.generate(result)

        return result

    def get_review(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Fetch review record by review_id."""
        return self.repository.get_review_by_id(review_id)

    def generate_pdf_for_review(self, review_data: Dict[str, Any]) -> str:
        """Generate PDF report for given review data."""
        return self.pdf_generator.generate(review_data)

    def generate_json_for_review(self, review_data: Dict[str, Any]) -> str:
        """Generate JSON report for given review data."""
        return self.json_generator.generate(review_data)
