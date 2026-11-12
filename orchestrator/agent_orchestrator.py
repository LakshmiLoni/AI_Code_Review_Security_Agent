"""Orchestrator: Multi-Agent Review Workflow.

Orchestrates the complete lifecycle:
1. Language detection & syntax verification.
2. Concurrent parallel execution of Code Analysis and Security agents via ThreadPoolExecutor.
3. Consolidation, scoring, and deduplication of findings.
4. Remediation generation with RAG-grounded safety rationales.
5. GitHub-style Pull Request review generation.
6. SQLite database persistence with source retention policy.
7. Report generation (JSON and PDF).
Error resilient: an error in any agent does not crash the pipeline.
"""
import concurrent.futures
import datetime
import json
import logging
from typing import Dict, Any, Optional

from config import Config
from agents.code_analysis_agent import CodeAnalysisAgent
from agents.security_agent import SecurityAgent
from agents.remediation_agent import RemediationAgent
from agents.pr_summary_agent import PRSummaryAgent
from agents.code_assistant_agent import CodeAssistantAgent

from modules.code_submission import CodeSubmissionHandler
from modules.findings_manager import FindingsManager
from modules.report_generator import ReportGenerator

from database.db import get_db_session, init_db
from database.models import CodeReview, ReviewFinding
from utils.helpers import generate_review_id
from utils.language_detector import detect_language, UnsupportedLanguageError
from utils.syntax_validator import validate_syntax

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Manages multi-agent parallel execution, synthesis, and persistence."""

    def __init__(self):
        self.code_analysis_agent = CodeAnalysisAgent()
        self.security_agent = SecurityAgent()
        self.remediation_agent = RemediationAgent()
        self.pr_summary_agent = PRSummaryAgent()
        self.code_assistant_agent = CodeAssistantAgent()

        self.submission_handler = CodeSubmissionHandler()
        self.report_generator = ReportGenerator()

        # Ensure database tables exist
        init_db()

    def run_review(
        self,
        code: str,
        filename: Optional[str] = None,
        detected_language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute the end-to-end multi-agent review workflow.

        Args:
            code: Source code text.
            filename: Optional filename.
            detected_language: Optional pre-detected language.

        Returns:
            Complete review result dictionary.
        """
        review_id = generate_review_id()
        code_clean = (code or "").strip()

        if not code_clean:
            return {
                "success": False,
                "review_id": review_id,
                "error": "Source code cannot be empty.",
            }

        # 1. Automatic Language Detection
        if not detected_language:
            try:
                language, confidence, reason = detect_language(code_clean, filename=filename)
            except UnsupportedLanguageError as exc:
                return {
                    "success": False,
                    "review_id": review_id,
                    "error": str(exc),
                }
        else:
            language = detected_language.lower().strip()

        # Generate filename if not provided
        if not filename:
            ext = ".py" if language == "python" else ".java"
            timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"snippet_{timestamp}{ext}"

        # 2. Syntax Validation
        is_valid_syntax, syntax_err, err_line = validate_syntax(code_clean, language)
        if not is_valid_syntax:
            return {
                "success": False,
                "review_id": review_id,
                "error": f"Syntax Validation Error in '{filename}': {syntax_err}",
                "line_number": err_line,
                "detected_language": language,
            }

        # 3. Parallel Multi-Agent Execution: Code Analysis + Security Vulnerability
        quality_findings = []
        security_findings = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_quality = executor.submit(
                self._safe_execute_agent,
                self.code_analysis_agent.analyze,
                code_clean,
                language,
                filename
            )
            future_security = executor.submit(
                self._safe_execute_agent,
                self.security_agent.analyze,
                code_clean,
                language,
                filename
            )

            # Wait for both agents to complete
            done, _ = concurrent.futures.wait(
                [future_quality, future_security],
                timeout=60,
                return_when=concurrent.futures.ALL_COMPLETED
            )

            for future in done:
                if future == future_quality:
                    quality_findings = future.result() or []
                elif future == future_security:
                    security_findings = future.result() or []

        # 4. Merge & Deduplicate Findings
        consolidated_findings = FindingsManager.consolidate_findings(
            quality_findings=quality_findings,
            security_findings=security_findings,
        )

        # 5. Severity Metrics & Code Health Score
        metrics = FindingsManager.compute_summary_metrics(consolidated_findings)

        # 6. Remediation Agent: Generate Prioritized Roadmap
        remediation_data = self.remediation_agent.generate_remediation_plan(
            findings=consolidated_findings,
            detected_language=language,
        )

        # 7. PR Summary Agent: Produce Merge Readiness Review
        pr_review = self.pr_summary_agent.generate_review(
            findings=consolidated_findings,
            detected_language=language,
            health_data=metrics,
            remediation_data=remediation_data,
            filename=filename,
        )

        # 8. Construct Complete Result Payload
        review_result = {
            "success": True,
            "review_id": review_id,
            "filename": filename,
            "detected_language": language,
            "health_score": metrics["health_score"],
            "letter_grade": metrics["grade"],
            "pr_status": pr_review["pr_status"],
            "status_badge": pr_review["status_badge"],
            "executive_summary": pr_review["executive_summary"],
            "verdict_note": pr_review["verdict_note"],
            "total_findings": metrics["total_findings"],
            "critical_count": metrics["critical_count"],
            "high_count": metrics["high_count"],
            "medium_count": metrics["medium_count"],
            "low_count": metrics["low_count"],
            "findings": consolidated_findings,
            "security_observations": pr_review["security_observations"],
            "quality_observations": pr_review["quality_observations"],
            "recommended_fixes": pr_review["recommended_fixes"],
            "roadmap": remediation_data.get("prioritized_roadmap", []),
            "markdown_summary": pr_review["markdown_summary"],
            "retained_source_code": code_clean if Config.RETAIN_SOURCE_CODE else None,
        }

        # 9. Persist to SQLite Database
        self._persist_to_database(review_result)

        # 10. Generate Downloadable PDF and JSON Reports
        try:
            json_path = self.report_generator.generate_json_report(review_result)
            pdf_path = self.report_generator.generate_pdf_report(review_result)
            review_result["json_report_path"] = json_path
            review_result["pdf_report_path"] = pdf_path
        except Exception as exc:
            logger.error("Error generating reports for %s: %s", review_id, exc)

        return review_result

    def _safe_execute_agent(self, agent_fn, code: str, language: str, filename: str):
        """Execute agent analysis with exception isolation."""
        try:
            return agent_fn(code, language, filename)
        except Exception as exc:
            logger.error("Agent execution failed for %s: %s", getattr(agent_fn, "__name__", "agent"), exc)
            return []

    def _persist_to_database(self, data: Dict[str, Any]):
        """Persist review metadata and individual findings to SQLite."""
        session = get_db_session()
        try:
            review_entry = CodeReview(
                review_id=data["review_id"],
                filename=data["filename"],
                detected_language=data["detected_language"],
                health_score=data["health_score"],
                letter_grade=data["letter_grade"],
                pr_status=data["pr_status"],
                executive_summary=data["executive_summary"],
                pr_summary_json=json.dumps(data.get("roadmap", [])),
                total_findings=data["total_findings"],
                critical_count=data["critical_count"],
                high_count=data["high_count"],
                medium_count=data["medium_count"],
                low_count=data["low_count"],
                retained_source_code=data.get("retained_source_code"),
            )
            session.add(review_entry)
            session.flush()

            for item in data.get("findings", []):
                finding_entry = ReviewFinding(
                    review_id=data["review_id"],
                    finding_type=item.get("finding_type", "SECURITY"),
                    title=item.get("title", ""),
                    category=item.get("category", "General"),
                    severity=str(item.get("severity", "LOW")).upper(),
                    heuristic_score=float(item.get("heuristic_score", 1.0)),
                    line_number=int(item.get("line_number", 1)),
                    filename=item.get("filename", data["filename"]),
                    description=item.get("description", ""),
                    risk_explanation=item.get("risk_explanation", ""),
                    evidence_snippet=item.get("evidence_snippet", ""),
                    remediation_recommendation=item.get("remediation_recommendation", ""),
                    corrected_code=item.get("corrected_code", ""),
                    is_confirmed_pattern=bool(item.get("is_confirmed_pattern", True)),
                )
                session.add(finding_entry)

            session.commit()
        except Exception as exc:
            session.rollback()
            logger.error("Database persistence failed for %s: %s", data.get("review_id"), exc)
        finally:
            session.close()
