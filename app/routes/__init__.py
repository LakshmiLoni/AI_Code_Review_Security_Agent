"""Blueprint route modules."""
from .main_routes import main_bp
from .review_routes import review_bp
from .report_routes import report_bp
from .assistant_routes import assistant_bp

__all__ = ["main_bp", "review_bp", "report_bp", "assistant_bp"]
