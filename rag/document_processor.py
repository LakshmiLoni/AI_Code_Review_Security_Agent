"""RAG Document Processor.

Coordinates document loading, structural parsing, metadata extraction,
and chunking for the secure coding knowledge base.
"""
from typing import List, Dict, Any
from .document_loader import DocumentLoader
from .text_splitter import MarkdownTextSplitter


class DocumentProcessor:
    """Processes Markdown documents into searchable chunks."""

    def __init__(self, kb_dir: str):
        self.loader = DocumentLoader(kb_dir)
        self.splitter = MarkdownTextSplitter()

    def load_and_chunk(self) -> List[Dict[str, Any]]:
        """Load all knowledge base documents and split into chunks."""
        docs = self.loader.load_documents()
        all_chunks = []
        for doc in docs:
            chunks = self.splitter.split_document(doc)
            all_chunks.extend(chunks)
        return all_chunks


__all__ = ["DocumentProcessor", "DocumentLoader", "MarkdownTextSplitter"]
