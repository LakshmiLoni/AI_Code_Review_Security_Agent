import pytest

from knowledge_base.document_loader import extract_source_urls, load_documents
from knowledge_base.text_chunker import chunk_text
from knowledge_base.text_cleaner import clean_text


def test_clean_text_normalises():
    raw = "Title\r\n\r\n\r\n\r\nBody\ttext   \n<!-- hidden -->\u200bEnd"
    cleaned = clean_text(raw)
    assert "\r" not in cleaned
    assert "\n\n\n" not in cleaned
    assert "hidden" not in cleaned and "\u200b" not in cleaned
    assert "   \n" not in cleaned


def test_clean_text_empty():
    assert clean_text("") == ""


def test_chunking_respects_size_and_overlaps():
    text = " ".join(f"word{i}" for i in range(600))
    chunks = chunk_text(text, chunk_size=200, chunk_overlap=40)
    assert len(chunks) > 3
    assert all(len(c.text) <= 200 for c in chunks)
    # consecutive chunks overlap
    for a, b in zip(chunks, chunks[1:]):
        assert b.start < a.end
    # nothing is lost
    assert chunks[0].start == 0 and chunks[-1].end == len(text)
    assert [c.index for c in chunks] == list(range(len(chunks)))


def test_chunking_tracks_section():
    text = "# Title\n\nIntro.\n\n## SQL\n\n" + ("SQL text. " * 80) + "\n\n## XSS\n\n" + ("XSS text. " * 80)
    chunks = chunk_text(text, chunk_size=300, chunk_overlap=50)
    assert any(c.section == "SQL" for c in chunks)
    assert any(c.section == "XSS" for c in chunks)


def test_short_text_single_chunk():
    chunks = chunk_text("short text", chunk_size=100, chunk_overlap=10)
    assert len(chunks) == 1 and chunks[0].text == "short text"


def test_empty_text_no_chunks():
    assert chunk_text("   ", 100, 10) == []


@pytest.mark.parametrize("size,overlap", [(0, 0), (100, 100), (100, 150), (100, -1)])
def test_invalid_chunk_parameters(size, overlap):
    with pytest.raises(ValueError):
        chunk_text("some text", size, overlap)


def test_extract_source_urls():
    text = "# T\n\nbody https://not-a-source.example\n\n## Sources\n- https://a.example/x\n- https://b.example/y.\n\n## Other\nhttps://c.example"
    assert extract_source_urls(text) == ["https://a.example/x", "https://b.example/y"]


def test_load_real_knowledge_base_documents():
    docs = load_documents()
    names = {d.name for d in docs}
    expected = {
        "owasp_top_10.md", "sql_injection.md", "xss_prevention.md", "csrf_prevention.md", "secrets_management.md",
        "authentication_authorization.md", "access_control.md", "python_secure_coding.md", "java_secure_coding.md",
        "code_smells.md", "rag_architecture.md",
    }
    assert expected <= names
    for doc in docs:
        assert doc.title
        assert doc.source_urls, f"{doc.name} has no source URLs"
        assert all(u.startswith("http") for u in doc.source_urls)


def test_load_missing_directory(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_documents(tmp_path / "nope")
    with pytest.raises(FileNotFoundError):
        load_documents(tmp_path)  # exists but has no .md files
