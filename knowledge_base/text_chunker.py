"""Step 3 of the RAG pipeline: split text into overlapping chunks.

Chunks are windows of at most ``chunk_size`` characters. Window ends snap back
to a natural boundary (blank line > newline > sentence end > space) and each
new window starts ``chunk_overlap`` characters before the previous one ended,
so ideas that straddle a boundary appear in both chunks.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Tuple

from config import settings

_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


@dataclass
class Chunk:
    text: str
    index: int
    start: int  # character offset in the cleaned document
    end: int
    section: str  # nearest preceding Markdown heading


def _heading_positions(text: str) -> List[Tuple[int, str]]:
    return [(m.start(), m.group(2)) for m in _HEADING.finditer(text)]


def _section_at(position: int, headings: List[Tuple[int, str]]) -> str:
    section = ""
    for start, title in headings:
        if start <= position:
            section = title
        else:
            break
    return section


def _snap_end(text: str, start: int, hard_end: int) -> int:
    """Move ``hard_end`` back to a natural boundary, but never before the window midpoint."""
    if hard_end >= len(text):
        return len(text)
    floor = start + (hard_end - start) // 2
    window = text[floor:hard_end]
    for separator in ("\n\n", "\n", ". ", " "):
        position = window.rfind(separator)
        if position != -1:
            return floor + position + len(separator)
    return hard_end


def chunk_text(text: str, chunk_size: int = None, chunk_overlap: int = None) -> List[Chunk]:
    """Split ``text`` into overlapping :class:`Chunk` objects."""
    chunk_size = settings.CHUNK_SIZE if chunk_size is None else chunk_size
    chunk_overlap = settings.CHUNK_OVERLAP if chunk_overlap is None else chunk_overlap
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be >= 0 and smaller than chunk_size")
    if not text or not text.strip():
        return []

    headings = _heading_positions(text)
    chunks: List[Chunk] = []
    start = 0
    while start < len(text):
        end = _snap_end(text, start, min(start + chunk_size, len(text)))
        piece = text[start:end].strip()
        if piece:
            lead = len(text[start:end]) - len(text[start:end].lstrip())
            chunks.append(Chunk(piece, len(chunks), start + lead, end, _section_at(start + lead, headings)))
        if end >= len(text):
            break
        next_start = end - chunk_overlap
        start = next_start if next_start > start else end  # always make progress
    return chunks
