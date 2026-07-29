import os
import json
import re
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from app.config import KNOWLEDGE_BASE_DIR, INDEX_DIR

_model = None


def get_embedder():
    """Lazily load the embedding model once and reuse it (it's expensive to load)."""
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def chunk_document(raw_text: str) -> list[dict]:
    """Splits a knowledge base file into topic-sized chunks.
    Each chunk keeps its 'TOPIC:' heading as metadata, which gives every
    retrieved chunk a traceable label (used later to explain *why* a
    question was generated)."""
    blocks = re.split(r"\n(?=TOPIC:)", raw_text.strip())
    chunks = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        topic_match = re.match(r"TOPIC:\s*(.+)", block)
        topic = topic_match.group(1).strip() if topic_match else "General"
        body = re.sub(r"^TOPIC:.*\n?", "", block).strip()
        chunks.append({"topic": topic, "text": body})
    return chunks


def build_index_for_role(role_id: str):
    """Builds (or rebuilds) the FAISS index for a single role's knowledge base file."""
    kb_path = os.path.join(KNOWLEDGE_BASE_DIR, f"{role_id}.txt")
    if not os.path.exists(kb_path):
        raise FileNotFoundError(f"No knowledge base file for role '{role_id}' at {kb_path}")

    with open(kb_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    chunks = chunk_document(raw_text)
    embedder = get_embedder()
    texts_to_embed = [f"{c['topic']}. {c['text']}" for c in chunks]
    embeddings = embedder.encode(texts_to_embed, normalize_embeddings=True)
    embeddings = np.array(embeddings, dtype="float32")

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # cosine similarity via normalized inner product
    index.add(embeddings)

    os.makedirs(INDEX_DIR, exist_ok=True)
    faiss.write_index(index, os.path.join(INDEX_DIR, f"{role_id}.index"))
    with open(os.path.join(INDEX_DIR, f"{role_id}.json"), "w", encoding="utf-8") as f:
        json.dump(chunks, f)

    return len(chunks)


def build_all_indexes():
    results = {}
    for fname in os.listdir(KNOWLEDGE_BASE_DIR):
        if fname.endswith(".txt"):
            role_id = fname[:-4]
            results[role_id] = build_index_for_role(role_id)
    return results


if __name__ == "__main__":
    print(build_all_indexes())
