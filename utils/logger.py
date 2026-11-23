"""Utils: Application Logger.

Configures application logging with clean formatting safe for all platforms.
"""
import logging
import sys


def get_logger(name: str = "ai_code_review") -> logging.Logger:
    """Retrieve configured logger instance."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
