"""Retriever service providing contextual retrieval and citations."""

from pathlib import Path
from typing import Dict, List, Any
from .document_loader import DocumentLoader
from .chunker import MarkdownChunker
from .vector_store import KnowledgeVectorStore


class KnowledgeRetriever:
    """Manages indexing, semantic query execution, and source citation."""

    def __init__(self, kb_dir: Path, chroma_dir: Path):
        self.kb_dir = Path(kb_dir).resolve()
        self.chroma_dir = Path(chroma_dir).resolve()
        self.loader = DocumentLoader(self.kb_dir)
        self.chunker = MarkdownChunker()
        self.vector_store = KnowledgeVectorStore(self.chroma_dir)

        # Automatically index if the store has 0 chunks
        if self.vector_store.get_stats()["total_chunks"] == 0:
            self.index_knowledge_base()

    def index_knowledge_base(self) -> int:
        """Load all KB markdown docs, chunk them, and add to vector store."""
        docs = self.loader.load_all_documents()
        all_chunks = []
        for doc in docs:
            chunks = self.chunker.chunk_document(doc)
            all_chunks.extend(chunks)

        count = self.vector_store.add_chunks(all_chunks)
        print(f"[KnowledgeRetriever] Successfully indexed {count} chunks across {len(docs)} documents.")
        return count

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve top_k matching chunks with citations."""
        return self.vector_store.query(query, top_k=top_k)

    def retrieve_for_finding(self, rule_id: str, title: str, cwe: str = "") -> List[Dict[str, Any]]:
        """Retrieve relevant knowledge guidance for a specific code finding."""
        search_terms = f"{rule_id} {title} {cwe}"
        return self.retrieve(search_terms, top_k=2)

    def format_citations(self, results: List[Dict[str, Any]]) -> str:
        """Format retrieval results as clean markdown citations."""
        if not results:
            return "No direct knowledge base citations retrieved."

        lines = ["### Knowledge Base Citations:"]
        for r in results:
            lines.append(f"- **{r.get('title', 'Guideline')}** (File: `{r.get('filename')}`, Score: {r.get('score')}):")
            # First 200 chars preview
            content_preview = r.get("content", "").strip()[:200].replace("\n", " ")
            lines.append(f"  > \"{content_preview}...\"")
        return "\n".join(lines)
