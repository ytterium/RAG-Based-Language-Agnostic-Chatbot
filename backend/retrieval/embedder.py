"""
BGE-M3 Dense Embedding Wrapper and ChromaDB Vector Store Interface.
Handles persistent indexing and multilingual semantic vector search.
"""
import os
from typing import List, Dict, Any, Optional
import chromadb
from sentence_transformers import SentenceTransformer

try:
    from config import BGE_M3_MODEL, CHROMADB_PATH, CHROMA_COLLECTION_NAME, TOP_K_FUSED
except ImportError:
    from backend.config import BGE_M3_MODEL, CHROMADB_PATH, CHROMA_COLLECTION_NAME, TOP_K_FUSED

_embed_model: Optional[SentenceTransformer] = None
_chroma_client: Optional[chromadb.PersistentClient] = None
_collection = None


# WHAT: Lazy-load and cache the BGE-M3 SentenceTransformer model in global memory.
# WHY: Avoids expensive re-initialization (~2.24 GB weight loading) on every individual retrieval request.
def get_embed_model() -> SentenceTransformer:
    """Lazy-load BGE-M3 embedding model."""
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer(BGE_M3_MODEL)
    return _embed_model


# WHAT: Initialize or retrieve the persistent ChromaDB collection instance.
# WHY: PersistentClient saves vectors to disk (data/processed/chromadb/) ensuring index survives server restarts.
def get_collection():
    """Lazy-load ChromaDB persistent client and collection."""
    global _chroma_client, _collection
    if _collection is None:
        os.makedirs(CHROMADB_PATH, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=CHROMADB_PATH)
        _collection = _chroma_client.get_or_create_collection(CHROMA_COLLECTION_NAME)
    return _collection


# WHAT: Generate 1024-dim BGE-M3 dense embeddings for notice chunks and index them into ChromaDB.
# WHY: Dense vectors capture cross-lingual semantic intent (Hindi, Hinglish, English) without exact keyword matching.
def build_chromadb_index(chunks: List[Dict[str, Any]]) -> None:
    """
    Index all document chunks into ChromaDB.
    Called by run_ingestion.py.
    """
    if not chunks:
        print("[EMBEDDER] No chunks to index into ChromaDB.")
        return

    model = get_embed_model()
    collection = get_collection()

    texts = [c["text"] for c in chunks]
    ids = [c["metadata"]["chunk_id"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    # WHAT: Batch-encode chunk texts with normalization.
    # WHY: L2-normalized embeddings enable cosine similarity computation via Euclidean/dot product metrics.
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        batch_size=32,
        show_progress_bar=True
    ).tolist()

    # WHAT: Deduplicate IDs to strictly enforce ChromaDB's unique ID constraint.
    # WHY: Prevents DuplicateIDError when multiple chunks or notices originate from the same base URL/source.
    seen_ids = set()
    unique_ids = []
    for i, cid in enumerate(ids):
        unique_id = cid
        counter = 1
        while unique_id in seen_ids:
            unique_id = f"{cid}_{counter}"
            counter += 1
        seen_ids.add(unique_id)
        metadatas[i]["chunk_id"] = unique_id
        unique_ids.append(unique_id)

    # WHAT: Upsert unique documents into ChromaDB.
    # WHY: Upsert guarantees idempotency so repeated ingestion runs safely refresh data without duplicate key errors.
    collection.upsert(
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=unique_ids
    )


# WHAT: Encode incoming user query with BGE-M3 and perform approximate nearest neighbor search in ChromaDB.
# WHY: Fetches the top-k semantically closest context passages regardless of exact token/spelling differences.
def dense_search(query: str, top_k: int = TOP_K_FUSED) -> List[Dict[str, Any]]:
    """
    Search ChromaDB using BGE-M3 embeddings.
    Returns list of matching chunk dicts with similarity score.
    """
    collection = get_collection()
    total_docs = collection.count()
    if total_docs == 0:
        return []

    model = get_embed_model()
    q_embedding = model.encode([query], normalize_embeddings=True).tolist()

    k = min(top_k, total_docs)
    results = collection.query(query_embeddings=q_embedding, n_results=k)

    if not results or not results["documents"] or not results["documents"][0]:
        return []

    return [
        {
            "text": doc,
            "metadata": meta,
            "score": round(1.0 - dist, 4),
            "rank_index": i
        }
        for i, (doc, meta, dist) in enumerate(
            zip(results["documents"][0], results["metadatas"][0], results["distances"][0])
        )
    ]
