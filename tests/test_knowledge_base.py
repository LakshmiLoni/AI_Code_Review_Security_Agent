"""Tests for knowledge base and RAG pipeline."""
import unittest
from utils.validate_knowledge_base import validate_knowledge_base
from rag.rag_pipeline import RAGPipeline


class TestKnowledgeBase(unittest.TestCase):
    """Test secure coding knowledge base and RAG retrieval."""

    def test_knowledge_base_lines_exceed_1001(self):
        is_valid, stats = validate_knowledge_base()
        self.assertTrue(is_valid)
        self.assertTrue(stats["meets_requirement"])
        self.assertGreaterEqual(stats["total_lines"], 1001)
        self.assertEqual(len(stats["empty_files"]), 0)
        self.assertEqual(len(stats["duplicates"]), 0)

    def test_rag_retrieval_finds_relevant_guidelines(self):
        pipeline = RAGPipeline()
        results = pipeline.retrieve_context("prevent SQL injection with parameterized queries", top_k=3)
        self.assertGreater(len(results), 0)
        top_title = results[0]["title"].lower()
        self.assertTrue("sql" in top_title or "injection" in top_title or "owasp" in top_title)


if __name__ == "__main__":
    unittest.main()
