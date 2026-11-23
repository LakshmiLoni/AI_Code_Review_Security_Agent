"""Agent 5: Conversational Code Assistant Agent.

Provides an interactive RAG-powered conversational assistant to explain
detected vulnerabilities, code quality smells, remediation steps, and secure
Python/Java development practices.
Uses Google Gemini API (gemini-2.5-flash) when configured, and provides an
authoritative grounded fallback engine using the secure coding knowledge base
when the Gemini API key is absent or offline.
"""
import os
import re
from typing import List, Dict, Any, Optional
from config import Config
from rag.rag_pipeline import RAGPipeline


class CodeAssistantAgent:
    """Agent 5: RAG-grounded conversational code and security assistant."""

    def __init__(self, rag_pipeline: Optional[RAGPipeline] = None):
        self.agent_name = "Conversational Code Assistant"
        self.rag_pipeline = rag_pipeline or RAGPipeline()
        self.gemini_model = None
        self._initialize_gemini()

    def _initialize_gemini(self):
        """Initialize Google Gemini client if API key is configured."""
        api_key = Config.GEMINI_API_KEY.strip()
        if api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel(Config.GEMINI_MODEL)
            except Exception:
                self.gemini_model = None
        else:
            self.gemini_model = None

    @property
    def is_gemini_active(self) -> bool:
        return self.gemini_model is not None

    def ask(
        self,
        question: str,
        review_context: Optional[Dict[str, Any]] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Process user question using RAG and generate an authoritative grounded answer.

        Args:
            question: User inquiry string.
            review_context: Optional active review metadata and findings list.
            chat_history: Optional list of previous chat turns [{"role": "user"|"assistant", "message": "..."}].

        Returns:
            Dictionary containing:
            - answer: str (Markdown formatted response)
            - citations: List[dict] (source documents used)
            - model_used: str ("gemini-2.5-flash" or "RAG Knowledge-Base Fallback")
        """
        clean_question = question.strip()
        if not clean_question:
            return {
                "answer": "Please ask a question about the code review findings or secure coding guidelines.",
                "citations": [],
                "model_used": "System",
            }

        # 1. Retrieve grounded documentation chunks from vector store
        retrieved_chunks = self.rag_pipeline.retrieve_context(clean_question, top_k=Config.TOP_K_RETRIEVAL)
        context_text = self.rag_pipeline.get_formatted_context(clean_question, top_k=Config.TOP_K_RETRIEVAL)

        # 2. Extract review findings summary if context provided
        review_summary_text = ""
        if review_context:
            filename = review_context.get("filename", "uploaded_file")
            lang = review_context.get("detected_language", "code")
            findings = review_context.get("findings", [])
            findings_desc = []
            for f in findings[:6]:
                findings_desc.append(
                    f"- [{f.get('severity')}] Line {f.get('line_number')}: {f.get('title')} ({f.get('category')})"
                )
            review_summary_text = (
                f"\nCURRENT ACTIVE CODE REVIEW ({filename}, {lang}):\n"
                f"Health Score: {review_context.get('health_score')}/100\n"
                f"Total Findings: {len(findings)}\n"
                + "\n".join(findings_desc)
                + "\n"
            )

        # 3. Format citations list
        citations = []
        for c in retrieved_chunks:
            citations.append({
                "title": c.get("title"),
                "section": c.get("section"),
                "source_file": c.get("source_file"),
                "relevance_score": c.get("score"),
            })

        # 4. Attempt Gemini generation if active
        if self.is_gemini_active:
            try:
                gemini_answer = self._generate_gemini_answer(
                    question=clean_question,
                    context=context_text,
                    review_summary=review_summary_text,
                    chat_history=chat_history or [],
                )
                return {
                    "answer": gemini_answer,
                    "citations": citations,
                    "model_used": Config.GEMINI_MODEL,
                }
            except Exception:
                # If Gemini API call fails (rate limit, offline, quota), use robust fallback
                pass

        # 5. Rule-Based RAG Fallback Engine
        fallback_answer = self._generate_fallback_answer(
            question=clean_question,
            retrieved_chunks=retrieved_chunks,
            review_context=review_context,
        )

        return {
            "answer": fallback_answer,
            "citations": citations,
            "model_used": "RAG Knowledge-Base Rule Engine (Offline/Fallback Mode)",
        }

    def _generate_gemini_answer(
        self,
        question: str,
        context: str,
        review_summary: str,
        chat_history: List[Dict[str, str]],
    ) -> str:
        """Call Gemini API with grounded context prompt."""
        system_instructions = (
            "You are an expert AI Application Security Engineer and Senior Code Review Assistant. "
            "Your job is to answer the user's question with precise, professional, and actionable advice. "
            "IMPORTANT RULES:\n"
            "1. Ground your answers strictly on the provided Secure Coding Knowledge Base documents and review findings.\n"
            "2. Provide clear vulnerable vs secure code examples in Python or Java where relevant.\n"
            "3. Do not invent security rules or make claims not supported by established standards (OWASP, CWE, NIST).\n"
            "4. Be concise, direct, and structured with Markdown headers and bullet points.\n"
        )

        history_str = ""
        if chat_history:
            recent_turns = chat_history[-4:]
            for turn in recent_turns:
                history_str += f"{turn.get('role', 'user').upper()}: {turn.get('message')}\n"

        full_prompt = (
            f"{system_instructions}\n\n"
            f"=== RETRIEVED SECURE CODING KNOWLEDGE BASE CONTEXT ===\n"
            f"{context}\n\n"
            f"{review_summary}\n"
            f"=== CONVERSATION HISTORY ===\n"
            f"{history_str}\n"
            f"USER QUESTION: {question}\n\n"
            f"ASSISTANT ANSWER:"
        )

        response = self.gemini_model.generate_content(full_prompt)
        return response.text.strip()

    def _generate_fallback_answer(
        self,
        question: str,
        retrieved_chunks: List[Dict[str, Any]],
        review_context: Optional[Dict[str, Any]],
    ) -> str:
        """Generate high-quality grounded answer from retrieved chunks without external API."""
        q_lower = question.lower()

        # Check if question is asking about specific finding in current review
        if review_context and ("this finding" in q_lower or "explain" in q_lower or "vulnerability" in q_lower):
            findings = review_context.get("findings", [])
            if findings:
                top_finding = findings[0]
                return (
                    f"### Analysis of Finding: {top_finding.get('title')}\n\n"
                    f"**Severity:** `{top_finding.get('severity')}` (CVSS Heuristic: `{top_finding.get('heuristic_score')}`)\n\n"
                    f"**Category:** {top_finding.get('category')}\n\n"
                    f"**Problem Explanation:**\n{top_finding.get('description')}\n\n"
                    f"**Identified Evidence at Line {top_finding.get('line_number')}:**\n"
                    f"```\n{top_finding.get('evidence_snippet')}\n```\n\n"
                    f"**Remediation Recommendation:**\n{top_finding.get('remediation_recommendation')}\n\n"
                    f"**Secure Refactored Code:**\n"
                    f"```\n{top_finding.get('corrected_code')}\n```\n\n"
                    f"> *Source Reference: Knowledge base standards retrieved for {top_finding.get('category')}.*"
                )

        if not retrieved_chunks:
            return (
                "I searched the secure coding knowledge base, but could not find a direct section matching "
                f"your query: *\"{question}\"*. Please try rephrasing with specific topics like 'SQL injection', "
                "'XSS', 'CSRF', 'cryptography', 'input validation', or 'code complexity'."
            )

        # Synthesize top 2 retrieved chunks into a clean, well-formatted grounded response
        top_chunk = retrieved_chunks[0]
        text_content = top_chunk.get("text", "")

        response_parts = [
            f"### Guidance: {top_chunk.get('title')} ({top_chunk.get('section')})\n",
            f"*Retrieved from Knowledge Base: `{top_chunk.get('source_file')}` (Relevance: {top_chunk.get('score')})*\n",
            text_content,
        ]

        if len(retrieved_chunks) > 1:
            second_chunk = retrieved_chunks[1]
            response_parts.append(
                f"\n\n---\n#### Additional Related Guidance: {second_chunk.get('title')} § {second_chunk.get('section')}\n"
                f"{second_chunk.get('text')[:400]}..."
            )

        return "\n".join(response_parts)
