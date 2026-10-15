
"""Retrieve relevant knowledge-base chunks using hybrid ranking."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Union

from config import settings
from knowledge_base.embedding_service import embedder_from_backend_id
from knowledge_base.vector_store import (
    URL_SEPARATOR,
    IndexNotBuiltError,
    VectorStore,
)


@dataclass
class RetrievedChunk:
    text: str
    source_file: str
    title: str
    section: str
    source_urls: List[str] = field(default_factory=list)
    score: float = 0.0
    chunk_index: int = 0


class Retriever:
    """Search the persistent index and rerank results using keywords."""

    STOPWORDS = {
        "a", "an", "and", "are", "as", "at", "be", "by",
        "do", "for", "from", "how", "i", "in", "is", "it",
        "of", "on", "or", "should", "the", "to", "what",
        "when", "where", "which", "with",
    }

    WORD_NORMALIZATION = {
        "passwords": "password",
        "keys": "key",
        "secrets": "secret",
        "credentials": "credential",
        "stored": "store",
        "storing": "store",
        "securely": "secure",
        "variables": "variable",
        "environment": "environment",
        "prevent": "prevention",
        "preventing": "prevention",
    }

    def __init__(
        self,
        persist_dir: Optional[Union[str, Path]] = None,
        store: Optional[VectorStore] = None,
        embedder=None,
    ):
        self.store = store or VectorStore(persist_dir)
        self._embedder = embedder

    def is_ready(self) -> bool:
        return self.store.is_built()

    def _get_embedder(self):
        if self._embedder is None:
            backend_id = self.store.backend_id()
            if not backend_id:
                raise IndexNotBuiltError(
                    "The knowledge-base index has not been built yet."
                )
            self._embedder = embedder_from_backend_id(backend_id)
        return self._embedder

    @classmethod
    def _tokens(cls, text: str) -> set[str]:
        words = re.findall(r"[a-zA-Z0-9]+", text.lower())
        normalized = []

        for word in words:
            if word in cls.STOPWORDS:
                continue

            word = cls.WORD_NORMALIZATION.get(word, word)

            # Basic singular normalization for ordinary plurals.
            if len(word) > 4 and word.endswith("s"):
                word = word[:-1]

            normalized.append(word)

        return set(normalized)

    @classmethod
    def _keyword_score(cls, query: str, row: dict) -> float:
        query_words = cls._tokens(query)
        if not query_words:
            return 0.0

        meta = row["metadata"]
        text = row["text"]
        title = meta.get("title", "")
        section = meta.get("section", "")
        filename = meta.get("source_file", "")

        content_words = cls._tokens(text)
        title_words = cls._tokens(title)
        section_words = cls._tokens(section)
        filename_words = cls._tokens(filename)

        # Give more importance to matches in titles and section headings.
        matched = len(query_words & content_words)
        title_matches = len(query_words & title_words)
        section_matches = len(query_words & section_words)
        filename_matches = len(query_words & filename_words)

        score = (
            0.60 * matched / len(query_words)
            + 0.20 * title_matches / len(query_words)
            + 0.15 * section_matches / len(query_words)
            + 0.05 * filename_matches / len(query_words)
        )

        # Boost exact important phrases.
        query_lower = query.lower()
        searchable = (
            f"{title} {section} {text} {filename}"
        ).lower()

        for phrase in (
            "api key",
            "api keys",
            "hardcoded credentials",
            "environment variables",
            "secret manager",
            "sql injection",
            "cross-site scripting",
        ):
            if phrase in query_lower and phrase in searchable:
                score += 0.15

        return min(score, 1.0)

    def search(
        self,
        query: str,
        top_k: int = settings.DEFAULT_TOP_K,
    ) -> List[RetrievedChunk]:
        """Return the most relevant chunks using vector and keyword ranking."""

        if not query or not query.strip():
            raise ValueError("Please enter a search query.")

        if top_k < 1:
            raise ValueError("Number of results must be at least 1.")

        if not self.store.is_built():
            raise IndexNotBuiltError(
                "The knowledge-base index has not been built yet. Build it first."
            )

        query = query.strip()
        vector = self._get_embedder().embed([query])[0]

        # Retrieve more candidates than requested so keyword ranking
        # can promote relevant chunks that hashing ranks poorly.
        candidate_k = 100
        rows = self.store.query(vector, candidate_k)

        if not rows:
            return []

        ranked = []

        for row in rows:
            meta = row["metadata"]
            vector_score = round(1.0 - float(row["distance"]), 4)
            keyword_score = self._keyword_score(query, row)

            # Keyword matching is especially useful with the offline
            # hashing backend. Vector ranking still helps with paraphrases.
            combined_score = (
                0.75 * keyword_score
                + 0.25 * max(0.0, min(1.0, vector_score))
            )

            ranked.append(
                (
                    combined_score,
                    keyword_score,
                    vector_score,
                    row,
                )
            )

        # Prefer results that actually match the query's key terms.
        ranked.sort(key=lambda item: item[0], reverse=True)

        # If lexical matches exist, avoid filling the result list with
        # unrelated chunks simply because the user requested more results.
        matching = [item for item in ranked if item[1] > 0]

        if matching:
            ranked = matching

        results = []

        for _, _, vector_score, row in ranked[:top_k]:
            meta = row["metadata"]
            urls = [
                url
                for url in (meta.get("source_urls") or "").split(
                    URL_SEPARATOR
                )
                if url
            ]

            results.append(
                RetrievedChunk(
                    text=row["text"],
                    source_file=meta["source_file"],
                    title=meta.get("title", meta["source_file"]),
                    section=meta.get("section", ""),
                    source_urls=urls,
                    score=vector_score,
                    chunk_index=int(meta.get("chunk_index", 0)),
                )
            )

        return results
