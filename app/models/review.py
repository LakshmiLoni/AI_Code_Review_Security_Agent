"""SQLite Review and Finding models with thread-safe connection handling."""

import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class DatabaseManager:
    """Manages SQLite schema creation, migrations, and transactions."""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path).resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self):
        """Initialize database tables with parameterized DDL."""
        with self.get_connection() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                review_uuid TEXT UNIQUE NOT NULL,
                filename TEXT NOT NULL,
                language TEXT NOT NULL,
                source_code TEXT NOT NULL,
                quality_score REAL DEFAULT 100.0,
                security_score REAL DEFAULT 100.0,
                status TEXT NOT NULL,
                summary_text TEXT,
                critical_count INTEGER DEFAULT 0,
                high_count INTEGER DEFAULT 0,
                medium_count INTEGER DEFAULT 0,
                low_count INTEGER DEFAULT 0,
                total_findings INTEGER DEFAULT 0,
                metrics_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                review_id INTEGER NOT NULL,
                finding_type TEXT NOT NULL,
                rule_id TEXT NOT NULL,
                title TEXT NOT NULL,
                severity TEXT NOT NULL,
                line_number INTEGER DEFAULT 0,
                code_snippet TEXT,
                explanation TEXT,
                why_it_matters TEXT,
                remediation TEXT,
                remediated_code TEXT,
                kb_reference TEXT,
                cwe_id TEXT,
                owasp_category TEXT,
                FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_reviews_created ON reviews(created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_findings_review ON findings(review_id);
            """)


class ReviewModel:
    """Operations for saving and retrieving code reviews."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def create_review(self, review_data: Dict[str, Any], findings: List[Dict[str, Any]]) -> str:
        review_uuid = review_data.get("review_uuid") or uuid.uuid4().hex
        metrics_json = json.dumps(review_data.get("metrics", {}))

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO reviews (
                review_uuid, filename, language, source_code,
                quality_score, security_score, status, summary_text,
                critical_count, high_count, medium_count, low_count,
                total_findings, metrics_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                review_uuid,
                review_data.get("filename", "untitled.py"),
                review_data.get("language", "python"),
                review_data.get("source_code", ""),
                review_data.get("quality_score", 100.0),
                review_data.get("security_score", 100.0),
                review_data.get("status", "Completed"),
                review_data.get("summary_text", ""),
                review_data.get("critical_count", 0),
                review_data.get("high_count", 0),
                review_data.get("medium_count", 0),
                review_data.get("low_count", 0),
                len(findings),
                metrics_json,
                datetime.utcnow().isoformat()
            ))

            review_id = cursor.lastrowid

            # Insert findings
            for f in findings:
                cursor.execute("""
                INSERT INTO findings (
                    review_id, finding_type, rule_id, title, severity,
                    line_number, code_snippet, explanation, why_it_matters,
                    remediation, remediated_code, kb_reference, cwe_id, owasp_category
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    review_id,
                    f.get("finding_type", "security"),
                    f.get("rule_id", "SEC-GEN-01"),
                    f.get("title", "Security Finding"),
                    f.get("severity", "Medium"),
                    f.get("line_number", 1),
                    f.get("code_snippet", ""),
                    f.get("explanation", ""),
                    f.get("why_it_matters", ""),
                    f.get("remediation", ""),
                    f.get("remediated_code", ""),
                    f.get("kb_reference", ""),
                    f.get("cwe_id", ""),
                    f.get("owasp_category", "")
                ))

            conn.commit()
            return review_uuid

    def get_review_by_uuid(self, review_uuid: str) -> Optional[Dict[str, Any]]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reviews WHERE review_uuid = ?", (review_uuid,))
            review_row = cursor.fetchone()
            if not review_row:
                return None

            review = dict(review_row)
            try:
                review["metrics"] = json.loads(review["metrics_json"] or "{}")
            except Exception:
                review["metrics"] = {}

            cursor.execute("SELECT * FROM findings WHERE review_id = ? ORDER BY id ASC", (review["id"],))
            finding_rows = cursor.fetchall()
            review["findings"] = [dict(f) for f in finding_rows]

            # Split into quality and security lists
            review["quality_findings"] = [f for f in review["findings"] if f["finding_type"] == "quality"]
            review["security_findings"] = [f for f in review["findings"] if f["finding_type"] == "security"]

            return review

    def get_all_reviews(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reviews ORDER BY id DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def delete_review(self, review_uuid: str) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reviews WHERE review_uuid = ?", (review_uuid,))
            conn.commit()
            return cursor.rowcount > 0

    def get_dashboard_metrics(self) -> Dict[str, Any]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) as total FROM reviews")
            total_reviews = cursor.fetchone()["total"]

            cursor.execute("""
            SELECT 
                count(*) as total_findings,
                sum(case when severity = 'Critical' then 1 else 0 end) as critical_count,
                sum(case when severity = 'High' then 1 else 0 end) as high_count,
                sum(case when severity = 'Medium' then 1 else 0 end) as medium_count,
                sum(case when severity = 'Low' then 1 else 0 end) as low_count,
                sum(case when finding_type = 'security' then 1 else 0 end) as security_total,
                sum(case when finding_type = 'quality' then 1 else 0 end) as quality_total
            FROM findings
            """)
            stats = dict(cursor.fetchone())

            cursor.execute("SELECT * FROM reviews ORDER BY id DESC LIMIT 5")
            recent_reviews = [dict(r) for r in cursor.fetchall()]

            return {
                "total_reviews": total_reviews,
                "total_findings": stats["total_findings"] or 0,
                "critical_count": stats["critical_count"] or 0,
                "high_count": stats["high_count"] or 0,
                "medium_count": stats["medium_count"] or 0,
                "low_count": stats["low_count"] or 0,
                "security_total": stats["security_total"] or 0,
                "quality_total": stats["quality_total"] or 0,
                "recent_reviews": recent_reviews
            }


class FindingModel:
    """Helper methods for findings data manipulation."""
    pass
