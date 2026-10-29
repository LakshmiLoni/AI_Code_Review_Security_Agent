"""Analysis Service wrapping Orchestrator and Database management."""

from pathlib import Path
from typing import Dict, Any, List, Optional
from ..agents.orchestrator import ReviewOrchestrator
from ..models.review import ReviewModel, DatabaseManager


class AnalysisService:
    """Service facade for submitting, inspecting, and retrieving code reviews."""

    def __init__(self, orchestrator: ReviewOrchestrator, review_model: ReviewModel):
        self.orchestrator = orchestrator
        self.model = review_model

    def review_code(
        self,
        source_code: str,
        filename: str = "snippet.py",
        language: str = "python"
    ) -> Dict[str, Any]:
        """Perform a full review and return the saved review record."""
        review_uuid, review_record = self.orchestrator.execute_review(
            source_code=source_code,
            filename=filename,
            language=language
        )
        return review_record

    def get_review(self, review_uuid: str) -> Optional[Dict[str, Any]]:
        return self.model.get_review_by_uuid(review_uuid)

    def get_recent_reviews(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self.model.get_all_reviews(limit=limit)

    def delete_review(self, review_uuid: str) -> bool:
        return self.model.delete_review(review_uuid)

    def get_dashboard_summary(self) -> Dict[str, Any]:
        return self.model.get_dashboard_metrics()
