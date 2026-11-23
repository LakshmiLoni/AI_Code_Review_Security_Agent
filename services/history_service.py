"""Services: Review History Service.

Coordinates retrieval of historical reviews, aggregated dashboard statistics,
and search operations via ReviewRepository.
"""
from typing import List, Dict, Any, Optional
from database.review_repository import ReviewRepository


class HistoryService:
    """Provides high-level queries for past review records."""

    def __init__(self, repository: Optional[ReviewRepository] = None):
        self.repository = repository or ReviewRepository()

    def get_history(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get past reviews ordered by date descending."""
        return self.repository.get_all_reviews(limit=limit, offset=offset)

    def get_review_by_id(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Get full review details by review_id."""
        return self.repository.get_review_by_id(review_id)

    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics calculated from actual review records."""
        return self.repository.get_dashboard_metrics()

    def delete_review(self, review_id: str) -> bool:
        """Delete review by review_id."""
        return self.repository.delete_review(review_id)
