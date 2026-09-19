# WHAT: Flask REST API application exposing the LangGraph self-corrective chatbot, health telemetry, and audit DB.
# WHY: Implements Layer 6 Backend API according to Section 5 of the architecture spec.
#      Serves as the bridge connecting the ReactJS frontend to the AI pipeline (LangGraph, ChromaDB, Ollama, SQLite).
#      Provides endpoints for student chat (/api/chat), operational health monitoring (/api/health),
#      administrative escalation review (/api/unresolved), and user evaluation feedback (/api/feedback).

import os
import sys
import time
import uuid
from typing import Dict, Any
from flask import Flask, request, jsonify
from flask_cors import CORS

# Ensure backend root is on Python sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config import OLLAMA_MODEL, CHROMA_COLLECTION_NAME
from agent.graph import chatbot_agent
from db.database import (
    init_db,
    get_unresolved_tickets,
    log_feedback,
    get_query_logs,
    update_ticket_status,
)
from retrieval.embedder import get_collection

# WHAT: Initialize the Flask application and configure cross-origin resource sharing (CORS).
# WHY: Allows the ReactJS frontend running on http://localhost:5173 to make cross-origin API calls without browser blocking.
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "*"]}})

# Initialize SQLite database schema on application startup
init_db()


# WHAT: Root index endpoint returning basic service metadata and API documentation link.
# WHY: Provides an immediate sanity check confirming the HTTP web server is active and responding.
@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "service": "RAG-Based Language Agnostic Chatbot API",
        "institution": "MAIT CSE (Team MNP059)",
        "version": "1.0.0",
        "status": "online",
        "endpoints": [
            "POST /api/chat",
            "GET /api/health",
            "GET /api/unresolved",
            "POST /api/feedback"
        ]
    }), 200


# WHAT: Health telemetry endpoint verifying readiness of Ollama, ChromaDB, and SQLite storage.
# WHY: Enables deployment health checks, frontend readiness polling, and automated container orchestration.
@app.route("/api/health", methods=["GET"])
def health_check():
    start_time = time.perf_counter()
    health_status: Dict[str, Any] = {
        "status": "ok",
        "model": OLLAMA_MODEL,
        "services": {}
    }

    # 1. Verify Ollama connectivity
    try:
        import ollama
        models_response = ollama.list()
        model_names = [m.get("model") or m.get("name", "") for m in models_response.get("models", [])]
        health_status["services"]["ollama"] = {
            "status": "ok",
            "models_available": model_names,
            "target_model_ready": any(OLLAMA_MODEL in m for m in model_names)
        }
    except Exception as e:
        health_status["services"]["ollama"] = {
            "status": "degraded",
            "error": str(e)
        }

    # 2. Verify ChromaDB vector store
    try:
        col = get_collection()
        chunk_count = col.count()
        health_status["services"]["chromadb"] = {
            "status": "ok",
            "collection": CHROMA_COLLECTION_NAME,
            "chunks_count": chunk_count
        }
    except Exception as e:
        health_status["services"]["chromadb"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "degraded"

    # 3. Verify SQLite audit database
    try:
        init_db()
        health_status["services"]["sqlite"] = {
            "status": "ok"
        }
    except Exception as e:
        health_status["services"]["sqlite"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "degraded"

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
    health_status["latency_ms"] = latency_ms

    return jsonify(health_status), 200


# WHAT: Core conversational endpoint invoking the LangGraph Self-Corrective Decision Engine.
# WHY: Executes the end-to-end question answering pipeline: Layer 3 linguistic normalization and query rewriting,
#      Layer 2 hybrid dense-sparse retrieval and cross-encoder re-ranking, and Layer 4 grounded response synthesis,
#      returning verified citations, language tags, and escalation indicators to the React client.
@app.route("/api/chat", methods=["POST"])
def chat():
    start_time = time.perf_counter()
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "status": "error",
            "error": "Missing or invalid JSON request payload"
        }), 400

    query = data.get("query")
    if not query or not str(query).strip():
        return jsonify({
            "status": "error",
            "error": "The 'query' field is required and cannot be empty"
        }), 400

    session_id = data.get("session_id") or f"sess_{uuid.uuid4().hex[:10]}"
    history = data.get("history") or []

    # Assemble initial state for LangGraph workflow execution
    initial_state = {
        "original_query": str(query).strip(),
        "session_id": str(session_id),
        "conversation_history": history,
        "retry_count": 0,
        "used_live_scraper": False,
        "escalated": False
    }

    try:
        # Run state machine through compiled LangGraph graph
        result = chatbot_agent.invoke(initial_state)
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        response_payload = {
            "response": result.get("final_response", ""),
            "citations": result.get("citations", []),
            "detected_language": result.get("detected_language", "en"),
            "escalated": result.get("escalated", False),
            "session_id": result.get("session_id", session_id),
            "latency_ms": latency_ms
        }
        return jsonify(response_payload), 200

    except Exception as e:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return jsonify({
            "status": "error",
            "error": f"Agent execution encountered an error: {str(e)}",
            "latency_ms": latency_ms
        }), 500


