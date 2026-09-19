# WHAT: Conditional routing functions determining transitions between LangGraph nodes.
# WHY: Implements Layer 4 LangGraph Self-Corrective Decision Engine according to Section III-D of the architecture spec.
#      Conditional edges inspect evaluation scores (relevance, hallucination) and retry counters
#      to dynamically decide whether the agent proceeds to generation, attempts query reformulation,
#      triggers regeneration, or halts and escalates to human administrative staff.

from typing import Dict, Any
from config import RELEVANCE_THRESHOLD, MAX_RETRY_COUNT


# WHAT: Determines routing after Node 1 (Document Relevance Grader).
# WHY: Decision logic:
#      1. If relevance score >= RELEVANCE_THRESHOLD (0.70): sufficient factual grounding exists -> "generate".
#      2. If retry count has reached or exceeded MAX_RETRY_COUNT (2): prevent infinite loops and escalate -> "escalate".
#      3. Otherwise: context is deficient -> route to Node 2 for query reformulation and re-retrieval -> "reformulate".
def route_after_grader(state: Dict[str, Any]) -> str:
    """
    Evaluates relevance score and retry count after Node 1.
    Returns: 'generate', 'reformulate', or 'escalate'.
    """
    score = state.get("relevance_score", 0.0)
    retries = state.get("retry_count", 0)

    if score >= RELEVANCE_THRESHOLD:
        return "generate"

    if retries >= MAX_RETRY_COUNT:
        return "escalate"

    return "reformulate"


# WHAT: Determines routing after Node 4 (Hallucination and Factuality Grader).
# WHY: Decision logic:
#      1. If draft response is verified grounded in source passages -> proceed to Node 5 -> "validate_language".
#      2. If ungrounded claims are detected but retry limit is reached -> accept draft to avoid deadlocks -> "validate_language".
#      3. If ungrounded claims are detected and retries remain -> route back to Node 3 for re-synthesis -> "regenerate".
def route_after_hallucination_check(state: Dict[str, Any]) -> str:
    """
    Evaluates factuality verification and retry limits after Node 4.
    Returns: 'validate_language' or 'regenerate'.
    """
    is_grounded = state.get("is_grounded", False)
    retries = state.get("retry_count", 0)

    if is_grounded:
        return "validate_language"

    if retries >= MAX_RETRY_COUNT:
        # Accept after max retries to avoid infinite loops
        return "validate_language"

    return "regenerate"
