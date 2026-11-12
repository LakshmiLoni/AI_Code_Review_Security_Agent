"""CLI Script: Build and Index the Secure Coding Knowledge Base.

Loads all Markdown documents, computes chunk embeddings, and persists them
in the ChromaDB / vector store index.
"""
import os
import sys

# Ensure project root is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from rag.rag_pipeline import RAGPipeline
from utils.validate_knowledge_base import validate_knowledge_base


def main():
    print("=" * 65)
    print("AI CODE REVIEW - BUILDING SECURE CODING KNOWLEDGE BASE INDEX")
    print("=" * 65)

    # 1. First validate markdown documentation lines
    print("\n[Step 1/2] Validating knowledge base line counts...")
    is_valid, stats = validate_knowledge_base()
    print(f" -> Found {stats['document_count']} markdown files with {stats['total_lines']} total lines.")
    if not is_valid:
        print("[ERROR] Knowledge base does not meet validation criteria.")
        sys.exit(1)
    print(" -> Validation PASSED (>= 1,001 lines requirement satisfied).")

    # 2. Build vector index
    print("\n[Step 2/2] Parsing, chunking, and generating vector embeddings...")
    pipeline = RAGPipeline()
    result = pipeline.build_index(force=True)

    print("\n" + "=" * 65)
    print("KNOWLEDGE BASE INDEXING SUMMARY")
    print("=" * 65)
    print(f"Status                  : {result.get('status')}")
    print(f"Documents Loaded        : {result.get('documents_loaded')}")
    print(f"Chunks Created          : {result.get('chunks_created')}")
    print(f"Embeddings Generated    : {result.get('embeddings_generated')}")
    print(f"Total Chunks in Index   : {result.get('total_indexed_chunks')}")
    print(f"ChromaDB Backend Active : {result.get('using_chromadb')}")
    print(f"SentenceTransformers    : {result.get('using_sentence_transformers')}")
    print(f"Elapsed Time            : {result.get('duration_seconds')} seconds")
    print("=" * 65)
    print("\n[SUCCESS] Knowledge base index built and persisted successfully!")

    # Perform a quick verification query
    print("\nRunning test verification query: 'SQL injection prevention in Python'...")
    test_results = pipeline.retrieve_context("SQL injection prevention in Python", top_k=2)
    print(f"Retrieved {len(test_results)} matching reference chunks:")
    for i, r in enumerate(test_results, 1):
        print(f"  {i}. {r['title']} § {r['section']} (Score: {r['score']})")


if __name__ == "__main__":
    main()
