"""Central configuration for Milestone 1.

Values can be overridden with environment variables or a local ``.env`` file
(see ``.env.example``). Nothing here requires a paid API key.
"""
from __future__ import annotations

import os
from pathlib import Path

try:  # python-dotenv is optional at runtime
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:  # pragma: no cover
    pass


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


# --- Paths ------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCUMENTS_DIR = PROJECT_ROOT / "knowledge_base" / "documents"
VECTOR_STORE_DIR = PROJECT_ROOT / "vector_store"
SAMPLE_CODE_DIR = PROJECT_ROOT / "sample_code"

# --- Submission limits ------------------------------------------------------
SUPPORTED_EXTENSIONS = {".py": "python", ".java": "java"}
MAX_FILE_SIZE_BYTES = _int_env("MAX_FILE_SIZE_KB", 512) * 1024
MAX_PASTE_CHARS = MAX_FILE_SIZE_BYTES  # same ceiling for pasted text
JAVAC_TIMEOUT_SECONDS = _int_env("JAVAC_TIMEOUT_SECONDS", 30)

# --- Language detection -----------------------------------------------------
# Minimum confidence (0-1) before a language is reported for pasted code.
DETECTION_CONFIDENCE_THRESHOLD = 0.65
# A file extension is overruled only if the content contradicts it this strongly.
EXTENSION_OVERRIDE_CONFIDENCE = 0.75

# --- RAG --------------------------------------------------------------------
EMBEDDING_BACKEND = os.environ.get("EMBEDDING_BACKEND", "sentence-transformers").strip().lower()
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
HASHING_DIMENSIONS = 384
CHUNK_SIZE = _int_env("CHUNK_SIZE", 800)  # characters
CHUNK_OVERLAP = _int_env("CHUNK_OVERLAP", 150)  # characters
COLLECTION_NAME = "secure_coding_kb"
DEFAULT_TOP_K = 4
