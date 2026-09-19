# WHAT: Assembly and compilation of the full LangGraph Agentic Self-Corrective Chatbot pipeline.
# WHY: Implements Layer 4 LangGraph Self-Corrective Decision Engine according to Section III-D of the architecture spec.
#      Orchestrates the entire multi-layer query flow:
#      Layer 3 (Linguistic Pre-processing) -> Layer 2 (Hybrid Retrieval: BGE-M3 + BM25 + RRF + Cross-Encoder) ->
#      Node 1 (Relevance Grader) -> Node 2 (Reformulation Loop) / Node 3 (Grounded Generation) ->
#      Node 4 (Factuality Grader) -> Node 5 (Language Validator) or Escalation Node.

from typing import Dict, Any
from langgraph.graph import StateGraph, END

from agent.state import AgentState
from agent.nodes import (
    relevance_grader_node,
    reformulation_node,
    grounded_generator_node,
    hallucination_grader_node,
    language_validator_node,
)
from agent.edges import route_after_grader, route_after_hallucination_check

from retrieval.embedder import dense_search
from retrieval.sparse_search import sparse_search
from retrieval.rrf_fusion import reciprocal_rank_fusion
from retrieval.reranker import rerank
from linguistic.detector import detect_language
from linguistic.normalizer import normalize_query
from linguistic.query_rewriter import rewrite_query


# WHAT: Entry node executing Layer 3 Linguistic Pre-Processing.
# WHY: Runs before any retrieval is performed. Detects language ('en' or 'hi'), normalizes colloquial
#      Hinglish idioms into canonical institutional English concepts, and resolves conversational
#      pronoun references into self-contained standalone search queries.
def linguistic_preprocessing_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Entry Node: Runs language detection, Hinglish normalization, and contextual query rewriting.
    """
    query = state.get("original_query", "")
    lang = detect_language(query)
    normalized = normalize_query(query, lang)
    rewritten = rewrite_query(normalized, state.get("conversation_history", []))

    return {
        **state,
        "detected_language": lang,
        "normalized_query": normalized,
        "rewritten_query": rewritten
    }


# WHAT: Retrieval node executing Layer 2 Hybrid Search across ChromaDB and BM25.
# WHY: Executes dual-index retrieval using rewritten query:
#      1. BGE-M3 dense semantic search in ChromaDB.
#      2. BM25 sparse keyword search for circular numbers and dates.
#      3. RRF score fusion (k=60) combining top-10 candidates.
#      4. Cross-encoder re-ranking (BAAI/bge-reranker-v2-m3) yielding top-3 verified passages.
def hybrid_retrieval_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retrieval Node: Dense + sparse hybrid retrieval with RRF fusion and cross-encoder re-ranking.
    """
    query = state.get("rewritten_query") or state.get("original_query", "")
    dense = dense_search(query)
    sparse = sparse_search(query)
    fused = reciprocal_rank_fusion(dense, sparse)
    reranked = rerank(query, fused)

    return {
        **state,
        "retrieved_chunks": reranked,
        "retry_count": state.get("retry_count", 0)
    }


# WHAT: Terminal node handling unresolvable queries by halting generation and issuing official contact details.
# WHY: When information is genuinely absent after query reformulation and search fallback,
#      the bot prevents hallucinations by halting generation, logging the ticket to SQLite,
#      and providing students with physical office hours and administrative email contacts.
def escalation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Escalation Node: Halts generation on out-of-domain queries and issues institutional contact card.
    """
    try:
        from db.database import log_escalation
        log_escalation(state)
    except Exception:
        # SQLite database logger will be fully active upon Milestone 6 completion
        pass

    escalation_message = (
        "I was unable to find reliable information for your query in the available notices. "
        "Please contact the administrative office directly:\n"
        "[Office] Room 101, Admin Block | [Hours] 9 AM - 5 PM (Mon-Fri) | [Email] admin@mait.ac.in"
    )
    return {
        **state,
        "final_response": escalation_message,
        "escalated": True
    }


# WHAT: LangGraph StateGraph pipeline construction and compilation.
# WHY: Assembles the 5-node self-corrective cyclical state machine with conditional routing edges.
workflow = StateGraph(AgentState)

# Register all graph nodes
workflow.add_node("linguistic_preprocess", linguistic_preprocessing_node)
workflow.add_node("hybrid_retrieval", hybrid_retrieval_node)
workflow.add_node("relevance_grader", relevance_grader_node)
workflow.add_node("reformulation", reformulation_node)
workflow.add_node("generator", grounded_generator_node)
workflow.add_node("hallucination_grader", hallucination_grader_node)
workflow.add_node("language_validator", language_validator_node)
workflow.add_node("escalation", escalation_node)

# Set graph entry point
workflow.set_entry_point("linguistic_preprocess")

# Core sequential pipeline edges
workflow.add_edge("linguistic_preprocess", "hybrid_retrieval")
workflow.add_edge("hybrid_retrieval", "relevance_grader")

# Conditional routing from Node 1 (Relevance Grader)
workflow.add_conditional_edges("relevance_grader", route_after_grader, {
    "generate": "generator",
    "reformulate": "reformulation",
    "escalate": "escalation"
})

# Reformulation loop back to relevance evaluation
workflow.add_edge("reformulation", "relevance_grader")

# Generation to Factuality Verification
workflow.add_edge("generator", "hallucination_grader")

# Conditional routing from Node 4 (Hallucination Grader)
workflow.add_conditional_edges("hallucination_grader", route_after_hallucination_check, {
    "validate_language": "language_validator",
    "regenerate": "generator"
})

# Terminal endpoints
workflow.add_edge("language_validator", END)
workflow.add_edge("escalation", END)

# WHAT: Compiled LangGraph runnable instance.
# WHY: Ready for synchronous or asynchronous invocation by Flask REST API or test scripts.
chatbot_agent = workflow.compile()
