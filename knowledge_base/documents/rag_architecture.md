# Introduction to Retrieval-Augmented Generation (RAG)

## Definition
Retrieval-Augmented Generation (RAG) combines an information-retrieval step with a text-generating language model. Instead of relying only on what the model memorised during training, the system first **retrieves** relevant passages from an external knowledge base and then supplies them to the model as context for **generating** the answer. The term comes from Lewis et al. (2020).

## Why RAG for a code-review agent
- The security knowledge (OWASP guidance, secure-coding rules) lives in documents we control and can update without retraining a model.
- Answers can **cite sources** (document and URL), which builds trust and supports review.
- It reduces hallucination because the model is grounded in retrieved text.
- Everything can run locally and for free in the retrieval stage.

## Pipeline stages
1. **Load** - read the source documents (here: Markdown files).
2. **Clean** - normalise newlines, remove noise, keep structure.
3. **Chunk** - split documents into small overlapping pieces (e.g. 800 characters with 150 overlap) so each piece holds one idea and fits the embedding model; overlap preserves context across boundaries.
4. **Embed** - convert each chunk into a numeric vector with an embedding model so that similar meanings get nearby vectors (here: `all-MiniLM-L6-v2` from Sentence-Transformers, 384 dimensions).
5. **Index** - store vectors, text and metadata (source file, title, URLs) in a vector database (here: ChromaDB, persisted on disk).
6. **Retrieve** - embed the user's query with the same model and fetch the nearest chunks by cosine similarity.
7. **Generate** (later milestone) - give the retrieved chunks plus the question to an LLM to produce a grounded answer with citations.

## Key concepts
- **Embedding**: dense vector representing text meaning.
- **Cosine similarity**: measures the angle between two vectors; 1 means the same direction.
- **Top-k**: number of chunks returned.
- **Metadata**: extra fields stored with each chunk, used to cite sources.
- **Index refresh**: re-embedding only documents that changed (done by hashing document contents).

## Trade-offs and tips
- Chunks too large dilute meaning; too small lose context. Overlap helps.
- The same embedding model must be used for indexing and querying.
- Retrieval quality depends on document quality; keep documents concise and well structured.
- Evaluate with realistic questions (e.g. "how do I prevent SQL injection in Java?").

## Scope in this project
Milestone 1 implements stages 1-6 (retrieval only). Stage 7 (LLM generation) belongs to the Conversational Code Assistant and Remediation Agent in later milestones.

## Sources
- https://arxiv.org/abs/2005.11401
- https://www.sbert.net/
- https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- https://docs.trychroma.com/