# WHAT: Administrative endpoint fetching unresolved queries queued for human staff review.
# WHY: Implements staff triage functionality (Section III-D & Milestone 7) enabling campus administrators
#      to review inquiries where official notices lacked sufficient answers.
@app.route("/api/unresolved", methods=["GET"])
def unresolved_tickets():
    try:
        limit = request.args.get("limit", default=50, type=int)
        status_filter = request.args.get("status", default="PENDING_STAFF_REVIEW", type=str)
        
        # If 'all' is passed, fetch all tickets without status filtering
        effective_status = None if status_filter.lower() == "all" else status_filter

        tickets = get_unresolved_tickets(limit=limit, status=effective_status)
        return jsonify({
            "status": "ok",
            "count": len(tickets),
            "tickets": tickets
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": f"Failed to retrieve unresolved tickets: {str(e)}"
        }), 500


# WHAT: Student feedback collection endpoint recording thumbs up (+1) or thumbs down (-1/0) ratings.
# WHY: Stores explicit human evaluation ratings in SQLite to calculate deflection satisfaction
#      and provide ground-truth feedback for continuous prompt and retrieval optimization.
@app.route("/api/feedback", methods=["POST"])
def submit_feedback():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            "status": "error",
            "error": "Missing or invalid JSON request payload"
        }), 400

    rating = data.get("rating")
    if rating is None:
        return jsonify({
            "status": "error",
            "error": "The 'rating' field is required (e.g. 1 for thumbs-up, -1 or 0 for thumbs-down)"
        }), 400

    # Normalize boolean or numeric ratings
    try:
        if isinstance(rating, bool):
            norm_rating = 1 if rating else 0
        else:
            norm_rating = int(rating)
    except (ValueError, TypeError):
        return jsonify({
            "status": "error",
            "error": "Rating must be an integer (1 or 0/-1) or boolean"
        }), 400

    session_id = data.get("session_id")
    query_id = data.get("query_id")
    comment = data.get("comment")

    try:
        feedback_id = log_feedback(
            rating=norm_rating,
            session_id=session_id,
            query_id=query_id,
            comment=comment
        )
        return jsonify({
            "status": "ok",
            "message": "Feedback recorded successfully",
            "feedback_id": feedback_id
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": f"Failed to record feedback: {str(e)}"
        }), 500


# WHAT: Global unhandled exception handler converting Python errors into structured JSON responses.
# WHY: Prevents uncaught application errors from leaking raw server traces to frontend clients.
@app.errorhandler(Exception)
def handle_unexpected_error(e):
    return jsonify({
        "status": "error",
        "error": "An unexpected server error occurred",
        "details": str(e)
    }), 500


# WHAT: Main application execution entry point.
# WHY: Launches the Flask WSGI development server on port 5000 bound to all network interfaces.
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"[*] Starting MAIT Chatbot REST API server on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
