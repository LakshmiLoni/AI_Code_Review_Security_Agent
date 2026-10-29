"""Conversational Code Assistant Agent."""

from typing import Dict, Any, Optional
from ..services.llm_service import LLMService
from ..services.knowledge_service import KnowledgeService


class AssistantAgent:
    """Conversational agent for answering student questions about code security."""

    def __init__(self, llm_service: LLMService, knowledge_service: KnowledgeService):
        self.llm = llm_service
        self.kb = knowledge_service

    def answer_question(
        self,
        question: str,
        review_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Answer a student question using retrieved KB context and Gemini / local synthesis."""
        # Retrieve relevant chunks from knowledge base
        chunks = self.kb.query(question, top_k=3)

        # Generate response
        result = self.llm.generate_chat_response(
            user_message=question,
            retrieved_context=chunks,
            review_context=review_context
        )

        return result
