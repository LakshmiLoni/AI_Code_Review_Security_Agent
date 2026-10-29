"""Application Configuration."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if available
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    """Base application configuration with secure defaults."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secure-key-0dea1eea-d1fc-4099-9e5d-3ce331ed4686")
    BASE_DIR = BASE_DIR

    # Paths
    DATABASE_PATH = BASE_DIR / "data" / "reviews.db"
    KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
    CHROMA_DIR = BASE_DIR / "chroma_db"
    REPORTS_DIR = BASE_DIR / "reports"
    UPLOAD_FOLDER = BASE_DIR / "uploads"

    # Upload & input constraints
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 Megabytes
    ALLOWED_EXTENSIONS = {".py", ".java"}

    # Gemini configuration
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    # Security settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
