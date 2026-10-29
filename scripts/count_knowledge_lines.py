"""Knowledge Base Line Counter and Verifier.

This script counts the non-empty, non-blank lines in
knowledge_base/secure_coding_knowledge_base.md and verifies that it meets
the strict requirement of at least 1,200 meaningful non-blank lines.
"""

import sys
from pathlib import Path


MIN_REQUIRED_LINES = 1200


def count_nonblank_lines(file_path: Path) -> int:
    """Count non-blank lines in the given text file."""
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f]

    # Non-blank line: line with at least one non-whitespace character
    nonblank = [line for line in lines if line]
    return len(nonblank)


def verify_knowledge_base(kb_file: Path) -> int:
    """Count lines and exit with code 0 if >= 1200, else code 1."""
    try:
        count = count_nonblank_lines(kb_file)
        print(f"[KB Verifier] Target file: {kb_file}")
        print(f"[KB Verifier] Non-blank line count: {count}")
        print(f"[KB Verifier] Minimum required: {MIN_REQUIRED_LINES}")

        if count >= MIN_REQUIRED_LINES:
            print(f"[KB Verifier] SUCCESS: Knowledge base meets the line count requirement ({count} >= {MIN_REQUIRED_LINES}).")
            return count
        else:
            deficit = MIN_REQUIRED_LINES - count
            print(f"[KB Verifier] FAILED: Knowledge base is short by {deficit} lines ({count} < {MIN_REQUIRED_LINES}).")
            sys.exit(1)
    except Exception as e:
        print(f"[KB Verifier] ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Base directory relative to this script
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    kb_path = project_root / "knowledge_base" / "secure_coding_knowledge_base.md"

    # Allow custom path argument if provided
    if len(sys.argv) > 1:
        kb_path = Path(sys.argv[1]).resolve()

    count = verify_knowledge_base(kb_path)
