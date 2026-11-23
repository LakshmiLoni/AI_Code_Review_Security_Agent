"""Analysis package."""
from .language_detector import detect_language, UnsupportedLanguageError, SUPPORTED_EXTENSIONS
from .syntax_validator import validate_syntax, validate_python_syntax, validate_java_syntax
from .python_analyzer import PythonAnalyzer
from .java_analyzer import JavaAnalyzer
from .vulnerability_rules import (
    OWASP_CATEGORIES,
    COMMON_SECRET_PATTERNS,
    PYTHON_SECURITY_PATTERNS,
    JAVA_SECURITY_PATTERNS
)
from .code_quality import (
    calculate_finding_score,
    get_severity_label,
    calculate_code_health_score,
    SEVERITY_RANGES,
    SEVERITY_PENALTIES
)

__all__ = [
    "detect_language",
    "UnsupportedLanguageError",
    "SUPPORTED_EXTENSIONS",
    "validate_syntax",
    "validate_python_syntax",
    "validate_java_syntax",
    "PythonAnalyzer",
    "JavaAnalyzer",
    "OWASP_CATEGORIES",
    "COMMON_SECRET_PATTERNS",
    "PYTHON_SECURITY_PATTERNS",
    "JAVA_SECURITY_PATTERNS",
    "calculate_finding_score",
    "get_severity_label",
    "calculate_code_health_score",
    "SEVERITY_RANGES",
    "SEVERITY_PENALTIES",
]
