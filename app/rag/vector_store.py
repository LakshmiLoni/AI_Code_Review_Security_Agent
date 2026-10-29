"""Vector Store for Security Knowledge Base.

Supports ChromaDB when available, and provides a lightweight, local
scikit-learn TF-IDF + Cosine Similarity vector store fallback with zero
external API dependencies.
"""

import os
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class KnowledgeVectorStore:
    """Hybrid Vector Store with ChromaDB adapter and TF-IDF fallback."""

    def __init__(self, storage_dir: Path):
        self.storage_dir = Path(storage_dir).resolve()
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.use_chroma = CHROMADB_AVAILABLE
        self.chroma_client = None
        self.chroma_collection = None

        # Fallback in-memory / serialized attributes
        self.chunks: List[Dict[str, Any]] = []
        self.tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self.fallback_file = self.storage_dir / "tfidf_index.pkl"

        self._init_backend()

    def _init_backend(self):
        if self.use_chroma:
            try:
                self.chroma_client = chromadb.PersistentClient(path=str(self.storage_dir))
                self.chroma_collection = self.chroma_client.get_or_create_collection(
                    name="secure_coding_kb",
                    metadata={"description": "Secure coding and security guidelines"}
                )
                print("[VectorStore] Initialized ChromaDB persistent backend.")
                return
            except Exception as e:
                print(f"[VectorStore] ChromaDB initialization failed: {e}. Falling back to TF-IDF.")
                self.use_chroma = False

        # Fallback initialization
        self._load_fallback_index()

    def _load_fallback_index(self):
        if self.fallback_file.is_file():
            try:
                with open(self.fallback_file, "rb") as f:
                    data = pickle.load(f)
                    self.chunks = data.get("chunks", [])
                    self.tfidf_vectorizer = data.get("vectorizer")
                    self.tfidf_matrix = data.get("matrix")
                print(f"[VectorStore] Loaded {len(self.chunks)} chunks from local TF-IDF cache.")
            except Exception as e:
                print(f"[VectorStore] Failed loading local TF-IDF cache: {e}")

    def _save_fallback_index(self):
        try:
            with open(self.fallback_file, "wb") as f:
                pickle.dump({
                    "chunks": self.chunks,
                    "vectorizer": self.tfidf_vectorizer,
                    "matrix": self.tfidf_matrix
                }, f)
            print(f"[VectorStore] Saved {len(self.chunks)} chunks to local TF-IDF cache.")
        except Exception as e:
            print(f"[VectorStore] Error saving TF-IDF cache: {e}")

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        if not chunks:
            return 0

        if self.use_chroma and self.chroma_collection:
            ids = [c["chunk_id"] for c in chunks]
            documents = [c["content"] for c in chunks]
            metadatas = [{
                "filename": c.get("filename", ""),
                "section": c.get("section", ""),
                "title": c.get("title", ""),
                "word_count": c.get("word_count", 0)
            } for c in chunks]

            self.chroma_collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            return len(chunks)

        # Fallback with scikit-learn TF-IDF
        self.chunks = chunks
        if SKLEARN_AVAILABLE:
            docs = [c["content"] for c in self.chunks]
            self.tfidf_vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2),
                max_features=5000
            )
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(docs)
            self._save_fallback_index()
        return len(chunks)

    def query(self, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve the top_k most relevant chunks for query_text."""
        if not query_text or not query_text.strip():
            return []

        if self.use_chroma and self.chroma_collection:
            try:
                results = self.chroma_collection.query(
                    query_texts=[query_text],
                    n_results=top_k
                )
                output = []
                if results and "documents" in results and results["documents"]:
                    docs = results["documents"][0]
                    metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
                    ids = results["ids"][0] if "ids" in results else [""] * len(docs)
                    distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)

                    for doc, meta, cid, dist in zip(docs, metas, ids, distances):
                        # Approximate similarity from distance
                        score = max(0.0, 1.0 - (dist if dist is not None else 0.5))
                        output.append({
                            "chunk_id": cid,
                            "content": doc,
                            "title": meta.get("title", "KB Document"),
                            "filename": meta.get("filename", ""),
                            "section": meta.get("section", ""),
                            "score": round(score, 3)
                        })
                return output
            except Exception as e:
                print(f"[VectorStore] Chroma query failed: {e}. Falling back to TF-IDF.")

        # Fallback using TF-IDF and Cosine Similarity
        if SKLEARN_AVAILABLE and self.tfidf_vectorizer and self.tfidf_matrix is not None and self.chunks:
            query_vec = self.tfidf_vectorizer.transform([query_text])
            sims = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

            top_indices = sims.argsort()[::-1][:top_k]
            output = []
            for idx in top_indices:
                score = float(sims[idx])
                if score > 0.01:  # Filter out totally irrelevant zeros
                    chunk = self.chunks[idx]
                    output.append({
                        "chunk_id": chunk["chunk_id"],
                        "content": chunk["content"],
                        "title": chunk.get("title", "KB Document"),
                        "filename": chunk.get("filename", ""),
                        "section": chunk.get("section", ""),
                        "score": round(score, 3)
                    })
            if output:
                return output

        # Keyword match fallback if vectorization yielded no matches
        return self._keyword_fallback(query_text, top_k)

    def _keyword_fallback(self, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        tokens = set(query_text.lower().split())
        scored = []
        for c in self.chunks:
            content_lower = c["content"].lower()
            matches = sum(1 for t in tokens if t in content_lower)
            if matches > 0:
                scored.append((matches, c))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for count, c in scored[:top_k]:
            results.append({
                "chunk_id": c["chunk_id"],
                "content": c["content"],
                "title": c.get("title", "KB Document"),
                "filename": c.get("filename", ""),
                "section": c.get("section", ""),
                "score": round(min(1.0, count / max(1, len(tokens))), 3)
            })
        return results

    def get_stats(self) -> Dict[str, Any]:
        return {
            "backend": "ChromaDB" if (self.use_chroma and self.chroma_collection) else "Local TF-IDF Vectorizer",
            "chroma_available": CHROMADB_AVAILABLE,
            "sklearn_available": SKLEARN_AVAILABLE,
            "total_chunks": len(self.chunks) if not (self.use_chroma and self.chroma_collection) else (
                self.chroma_collection.count() if self.chroma_collection else 0
            ),
            "storage_path": str(self.storage_dir)
        }
