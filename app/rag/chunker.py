"""Markdown-aware semantic chunker for knowledge base indexing."""

import re
from typing import Dict, List, Any


class MarkdownChunker:
    """Splits markdown security documents into cohesive semantic chunks."""

    def __init__(self, max_chunk_chars: int = 1500, overlap_chars: int = 150):
        self.max_chunk_chars = max_chunk_chars
        self.overlap_chars = overlap_chars

    def chunk_document(self, doc_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        filename = doc_info["filename"]
        content = doc_info["content"]

        chunks = []
        # Split on level-2 headers ('## ')
        section_pattern = re.compile(r"(^##\s+[^\n]+)", re.MULTILINE)
        parts = section_pattern.split(content)

        preamble = parts[0].strip()
        if preamble:
            chunks.append({
                "chunk_id": f"{filename}#preamble",
                "filename": filename,
                "section": "Overview",
                "title": f"{filename} - Overview",
                "content": preamble,
                "word_count": len(preamble.split())
            })

        for i in range(1, len(parts), 2):
            header = parts[i].strip()
            body = parts[i + 1].strip() if i + 1 < len(parts) else ""

            # Extract section title (e.g. "## 5. SQL Injection")
            clean_title = re.sub(r"^##\s+", "", header)
            # Further split by subheadings if body is large
            sub_chunks = self._chunk_section_body(filename, clean_title, body)
            chunks.extend(sub_chunks)

        return chunks

    def _chunk_section_body(self, filename: str, section_title: str, body: str) -> List[Dict[str, Any]]:
        sub_pattern = re.compile(r"(^###\s+[^\n]+)", re.MULTILINE)
        parts = sub_pattern.split(body)

        if len(parts) <= 1:
            # No subheadings; treat as single or windowed chunk
            return [{
                "chunk_id": f"{filename}#{re.sub(r'[^a-zA-Z0-9]', '_', section_title)[:40]}",
                "filename": filename,
                "section": section_title,
                "title": f"{section_title}",
                "content": f"## {section_title}\n\n{body}",
                "word_count": len(body.split())
            }]

        sub_chunks = []
        lead_in = parts[0].strip()
        if lead_in:
            sub_chunks.append({
                "chunk_id": f"{filename}#{re.sub(r'[^a-zA-Z0-9]', '_', section_title)[:40]}_lead",
                "filename": filename,
                "section": section_title,
                "title": f"{section_title} - Introduction",
                "content": f"## {section_title}\n\n{lead_in}",
                "word_count": len(lead_in.split())
            })

        for j in range(1, len(parts), 2):
            sub_header = parts[j].strip()
            sub_body = parts[j + 1].strip() if j + 1 < len(parts) else ""
            clean_sub_title = re.sub(r"^###\s+", "", sub_header)

            chunk_text = f"## {section_title}\n### {clean_sub_title}\n\n{sub_body}"
            sub_chunks.append({
                "chunk_id": f"{filename}#{re.sub(r'[^a-zA-Z0-9]', '_', clean_sub_title)[:40]}",
                "filename": filename,
                "section": section_title,
                "title": f"{section_title} - {clean_sub_title}",
                "content": chunk_text,
                "word_count": len(chunk_text.split())
            })

        return sub_chunks
