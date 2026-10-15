"""Step 4 of the RAG pipeline: turn text into embedding vectors.

Two interchangeable local backends (no API key, no network at query time):

``sentence-transformers`` (default)
    Semantic embeddings from a local model (``all-MiniLM-L6-v2``, ~90 MB).
    The model is downloaded once from Hugging Face and then cached.

``hashing``
    A tiny offline *lexical* embedder (hashed bag-of-words). It needs no
    download and is used by the automated tests and as an emergency fallback.
    It matches shared words only, so retrieval quality is lower.

The backend used to build an index is stored with the index, and the retriever
automatically uses the same backend for queries.
"""
from __future__ import annotations

import hashlib
import math
import re
from typing import List, Optional, Sequence

from config import settings

TROUBLESHOOTING = """\
Could not load the sentence-transformers embedding model.

Common causes and fixes:
1. First run needs internet to download the model (~90 MB). Check your connection / proxy / firewall.
2. The package may be missing: python -m pip install sentence-transformers
3. Corporate or college networks may block huggingface.co - ask IT to allow it, or download the model
   on another network; it is cached under %USERPROFILE%\\.cache\\huggingface .
4. Not enough disk space or a permissions error in the cache folder - free space or set HF_HOME to a writable folder.
5. As a temporary offline fallback you can build the index with the lexical backend:
       python -m knowledge_base.build_index --backend hashing --force
   (lower retrieval quality, but needs no download).
"""


class EmbeddingError(RuntimeError):
    """Raised when an embedding backend cannot be loaded or used."""


class HashingEmbedder:
    """Deterministic, dependency-free lexical embedder (signed feature hashing)."""

    backend = "hashing"
    _TOKEN = re.compile(r"[a-z0-9_]+")
    _STOP = {"the", "a", "an", "and", "or", "of", "to", "in", "is", "are", "for", "on", "with", "as", "by", "it", "that", "this"}

    def __init__(self, dimensions: int = settings.HASHING_DIMENSIONS):
        self.dimensions = dimensions
        self.model_name = f"hashing-{dimensions}"

    @property
    def backend_id(self) -> str:
        return self.model_name

    def _vector(self, text: str) -> List[float]:
        tokens = [t for t in self._TOKEN.findall(text.lower()) if t not in self._STOP]
        features = tokens + [f"{a}_{b}" for a, b in zip(tokens, tokens[1:])]
        vec = [0.0] * self.dimensions
        for feature in features:
            digest = hashlib.md5(feature.encode("utf-8")).digest()
            slot = int.from_bytes(digest[:4], "little") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vec[slot] += sign
        norm = math.sqrt(sum(v * v for v in vec))
        return [v / norm for v in vec] if norm else vec

    def embed(self, texts: Sequence[str]) -> List[List[float]]:
        return [self._vector(t) for t in texts]


class SentenceTransformerEmbedder:
    """Local semantic embeddings via the ``sentence-transformers`` library."""

    backend = "sentence-transformers"

    def __init__(self, model_name: str = settings.EMBEDDING_MODEL):
        self.model_name = model_name
        self._model = None

    @property
    def backend_id(self) -> str:
        return f"st:{self.model_name}"

    def _load(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self.model_name)
            except Exception as exc:  # import errors, download failures, OS errors...
                raise EmbeddingError(f"{type(exc).__name__}: {exc}\n\n{TROUBLESHOOTING}") from exc
        return self._model

    def embed(self, texts: Sequence[str]) -> List[List[float]]:
        model = self._load()
        vectors = model.encode(list(texts), batch_size=32, normalize_embeddings=True, show_progress_bar=False)
        return [list(map(float, v)) for v in vectors]


def get_embedder(backend: Optional[str] = None, model_name: Optional[str] = None):
    """Factory. ``backend`` is ``sentence-transformers`` or ``hashing``."""
    backend = (backend or settings.EMBEDDING_BACKEND).lower()
    if backend == "hashing":
        return HashingEmbedder()
    if backend in ("sentence-transformers", "sentence_transformers", "st"):
        return SentenceTransformerEmbedder(model_name or settings.EMBEDDING_MODEL)
    raise ValueError(f"Unknown embedding backend '{backend}'. Use 'sentence-transformers' or 'hashing'.")


def embedder_from_backend_id(backend_id: str):
    """Recreate the embedder that built an index from its stored ``backend_id``."""
    if backend_id.startswith("hashing"):
        try:
            return HashingEmbedder(int(backend_id.split("-")[1]))
        except (IndexError, ValueError):
            return HashingEmbedder()
    if backend_id.startswith("st:"):
        return SentenceTransformerEmbedder(backend_id[3:])
    raise ValueError(f"Unrecognised embedding backend id: {backend_id}")
