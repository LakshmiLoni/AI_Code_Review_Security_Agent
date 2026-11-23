"""Module: Report Generator (Facade).

Delegates to the reports package generators (PDFReportGenerator & JSONReportGenerator).
Enforces zero code leakage, table-based recommendations, and clean A4 formatting.
"""
from typing import Dict, Any
from reports.pdf_generator import PDFReportGenerator
from reports.json_generator import JSONReportGenerator
from reports.recommendation_formatter import RecommendationFormatter
from config import Config


class ReportGenerator:
    """Facade for generating downloadable PDF and JSON code review reports."""

    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or Config.REPORTS_DIR
        self.pdf_generator = PDFReportGenerator(self.output_dir)
        self.json_generator = JSONReportGenerator(self.output_dir)

    def generate_json_report(self, review_data: Dict[str, Any]) -> str:
        """Generate structured sanitized JSON report file."""
        return self.json_generator.generate(review_data)

    def generate_pdf_report(self, review_data: Dict[str, Any]) -> str:
        """Generate formal sanitized A4 PDF report file."""
        return self.pdf_generator.generate(review_data)


__all__ = ["ReportGenerator", "PDFReportGenerator", "JSONReportGenerator", "RecommendationFormatter"]
