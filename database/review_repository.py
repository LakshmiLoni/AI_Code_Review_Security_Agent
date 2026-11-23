"""Database Review Repository.

Encapsulates all persistence, retrieval, search, and metric aggregation
for code review sessions and findings.
"""
import json
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import desc, func

from .db import get_db_session, init_db
from .models import CodeReview, ReviewFinding

logger = logging.getLogger(__name__)


class ReviewRepository:
    """Repository handling database operations for code reviews."""

    def __init__(self):
        init_db()

    def save_review(self, review_data: Dict[str, Any]) -> bool:
        """Persist or update a code review and its findings."""
        session = get_db_session()
        try:
            review_id = review_data.get("review_id")
            if not review_id:
                raise ValueError("Review ID is required to persist a code review.")

            # Check if review already exists
            existing = session.query(CodeReview).filter_by(review_id=review_id).first()
            if existing:
                # Update existing record
                existing.filename = review_data.get("filename", existing.filename)
                existing.detected_language = review_data.get("detected_language", existing.detected_language)
                existing.health_score = float(review_data.get("health_score", existing.health_score))
                existing.letter_grade = review_data.get("letter_grade", existing.letter_grade)
                existing.pr_status = review_data.get("pr_status", existing.pr_status)
                existing.executive_summary = review_data.get("executive_summary", existing.executive_summary)
                existing.pr_summary_json = json.dumps(review_data.get("roadmap", []))
                existing.total_findings = int(review_data.get("total_findings", 0))
                existing.critical_count = int(review_data.get("critical_count", 0))
                existing.high_count = int(review_data.get("high_count", 0))
                existing.medium_count = int(review_data.get("medium_count", 0))
                existing.low_count = int(review_data.get("low_count", 0))
                existing.retained_source_code = review_data.get("retained_source_code")

                # Remove old findings to prevent duplicates on update
                session.query(ReviewFinding).filter_by(review_id=review_id).delete()
            else:
                new_review = CodeReview(
                    review_id=review_id,
                    filename=review_data.get("filename", "unknown"),
                    detected_language=review_data.get("detected_language", "unknown"),
                    health_score=float(review_data.get("health_score", 100.0)),
                    letter_grade=review_data.get("letter_grade", "A"),
                    pr_status=review_data.get("pr_status", "APPROVED"),
                    executive_summary=review_data.get("executive_summary", ""),
                    pr_summary_json=json.dumps(review_data.get("roadmap", [])),
                    total_findings=int(review_data.get("total_findings", 0)),
                    critical_count=int(review_data.get("critical_count", 0)),
                    high_count=int(review_data.get("high_count", 0)),
                    medium_count=int(review_data.get("medium_count", 0)),
                    low_count=int(review_data.get("low_count", 0)),
                    retained_source_code=review_data.get("retained_source_code"),
                )
                session.add(new_review)

            session.flush()

            # Insert findings
            for item in review_data.get("findings", []):
                finding = ReviewFinding(
                    review_id=review_id,
                    finding_type=item.get("finding_type", "SECURITY"),
                    title=item.get("title", "Untitled Finding"),
                    category=item.get("category", "General"),
                    severity=str(item.get("severity", "LOW")).upper(),
                    heuristic_score=float(item.get("heuristic_score", 1.0)),
                    line_number=int(item.get("line_number", 1)),
                    filename=item.get("filename", review_data.get("filename", "unknown")),
                    description=item.get("description", ""),
                    risk_explanation=item.get("risk_explanation", ""),
                    evidence_snippet=item.get("evidence_snippet", ""),
                    remediation_recommendation=item.get("remediation_recommendation", ""),
                    corrected_code=item.get("corrected_code", ""),
                    is_confirmed_pattern=bool(item.get("is_confirmed_pattern", True)),
                )
                session.add(finding)

            session.commit()
            return True
        except Exception as exc:
            session.rollback()
            logger.error("Failed to save review %s: %s", review_data.get("review_id"), exc)
            return False
        finally:
            session.close()

    def get_review_by_id(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve full review details and associated findings by review_id."""
        session = get_db_session()
        try:
            review = session.query(CodeReview).filter_by(review_id=review_id).first()
            if not review:
                return None

            data = review.to_dict()
            findings = (
                session.query(ReviewFinding)
                .filter_by(review_id=review_id)
                .order_by(ReviewFinding.line_number.asc())
                .all()
            )
            data["findings"] = [f.to_dict() for f in findings]
            data["roadmap"] = data.get("pr_summary", [])
            return data
        finally:
            session.close()

    def get_all_reviews(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Retrieve list of past reviews sorted by timestamp descending."""
        session = get_db_session()
        try:
            reviews = (
                session.query(CodeReview)
                .order_by(desc(CodeReview.timestamp))
                .limit(limit)
                .offset(offset)
                .all()
            )
            return [r.to_dict() for r in reviews]
        finally:
            session.close()

    def get_review_count(self) -> int:
        """Get total number of reviews stored in the database."""
        session = get_db_session()
        try:
            return session.query(func.count(CodeReview.id)).scalar() or 0
        finally:
            session.close()

    def delete_review(self, review_id: str) -> bool:
        """Delete a review and all associated findings."""
        session = get_db_session()
        try:
            review = session.query(CodeReview).filter_by(review_id=review_id).first()
            if not review:
                return False
            session.delete(review)
            session.commit()
            return True
        except Exception as exc:
            session.rollback()
            logger.error("Failed to delete review %s: %s", review_id, exc)
            return False
        finally:
            session.close()

    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Aggregate actual real metrics across all stored reviews for the dashboard."""
        session = get_db_session()
        try:
            total_reviews = session.query(func.count(CodeReview.id)).scalar() or 0
            if total_reviews == 0:
                return {
                    "total_reviews": 0,
                    "avg_health_score": 0.0,
                    "total_findings": 0,
                    "critical_count": 0,
                    "high_count": 0,
                    "medium_count": 0,
                    "low_count": 0,
                    "languages": {},
                    "pr_status_counts": {},
                    "recent_reviews": [],
                }

            avg_score = session.query(func.avg(CodeReview.health_score)).scalar() or 100.0
            sum_crit = session.query(func.sum(CodeReview.critical_count)).scalar() or 0
            sum_high = session.query(func.sum(CodeReview.high_count)).scalar() or 0
            sum_med = session.query(func.sum(CodeReview.medium_count)).scalar() or 0
            sum_low = session.query(func.sum(CodeReview.low_count)).scalar() or 0
            total_findings = sum_crit + sum_high + sum_med + sum_low

            # Language breakdown
            lang_rows = (
                session.query(CodeReview.detected_language, func.count(CodeReview.id))
                .group_by(CodeReview.detected_language)
                .all()
            )
            languages = {lang.capitalize(): count for lang, count in lang_rows}

            # PR status breakdown
            status_rows = (
                session.query(CodeReview.pr_status, func.count(CodeReview.id))
                .group_by(CodeReview.pr_status)
                .all()
            )
            pr_statuses = {st: count for st, count in status_rows}

            # 5 most recent reviews
            recent = (
                session.query(CodeReview)
                .order_by(desc(CodeReview.timestamp))
                .limit(5)
                .all()
            )

            return {
                "total_reviews": total_reviews,
                "avg_health_score": round(float(avg_score), 1),
                "total_findings": int(total_findings),
                "critical_count": int(sum_crit),
                "high_count": int(sum_high),
                "medium_count": int(sum_med),
                "low_count": int(sum_low),
                "languages": languages,
                "pr_status_counts": pr_statuses,
                "recent_reviews": [r.to_dict() for r in recent],
            }
        finally:
            session.close()
