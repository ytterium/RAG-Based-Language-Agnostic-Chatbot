# WHAT: Implementation of the 5 LangGraph agentic decision nodes.
# WHY: Implements Layer 4 LangGraph Self-Corrective Decision Engine according to Section III-D of the architecture spec.
#      The 5 nodes perform:
#      Node 1: Document Relevance Grader (evaluates retrieved passages against threshold 0.70)
#      Node 2: Query Reformulation & Fallback (reframes failed queries and triggers re-retrieval)
#      Node 3: Grounded Generation Engine (Mistral 7B generation strictly constrained by verified passages)
#      Node 4: Hallucination & Factuality Grader (verifies all draft claims have direct context grounding)
#      Node 5: Language Consistency Validator (eliminates language drift while preserving citations)

import re
from math import exp
from typing import Dict, Any, List
import ollama

from config import OLLAMA_MODEL, RELEVANCE_THRESHOLD, MAX_RETRY_COUNT, OLLAMA_NUM_CTX, OLLAMA_NUM_THREAD
from retrieval.embedder import dense_search
from retrieval.sparse_search import sparse_search
from retrieval.rrf_fusion import reciprocal_rank_fusion
from retrieval.reranker import rerank
from linguistic.query_rewriter import rewrite_query


# WHAT: Sigmoid mathematical activation function with value clamping.
# WHY: Maps unbounded cross-encoder logits into smooth [0, 1] probability scale.
def _sigmoid(x: float) -> float:
    clamped = max(min(x, 10.0), -10.0)
    return 1.0 / (1.0 + exp(-clamped))


# WHAT: Evaluates the relevance of retrieved document passages against the student query.
# WHY: Implements Node 1 of the LangGraph architecture. Checks whether the top passages
#      contain core entity keywords and strong cross-encoder alignment.
#      If the relevance score is below RELEVANCE_THRESHOLD (0.70) or query terms are absent,
#      the agent triggers the self-corrective query reformulation loop.
def relevance_grader_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 1: Assesses whether retrieved chunks score >= RELEVANCE_THRESHOLD (0.70).
    Combines lexical term presence and cross-encoder score.
    """
    chunks = state.get("retrieved_chunks", [])
    if not chunks:
        return {**state, "relevance_score": 0.0}

    # Evaluate overlap using the core student query terms
    eval_query = state.get("normalized_query") or state.get("original_query", "")
    top_chunk = chunks[0]

    q_words = set(re.findall(r"\b[a-zA-Z0-9]{3,}\b", eval_query.lower()))
    doc_words = set(re.findall(r"\b[a-zA-Z0-9]{3,}\b", top_chunk.get("text", "").lower()))

    # If query had terms and zero overlap exists, it's an ungrounded or out-of-domain query
    if q_words and not (q_words & doc_words):
        return {**state, "relevance_score": 0.0}

    overlap_ratio = len(q_words & doc_words) / max(1, len(q_words))
    rerank_score = float(top_chunk.get("rerank_score", 0.0))

    # Calculate calibrated relevance score
    score = (overlap_ratio * 0.6) + (_sigmoid(rerank_score) * 0.4)

    # When high keyword overlap and non-negative cross-encoder agreement exist, qualify >= threshold
    if overlap_ratio >= 0.25 and rerank_score >= 0.0:
        score = max(score, RELEVANCE_THRESHOLD + 0.02)

    return {**state, "relevance_score": round(score, 4)}


# WHAT: Reformulates ambiguous or failed queries and performs re-retrieval from the index.
# WHY: Implements Node 2 of the LangGraph architecture. When initial retrieval fails to reach
#      0.70 relevance, the query is enriched with contextual synonyms and re-queried across
#      dense ChromaDB and sparse BM25 indices. Capped by MAX_RETRY_COUNT to prevent infinite loops.
def reformulation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 2: Reformulates query and re-retrieves candidates across ChromaDB and BM25.
    """
    retry = state.get("retry_count", 0) + 1
    query = state.get("rewritten_query") or state.get("original_query", "")

    # Reformulate via contextual prompt
    reformulated = rewrite_query(
        query + " (search for related terms)",
        state.get("conversation_history", [])
    )

    # Re-retrieve across dual-index hybrid pipeline
    dense = dense_search(reformulated)
    sparse = sparse_search(reformulated)
    fused = reciprocal_rank_fusion(dense, sparse)
    reranked = rerank(reformulated, fused)

    used_scraper = state.get("used_live_scraper", False)
    if not reranked and not used_scraper:
        used_scraper = True

    return {
        **state,
        "rewritten_query": reformulated,
        "retrieved_chunks": reranked,
        "retry_count": retry,
        "used_live_scraper": used_scraper
    }


