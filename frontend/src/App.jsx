// WHAT: Root React application container rendering the institutional header, system telemetry,
//      staff escalation triage modal, ChatWindow, and architecture footer.
// WHY: Wires up the complete Milestone 8 frontend interface, connecting the user to the Flask backend,
//      monitoring live server health (ChromaDB + Ollama + SQLite), and enabling review of escalation tickets.

import React, { useState, useEffect } from 'react';
import {
  GraduationCap,
  Activity,
  ShieldCheck,
  Cpu,
  Database,
  Layers,
  Inbox,
  X,
  ExternalLink,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
} from 'lucide-react';
import ChatWindow from './components/ChatWindow';
import { checkHealth, getUnresolvedTickets } from './services/api';

export default function App() {
  const [healthData, setHealthData] = useState(null);
  const [healthLoading, setHealthLoading] = useState(true);
  const [showTicketsModal, setShowTicketsModal] = useState(false);
  const [tickets, setTickets] = useState([]);
  const [ticketsLoading, setTicketsLoading] = useState(false);

  // WHAT: Fetch real-time health telemetry on component mount and every 30 seconds.
  // WHY: Verifies that the Flask REST API, Ollama LLM, ChromaDB vector store, and SQLite DB are operational.
  const fetchHealthStatus = async () => {
    setHealthLoading(true);
    try {
      const data = await checkHealth();
      setHealthData(data);
    } catch (err) {
      console.error('Failed to load backend health:', err);
    } finally {
      setHealthLoading(false);
    }
  };

  useEffect(() => {
    fetchHealthStatus();
    const interval = setInterval(fetchHealthStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  // WHAT: Fetch unresolved administrative escalation tickets when modal is opened.
  // WHY: Displays human staff review triage queue (Milestone 6/7) to demonstrate administrative deflection tracking.
  const handleOpenTicketsModal = async () => {
    setShowTicketsModal(true);
    setTicketsLoading(true);
    try {
      const data = await getUnresolvedTickets(50, 'PENDING_STAFF_REVIEW');
      setTickets(data.tickets || []);
    } catch (err) {
      console.error('Failed to load unresolved tickets:', err);
    } finally {
      setTicketsLoading(false);
    }
  };

  const isHealthy = healthData?.status === 'ok';
  const chunkCount = healthData?.services?.chromadb?.chunks_count ?? 354;
  const activeModel = healthData?.model || 'mistrallite';

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-100 via-slate-50 to-slate-100 flex flex-col font-sans text-slate-800 antialiased">
      {/* Top Institutional Header Navbar */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-xs">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          {/* Institution Crest and Title */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-700 text-white flex items-center justify-center font-bold text-lg shadow-sm">
              <GraduationCap className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base font-bold text-slate-900 leading-tight">
                  MAIT Smart Query Response Desk
                </h1>
                <span className="hidden sm:inline-block text-[10px] font-semibold bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">
                  Team MNP059
                </span>
              </div>
              <p className="text-xs text-slate-500">
                Department of Computer Science & Engineering • Language Agnostic RAG
              </p>
            </div>
          </div>

          {/* Right Action & Telemetry Area */}
          <div className="flex items-center gap-2 sm:gap-3">
            {/* System Health Telemetry Badge */}
            <div
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                isHealthy
                  ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                  : 'bg-rose-50 text-rose-800 border-rose-200'
              }`}
              title={
                isHealthy
                  ? `Backend Online • Ollama: ${activeModel} • ChromaDB: ${chunkCount} chunks`
                  : 'Backend Offline or Degraded'
              }
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  isHealthy ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'
                }`}
              />
              <span className="hidden md:inline">
                {isHealthy ? `ChromaDB: ${chunkCount} chunks` : 'API Offline'}
              </span>
              <span className="md:hidden">{isHealthy ? 'Online' : 'Offline'}</span>
            </div>

            {/* Staff Escalation Review Button */}
            <button
              type="button"
              onClick={handleOpenTicketsModal}
              className="inline-flex items-center gap-1.5 text-xs font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 px-3 py-1.5 rounded-lg transition-colors cursor-pointer shadow-2xs"
              title="View administrative escalation queue"
            >
              <Inbox className="w-3.5 h-3.5 text-slate-500" />
              <span className="hidden sm:inline">Staff Triage</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 py-6 sm:py-8 flex flex-col justify-center">
        <ChatWindow />

        {/* System Architecture Pills Strip */}
        <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-2 text-center text-xs">
          <div className="bg-white/80 border border-slate-200 rounded-lg p-2.5 shadow-2xs flex items-center justify-center gap-1.5 text-slate-600">
            <Cpu className="w-3.5 h-3.5 text-blue-600" />
            <span className="font-medium">LangGraph Engine</span>
          </div>
          <div className="bg-white/80 border border-slate-200 rounded-lg p-2.5 shadow-2xs flex items-center justify-center gap-1.5 text-slate-600">
            <Layers className="w-3.5 h-3.5 text-indigo-600" />
            <span className="font-medium">BGE-M3 + BM25 RRF</span>
          </div>
          <div className="bg-white/80 border border-slate-200 rounded-lg p-2.5 shadow-2xs flex items-center justify-center gap-1.5 text-slate-600">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span className="font-medium">Adaptive OCR</span>
          </div>
          <div className="bg-white/80 border border-slate-200 rounded-lg p-2.5 shadow-2xs flex items-center justify-center gap-1.5 text-slate-600">
            <Database className="w-3.5 h-3.5 text-purple-600" />
            <span className="font-medium">SQLite Audit Log</span>
          </div>
        </div>
      </main>

      {/* Staff Escalation Triage Modal */}
      {showTicketsModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 max-w-2xl w-full max-h-[85vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            {/* Modal Header */}
            <div className="px-5 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <div className="flex items-center gap-2.5">
                <div className="p-1.5 bg-amber-100 text-amber-800 rounded-lg">
                  <Inbox className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-800">
                    Administrative Escalation Queue (Staff Triage)
                  </h3>
                  <p className="text-xs text-slate-500">
                    Live records from SQLite database table: <code>escalation_tickets</code>
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setShowTicketsModal(false)}
                className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="flex-1 overflow-y-auto p-5 space-y-3">
              {ticketsLoading ? (
                <div className="text-center py-8 text-slate-500 text-xs flex items-center justify-center gap-2">
                  <RefreshCw className="w-4 h-4 animate-spin text-blue-600" />
                  <span>Loading pending tickets from backend...</span>
                </div>
              ) : tickets.length === 0 ? (
                <div className="text-center py-8 text-slate-500 text-xs">
                  <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2 opacity-80" />
                  <p className="font-semibold text-slate-700">No Pending Escalations</p>
                  <p className="mt-1">All institutional inquiries have been verified or resolved.</p>
                </div>
              ) : (
                tickets.map((t) => (
                  <div
                    key={t.ticket_id}
                    className="border border-slate-200 rounded-xl p-3.5 bg-slate-50/70 hover:bg-slate-50 transition-colors text-xs space-y-1.5 shadow-2xs"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-mono text-slate-400">
                        Ticket #{t.ticket_id} • Session {t.session_id.substring(0, 10)}
                      </span>
                      <span className="font-semibold bg-amber-100 text-amber-800 border border-amber-200 px-2 py-0.5 rounded-full text-[10px]">
                        {t.status}
                      </span>
                    </div>
                    <p className="font-medium text-slate-800 text-sm">{t.unresolved_query}</p>
                    <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1 border-t border-slate-200/60">
                      <span>Reason: {t.failure_reason || 'Low relevance retrieval'}</span>
                      <span>{t.created_at || 'Just now'}</span>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Modal Footer */}
            <div className="px-5 py-3 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-xs">
              <span className="text-slate-500">
                {tickets.length} total pending item(s) logged
              </span>
              <button
                type="button"
                onClick={() => setShowTicketsModal(false)}
                className="bg-slate-800 hover:bg-slate-900 text-white font-medium px-4 py-1.5 rounded-lg transition-colors cursor-pointer"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-4 mt-auto">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 text-center text-xs text-slate-500 space-y-1">
          <p>
            <strong>Maharaja Agrasen Institute of Technology (MAIT)</strong> • B.Tech CSE Final Year Minor Project
          </p>
          <p className="text-[11px] text-slate-400">
            Self-Corrective LangGraph • Multilingual BGE-M3 • BM25 Lexical • Mistral 7B Grounding
          </p>
        </div>
      </footer>
    </div>
  );
}
