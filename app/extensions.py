"""Centralized extensions and services for dependency injection."""

from typing import Optional
from .config import Config
from .models.review import DatabaseManager, ReviewModel
from .services.code_parser import CodeParser
from .services.knowledge_service import KnowledgeService
from .services.llm_service import LLMService
from .services.analysis_service import AnalysisService
from .services.report_service import ReportService
from .agents.code_quality_agent import CodeQualityAgent
from .agents.security_agent import SecurityAgent
from .agents.remediation_agent import RemediationAgent
from .agents.review_summary_agent import ReviewSummaryAgent
from .agents.assistant_agent import AssistantAgent
from .agents.orchestrator import ReviewOrchestrator


class ServiceContainer:
    """Singleton-style container holding instantiated application services."""

    def __init__(self, config: Optional[Config] = None):
        cfg = config or Config()

        # Database and Models
        self.db_manager = DatabaseManager(cfg.DATABASE_PATH)
        self.review_model = ReviewModel(self.db_manager)

        # Knowledge Base and RAG
        self.knowledge_service = KnowledgeService(
            kb_dir=cfg.KNOWLEDGE_BASE_DIR,
            chroma_dir=cfg.CHROMA_DIR
        )

        # LLM Service
        self.llm_service = LLMService(
            api_key=cfg.GEMINI_API_KEY,
            model_name=cfg.GEMINI_MODEL
        )

        # Agents
        self.code_parser = CodeParser()
        self.quality_agent = CodeQualityAgent()
        self.security_agent = SecurityAgent()
        self.remediation_agent = RemediationAgent()
        self.summary_agent = ReviewSummaryAgent()
        self.assistant_agent = AssistantAgent(
            llm_service=self.llm_service,
            knowledge_service=self.knowledge_service
        )

        # Orchestrator
        self.orchestrator = ReviewOrchestrator(
            parser=self.code_parser,
            quality_agent=self.quality_agent,
            security_agent=self.security_agent,
            remediation_agent=self.remediation_agent,
            summary_agent=self.summary_agent,
            knowledge_service=self.knowledge_service,
            review_model=self.review_model
        )

        # High-level services
        self.analysis_service = AnalysisService(
            orchestrator=self.orchestrator,
            review_model=self.review_model
        )
        self.report_service = ReportService()


# Global container instance
services: Optional[ServiceContainer] = None


def init_extensions(app) -> ServiceContainer:
    """Initialize all services with the given Flask app configuration."""
    global services
    cfg = app.config.get("APP_CONFIG_OBJECT", Config())
    services = ServiceContainer(cfg)
    return services