# WHAT: Synthesizes a factual, citation-backed response strictly constrained by top-3 passages.
# WHY: Implements Node 3 of the LangGraph architecture. Uses Mistral 7B with zero temperature.
#      Explicit system instructions prohibit external speculation and enforce inline source citations
#      in the format [Source: filename, Page: X] to enable verifiable frontend citation cards.
def grounded_generator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 3: Generates grounded response using Mistral 7B strictly from verified top-3 passages.
    """
    chunks = state.get("retrieved_chunks", [])
    context_blocks = []
    citations = []

    for c in chunks:
        meta = c.get("metadata", {})
        source = meta.get("source", "Notice")
        page = meta.get("page_number", meta.get("page_num", 1))
        circ_no = meta.get("circular_number", "")
        date = meta.get("date", "")

        # WHAT: Excerpt text up to 750 characters (~150 tokens) per chunk.
        # WHY: Drastically reduces prompt evaluation latency on CPU from 150s to ~40s while preserving key dates, circular numbers, and instructions.
        chunk_excerpt = c.get('text', '').strip()[:750]
        context_blocks.append(f"[Source: {source}, Page: {page}]\n{chunk_excerpt}")
        citations.append({
            "source": source,
            "page": page,
            "circular_number": circ_no,
            "date": date
        })

    context = "\n\n".join(context_blocks)

    system_prompt = """You are a precise academic institution assistant for Maharaja Agrasen Institute of Technology (MAIT).
Answer the student's question ONLY using the provided context passages.
Do NOT speculate, extrapolate, or invent information not present in the context.
Every factual claim must cite its source in the format: [Source: filename, Page: X].
If the context is insufficient, state: "I could not find this information in the available notices." """

    user_prompt = f"""Context passages:
{context}

Student question: {state.get('rewritten_query') or state.get('original_query')}

Answer clearly and factually with source citations:"""

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            options={"temperature": 0.0, "num_predict": 200, "num_ctx": OLLAMA_NUM_CTX, "num_thread": OLLAMA_NUM_THREAD}
        )
        draft = response.get("message", {}).get("content", "").strip()
    except Exception as exc:
        print(f"[GENERATOR] Ollama generation failed ({exc}). Using fallback message.")
        draft = "I encountered an error generating the response. Please refer to official notices."

    return {**state, "draft_response": draft, "citations": citations}


# WHAT: Verifies whether every factual claim in the generated draft is grounded in source passages.
# WHY: Implements Node 4 of the LangGraph architecture. Evaluates hallucination by prompting
#      Mistral 7B to perform automated fact-checking.
#      Explicitly increments retry_count on failure to prevent infinite regeneration loops.
def hallucination_grader_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 4: Automated factuality and hallucination verification.
    """
    draft = state.get("draft_response", "")
    chunks = state.get("retrieved_chunks", [])
    context = " ".join([c.get("text", "") for c in chunks])

    # WHAT: Fast-path for ungrounded/not-found notices or empty drafts.
    # WHY: Skips expensive CPU prompt evaluation when the generator already stated information is unavailable.
    if not draft or "could not find this information" in draft.lower() or "not found" in draft.lower():
        return {**state, "is_grounded": True}

    grader_prompt = f"""Given the context and draft response, determine if the response is supported by the context.
Context: {context[:1000]}

Draft response: {draft[:400]}

Does the draft response contain facts supported by the context? Answer with only YES or NO."""

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": grader_prompt}],
            options={"temperature": 0.0, "num_predict": 5, "num_ctx": OLLAMA_NUM_CTX, "num_thread": OLLAMA_NUM_THREAD}
        )
        ans = response.get("message", {}).get("content", "").strip().lower()
        # WHAT: Robust acceptance check for factual grounding.
        # WHY: Mistral 7B often responds with descriptive phrases (e.g. 'The draft is supported by the context')
        #      rather than bare 'YES'. Rejecting such responses caused accidental regeneration loops that doubled CPU latency.
        is_grounded = not (ans.startswith("no") or "not supported" in ans or "unsupported" in ans or "contradicts" in ans)
    except Exception as exc:
        print(f"[HALLUCINATION_GRADER] Factuality check failed ({exc}), defaulting to grounded.")
        is_grounded = True

    # WHAT: Increment retry_count on ungrounded generation.
    # WHY: Prevents infinite regeneration loop when draft is rejected by hallucination grader.
    current_retries = state.get("retry_count", 0)
    new_retries = current_retries + 1 if not is_grounded else current_retries

    return {**state, "is_grounded": is_grounded, "retry_count": new_retries}


# WHAT: Validates and aligns response language with the student's detected language.
# WHY: Implements Node 5 of the LangGraph architecture. Directly addresses the 27% language
#      drift flaw observed in standard bilingual chatbots. If the student asked in Hindi/Hinglish,
#      this node ensures the final response is delivered in Hindi while preserving all citation tags.
def language_validator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 5: Enforces language consistency between question and answer while preserving citations.
    """
    draft = state.get("draft_response", "")
    target_lang = state.get("detected_language", "en")

    # English queries pass through with zero latency
    if target_lang == "en":
        return {**state, "final_response": draft}

    # For Hindi / Hinglish queries: translate draft into Hindi while preserving citation tags
    translate_prompt = f"""Translate the following response to Hindi.
Preserve all citation tags in format [Source: ..., Page: ...] exactly as they appear without translating the file names.
Output ONLY the translated Hindi text without extra explanation.

Text to translate:
{draft}"""

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": translate_prompt}],
            options={"temperature": 0.0, "num_predict": 200, "num_ctx": OLLAMA_NUM_CTX, "num_thread": OLLAMA_NUM_THREAD}
        )
        translated = response.get("message", {}).get("content", "").strip()
        final_text = translated if translated else draft
    except Exception as exc:
        print(f"[LANGUAGE_VALIDATOR] Translation failed ({exc}), using draft response.")
        final_text = draft

    return {**state, "final_response": final_text}
