"""
Reciprocal Rank Fusion (RRF) Algorithm.
Combines ranked candidates from BGE-M3 dense semantic search and BM25 lexical sparse search.
Formula: RRF_score(d) = SUM_{m in models} [ 1 / (k + rank_m(d)) ]
Uses constant k=60 to balance high-ranking dense and exact lexical matches.
"""
from typing import List, Dict, Any

try:
    from config import RRF_K, TOP_K_FUSED
except ImportError:
    from backend.config import RRF_K, TOP_K_FUSED


# WHAT: Merges dense semantic hits and BM25 lexical hits using the standard Reciprocal Rank Fusion formula.
# WHY: Dense models output arbitrary cosine similarities while BM25 outputs unbounded TF-IDF scores.
#      RRF operates strictly on reciprocal rank orders (1 / (k + rank)), creating a normalized, scale-invariant
#      ensemble where documents scoring high in both dense and sparse retrieval are ranked highest.
def reciprocal_rank_fusion(
    dense_results: List[Dict[str, Any]],
    sparse_results: List[Dict[str, Any]],
    k: int = RRF_K,
    top_k: int = TOP_K_FUSED
) -> List[Dict[str, Any]]:
    """
    Fuse dense and sparse ranked retrieval lists using Reciprocal Rank Fusion.

    Args:
        dense_results: Ranked list of candidates from dense vector search.
        sparse_results: Ranked list of candidates from BM25 sparse search.
        k: Smoothing constant (default: 60).
        top_k: Maximum number of fused candidates to return (default: 10).

    Returns:
        List of fused chunk dictionaries sorted in descending order of RRF score.
    """
    scores: Dict[str, float] = {}
    chunk_map: Dict[str, Dict[str, Any]] = {}
    dense_ranks: Dict[str, int] = {}
    sparse_ranks: Dict[str, int] = {}

    # WHAT: Score dense search results according to their ranking positions.
    # WHY: Higher-ranked dense hits receive higher base RRF contributions.
    for rank_idx, result in enumerate(dense_results):
        chunk_id = result.get("metadata", {}).get("chunk_id") or str(hash(result.get("text", "")))
        rrf_contribution = 1.0 / (k + rank_idx + 1)
        scores[chunk_id] = scores.get(chunk_id, 0.0) + rrf_contribution
        chunk_map[chunk_id] = result
        dense_ranks[chunk_id] = rank_idx + 1

    # WHAT: Add BM25 sparse search score contributions to matching chunk IDs.
    # WHY: Chunks that match both semantic meaning AND exact keywords receive double score boosts.
    for rank_idx, result in enumerate(sparse_results):
        chunk_id = result.get("metadata", {}).get("chunk_id") or str(hash(result.get("text", "")))
        rrf_contribution = 1.0 / (k + rank_idx + 1)
        scores[chunk_id] = scores.get(chunk_id, 0.0) + rrf_contribution
        chunk_map[chunk_id] = result
        sparse_ranks[chunk_id] = rank_idx + 1

    # WHAT: Sort combined chunks by accumulated RRF score in descending order.
    # WHY: Prioritizes the strongest joint-agreement candidates for the downstream cross-encoder reranker.
    sorted_ids = sorted(scores.keys(), key=lambda cid: scores[cid], reverse=True)

    fused_candidates: List[Dict[str, Any]] = []
    for cid in sorted_ids[:top_k]:
        candidate = dict(chunk_map[cid])
        candidate["rrf_score"] = round(scores[cid], 5)
        candidate["dense_rank"] = dense_ranks.get(cid, None)
        candidate["sparse_rank"] = sparse_ranks.get(cid, None)
        fused_candidates.append(candidate)

    return fused_candidates
