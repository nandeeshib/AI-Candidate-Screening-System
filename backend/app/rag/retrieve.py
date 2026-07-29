import os
import json
import numpy as np
import faiss
from app.config import INDEX_DIR, RAG_TOP_K
from app.rag.ingest import get_embedder, build_index_for_role

_index_cache: dict[str, faiss.Index] = {}
_chunks_cache: dict[str, list] = {}


def _load_role_index(role_id: str):
    if role_id in _index_cache:
        return _index_cache[role_id], _chunks_cache[role_id]

    index_path = os.path.join(INDEX_DIR, f"{role_id}.index")
    chunks_path = os.path.join(INDEX_DIR, f"{role_id}.json")

    if not (os.path.exists(index_path) and os.path.exists(chunks_path)):
        # Build on demand if the app starts fresh without a pre-built index
        build_index_for_role(role_id)

    index = faiss.read_index(index_path)
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    _index_cache[role_id] = index
    _chunks_cache[role_id] = chunks
    return index, chunks


def retrieve(role_id: str, query: str, top_k: int = None) -> list[dict]:
    """Returns the top_k most relevant knowledge base chunks for a query,
    each with its topic label and similarity score."""
    top_k = top_k or RAG_TOP_K
    index, chunks = _load_role_index(role_id)

    embedder = get_embedder()
    query_vec = embedder.encode([query], normalize_embeddings=True)
    query_vec = np.array(query_vec, dtype="float32")

    scores, indices = index.search(query_vec, min(top_k, len(chunks)))

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        chunk = chunks[idx]
        results.append({
            "topic": chunk["topic"],
            "text": chunk["text"],
            "score": float(score),
        })
    return results
