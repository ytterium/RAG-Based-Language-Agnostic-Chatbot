// WHAT: Main interactive chat window containing the scrollable message feed, auto-scroll,
//      suggested prompts, and query input interface.
// WHY: Implements Task 8.2 as the central user-facing chat container. Manages multi-turn conversation
//      history, coordinates with `services/api.js` for Flask `/api/chat` requests, and displays loading/error states.

import React, { useState, useEffect, useRef } from 'react';
import { Send, RotateCcw, Sparkles, AlertCircle, Loader2 } from 'lucide-react';
import MessageBubble from './MessageBubble';
import { sendChatMessage } from '../services/api';

// Initial institutional greeting
const INITIAL_WELCOME_MESSAGE = {
  id: 'welcome-001',
  sender: 'assistant',
  content:
    'Hello! I am the MAIT Smart Academic Assistant.\n\n' +
    'I can answer questions regarding official institutional notices, scholarship deadlines, fee payment schedules, ' +
    'examination rules, and circulars. You can ask in English, Hindi (हिन्दी), or Hinglish.',
  citations: [],
  detected_language: 'en',
  escalated: false,
  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
};

// Recommended test prompts
const SUGGESTED_PROMPTS = [
  'What is the scholarship deadline?',
  'fees kab bharna hai',
  'When is the last date for exam form?',
  'xyzunknown123',
];

export default function ChatWindow() {
  const [messages, setMessages] = useState([INITIAL_WELCOME_MESSAGE]);
  const [inputQuery, setInputQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [sessionId, setSessionId] = useState(() => `sess_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // WHAT: Auto-scroll message feed to bottom whenever new messages arrive or loading state changes.
  // WHY: Ensures the student immediately sees incoming responses, citations, or typing indicators without manual scrolling.
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Focus input field on initial mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // WHAT: Reset chat session and initialize fresh session ID.
  // WHY: Allows starting a new inquiry context cleanly without lingering multi-turn query rewriter state.
  const handleReset = () => {
    setMessages([
      {
        ...INITIAL_WELCOME_MESSAGE,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
    setSessionId(`sess_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`);
    setErrorMessage(null);
    setInputQuery('');
    inputRef.current?.focus();
  };

  // WHAT: Submit student question to backend LangGraph engine.
  // WHY: Gathers conversation history, dispatches HTTP POST /api/chat, updates local state with bot response,
  //      citations, detected language, and escalation flags.
  const handleSendMessage = async (queryText) => {
    const textToSend = (queryText || inputQuery).trim();
    if (!textToSend || isLoading) return;

    setErrorMessage(null);

    // Format new user turn
    const userMessage = {
      id: `user_${Date.now()}`,
      sender: 'user',
      content: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    // Format history for backend LangChain/Ollama format
    const currentHistory = messages
      .filter((m) => m.id !== 'welcome-001')
      .map((m) => ({
        role: m.sender === 'user' ? 'user' : 'assistant',
        content: m.content,
      }));

    setMessages((prev) => [...prev, userMessage]);
    setInputQuery('');
    setIsLoading(true);

    try {
      const data = await sendChatMessage(textToSend, sessionId, currentHistory);

      const botMessage = {
        id: `bot_${Date.now()}`,
        sender: 'assistant',
        content: data.response || 'No response text received from agent.',
        citations: data.citations || [],
        detected_language: data.detected_language || 'en',
        escalated: Boolean(data.escalated),
        latency_ms: data.latency_ms || null,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error('[ChatWindow] Error getting response:', err);
      setErrorMessage(err.message || 'Failed to get a response from MAIT Chatbot backend.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-[700px] max-h-[82vh] bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden">
      {/* Top Window Header */}
      <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-200 bg-gradient-to-r from-slate-50 to-slate-100/60">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 bg-blue-600 text-white rounded-lg shadow-2xs">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-800">MAIT Institutional Query Desk</h2>
            <p className="text-[11px] text-slate-500 font-mono">
              Session: {sessionId.substring(0, 16)}...
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={handleReset}
          className="inline-flex items-center gap-1.5 text-xs text-slate-600 hover:text-slate-900 bg-white hover:bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-lg font-medium transition-all shadow-2xs"
          title="Start fresh conversation"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>New Chat</span>
        </button>
      </div>

      {/* Message Feed Area */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-2 bg-slate-50/50">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} sessionId={sessionId} />
        ))}

        {/* Loading typing indicator */}
        {isLoading && (
          <div className="flex items-start gap-3 my-4">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 text-white flex items-center justify-center shrink-0 shadow-sm mt-1 animate-pulse">
              <Sparkles className="w-4 h-4" />
            </div>
            <div className="bg-white border border-slate-200 rounded-2xl rounded-bl-xs px-4 py-3 shadow-xs text-sm text-slate-600 flex items-center gap-2.5">
              <Loader2 className="w-4 h-4 text-blue-600 animate-spin" />
              <span>Synthesizing answer from verified notices (LangGraph Self-Corrective Engine)...</span>
            </div>
          </div>
        )}

        {/* Error Notification Banner */}
        {errorMessage && (
          <div className="my-3 p-3 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-xs flex items-start gap-2 shadow-2xs">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="font-semibold">Query Processing Failed</p>
              <p className="mt-0.5 text-rose-700">{errorMessage}</p>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompt Chips */}
      <div className="px-4 py-2 border-t border-slate-100 bg-white flex items-center gap-1.5 overflow-x-auto text-xs">
        <span className="text-[11px] font-semibold text-slate-400 shrink-0 uppercase tracking-wider pl-1">
          Suggestions:
        </span>
        {SUGGESTED_PROMPTS.map((prompt, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => handleSendMessage(prompt)}
            disabled={isLoading}
            className="shrink-0 bg-slate-100 hover:bg-blue-50 hover:text-blue-700 hover:border-blue-200 border border-slate-200 text-slate-600 px-2.5 py-1 rounded-full text-xs transition-colors cursor-pointer disabled:opacity-50"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Query Bar */}
      <div className="p-3 sm:p-4 border-t border-slate-200 bg-white">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="flex items-center gap-2"
        >
          <input
            ref={inputRef}
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about notices, fees, scholarships... (English, हिन्दी, Hinglish)"
            disabled={isLoading}
            className="flex-1 px-4 py-3 bg-slate-50 border border-slate-300 focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-100 rounded-xl text-sm text-slate-800 transition-all placeholder:text-slate-400 disabled:opacity-60"
          />

          <button
            type="submit"
            disabled={!inputQuery.trim() || isLoading}
            className="inline-flex items-center justify-center p-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-200 disabled:text-slate-400 text-white rounded-xl shadow-xs transition-all cursor-pointer disabled:cursor-not-allowed shrink-0"
            title="Send query"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </form>

        <div className="flex items-center justify-between text-[11px] text-slate-400 mt-2 px-1">
          <span>Press <strong>Enter</strong> to send</span>
          <span>Zero Hallucination Grounding • MAIT CSE</span>
        </div>
      </div>
    </div>
  );
}
