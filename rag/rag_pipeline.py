"""RAG Pipeline Orchestrator.

Manages indexing of knowledge base documents and context retrieval
for both the multi-agent review pipeline and the conversational code assistant.
"""
import os
import time
from typing import List, Dict, Any, Optional
from config import Config
from .document_loader import DocumentLoader
from .text_splitter import MarkdownTextSplitter
from .embedding_manager import EmbeddingManager
from .vector_store import VectorStore
from .retriever import KnowledgeRetriever


class RAGPipeline:
    """End-to-end RAG indexing and retrieval pipeline."""

    def __init__(
        self,
        kb_dir: Optional[str] = None,
        persist_dir: Optional[str] = None,
    ):
        self.kb_dir = kb_dir or Config.KNOWLEDGE_BASE_DIR
        self.persist_dir = persist_dir or Config.CHROMA_DIR

        self.document_loader = DocumentLoader(self.kb_dir)
        self.text_splitter = MarkdownTextSplitter(chunk_size=800, chunk_overlap=120)
        self.embedding_manager = EmbeddingManager(Config.EMBEDDING_MODEL_NAME)
        self.vector_store = VectorStore(self.persist_dir)
        self.retriever = KnowledgeRetriever(self.vector_store, self.embedding_manager)

    def build_index(self, force: bool = False) -> Dict[str, Any]:
        """Build or refresh vector store index from markdown documents.

        Args:
            force: If True, re-indexes even if vector store already has records.

        Returns:
            Dictionary of indexing statistics.
        """
        start_time = time.time()
        existing_count = self.vector_store.count()

        if existing_count > 0 and not force:
            return {
                "status": "already_indexed",
                "indexed_chunks": existing_count,
                "message": f"Knowledge base already indexed with {existing_count} chunks. Pass force=True to rebuild.",
                "duration_seconds": round(time.time() - start_time, 2),
            }

        # 1. Load documents
        documents = self.document_loader.load_documents()

        # 2. Split into chunks
        chunks = self.text_splitter.split_documents(documents)

        # 3. Extract text payloads
        chunk_ids = [c["chunk_id"] for c in chunks]
        texts = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        # 4. Generate embeddings
        embeddings = self.embedding_manager.embed_texts(texts)

        # 5. Store in vector store
        self.vector_store.add_documents(
            chunk_ids=chunk_ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

        duration = round(time.time() - start_time, 2)
        return {
            "status": "success",
            "documents_loaded": len(documents),
            "chunks_created": len(chunks),
            "embeddings_generated": len(embeddings),
            "total_indexed_chunks": self.vector_store.count(),
            "using_chromadb": self.vector_store.is_chromadb_active,
            "using_sentence_transformers": self.embedding_manager.is_using_sentence_transformers,
            "duration_seconds": duration,
        }

    def retrieve_context(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Retrieve structured citations for a query."""
        # Auto-index on first query if store is empty
        if self.vector_store.is_empty():
            self.build_index()
        return self.retriever.retrieve(query, top_k=top_k)

    def get_formatted_context(self, query: str, top_k: int = 4) -> str:
        """Retrieve textual context string for LLM injection."""
        if self.vector_store.is_empty():
            self.build_index()
        return self.retriever.get_context_string(query, top_k=top_k)
