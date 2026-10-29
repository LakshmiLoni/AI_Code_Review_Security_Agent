"""Script to index or re-index the Knowledge Base into the retrieval vector store."""

import sys
from pathlib import Path

# Add project root to sys.path so app modules import properly
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.rag.retriever import KnowledgeRetriever


def main():
    kb_dir = project_root / "knowledge_base"
    chroma_dir = project_root / "chroma_db"

    print(f"[IndexScript] Knowledge Base Directory: {kb_dir}")
    print(f"[IndexScript] Vector Store Directory: {chroma_dir}")

    retriever = KnowledgeRetriever(kb_dir=kb_dir, chroma_dir=chroma_dir)
    count = retriever.index_knowledge_base()

    stats = retriever.vector_store.get_stats()
    print("[IndexScript] Indexing complete!")
    print(f"[IndexScript] Backend: {stats['backend']}")
    print(f"[IndexScript] Total Chunks Indexed: {stats['total_chunks']}")

    # Quick test query
    test_q = "How to prevent SQL injection in Python with parameterized queries?"
    print(f"\n[IndexScript] Testing retrieval with query: '{test_q}'")
    results = retriever.retrieve(test_q, top_k=2)
    for i, r in enumerate(results, 1):
        print(f"  Result {i}: [{r['title']}] (Score: {r['score']})")


if __name__ == "__main__":
    main()
