"""Steps 5-6 of the RAG pipeline: persistent ChromaDB vector store and indexing.

* The index lives on disk (``vector_store/``) and survives restarts.
* ``build_index`` is incremental: each document's SHA-256 hash is stored on its
  chunks, so unchanged documents are skipped and only new/changed documents are
  re-embedded. ``force=True`` rebuilds everything.
* Every chunk carries source metadata (file, title, section, source URLs).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Union

from config import settings
from knowledge_base.document_loader import Document
from knowledge_base.text_chunker import chunk_text
from knowledge_base.text_cleaner import clean_text

URL_SEPARATOR = "|"


class IndexNotBuiltError(RuntimeError):
    """Raised when searching before the index exists."""


@dataclass
class IndexStats:
    documents_total: int = 0
    documents_indexed: List[str] = field(default_factory=list)
    documents_skipped: List[str] = field(default_factory=list)
    documents_removed: List[str] = field(default_factory=list)
    chunks_added: int = 0
    chunks_total: int = 0
    backend_id: str = ""
    rebuilt_from_scratch: bool = False


def _chromadb():
    try:
        import chromadb
        from chromadb.config import Settings

        return chromadb, Settings
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("chromadb is not installed. Run: python -m pip install chromadb") from exc


class VectorStore:
    def __init__(self, persist_dir: Optional[Union[str, Path]] = None, collection_name: str = settings.COLLECTION_NAME):
        self.persist_dir = Path(persist_dir) if persist_dir else settings.VECTOR_STORE_DIR
        self.collection_name = collection_name
        chromadb, Settings = _chromadb()
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(self.persist_dir), settings=Settings(anonymized_telemetry=False))

    # ------------------------------------------------------------------ helpers
    def _existing(self):
        try:
            return self._client.get_collection(self.collection_name)
        except Exception:
            return None

    def _create(self, backend_id: str):
        return self._client.create_collection(
            self.collection_name, metadata={"hnsw:space": "cosine", "embedding_backend": backend_id}
        )

    def _drop(self) -> None:
        try:
            self._client.delete_collection(self.collection_name)
        except Exception:
            pass

    # ------------------------------------------------------------------ status
    def is_built(self) -> bool:
        collection = self._existing()
        return collection is not None and collection.count() > 0

    def count(self) -> int:
        collection = self._existing()
        return collection.count() if collection else 0

    def backend_id(self) -> Optional[str]:
        collection = self._existing()
        return (collection.metadata or {}).get("embedding_backend") if collection else None

    def indexed_documents(self) -> Dict[str, str]:
        """Return ``{document name: content hash}`` for everything in the index."""
        collection = self._existing()
        if not collection or collection.count() == 0:
            return {}
        metadatas = collection.get(include=["metadatas"])["metadatas"]
        return {m["source_file"]: m["content_hash"] for m in metadatas}

    def info(self) -> Dict[str, object]:
        docs = self.indexed_documents()
        return {"built": self.is_built(), "chunks": self.count(), "documents": sorted(docs), "backend": self.backend_id(),
                "path": str(self.persist_dir)}

    # ------------------------------------------------------------------ indexing
    def build_index(
        self,
        documents: Sequence[Document],
        embedder,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        force: bool = False,
        progress: Optional[Callable[[str], None]] = None,
    ) -> IndexStats:
        """Build or refresh the index. Only changed documents are re-embedded unless ``force``."""
        say = progress or (lambda _msg: None)
        stats = IndexStats(documents_total=len(documents), backend_id=embedder.backend_id)

        # Fail early: make sure the embedder works BEFORE touching an existing index,
        # so a failed model download can never destroy a working index.
        embedder.embed(["embedding self-test"])

        collection = self._existing()
        if collection is not None and (force or (collection.metadata or {}).get("embedding_backend") != embedder.backend_id):
            if not force:
                say("Embedding backend changed since the last build - rebuilding the whole index.")
            self._drop()
            collection = None
            stats.rebuilt_from_scratch = True
        if collection is None:
            collection = self._create(embedder.backend_id)
            stats.rebuilt_from_scratch = True

        indexed = self.indexed_documents()
        current_names = {d.name for d in documents}

        for removed in sorted(set(indexed) - current_names):
            collection.delete(where={"source_file": removed})
            stats.documents_removed.append(removed)
            say(f"Removed deleted document: {removed}")

        for doc in documents:
            if indexed.get(doc.name) == doc.content_hash:
                stats.documents_skipped.append(doc.name)
                continue
            if doc.name in indexed:  # changed -> drop old chunks first
                collection.delete(where={"source_file": doc.name})
            chunks = chunk_text(clean_text(doc.text), chunk_size, chunk_overlap)
            if not chunks:
                continue
            say(f"Embedding {doc.name} ({len(chunks)} chunks)...")
            texts = [c.text for c in chunks]
            # Prefix title/section so the embedding knows the chunk's context.
            embed_inputs = [f"{doc.title} - {c.section}\n{c.text}" if c.section else f"{doc.title}\n{c.text}" for c in chunks]
            vectors = embedder.embed(embed_inputs)
            collection.add(
                ids=[f"{doc.name}::{c.index}" for c in chunks],
                embeddings=vectors,
                documents=texts,
                metadatas=[
                    {
                        "source_file": doc.name,
                        "title": doc.title,
                        "section": c.section,
                        "chunk_index": c.index,
                        "source_urls": URL_SEPARATOR.join(doc.source_urls),
                        "content_hash": doc.content_hash,
                    }
                    for c in chunks
                ],
            )
            stats.documents_indexed.append(doc.name)
            stats.chunks_added += len(chunks)

        stats.chunks_total = collection.count()
        return stats

    # ------------------------------------------------------------------ querying
    def query(self, query_vector: List[float], top_k: int = settings.DEFAULT_TOP_K) -> List[dict]:
        collection = self._existing()
        if collection is None or collection.count() == 0:
            raise IndexNotBuiltError("The knowledge-base index has not been built yet.")
        result = collection.query(
            query_embeddings=[query_vector],
            n_results=max(1, min(top_k, collection.count())),
            include=["documents", "metadatas", "distances"],
        )
        rows = []
        for text, meta, dist in zip(result["documents"][0], result["metadatas"][0], result["distances"][0]):
            rows.append({"text": text, "metadata": meta, "distance": dist})
        return rows
