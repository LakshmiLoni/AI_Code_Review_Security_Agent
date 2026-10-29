"""Knowledge Base Service providing integration between RAG and the web app."""

from pathlib import Path
from typing import Dict, List, Any
from ..rag.retriever import KnowledgeRetriever
from ..rag.document_loader import DocumentLoader


class KnowledgeService:
    """High-level service for knowledge base querying and verification."""

    def __init__(self, kb_dir: Path, chroma_dir: Path):
        self.kb_dir = Path(kb_dir).resolve()
        self.chroma_dir = Path(chroma_dir).resolve()
        self.retriever = KnowledgeRetriever(kb_dir=self.kb_dir, chroma_dir=self.chroma_dir)
        self.loader = DocumentLoader(self.kb_dir)

    def get_line_count(self) -> int:
        """Count actual nonblank lines in the main knowledge base file."""
        kb_file = self.kb_dir / "secure_coding_knowledge_base.md"
        if not kb_file.is_file():
            return 0
        with open(kb_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        return len(lines)

    def get_stats(self) -> Dict[str, Any]:
        """Aggregate knowledge base statistics for dashboard display."""
        store_stats = self.retriever.vector_store.get_stats()
        manifest = self.loader.load_manifest()

        return {
            "nonblank_line_count": self.get_line_count(),
            "minimum_required_lines": 1200,
            "meets_requirement": self.get_line_count() >= 1200,
            "backend": store_stats.get("backend", "Local TF-IDF"),
            "total_chunks": store_stats.get("total_chunks", 0),
            "topics_count": len(manifest.get("topics", [])),
            "topics": manifest.get("topics", [])
        }

    def query(self, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        return self.retriever.retrieve(query_text, top_k=top_k)

    def rebuild_index(self) -> int:
        return self.retriever.index_knowledge_base()
