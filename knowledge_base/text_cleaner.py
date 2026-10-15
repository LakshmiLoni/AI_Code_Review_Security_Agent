"""Step 2 of the RAG pipeline: clean and normalise document text.

Markdown structure (headings, lists, code fences) is deliberately preserved
because the chunker uses headings, and code examples are valuable context.
"""
from __future__ import annotations

import re
import unicodedata

_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_ZERO_WIDTH = re.compile(r"[\u200b\u200c\u200d\u2060\ufeff]")
_MANY_BLANK_LINES = re.compile(r"\n{3,}")


def clean_text(text: str) -> str:
    """Return normalised text: unified newlines, no HTML comments / zero-width
    characters, no trailing whitespace, and at most one blank line in a row."""
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\t", "    ")
    text = _HTML_COMMENT.sub("", text)
    text = _ZERO_WIDTH.sub("", text)
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    text = _MANY_BLANK_LINES.sub("\n\n", text)
    return text.strip()
