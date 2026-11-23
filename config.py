"""Application Configuration for AI Code Review & Security Analysis Agent."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "ai-code-review-secret-key-2026")
    
    # Storage paths
    PROJECT_ROOT = str(BASE_DIR)
    DATA_DIR = os.path.join(PROJECT_ROOT, "database")
    
    # Reports storage: storage/reports as primary, reports/ as fallback
    STORAGE_DIR = os.path.join(PROJECT_ROOT, "storage")
    REPORTS_DIR = os.path.join(STORAGE_DIR, "reports")
    LEGACY_REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
    
    # ChromaDB / vector storage
    CHROMA_DIR = os.path.join(STORAGE_DIR, "chroma_db")
    LEGACY_CHROMA_DIR = os.path.join(PROJECT_ROOT, "chroma_db")
    
    # Knowledge base directories
    KB_ROOT_DIR = os.path.join(PROJECT_ROOT, "knowledge_base")
    SECURE_DOCS_DIR = os.path.join(KB_ROOT_DIR, "secure_coding_documents")
    KNOWLEDGE_BASE_DIR = SECURE_DOCS_DIR if os.path.exists(SECURE_DOCS_DIR) else KB_ROOT_DIR
    
    # File uploads & temporary storage
    UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, "uploads")
    
    # SQLite Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", 
        f"sqlite:///{os.path.join(DATA_DIR, 'ai_code_review.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Source Code Retention Policy
    # Store evidence snippets only by default. Only retain full source code if explicitly configured True.
    RETAIN_SOURCE_CODE = os.environ.get("RETAIN_SOURCE_CODE", "false").lower() in ("true", "1", "yes")
    
    # Upload limits: 5 MB maximum
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS = {".py", ".java"}
    
    # Gemini AI API Configuration
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    
    # RAG / Embeddings
    EMBEDDING_MODEL_NAME = os.environ.get("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    CHROMA_COLLECTION_NAME = "secure_coding_kb"
    TOP_K_RETRIEVAL = int(os.environ.get("TOP_K_RETRIEVAL", 4))
    
    # Thread pool for parallel agent execution
    MAX_WORKERS = int(os.environ.get("MAX_WORKERS", 4))
    
    # Severities
    SEVERITY_THRESHOLDS = {
        "CRITICAL": (9.0, 10.0),
        "HIGH": (7.0, 8.9),
        "MEDIUM": (4.0, 6.9),
        "LOW": (0.1, 3.9),
    }

    @classmethod
    def init_app(cls, app=None):
        """Ensure necessary runtime directories exist."""
        for d in [
            cls.DATA_DIR, 
            cls.REPORTS_DIR, 
            cls.LEGACY_REPORTS_DIR,
            cls.CHROMA_DIR, 
            cls.LEGACY_CHROMA_DIR,
            cls.UPLOAD_FOLDER,
            cls.STORAGE_DIR,
            cls.SECURE_DOCS_DIR
        ]:
            os.makedirs(d, exist_ok=True)
