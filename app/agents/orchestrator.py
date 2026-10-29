"""Review Orchestrator Agent.

Directs the execution lifecycle of CodeParser, QualityAgent, SecurityAgent,
RemediationAgent, SummaryAgent, and Database persistence.
"""

from typing import Dict, Any, Tuple
from ..services.code_parser import CodeParser
from .code_quality_agent import CodeQualityAgent
from .security_agent import SecurityAgent
from .remediation_agent import RemediationAgent
from .review_summary_agent import ReviewSummaryAgent
from ..services.knowledge_service import KnowledgeService
from ..models.review import ReviewModel


class ReviewOrchestrator:
    """Coordinates parsing, multi-agent analysis, remediation, and database persistence."""

    def __init__(
        self,
        parser: CodeParser,
        quality_agent: CodeQualityAgent,
        security_agent: SecurityAgent,
        remediation_agent: RemediationAgent,
        summary_agent: ReviewSummaryAgent,
        knowledge_service: KnowledgeService,
        review_model: ReviewModel
    ):
        self.parser = parser
        self.quality_agent = quality_agent
        self.security_agent = security_agent
        self.remediation_agent = remediation_agent
        self.summary_agent = summary_agent
        self.kb = knowledge_service
        self.model = review_model

    def execute_review(
        self,
        source_code: str,
        filename: str = "submitted_code.py",
        language: str = "python"
    ) -> Tuple[str, Dict[str, Any]]:
        """Run full review pipeline, persist results, and return review UUID and summary."""
        # 1. Parse code into AST and extract structural metrics
        parsed = self.parser.parse(source_code, language=language)

        # 2. Quality Agent Analysis
        quality_findings = self.quality_agent.analyze(parsed)

        # 3. Security Agent Analysis
        security_findings = self.security_agent.analyze(parsed)

        # 4. Enrich Security Findings with Knowledge Base context
        for f in security_findings:
            if not f.get("kb_reference"):
                query = f"{f.get('rule_id')} {f.get('title')}"
                kb_hits = self.kb.query(query, top_k=1)
                if kb_hits:
                    f["kb_reference"] = kb_hits[0].get("title", "Knowledge Base Standard")

        # 5. Remediation Agent: Generate side-by-side corrected code and human labels
        all_findings = quality_findings + security_findings
        enhanced_findings = self.remediation_agent.enhance_findings(all_findings, source_code)

        # Re-split into quality and security
        enhanced_quality = [f for f in enhanced_findings if f.get("finding_type") == "quality"]
        enhanced_security = [f for f in enhanced_findings if f.get("finding_type") == "security"]

        # 6. Summary Agent: Calculate scores, executive summary, remaining risks
        summary_info = self.summary_agent.generate_summary(
            enhanced_quality,
            enhanced_security,
            parsed.metrics
        )

        # 7. Package and persist in SQLite
        review_data = {
            "filename": filename,
            "language": language,
            "source_code": source_code,
            "quality_score": summary_info["quality_score"],
            "security_score": summary_info["security_score"],
            "status": summary_info["status"],
            "summary_text": summary_info["summary_text"],
            "critical_count": summary_info["critical_count"],
            "high_count": summary_info["high_count"],
            "medium_count": summary_info["medium_count"],
            "low_count": summary_info["low_count"],
            "metrics": {
                **parsed.metrics,
                "remaining_risks": summary_info["remaining_risks"],
                "recommended_fixes": summary_info["recommended_fixes"],
                "disclaimer": summary_info["disclaimer"]
            }
        }

        review_uuid = self.model.create_review(review_data, enhanced_findings)
        complete_review = self.model.get_review_by_uuid(review_uuid)

        return review_uuid, complete_review
