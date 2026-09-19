"""
Cross-Encoder Re-Ranking Module.
Uses BAAI/bge-reranker-v2-m3 cross-encoder to evaluate query-document pairs
and produce the final top-3 highly relevant context passages.
"""
from typing import List, Dict, Any, Optional
from sentence_transformers import CrossEncoder

try:
    from config import RERANKER_MODEL, TOP_K_FINAL
except ImportError:
    from backend.config import RERANKER_MODEL, TOP_K_FINAL

_reranker: Optional[CrossEncoder] = None


# WHAT: Lazy-load and cache the BAAI/bge-reranker-v2-m3 CrossEncoder model.
# WHY: Loading weights is computationally intensive; caching ensures fast sub-second scoring on subsequent user queries.
def get_reranker() -> CrossEncoder:
    """Lazy-load cross-encoder re-ranking model."""
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder(RERANKER_MODEL)
    return _reranker


# WHAT: Score (query, candidate_passage) pairs jointly through full cross-attention and return the top-3 passages.
# WHY: Bi-encoders (like BGE-M3) encode query and passage independently; cross-encoders process query and text
#      together through all transformer layers, capturing nuanced token interactions and stripping out background noise.
def rerank(
    query: str,
    candidates: List[Dict[str, Any]],
    top_k: int = TOP_K_FINAL
) -> List[Dict[str, Any]]:
    """
    Re-rank candidate passages against the query using cross-encoder attention.

    Args:
        query: Student or reformulated user query string.
        candidates: List of fused candidate chunk dictionaries from RRF.
        top_k: Number of final passages to retain (default: 3).

    Returns:
        Top-k passages sorted by descending cross-encoder relevance score.
    """
    if not candidates:
        return []

    try:
        reranker = get_reranker()
        pairs = [(query, c["text"]) for c in candidates]
        scores = reranker.predict(pairs)

        # WHAT: Attach the cross-encoder relevance score to each candidate dict and sort in descending order.
        # WHY: Downstream LangGraph evaluation nodes (e.g., Node 1 Relevance Grader) inspect rerank_score directly.
        scored_candidates = []
        for score, cand in zip(scores, candidates):
            item = dict(cand)
            item["rerank_score"] = round(float(score), 4)
            scored_candidates.append(item)

        ranked = sorted(scored_candidates, key=lambda x: x["rerank_score"], reverse=True)
        return ranked[:top_k]

    except Exception as exc:
        print(f"[RERANKER] CrossEncoder scoring failed ({exc}). Falling back to RRF rank order.")
        # Fallback to existing RRF rank order if model fails
        return candidates[:top_k]
