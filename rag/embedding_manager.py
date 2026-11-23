"""Embedding Manager for Vector Representation.

Generates dense vector embeddings using Sentence Transformers (all-MiniLM-L6-v2)
when available, with a deterministic term-frequency fallback vectorizer when offline
or when native dependencies are constrained.
"""
import binascii
import math
import re
from typing import List


class EmbeddingManager:
    """Manages embedding generation for documents and search queries."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", dimension: int = 384):
        self.model_name = model_name
        self.dimension = dimension
        self._st_model = None
        self._use_sentence_transformers = False

        self._initialize_model()

    def _initialize_model(self):
        """Attempt to load SentenceTransformer; fallback to local vectorizer if unavailable."""
        try:
            from sentence_transformers import SentenceTransformer
            # Use local_files_only to prevent network hang in offline environments
            self._st_model = SentenceTransformer(self.model_name, local_files_only=True)
            self._use_sentence_transformers = True
        except Exception:
            self._st_model = None
            self._use_sentence_transformers = False

    @property
    def is_using_sentence_transformers(self) -> bool:
        return self._use_sentence_transformers

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate normalized embedding vectors for a list of text strings."""
        if not texts:
            return []

        if self._use_sentence_transformers and self._st_model:
            try:
                embeddings = self._st_model.encode(texts, normalize_embeddings=True)
                return [emb.tolist() for emb in embeddings]
            except Exception:
                pass

        # Fallback deterministic normalized vectorizer
        return [self._fallback_embed(t) for t in texts]

    def embed_query(self, query: str) -> List[float]:
        """Generate normalized embedding vector for a single query."""
        results = self.embed_texts([query])
        return results[0] if results else [0.0] * self.dimension

    def _fallback_embed(self, text: str) -> List[float]:
        """Generate a reproducible, L2-normalized 384-dimensional dense vector.

        Uses deterministic CRC32 hashing to guarantee identical vectors
        across separate Python processes and application restarts.
        """
        vec = [0.0] * self.dimension
        words = re.findall(r"\b[a-zA-Z0-9_-]{2,}\b", text.lower())

        if not words:
            vec[0] = 1.0
            return vec

        # High-value security vocabulary gets boosted weight in fallback mode
        boosted_terms = {
            "sql": 3.0, "injection": 3.0, "xss": 3.0, "csrf": 3.0,
            "parameterized": 2.5, "command": 2.5, "pickle": 2.5,
            "deserialization": 2.5, "traversal": 2.5, "secret": 2.0,
            "cryptography": 2.0, "md5": 2.0, "sha1": 2.0, "ecb": 2.0,
            "auth": 2.0, "authentication": 2.0, "authorization": 2.0,
        }

        for word in words:
            # Deterministic CRC32 integer hash across all processes
            crc = binascii.crc32(word.encode("utf-8"))
            idx1 = crc % self.dimension
            idx2 = (crc >> 8) % self.dimension
            weight = boosted_terms.get(word, 1.0)
            sign = 1.0 if ((crc & 1) == 0) else -1.0

            vec[idx1] += 1.0 * weight * sign
            vec[idx2] += 0.5 * weight * sign

        # L2 Normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0.0:
            vec = [x / norm for x in vec]
        else:
            vec[0] = 1.0

        return vec
