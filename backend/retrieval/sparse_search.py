"""
BM25 Lexical Sparse Search Retriever.
Indexes exact keywords, numerical dates, circular IDs, and form identifiers.
Complements dense semantic embeddings to prevent dilution of precise identifiers.
"""
import os
import pickle
from typing import List, Dict, Any, Tuple, Optional
from rank_bm25 import BM25Okapi

try:
    from config import BM25_STORE_PATH, TOP_K_FUSED
except ImportError:
    from backend.config import BM25_STORE_PATH, TOP_K_FUSED

_bm25: Optional[BM25Okapi] = None
_chunks: Optional[List[Dict[str, Any]]] = None


def build_bm25_index(chunks: List[Dict[str, Any]]) -> BM25Okapi:
    """
    Build BM25 index from a list of chunks.
    """
    texts = [c["text"] for c in chunks]
    tokenized_corpus = [t.lower().split() for t in texts]
    return BM25Okapi(tokenized_corpus)


def load_bm25() -> Tuple[Optional[BM25Okapi], List[Dict[str, Any]]]:
    """
    Load serialized BM25 index and chunk metadata from disk.
    """
    global _bm25, _chunks
    if _bm25 is None or _chunks is None:
        if not os.path.exists(BM25_STORE_PATH):
            return None, []
        with open(BM25_STORE_PATH, "rb") as f:
            data = pickle.load(f)
        _bm25 = data["bm25"]
        _chunks = data["chunks"]
    return _bm25, _chunks


def sparse_search(query: str, top_k: int = TOP_K_FUSED) -> List[Dict[str, Any]]:
    """
    Search BM25 lexical index for exact keywords, circular IDs, and dates.
    """
    bm25, chunks = load_bm25()
    if bm25 is None or not chunks:
        return []

    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)

    k = min(top_k, len(chunks))
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]

    return [
        {
            "text": chunks[i]["text"],
            "metadata": chunks[i]["metadata"],
            "score": float(scores[i]),
            "rank_index": idx
        }
        for idx, i in enumerate(top_indices)
    ]
