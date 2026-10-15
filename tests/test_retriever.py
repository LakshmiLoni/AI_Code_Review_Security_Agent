"""Index + retrieval tests use the offline 'hashing' embedder, so they need no
model download. The sentence-transformers backend is covered by an optional test."""
import pytest

from knowledge_base.document_loader import Document, load_documents
from knowledge_base.embedding_service import HashingEmbedder, get_embedder
from knowledge_base.retriever import Retriever
from knowledge_base.vector_store import IndexNotBuiltError, VectorStore


@pytest.fixture()
def embedder():
    return HashingEmbedder()


@pytest.fixture()
def built_store(tmp_path, embedder):
    store = VectorStore(tmp_path / "chroma")
    stats = store.build_index(load_documents(), embedder, 800, 150)
    return store, stats


def test_hashing_embedder_is_deterministic_and_normalised(embedder):
    a, b = embedder.embed(["sql injection"]), embedder.embed(["sql injection"])
    assert a == b
    assert abs(sum(x * x for x in a[0]) - 1.0) < 1e-6
    assert len(a[0]) == 384


def test_build_index_creates_chunks_with_metadata(built_store):
    store, stats = built_store
    assert stats.chunks_total > 30
    assert len(stats.documents_indexed) == 11
    assert store.is_built()
    docs = store.indexed_documents()
    assert "sql_injection.md" in docs


def test_search_returns_relevant_source_and_urls(built_store, embedder):
    store, _ = built_store
    retriever = Retriever(store=store, embedder=embedder)
    results = retriever.search("How do I prevent SQL injection with prepared statements?", top_k=4)
    assert results
    assert results[0].source_file == "sql_injection.md"
    assert results[0].source_urls and results[0].source_urls[0].startswith("https://")
    assert results[0].text.strip()
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.parametrize(
    "query,expected",
    [
        ("escape output to stop cross-site scripting", "xss_prevention.md"),
        ("anti-CSRF token for forged requests", "csrf_prevention.md"),
        ("hardcoded password in source code environment variable", "secrets_management.md"),
        ("what is retrieval augmented generation embeddings chunking", "rag_architecture.md"),
    ],
)
def test_topic_queries_hit_expected_document(built_store, embedder, query, expected):
    store, _ = built_store
    results = Retriever(store=store, embedder=embedder).search(query, top_k=3)
    assert expected in {r.source_file for r in results}


def test_index_persists_between_runs_and_retriever_autodetects_backend(tmp_path, embedder):
    path = tmp_path / "chroma"
    VectorStore(path).build_index(load_documents(), embedder, 800, 150)

    # Brand-new objects, as if the app were restarted: nothing is rebuilt.
    reopened = Retriever(persist_dir=path)
    assert reopened.is_ready()
    results = reopened.search("broken access control IDOR ownership check")
    assert results and results[0].source_file in {"access_control.md", "owasp_top_10.md"}


def test_refresh_skips_unchanged_documents(built_store, embedder):
    store, first = built_store
    second = store.build_index(load_documents(), embedder, 800, 150)
    assert second.chunks_added == 0
    assert len(second.documents_skipped) == 11
    assert second.chunks_total == first.chunks_total


def test_refresh_reindexes_changed_and_removes_deleted(tmp_path, embedder):
    store = VectorStore(tmp_path / "chroma")
    docs = [
        Document("a.md", "Doc A", "# Doc A\n\nApples are red.\n\n## Sources\n- https://a.example", ["https://a.example"], "h1"),
        Document("b.md", "Doc B", "# Doc B\n\nBananas are yellow.\n\n## Sources\n- https://b.example", ["https://b.example"], "h2"),
    ]
    store.build_index(docs, embedder)
    docs[0] = Document("a.md", "Doc A", "# Doc A\n\nApples are green now.", ["https://a.example"], "h1-changed")
    stats = store.build_index(docs[:1], embedder)   # a.md changed, b.md deleted
    assert stats.documents_indexed == ["a.md"]
    assert stats.documents_removed == ["b.md"]
    assert set(store.indexed_documents()) == {"a.md"}


def test_force_rebuild(built_store, embedder):
    store, first = built_store
    again = store.build_index(load_documents(), embedder, 800, 150, force=True)
    assert again.rebuilt_from_scratch
    assert again.chunks_total == first.chunks_total


def test_search_before_build_raises(tmp_path, embedder):
    retriever = Retriever(persist_dir=tmp_path / "empty", embedder=embedder)
    assert not retriever.is_ready()
    with pytest.raises(IndexNotBuiltError):
        retriever.search("anything")


def test_empty_query_rejected(built_store, embedder):
    store, _ = built_store
    with pytest.raises(ValueError):
        Retriever(store=store, embedder=embedder).search("   ")


def test_unknown_backend_name():
    with pytest.raises(ValueError):
        get_embedder("does-not-exist")


def test_sentence_transformers_backend_if_available(tmp_path):
    """Optional: runs only when the model is available locally / downloadable."""
    st_mod = pytest.importorskip("sentence_transformers")  # noqa: F841
    from knowledge_base.embedding_service import EmbeddingError, SentenceTransformerEmbedder

    embedder = SentenceTransformerEmbedder()
    try:
        vectors = embedder.embed(["sql injection", "cross site scripting"])
    except EmbeddingError:
        pytest.skip("embedding model could not be downloaded in this environment")
    assert len(vectors) == 2 and len(vectors[0]) == 384


def test_failed_embedder_does_not_destroy_existing_index(built_store):
    from knowledge_base.embedding_service import EmbeddingError

    class BrokenEmbedder:
        backend_id = "st:broken-model"

        def embed(self, texts):
            raise EmbeddingError("model unavailable")

    store, first = built_store
    with pytest.raises(EmbeddingError):
        store.build_index(load_documents(), BrokenEmbedder(), 800, 150, force=True)
    assert store.count() == first.chunks_total   # old index intact
