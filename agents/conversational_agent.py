"""Agent 5: Conversational Code Assistant Agent.

Provides an interactive RAG-powered assistant to explain findings,
remediations, and secure coding practices.
"""
from .code_assistant_agent import CodeAssistantAgent


class ConversationalAgent(CodeAssistantAgent):
    """Alias for Conversational Code Assistant."""
    pass


__all__ = ["ConversationalAgent", "CodeAssistantAgent"]
