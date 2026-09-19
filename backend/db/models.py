# WHAT: SQLAlchemy ORM models for query audit logging and escalation ticket tracking.
# WHY: Implements Layer 5 Relational DB & SQLite Audit Logging according to Section 5 of the architecture spec.
#      Maintains a persistent record of all incoming student interactions (queries, language, latency,
#      retrieval sources, grounding evaluations) and captures unresolvable queries into an administrative
#      escalation queue for offline staff triage and RAGAS evaluation benchmarking.

from datetime import datetime
from typing import Dict, Any
from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

# WHAT: Base class for declarative SQLAlchemy model mappings.
# WHY: Establishes the shared metadata catalog used by Alembic/SQLAlchemy to generate SQLite tables.
Base = declarative_base()


# WHAT: Relational model representing interaction telemetry for every student query.
# WHY: Records end-to-end execution details (language detection, contextual rewrites, retrieved chunk citations,
#      relevance and hallucination grading, OCR methods, latency) for auditing and RAGAS evaluation.
class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False, default="default_session")
    user_query = Column(Text, nullable=False)
    detected_language = Column(String(10), nullable=True)
    rewritten_query = Column(Text, nullable=True)
    retrieved_sources = Column(Text, nullable=True)   # Serialized JSON array of source filenames/citations
    relevance_score = Column(Float, nullable=True)
    generated_response = Column(Text, nullable=True)
    is_grounded = Column(Integer, nullable=True)      # 1 = grounded, 0 = failed factuality check
    ocr_method = Column(String(50), nullable=True)    # Tracks extraction path: 'pymupdf', 'tesseract', 'pixtral'
    latency_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())

    # WHAT: Serialization helper converting the QueryLog ORM instance into a JSON-compatible Python dictionary.
    # WHY: Simplifies data delivery across Flask REST API endpoints and RAGAS evaluation exporters.
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_query": self.user_query,
            "detected_language": self.detected_language,
            "rewritten_query": self.rewritten_query,
            "retrieved_sources": self.retrieved_sources,
            "relevance_score": self.relevance_score,
            "generated_response": self.generated_response,
            "is_grounded": bool(self.is_grounded) if self.is_grounded is not None else None,
            "ocr_method": self.ocr_method,
            "latency_ms": self.latency_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# WHAT: Relational model capturing unresolved or out-of-domain queries routed to the escalation desk.
# WHY: When student queries cannot be answered with high confidence (>0.70 relevance) from available notices,
#      the system halts generation to prevent hallucination and persists an escalation ticket for staff review.
class EscalationTicket(Base):
    __tablename__ = "escalation_tickets"

    ticket_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False, default="default_session")
    unresolved_query = Column(Text, nullable=False)
    detected_language = Column(String(10), nullable=True)
    failure_reason = Column(Text, nullable=True)
    status = Column(String(50), default="PENDING_STAFF_REVIEW", server_default="PENDING_STAFF_REVIEW")
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())

    # WHAT: Serialization helper converting the EscalationTicket ORM instance into a JSON-compatible dictionary.
    # WHY: Provides structured data payloads for the administrative review endpoint (GET /api/unresolved).
    def to_dict(self) -> Dict[str, Any]:
        return {
            "ticket_id": self.ticket_id,
            "session_id": self.session_id,
            "unresolved_query": self.unresolved_query,
            "detected_language": self.detected_language,
            "failure_reason": self.failure_reason,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# WHAT: Relational model capturing student thumbs-up/down feedback on generated answers.
# WHY: Stores explicit human evaluation ratings in SQLite to enable RAGAS calibration and continuous feedback loops.
class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=True, default="default_session")
    query_id = Column(Integer, nullable=True)
    rating = Column(Integer, nullable=False)          # 1 = thumbs-up (+1), 0 or -1 = thumbs-down
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())

    # WHAT: Serialization helper converting UserFeedback ORM instance into a JSON-compatible dictionary.
    # WHY: Provides structured data payloads for administrative analytics and feedback inspection.
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "query_id": self.query_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

