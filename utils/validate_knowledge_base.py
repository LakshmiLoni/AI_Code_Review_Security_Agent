"""Knowledge base validator.

Validates that the knowledge base meets the minimum line count requirement (1,001 lines),
checks for empty documents, detects potential duplicate files, and reports detailed stats.
"""
import os
import sys
import hashlib
from typing import Dict, List, Tuple


def get_kb_directory() -> str:
    """Resolve the absolute path to the knowledge base directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    kb_dir = os.path.join(project_root, "knowledge_base")
    return kb_dir


def validate_knowledge_base(kb_dir: str = None) -> Tuple[bool, Dict]:
    """Validate all markdown documents in the knowledge base."""
    if kb_dir is None:
        kb_dir = get_kb_directory()

    if not os.path.exists(kb_dir):
        return False, {
            "error": f"Knowledge base directory not found at {kb_dir}",
            "total_lines": 0,
            "document_count": 0,
            "meets_requirement": False,
        }

    md_files = [f for f in os.listdir(kb_dir) if f.endswith(".md")]
    stats = {
        "kb_dir": kb_dir,
        "document_count": len(md_files),
        "total_lines": 0,
        "files": {},
        "empty_files": [],
        "duplicates": [],
        "meets_requirement": False,
        "target_minimum": 1001,
    }

    seen_hashes = {}
    total_lines = 0

    for filename in sorted(md_files):
        file_path = os.path.join(kb_dir, filename)
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        line_count = len(content.splitlines())
        total_lines += line_count

        file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        if file_hash in seen_hashes:
            stats["duplicates"].append((filename, seen_hashes[file_hash]))
        else:
            seen_hashes[file_hash] = filename

        if line_count == 0 or not content.strip():
            stats["empty_files"].append(filename)

        stats["files"][filename] = {
            "lines": line_count,
            "bytes": len(content),
            "is_empty": (line_count == 0),
        }

    stats["total_lines"] = total_lines
    stats["meets_requirement"] = total_lines >= 1001

    is_valid = (
        stats["meets_requirement"]
        and len(stats["empty_files"]) == 0
        and len(stats["duplicates"]) == 0
    )

    return is_valid, stats


def main():
    """CLI runner for knowledge base validation."""
    is_valid, stats = validate_knowledge_base()
    print("=" * 60)
    print("AI CODE REVIEW - SECURE CODING KNOWLEDGE BASE VALIDATOR")
    print("=" * 60)
    print(f"Directory: {stats.get('kb_dir')}")
    print(f"Total Markdown Documents: {stats.get('document_count')}")
    print("-" * 60)
    for fname, data in stats.get("files", {}).items():
        print(f" - {fname:<35} : {data['lines']:>4} lines ({data['bytes']} bytes)")
    print("-" * 60)
    print(f"Total Line Count: {stats['total_lines']} lines")
    print(f"Target Requirement: >= {stats['target_minimum']} lines")

    if stats["empty_files"]:
        print(f"[WARNING] Empty documents found: {stats['empty_files']}")
    else:
        print("[OK] No empty documents found.")

    if stats["duplicates"]:
        print(f"[WARNING] Duplicate documents found: {stats['duplicates']}")
    else:
        print("[OK] No duplicate documents found.")

    if stats["meets_requirement"]:
        print(f"\n[SUCCESS] Knowledge base requirement satisfied! ({stats['total_lines']} >= 1,001 lines)")
        sys.exit(0)
    else:
        print(f"\n[FAILURE] Knowledge base requirement failed! ({stats['total_lines']} < 1,001 lines)")
        sys.exit(1)


if __name__ == "__main__":
    main()
