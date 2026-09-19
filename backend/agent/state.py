# WHAT: LangGraph AgentState TypedDict definition tracking the full lifecycle of a student query.
# WHY: Implements Layer 4 LangGraph Self-Corrective Engine according to Section III-D of the architecture spec.
#      A stateful agentic workflow requires an explicit typed state container passed between all nodes.
#      The state preserves original and pre-processed linguistic inputs, retrieved context passages,
#      evaluator scores, retry bounds, citation metadata, and final synthesized outputs.

from typing import TypedDict, List, Dict, Any, Optional

# WHAT: Explicit state definition for the 5-node LangGraph self-corrective workflow.
# WHY: Uses TypedDict with total=False to permit incremental state updates across sequential graph nodes
#      without requiring all fields to be initialized at invocation time.
class AgentState(TypedDict, total=False):
    # ── User Input & Linguistic Pre-Processing (Layer 3) ───────────────────
    session_id: str                             # Unique conversation session identifier
    original_query: str                         # Raw user query as submitted by the student
    normalized_query: str                       # Phonetically normalized query (Hinglish -> English concepts)
    detected_language: str                      # Source language code ('en' or 'hi')
    conversation_history: List[Dict[str, str]]  # Prior multi-turn conversational messages

    # ── Context Resolution & Hybrid Retrieval (Layer 2) ───────────────────
    rewritten_query: str                        # Standalone question with resolved conversational pronouns
    retrieved_chunks: List[Dict[str, Any]]      # Verified top-k context chunks from cross-encoder re-ranking
    relevance_score: float                      # Normalized relevance score assessed by Node 1
    retry_count: int                            # Number of reformulation attempts (capped at MAX_RETRY_COUNT)
    used_live_scraper: bool                     # Flag indicating whether live web fallback has been triggered
    ocr_method: str                             # OCR extraction path ('pymupdf', 'tesseract', 'pixtral')

    # ── Verification & Generation (Layer 4) ───────────────────────────────
    draft_response: str                         # Grounded response candidate synthesized by Mistral 7B
    citations: List[Dict[str, Any]]             # Granular citation references (source, page, circular_num, date)
    is_grounded: bool                           # Hallucination assessment (True if facts verified in context)
    escalated: bool                             # Escalation trigger flag (True if query unresolvable in notices)
    final_response: str                         # Final validated response delivered to the student UI
    latency_ms: float                           # Overall response latency in milliseconds (Layer 5 telemetry)
