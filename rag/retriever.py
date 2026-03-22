import numpy as np
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("all-MiniLM-L6-v2")


def retrieve_chunks(query: str, index, chunks: list[str], top_k=4) -> list[str]:
    q_vec = np.array(embedder.encode([query])).astype("float32")
    _, indices = index.search(q_vec, top_k)
    return [chunks[i] for i in indices[0] if i < len(chunks)]