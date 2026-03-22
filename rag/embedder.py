import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# load once at module level
embedder = SentenceTransformer("all-MiniLM-L6-v2")


def build_faiss_index(chunks: list[str]):
    print("Building embeddings...")
    vecs = embedder.encode(chunks, show_progress_bar=False)
    vecs = np.array(vecs).astype("float32")

    index = faiss.IndexFlatL2(vecs.shape[1])
    index.add(vecs)

    print(f"Index ready — {index.ntotal} vectors")
    return index, chunks