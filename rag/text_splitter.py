"""Section-Aware Markdown Text Splitter.

Splits Markdown documents into semantically coherent chunks based on
H2/H3 headers and character boundaries, preserving code snippets and context.
"""
import re
from typing import List, Dict, Any


class MarkdownTextSplitter:
    """Splits markdown content into semantic section chunks."""

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split a loaded document into chunk dictionaries.

        Args:
            document: Dict containing 'doc_id', 'title', 'content', 'metadata'.

        Returns:
            List of chunk dicts:
            - chunk_id: str
            - doc_id: str
            - title: str
            - section: str
            - text: str
            - metadata: dict
        """
        content = document["content"]
        doc_id = document["doc_id"]
        base_title = document["title"]
        base_meta = document.get("metadata", {})

        # Split on markdown headers: ## or ###
        header_pattern = re.compile(r"(^#{2,3}\s+.+$)", re.MULTILINE)
        sections = header_pattern.split(content)

        chunks = []
        current_section_title = base_title
        chunk_counter = 0

        for part in sections:
            part_stripped = part.strip()
            if not part_stripped:
                continue

            # If this part is a header, update current section title
            if part_stripped.startswith("##"):
                current_section_title = part_stripped.lstrip("#").strip()
                continue

            # Sub-split long section if it exceeds chunk_size
            if len(part_stripped) <= self.chunk_size:
                chunk_counter += 1
                chunk_id = f"{doc_id}#chunk_{chunk_counter}"
                chunks.append({
                    "chunk_id": chunk_id,
                    "doc_id": doc_id,
                    "title": base_title,
                    "section": current_section_title,
                    "text": f"[{base_title} - {current_section_title}]\n\n{part_stripped}",
                    "metadata": {
                        **base_meta,
                        "chunk_id": chunk_id,
                        "section": current_section_title,
                    },
                })
            else:
                # Break large sections with overlap
                start = 0
                while start < len(part_stripped):
                    end = start + self.chunk_size
                    # Try to break at a newline or space rather than mid-word
                    if end < len(part_stripped):
                        break_point = part_stripped.rfind("\n", start, end)
                        if break_point == -1 or break_point <= start:
                            break_point = part_stripped.rfind(" ", start, end)
                        if break_point > start:
                            end = break_point

                    sub_text = part_stripped[start:end].strip()
                    if sub_text:
                        chunk_counter += 1
                        chunk_id = f"{doc_id}#chunk_{chunk_counter}"
                        chunks.append({
                            "chunk_id": chunk_id,
                            "doc_id": doc_id,
                            "title": base_title,
                            "section": current_section_title,
                            "text": f"[{base_title} - {current_section_title}]\n\n{sub_text}",
                            "metadata": {
                                **base_meta,
                                "chunk_id": chunk_id,
                                "section": current_section_title,
                            },
                        })

                    start = end - self.chunk_overlap
                    if start < 0 or start >= len(part_stripped) or end >= len(part_stripped):
                        break

        return chunks

    def split_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Split a collection of documents into chunks."""
        all_chunks = []
        for doc in documents:
            all_chunks.extend(self.split_document(doc))
        return all_chunks
