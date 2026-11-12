"""Knowledge Retriever for RAG Pipeline.

Retrieves top-k relevant document chunks for queries, formats citations,
and applies score thresholds.
"""
from typing import List, Dict, Any, Optional
from .embedding_manager import EmbeddingManager
from .vector_store import VectorStore


class KnowledgeRetriever:
    """Retrieves grounded context documents for code review questions and findings."""

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embedding_manager: Optional[EmbeddingManager] = None,
        min_relevance_threshold: float = 0.05,
    ):
        self.vector_store = vector_store or VectorStore()
        self.embedding_manager = embedding_manager or EmbeddingManager()
        self.min_relevance_threshold = min_relevance_threshold

    def retrieve(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Retrieve most relevant knowledge base chunks for a given query.

        Returns:
            List of dictionaries:
            - chunk_id: str
            - title: str
            - section: str
            - source_file: str
            - score: float (relevance similarity)
            - text: str (document content)
        """
        if not query or not query.strip():
            return []

        query_emb = self.embedding_manager.embed_query(query.strip())
        raw_results = self.vector_store.query(query_emb, top_k=top_k)

        formatted = []
        for res in raw_results:
            score = res.get("score", 0.0)
            if score < self.min_relevance_threshold:
                continue

            meta = res.get("metadata", {})
            formatted.append({
                "chunk_id": res["id"],
                "title": meta.get("title", meta.get("source", "Knowledge Base")),
                "section": meta.get("section", "General Guidance"),
                "source_file": meta.get("source", "knowledge_base"),
                "score": score,
                "text": res.get("document", ""),
            })

        return formatted

    def get_context_string(self, query: str, top_k: int = 4) -> str:
        """Format retrieved chunks into a clean context prompt block."""
        results = self.retrieve(query, top_k=top_k)
        if not results:
            return "No specific secure coding documentation found for this query."

        context_blocks = []
        for idx, doc in enumerate(results, start=1):
            block = (
                f"--- DOCUMENT {idx}: {doc['title']} ({doc['source_file']} § {doc['section']}) ---\n"
                f"{doc['text']}\n"
            )
            context_blocks.append(block)

        return "\n".join(context_blocks)
