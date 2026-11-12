"""SQLAlchemy models for reviews, findings, and conversation history."""
import datetime
import json
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey
)
from sqlalchemy.orm import relationship
from .db import Base


class CodeReview(Base):
    """Represents an executed code review analysis session."""
    __tablename__ = "code_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(String(64), unique=True, nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    detected_language = Column(String(32), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    status = Column(String(32), default="COMPLETED", nullable=False)

    # Health & PR Scoring
    health_score = Column(Float, default=100.0, nullable=False)
    letter_grade = Column(String(8), default="A", nullable=False)
    pr_status = Column(String(64), default="APPROVED", nullable=False)
    executive_summary = Column(Text, nullable=True)
    pr_summary_json = Column(Text, nullable=True)

    # Aggregated Finding Counts
    total_findings = Column(Integer, default=0, nullable=False)
    critical_count = Column(Integer, default=0, nullable=False)
    high_count = Column(Integer, default=0, nullable=False)
    medium_count = Column(Integer, default=0, nullable=False)
    low_count = Column(Integer, default=0, nullable=False)

    # Retention Policy: Only populated if RETAIN_SOURCE_CODE=True
    retained_source_code = Column(Text, nullable=True)

    # Relationships
    findings = relationship("ReviewFinding", back_populates="review", cascade="all, delete-orphan")

    def to_dict(self):
        """Serialize review metadata to dictionary."""
        return {
            "id": self.id,
            "review_id": self.review_id,
            "filename": self.filename,
            "detected_language": self.detected_language,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC") if self.timestamp else None,
            "status": self.status,
            "health_score": self.health_score,
            "letter_grade": self.letter_grade,
            "pr_status": self.pr_status,
            "executive_summary": self.executive_summary,
            "pr_summary": json.loads(self.pr_summary_json) if self.pr_summary_json else {},
            "total_findings": self.total_findings,
            "critical_count": self.critical_count,
            "high_count": self.high_count,
            "medium_count": self.medium_count,
            "low_count": self.low_count,
            "has_retained_source": bool(self.retained_source_code),
        }


class ReviewFinding(Base):
    """Represents a specific code quality or security vulnerability finding."""
    __tablename__ = "review_findings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(String(64), ForeignKey("code_reviews.review_id"), nullable=False, index=True)
    finding_type = Column(String(32), nullable=False)  # "SECURITY" or "QUALITY"
    title = Column(String(255), nullable=False)
    category = Column(String(128), nullable=False)  # e.g., "OWASP A03:2021 - Injection"
    severity = Column(String(16), nullable=False)   # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    heuristic_score = Column(Float, nullable=False) # 0.1 to 10.0
    line_number = Column(Integer, nullable=False, default=1)
    filename = Column(String(255), nullable=False)

    description = Column(Text, nullable=False)
    risk_explanation = Column(Text, nullable=True)
    evidence_snippet = Column(Text, nullable=True)
    remediation_recommendation = Column(Text, nullable=True)
    corrected_code = Column(Text, nullable=True)
    is_confirmed_pattern = Column(Boolean, default=True, nullable=False)

    # Relationships
    review = relationship("CodeReview", back_populates="findings")

    def to_dict(self):
        """Serialize finding to dictionary."""
        return {
            "id": self.id,
            "review_id": self.review_id,
            "finding_type": self.finding_type,
            "title": self.title,
            "category": self.category,
            "severity": self.severity,
            "heuristic_score": self.heuristic_score,
            "line_number": self.line_number,
            "filename": self.filename,
            "description": self.description,
            "risk_explanation": self.risk_explanation,
            "evidence_snippet": self.evidence_snippet,
            "remediation_recommendation": self.remediation_recommendation,
            "corrected_code": self.corrected_code,
            "is_confirmed_pattern": self.is_confirmed_pattern,
        }


class ChatMessage(Base):
    """Represents an interactive conversation message in the conversational assistant."""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(String(64), nullable=True, index=True)
    role = Column(String(16), nullable=False)  # "user" or "assistant"
    message = Column(Text, nullable=False)
    citations_json = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "review_id": self.review_id,
            "role": self.role,
            "message": self.message,
            "citations": json.loads(self.citations_json) if self.citations_json else [],
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC") if self.timestamp else None,
        }
