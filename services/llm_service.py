"""Services: LLM Service.

Handles Gemini AI client interactions, prompt formatting, context injection,
and seamless fallback to deterministic rule engines when Gemini is unconfigured or offline.
"""
import os
import logging
from typing import Dict, Any, Optional, List
from config import Config

logger = logging.getLogger(__name__)


class LLMService:
    """Manages LLM inference and fallback behavior."""

    def __init__(self):
        self.model = None
        self._initialize()

    def _initialize(self):
        """Attempt to configure Google Gemini GenerativeModel."""
        api_key = Config.GEMINI_API_KEY.strip()
        if api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
                logger.info("Gemini LLM service initialized successfully with %s", Config.GEMINI_MODEL)
            except Exception as exc:
                logger.warning("Failed to initialize Gemini model: %s", exc)
                self.model = None
        else:
            self.model = None

    @property
    def is_available(self) -> bool:
        """Return True if live Gemini API is configured and accessible."""
        return self.model is not None

    def generate_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> Optional[str]:
        """Send prompt to Gemini model if available; return None if unavailable."""
        if not self.is_available:
            return None

        try:
            full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
            response = self.model.generate_content(full_prompt)
            if response and hasattr(response, "text") and response.text:
                return response.text.strip()
        except Exception as exc:
            logger.warning("Gemini API call failed: %s", exc)
        return None
