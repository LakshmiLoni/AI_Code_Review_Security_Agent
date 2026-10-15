"""Command-line entry point to build or refresh the knowledge-base index.

    python -m knowledge_base.build_index            # incremental refresh
    python -m knowledge_base.build_index --force    # rebuild everything
    python -m knowledge_base.build_index --backend hashing --force   # offline fallback
"""
from __future__ import annotations

import argparse
import sys
from typing import Callable, Optional

from config import settings
from knowledge_base.document_loader import load_documents
from knowledge_base.embedding_service import EmbeddingError, get_embedder
from knowledge_base.vector_store import IndexStats, VectorStore


def build_or_refresh_index(force: bool = False, backend: Optional[str] = None, documents_dir=None,
                           persist_dir=None, progress: Optional[Callable[[str], None]] = None) -> IndexStats:
    documents = load_documents(documents_dir)
    embedder = get_embedder(backend)
    store = VectorStore(persist_dir)
    return store.build_index(documents, embedder, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP, force=force, progress=progress)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build or refresh the secure-coding knowledge-base index.")
    parser.add_argument("--force", action="store_true", help="rebuild the whole index from scratch")
    parser.add_argument("--backend", choices=["sentence-transformers", "hashing"], default=None,
                        help="embedding backend (default from settings)")
    args = parser.parse_args(argv)
    try:
        stats = build_or_refresh_index(force=args.force, backend=args.backend, progress=print)
    except EmbeddingError as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 1
    print(f"\nDone. Backend: {stats.backend_id}")
    print(f"  Documents indexed : {len(stats.documents_indexed)} {stats.documents_indexed}")
    print(f"  Documents skipped : {len(stats.documents_skipped)} (unchanged)")
    print(f"  Documents removed : {len(stats.documents_removed)}")
    print(f"  Chunks added      : {stats.chunks_added}")
    print(f"  Total chunks      : {stats.chunks_total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
