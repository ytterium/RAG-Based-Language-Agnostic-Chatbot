# WHAT: Database connection manager, session lifecycle handlers, and CRUD operations for SQLite audit logging.
# WHY: Implements Layer 5 Relational DB & SQLite Audit Logging according to Section 5 of the architecture spec.
#      Provides thread-safe session management for SQLite, persist query interactions (latency, grounding, citations)
#      for RAGAS evaluation, and queues unresolved queries for administrative staff triage.

import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from config import SQLITE_DB_PATH
from db.models import Base, QueryLog, EscalationTicket, UserFeedback

# Global singleton handles for engine and session factory
_engine = None
_SessionLocal = None


# WHAT: Obtains or lazily initializes the SQLAlchemy database engine.
# WHY: Reuses database connection pool while allowing configurable path overrides for unit testing.
def get_engine(db_path: Optional[str] = None):
    global _engine, _SessionLocal
    target_path = db_path or SQLITE_DB_PATH
    
    # If engine is already configured for the target path, return existing instance
    if _engine is not None and not db_path:
        return _engine
        
    db_dir = os.path.dirname(os.path.abspath(target_path))
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
        
    engine = create_engine(
        f"sqlite:///{target_path}",
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    if not db_path:
        _engine = engine
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
    return engine


# WHAT: Obtains or creates the session factory bound to the active engine.
# WHY: Centralizes session creation for thread-safe operations across Flask requests and LangGraph background nodes.
def get_session_factory(db_path: Optional[str] = None):
    global _SessionLocal
    if _SessionLocal is None or db_path:
        engine = get_engine(db_path)
        factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        if not db_path:
            _SessionLocal = factory
        return factory
    return _SessionLocal


# WHAT: Initializes the SQLite database schema by creating all tables defined in models.py.
# WHY: Guarantees that query_logs and escalation_tickets tables exist prior to system query processing.
def init_db(db_path: Optional[str] = None):
    engine = get_engine(db_path)
    Base.metadata.create_all(bind=engine)
    return engine


# WHAT: Context manager providing an isolated, transactional database session.
# WHY: Enforces ACID guarantees: commits automatically on success, rolls back on error, and guarantees connection release.
@contextmanager
def get_session(db_path: Optional[str] = None):
    session_factory = get_session_factory(db_path)
    session: Session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# WHAT: Extracts interaction telemetry from LangGraph AgentState and persists an audit log into query_logs.
# WHY: Implements Layer 5 query logging to capture end-to-end telemetry (language, rewrites, citations,
#      grounding flags, relevance score, latency) needed for IEEE paper evaluation and RAGAS benchmarking.
def log_query(
    state: Dict[str, Any],
    session_id: Optional[str] = None,
    latency_ms: Optional[float] = None,
    ocr_method: Optional[str] = None
) -> int:
    init_db()

    resolved_session_id = session_id or state.get("session_id") or "default_session"
    user_query = state.get("original_query", "")
    detected_lang = state.get("detected_language")
    rewritten = state.get("rewritten_query")

    # Extract distinct source document names from citations or retrieved chunks
    sources: List[str] = []
    citations = state.get("citations") or []
    for c in citations:
        if isinstance(c, dict):
            src = c.get("source")
            if src and src not in sources:
                sources.append(src)
        elif isinstance(c, str) and c not in sources:
            sources.append(c)

    if not sources:
        chunks = state.get("retrieved_chunks") or []
        for ch in chunks:
            if isinstance(ch, dict):
                meta = ch.get("metadata", {})
                src = meta.get("source") or meta.get("file_name")
                if src and src not in sources:
                    sources.append(src)

    retrieved_sources_str = json.dumps(sources)

    relevance = state.get("relevance_score")
    if relevance is not None:
        try:
            relevance = float(relevance)
        except (ValueError, TypeError):
            relevance = 0.0

    generated_resp = state.get("final_response") or state.get("draft_response")

    grounded_flag = state.get("is_grounded")
    is_grounded_val = 1 if grounded_flag is True else (0 if grounded_flag is False else None)

    # Determine OCR method from chunks if available
    resolved_ocr_method = ocr_method or state.get("ocr_method")
    if not resolved_ocr_method:
        chunks = state.get("retrieved_chunks") or []
        if chunks and isinstance(chunks[0], dict):
            resolved_ocr_method = chunks[0].get("metadata", {}).get("ocr_method")
    if not resolved_ocr_method:
        resolved_ocr_method = "adaptive_router"

    resolved_latency = latency_ms if latency_ms is not None else state.get("latency_ms", 0.0)

    with get_session() as session:
        log_entry = QueryLog(
            session_id=resolved_session_id,
            user_query=user_query,
            detected_language=detected_lang,
            rewritten_query=rewritten,
            retrieved_sources=retrieved_sources_str,
            relevance_score=relevance,
            generated_response=generated_resp,
            is_grounded=is_grounded_val,
            ocr_method=resolved_ocr_method,
            latency_ms=float(resolved_latency),
            created_at=datetime.utcnow(),
        )
        session.add(log_entry)
        session.flush()
        log_id = log_entry.id

    return log_id


# WHAT: Persists an unresolved or out-of-domain query into the escalation_tickets table.
# WHY: Implements Layer 5 escalation logging when retrieval fails to reach the 0.70 relevance threshold,
#      capturing the student query for human administrative review and notice corpus enhancement.
def log_escalation(
    state: Dict[str, Any],
    session_id: Optional[str] = None,
    failure_reason: Optional[str] = None
) -> int:
    init_db()

    resolved_session_id = session_id or state.get("session_id") or "default_session"
    unresolved = state.get("original_query") or state.get("rewritten_query", "")
    detected_lang = state.get("detected_language")

    if not failure_reason:
        relevance = state.get("relevance_score", 0.0)
        if relevance is not None and float(relevance) < 0.70:
            failure_reason = f"Low document relevance score ({float(relevance):.2f} < 0.70)"
        elif state.get("is_grounded") is False:
            failure_reason = "Factuality grader rejected draft due to ungrounded claims"
        else:
            failure_reason = "Information unresolvable in institutional notice repository"

    with get_session() as session:
        ticket = EscalationTicket(
            session_id=resolved_session_id,
            unresolved_query=unresolved,
            detected_language=detected_lang,
            failure_reason=failure_reason,
            status="PENDING_STAFF_REVIEW",
            created_at=datetime.utcnow(),
        )
        session.add(ticket)
        session.flush()
        ticket_id = ticket.ticket_id

    return ticket_id


# WHAT: Fetches unresolved student escalation tickets ordered by descending submission date.
# WHY: Implements backend query retrieval for administrative staff review (Milestone 7: GET /api/unresolved).
def get_unresolved_tickets(limit: int = 50, status: str = "PENDING_STAFF_REVIEW") -> List[Dict[str, Any]]:
    init_db()
    with get_session() as session:
        query = session.query(EscalationTicket)
        if status:
            query = query.filter(EscalationTicket.status == status)
        tickets = query.order_by(EscalationTicket.ticket_id.desc()).limit(limit).all()
        return [t.to_dict() for t in tickets]


# WHAT: Updates the review status of an existing escalation ticket.
# WHY: Enables campus administrators to triage and mark tickets as 'RESOLVED' or 'IN_PROGRESS'.
def update_ticket_status(ticket_id: int, new_status: str) -> bool:
    init_db()
    with get_session() as session:
        ticket = session.query(EscalationTicket).filter(EscalationTicket.ticket_id == ticket_id).first()
        if ticket:
            ticket.status = new_status
            return True
        return False


# WHAT: Fetches historical query audit logs ordered by descending ID.
# WHY: Facilitates RAGAS evaluation dataset compilation and system telemetry inspection.
def get_query_logs(limit: int = 50) -> List[Dict[str, Any]]:
    init_db()
    with get_session() as session:
        logs = session.query(QueryLog).order_by(QueryLog.id.desc()).limit(limit).all()
        return [log.to_dict() for log in logs]


# WHAT: Records student thumbs-up/down feedback for a query into SQLite user_feedback table.
# WHY: Implements Milestone 7 POST /api/feedback persistence for user feedback analytics and RAGAS alignment.
def log_feedback(
    rating: int,
    session_id: Optional[str] = None,
    query_id: Optional[int] = None,
    comment: Optional[str] = None
) -> int:
    init_db()
    with get_session() as session:
        feedback = UserFeedback(
            session_id=session_id or "default_session",
            query_id=query_id,
            rating=int(rating),
            comment=comment,
            created_at=datetime.utcnow(),
        )
        session.add(feedback)
        session.flush()
        feedback_id = feedback.id
    return feedback_id


# WHAT: Fetches recorded user feedback entries from SQLite ordered by descending ID.
# WHY: Supports administrative inspection of student satisfaction and model response ratings.
def get_feedback_logs(limit: int = 50) -> List[Dict[str, Any]]:
    init_db()
    with get_session() as session:
        feedbacks = session.query(UserFeedback).order_by(UserFeedback.id.desc()).limit(limit).all()
        return [f.to_dict() for f in feedbacks]

