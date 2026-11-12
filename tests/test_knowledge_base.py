"""Tests for knowledge base and RAG pipeline."""
from utils.validate_knowledge_base import validate_knowledge_base
from rag.rag_pipeline import RAGPipeline


def test_knowledge_base_lines_exceed_1001():
    is_valid, stats = validate_knowledge_base()
    assert is_valid is True
    assert stats["meets_requirement"] is True
    assert stats["total_lines"] >= 1001
    assert len(stats["empty_files"]) == 0
    assert len(stats["duplicates"]) == 0


def test_rag_retrieval_finds_relevant_guidelines():
    pipeline = RAGPipeline()
    results = pipeline.retrieve_context("prevent SQL injection with parameterized queries", top_k=3)
    assert len(results) > 0
    # Top result should reference SQL or injection
    top_title = results[0]["title"].lower()
    assert "sql" in top_title or "injection" in top_title or "owasp" in top_title
