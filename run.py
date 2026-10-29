"""Main entrypoint for AI Code Review & Security Analysis Agent."""

import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from app import create_app
from app.config import Config

app = create_app(Config)

if __name__ == "__main__":
    host = os.environ.get("FLASK_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1")

    print(f"[*] Starting AI Code Review & Security Analysis Agent on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
