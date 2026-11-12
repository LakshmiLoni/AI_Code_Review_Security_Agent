"""Markdown Knowledge Base Document Loader.

Loads, parses, and extracts structural metadata from all Markdown files
stored in the secure coding knowledge base directory.
"""
import os
import re
from typing import List, Dict, Any


class DocumentLoader:
    """Loads Markdown documents and extracts metadata."""

    def __init__(self, kb_dir: str):
        self.kb_dir = kb_dir

    def load_documents(self) -> List[Dict[str, Any]]:
        """Load all .md files in the knowledge base directory.

        Returns:
            List of dictionaries containing:
            - doc_id: str (filename)
            - title: str (extracted H1 or filename)
            - content: str (raw document content)
            - line_count: int
            - metadata: dict
        """
        if not os.path.exists(self.kb_dir):
            raise FileNotFoundError(f"Knowledge base directory does not exist: {self.kb_dir}")

        documents = []
        md_files = [f for f in os.listdir(self.kb_dir) if f.endswith(".md")]

        for filename in sorted(md_files):
            filepath = os.path.join(self.kb_dir, filename)
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            # Extract primary H1 title if present
            title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            if title_match:
                title = title_match.group(1).strip()
            else:
                title = filename.replace(".md", "").replace("_", " ").title()

            doc_info = {
                "doc_id": filename,
                "title": title,
                "content": content,
                "filepath": filepath,
                "line_count": len(content.splitlines()),
                "metadata": {
                    "source": filename,
                    "title": title,
                    "category": self._infer_category(filename),
                },
            }
            documents.append(doc_info)

        return documents

    def _infer_category(self, filename: str) -> str:
        """Infer security or quality category based on filename."""
        name = filename.lower()
        if "owasp" in name or "top10" in name:
            return "OWASP General"
        elif "sql" in name or "xss" in name or "csrf" in name or "injection" in name:
            return "Injection & Web Vulnerabilities"
        elif "auth" in name or "secrets" in name:
            return "Authentication & Secrets"
        elif "crypt" in name:
            return "Cryptography"
        elif "file" in name or "path" in name or "deserial" in name:
            return "File & Data Integrity"
        elif "quality" in name or "clean" in name:
            return "Code Quality & Architecture"
        elif "api" in name:
            return "API Security"
        return "Defensive Engineering"
