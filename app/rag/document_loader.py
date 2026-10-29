"""Document Loader for Security Knowledge Base files."""

import json
from pathlib import Path
from typing import Dict, List, Any


class DocumentLoader:
    """Loads documents and manifests from the knowledge base directory."""

    def __init__(self, kb_dir: Path):
        self.kb_dir = Path(kb_dir).resolve()

    def load_manifest(self) -> Dict[str, Any]:
        manifest_file = self.kb_dir / "manifest.json"
        if manifest_file.is_file():
            with open(manifest_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"documents": [], "topics": []}

    def load_all_documents(self) -> List[Dict[str, Any]]:
        """Load all markdown documents from knowledge base directory."""
        docs = []
        if not self.kb_dir.is_dir():
            return docs

        for file_path in sorted(self.kb_dir.glob("*.md")):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                docs.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "content": content,
                    "size_bytes": file_path.stat().st_size
                })
            except Exception as e:
                print(f"[DocumentLoader] Error reading {file_path.name}: {e}")
        return docs
