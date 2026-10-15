"""Step 1 of the RAG pipeline: load Markdown knowledge documents from disk."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Union

from config import settings

_URL_RE = re.compile(r"https?://[^\s)>\]]+")
_SOURCES_HEADING = re.compile(r"^##\s+Sources?\s*$", re.IGNORECASE | re.MULTILINE)


@dataclass
class Document:
    """A raw knowledge document."""

    name: str  # file name, e.g. "sql_injection.md"
    title: str
    text: str
    source_urls: List[str] = field(default_factory=list)
    content_hash: str = ""


def extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def extract_source_urls(text: str) -> List[str]:
    """Collect URLs listed under the document's ``## Sources`` section."""
    match = _SOURCES_HEADING.search(text)
    if not match:
        return []
    section = text[match.end():]
    next_heading = re.search(r"^##\s+", section, re.MULTILINE)
    if next_heading:
        section = section[: next_heading.start()]
    seen: List[str] = []
    for url in _URL_RE.findall(section):
        url = url.rstrip(".,;")
        if url not in seen:
            seen.append(url)
    return seen


def load_documents(directory: Optional[Union[str, Path]] = None) -> List[Document]:
    """Load every ``*.md`` file in ``directory`` (default: knowledge_base/documents)."""
    folder = Path(directory) if directory else settings.DOCUMENTS_DIR
    if not folder.is_dir():
        raise FileNotFoundError(f"Knowledge-base folder not found: {folder}")

    documents: List[Document] = []
    for path in sorted(folder.glob("*.md")):
        text = path.read_text(encoding="utf-8-sig")
        if not text.strip():
            continue
        documents.append(
            Document(
                name=path.name,
                title=extract_title(text, path.stem.replace("_", " ").title()),
                text=text,
                source_urls=extract_source_urls(text),
                content_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
            )
        )
    if not documents:
        raise FileNotFoundError(f"No Markdown (.md) documents found in {folder}")
    return documents
