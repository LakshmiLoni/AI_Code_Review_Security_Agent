"""Test suite for Knowledge Base and RAG Subsystem."""

import unittest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.count_knowledge_lines import count_nonblank_lines, MIN_REQUIRED_LINES
from app.rag.retriever import KnowledgeRetriever
from app.rag.document_loader import DocumentLoader


class TestKnowledgeBase(unittest.TestCase):
    def setUp(self):
        self.kb_dir = PROJECT_ROOT / "knowledge_base"
        self.kb_file = self.kb_dir / "secure_coding_knowledge_base.md"
        self.chroma_dir = PROJECT_ROOT / "chroma_db"

    def test_line_count_meets_strict_requirement(self):
        """Strict verification: knowledge base must have at least 1,200 non-blank lines."""
        self.assertTrue(self.kb_file.is_file(), f"File does not exist: {self.kb_file}")
        count = count_nonblank_lines(self.kb_file)
        print(f"\n[TestKB] Verified line count: {count} (Minimum required: {MIN_REQUIRED_LINES})")
        self.assertGreaterEqual(count, MIN_REQUIRED_LINES)

    def test_manifest_metadata(self):
        """Verify manifest.json contains valid topic listings."""
        loader = DocumentLoader(self.kb_dir)
        manifest = loader.load_manifest()
        self.assertIn("topics", manifest)
        self.assertEqual(len(manifest["topics"]), 25)

    def test_rag_retrieval(self):
        """Verify semantic retrieval returns relevant chunks."""
        retriever = KnowledgeRetriever(kb_dir=self.kb_dir, chroma_dir=self.chroma_dir)
        results = retriever.retrieve("parameterized SQL query", top_k=2)
        self.assertTrue(len(results) > 0)
        top_hit = results[0]
        self.assertIn("title", top_hit)
        self.assertTrue("SQL" in top_hit["content"] or "query" in top_hit["content"].lower())


if __name__ == "__main__":
    unittest.main()
