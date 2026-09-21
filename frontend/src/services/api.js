// WHAT: Axios HTTP client service communicating with the Flask backend REST API.
// WHY: Implements Layer 5 API integration layer connecting the ReactJS frontend to backend endpoints
//      (/api/chat, /api/health, /api/unresolved, /api/feedback) with centralized error handling and timeouts.

import axios from 'axios';

// WHAT: Base URL for Flask REST API service.
// WHY: Defaults to port 5000 where backend/app.py runs; supports override via Vite environment variables.
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// WHAT: Pre-configured Axios instance with reasonable timeout for LLM inference passes.
// WHY: Agentic pipeline (hybrid search + Mistral 7B + verification nodes) can take 5-15 seconds locally on CPU/GPU.
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 300 seconds (5 min) timeout for local CPU LLM inference passes
  headers: {
    'Content-Type': 'application/json',
  },
});

// WHAT: Send user query and session history to LangGraph chatbot engine.
// WHY: Executes Layer 3 (linguistic router), Layer 2 (hybrid retrieval), and Layer 4 (LangGraph decision loop).
export const sendChatMessage = async (query, sessionId, history = []) => {
  try {
    const response = await apiClient.post('/api/chat', {
      query,
      session_id: sessionId,
      history,
    });
    return response.data;
  } catch (error) {
    console.error('[API] Error calling /api/chat:', error);
    if (error.response && error.response.data) {
      throw new Error(error.response.data.error || 'Server returned an error processing your query.');
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('Request timed out while waiting for LLM synthesis. Please retry.');
    } else {
      throw new Error('Unable to connect to MAIT Chatbot backend. Please ensure the Flask server is running.');
    }
  }
};

// WHAT: Query health status of Ollama, ChromaDB, and SQLite services.
// WHY: Allows the frontend navigation bar to display live service availability and vector chunk count.
export const checkHealth = async () => {
  try {
    const response = await apiClient.get('/api/health');
    return response.data;
  } catch (error) {
    console.warn('[API] Health check failed:', error.message);
    return {
      status: 'offline',
      error: error.message,
      services: {},
    };
  }
};

// WHAT: Fetch unresolved escalation tickets queued for human administrative staff review.
// WHY: Milestone 6 & 7 administrative triage capability allowing staff to review deflection misses.
export const getUnresolvedTickets = async (limit = 50, status = 'PENDING_STAFF_REVIEW') => {
  try {
    const response = await apiClient.get('/api/unresolved', {
      params: { limit, status },
    });
    return response.data;
  } catch (error) {
    console.error('[API] Error fetching unresolved tickets:', error);
    throw error;
  }
};

// WHAT: Submit student thumbs-up (+1) or thumbs-down (-1/0) satisfaction feedback to SQLite.
// WHY: Captures explicit student ground truth evaluation data for RAGAS metrics and administrative reporting.
export const submitFeedback = async (rating, sessionId, queryId = null, comment = '') => {
  try {
    const response = await apiClient.post('/api/feedback', {
      rating,
      session_id: sessionId,
      query_id: queryId,
      comment,
    });
    return response.data;
  } catch (error) {
    console.error('[API] Error submitting feedback:', error);
    throw error;
  }
};

export default apiClient;
