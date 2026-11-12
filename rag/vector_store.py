"""Vector Store Implementation.

Provides ChromaDB persistent storage support, with an integrated persistent
JSON vector store fallback for environments where native C++ libraries or
DLLs (e.g., cygrpc / SQLite extensions) are constrained.
"""
import os
import json
import math
from typing import List, Dict, Any, Optional
from config import Config


class VectorStore:
    """Manages persistent vector indexing and similarity retrieval."""

    def __init__(self, persist_dir: str = None, collection_name: str = None):
        self.persist_dir = persist_dir or Config.CHROMA_DIR
        self.collection_name = collection_name or Config.CHROMA_COLLECTION_NAME
        os.makedirs(self.persist_dir, exist_ok=True)

        self._chroma_client = None
        self._collection = None
        self._is_chromadb_active = False

        # Fallback local index state
        self._fallback_index_path = os.path.join(self.persist_dir, "vector_index.json")
        self._local_records: List[Dict[str, Any]] = []

        self._initialize_store()

    def _initialize_store(self):
        """Attempt to initialize ChromaDB; fallback to local persistent index if blocked."""
        try:
            import chromadb
            from chromadb.config import Settings
            self._chroma_client = chromadb.PersistentClient(
                path=self.persist_dir,
                settings=Settings(anonymized_telemetry=False)
            )
            self._collection = self._chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "AI Code Review Secure Coding Knowledge Base"}
            )
            self._is_chromadb_active = True
        except Exception:
            self._chroma_client = None
            self._collection = None
            self._is_chromadb_active = False
            self._load_local_records()

    def _load_local_records(self):
        """Load persistent records from local JSON index file."""
        if os.path.exists(self._fallback_index_path):
            try:
                with open(self._fallback_index_path, "r", encoding="utf-8") as f:
                    self._local_records = json.load(f)
            except Exception:
                self._local_records = []
        else:
            self._local_records = []

    def _save_local_records(self):
        """Persist local records to JSON index file."""
        with open(self._fallback_index_path, "w", encoding="utf-8") as f:
            json.dump(self._local_records, f, indent=2)

    @property
    def is_chromadb_active(self) -> bool:
        return self._is_chromadb_active

    def count(self) -> int:
        """Return the number of indexed document chunks."""
        if self._is_chromadb_active and self._collection:
            try:
                return self._collection.count()
            except Exception:
                pass
        return len(self._local_records)

    def is_empty(self) -> bool:
        """Check whether the vector store has any indexed records."""
        return self.count() == 0

    def add_documents(
        self,
        chunk_ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
    ):
        """Add document chunks and their embeddings to the store."""
        if not chunk_ids:
            return

        if self._is_chromadb_active and self._collection:
            try:
                # Sanitize metadata for ChromaDB (flat strings/numbers only)
                clean_metas = []
                for m in metadatas:
                    clean_m = {
                        k: str(v) if isinstance(v, (dict, list)) else v
                        for k, v in m.items()
                    }
                    clean_metas.append(clean_m)

                self._collection.upsert(
                    ids=chunk_ids,
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=clean_metas,
                )
                return
            except Exception:
                # If ChromaDB encounters an error, fallback to local index
                self._is_chromadb_active = False

        # Local index persistence
        existing_ids = {r["id"] for r in self._local_records}
        for cid, emb, doc, meta in zip(chunk_ids, embeddings, documents, metadatas):
            record = {
                "id": cid,
                "embedding": emb,
                "document": doc,
                "metadata": meta,
            }
            if cid in existing_ids:
                # Update existing
                for i, r in enumerate(self._local_records):
                    if r["id"] == cid:
                        self._local_records[i] = record
                        break
            else:
                self._local_records.append(record)
                existing_ids.add(cid)

        self._save_local_records()

    def query(
        self,
        query_embedding: List[float],
        top_k: int = 4,
    ) -> List[Dict[str, Any]]:
        """Query the vector store for the top-k most similar document chunks.

        Returns:
            List of dicts: {"id", "document", "metadata", "score"}
        """
        if self._is_chromadb_active and self._collection:
            try:
                res = self._collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                )
                results = []
                if res and "ids" in res and res["ids"]:
                    ids = res["ids"][0]
                    docs = res.get("documents", [[]])[0]
                    metas = res.get("metadatas", [[]])[0]
                    distances = res.get("distances", [[]])[0] if "distances" in res else [0.5] * len(ids)

                    for i in range(len(ids)):
                        # Convert distance to similarity score
                        dist = distances[i] if i < len(distances) else 0.5
                        sim = max(0.0, 1.0 - (dist / 2.0))
                        results.append({
                            "id": ids[i],
                            "document": docs[i] if i < len(docs) else "",
                            "metadata": metas[i] if i < len(metas) else {},
                            "score": round(sim, 3),
                        })
                return results
            except Exception:
                pass

        # Local cosine similarity retrieval
        if not self._local_records:
            self._load_local_records()

        scored = []
        for record in self._local_records:
            emb = record.get("embedding", [])
            sim = self._cosine_similarity(query_embedding, emb)
            scored.append({
                "id": record["id"],
                "document": record["document"],
                "metadata": record["metadata"],
                "score": round(sim, 3),
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Compute cosine similarity between two normalized or unnormalized vectors."""
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0

        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a, b in zip(v1, v2)))
        norm2 = math.sqrt(sum(b * b for a, b in zip(v1, v2)))

        if norm1 <= 0.0 or norm2 <= 0.0:
            return 0.0
        return dot / (norm1 * norm2)
