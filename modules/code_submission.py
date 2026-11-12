"""Module: Code Submission & Ingestion.

Handles direct code pasting, Python (.py) and Java (.java) file uploads,
automatic language identification, syntax validation, file-size enforcement,
and auto-naming of pasted code snippets.
"""
import os
import datetime
from typing import Tuple, Dict, Any, Optional
from werkzeug.datastructures import FileStorage
from config import Config
from utils.language_detector import detect_language, UnsupportedLanguageError
from utils.syntax_validator import validate_syntax


class CodeSubmissionHandler:
    """Manages ingestion, validation, and preparation of submitted code."""

    def __init__(self, max_size_bytes: int = None):
        self.max_size_bytes = max_size_bytes or Config.MAX_CONTENT_LENGTH

    def handle_pasted_code(self, code_text: str) -> Dict[str, Any]:
        """Process code pasted directly into the portal editor.

        Returns:
            Dictionary containing:
            - success: bool
            - code: str
            - filename: str
            - detected_language: str
            - confidence: float
            - line_count: int
            - error: Optional[str]
            - line_number: Optional[int]
        """
        code = (code_text or "").strip()
        if not code:
            return {
                "success": False,
                "error": "Submission is empty. Please paste your Python or Java source code.",
            }

        # 1. Automatic Language Detection
        try:
            language, confidence, reason = detect_language(code)
        except UnsupportedLanguageError as exc:
            return {"success": False, "error": str(exc)}

        # 2. Syntax Validation
        is_valid_syntax, syntax_err, err_line = validate_syntax(code, language)
        if not is_valid_syntax:
            return {
                "success": False,
                "error": f"Syntax Validation Failed: {syntax_err}",
                "line_number": err_line,
                "detected_language": language,
            }

        # 3. Auto-generate suitable filename
        ext = ".py" if language == "python" else ".java"
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"snippet_{timestamp}{ext}"

        return {
            "success": True,
            "code": code,
            "filename": filename,
            "detected_language": language,
            "confidence": confidence,
            "detection_reason": reason,
            "line_count": len(code.splitlines()),
            "source_type": "pasted",
        }

    def handle_uploaded_file(self, file_storage: FileStorage) -> Dict[str, Any]:
        """Process uploaded Python (.py) or Java (.java) source file.

        Returns:
            Dictionary containing processing status, code content, and metadata.
        """
        if not file_storage or not file_storage.filename:
            return {
                "success": False,
                "error": "No file uploaded. Please select a valid .py or .java file.",
            }

        orig_filename = os.path.basename(file_storage.filename)
        _, ext = os.path.splitext(orig_filename.lower())

        if ext not in Config.ALLOWED_EXTENSIONS:
            return {
                "success": False,
                "error": (
                    f"Unsupported file extension '{ext}'. Only Python (.py) and "
                    "Java (.java) files are accepted by the analyzer."
                ),
            }

        # Read content and enforce size limits
        content_bytes = file_storage.read()
        if len(content_bytes) > self.max_size_bytes:
            return {
                "success": False,
                "error": f"File size exceeds maximum allowed limit of {self.max_size_bytes // (1024*1024)} MB.",
            }

        try:
            code = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                code = content_bytes.decode("latin-1")
            except Exception:
                return {
                    "success": False,
                    "error": "Could not decode file content. Please ensure file is valid UTF-8 text.",
                }

        code_clean = code.strip()
        if not code_clean:
            return {
                "success": False,
                "error": f"Uploaded file '{orig_filename}' is empty.",
            }

        # Detect language with filename authority
        try:
            language, confidence, reason = detect_language(code_clean, filename=orig_filename)
        except UnsupportedLanguageError as exc:
            return {"success": False, "error": str(exc)}

        # Syntax Validation
        is_valid_syntax, syntax_err, err_line = validate_syntax(code_clean, language)
        if not is_valid_syntax:
            return {
                "success": False,
                "error": f"Syntax Validation Error in '{orig_filename}': {syntax_err}",
                "line_number": err_line,
                "detected_language": language,
            }

        return {
            "success": True,
            "code": code_clean,
            "filename": orig_filename,
            "detected_language": language,
            "confidence": confidence,
            "detection_reason": reason,
            "line_count": len(code_clean.splitlines()),
            "source_type": "uploaded",
        }
