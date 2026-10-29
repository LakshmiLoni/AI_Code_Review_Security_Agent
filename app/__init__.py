"""Flask Application Factory."""

from flask import Flask, render_template
from pathlib import Path
from .config import Config
from .extensions import init_extensions


def create_app(config_class=Config) -> Flask:
    """Create, configure, and return the Flask application instance."""
    app = Flask(
        __name__,
        template_folder=str(config_class.BASE_DIR / "templates"),
        static_folder=str(config_class.BASE_DIR / "static")
    )

    app.config.from_object(config_class)
    app.config["APP_CONFIG_OBJECT"] = config_class

    # Initialize extensions and multi-agent services
    init_extensions(app)

    # Register Blueprints
    from .routes.main_routes import main_bp
    from .routes.review_routes import review_bp
    from .routes.report_routes import report_bp
    from .routes.assistant_routes import assistant_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(review_bp, url_prefix="/reviews")
    app.register_blueprint(report_bp, url_prefix="/reports")
    app.register_blueprint(assistant_bp, url_prefix="/assistant")

    # Error Handlers
    @app.errorhandler(400)
    def bad_request_error(e):
        return render_template("error.html", error_code=400, message=str(e)), 400

    @app.errorhandler(404)
    def not_found_error(e):
        return render_template("error.html", error_code=404, message="The requested page or review could not be found."), 404

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return render_template("error.html", error_code=413, message="The uploaded file exceeds the 2MB size limit."), 413

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("error.html", error_code=500, message="An internal server error occurred."), 500

    return app
