// WHAT: Message bubble component rendering formatted user and assistant responses.
// WHY: Implements chat turn presentation, embedding CitationCard for Layer 2 provenance,
//      EscalationCard for confidence fallbacks, LanguageBadge for linguistic feedback,
//      latency telemetry, and thumbs up/down feedback triggers for SQLite audit recording.

import React, { useState } from 'react';
import { User, Bot, Clock, ThumbsUp, ThumbsDown, Check, Zap } from 'lucide-react';
import LanguageBadge from './LanguageBadge';
import CitationCard from './CitationCard';
import EscalationCard from './EscalationCard';
import { submitFeedback } from '../services/api';

export default function MessageBubble({ message, sessionId }) {
  const [feedbackState, setFeedbackState] = useState(message.feedback || null);
  const [submittingFeedback, setSubmittingFeedback] = useState(false);

  const isUser = message.sender === 'user';

  // WHAT: Handle student thumbs-up / thumbs-down rating.
  // WHY: Sends student evaluation data to Flask /api/feedback to satisfy Milestone 7/8 SQLite logging.
  const handleFeedback = async (rating) => {
    if (submittingFeedback || feedbackState !== null) return;
    setSubmittingFeedback(true);
    try {
      await submitFeedback(rating, sessionId, message.queryId || null);
      setFeedbackState(rating);
    } catch (err) {
      console.error('Failed to submit feedback:', err);
    } finally {
      setSubmittingFeedback(false);
    }
  };

  // Helper to render text with basic markdown-like bold and line-break formatting
  const renderFormattedText = (text) => {
    if (!text) return null;
    const paragraphs = text.split('\n\n');
    return paragraphs.map((para, pIdx) => {
      const lines = para.split('\n');
      return (
        <p key={pIdx} className={pIdx > 0 ? 'mt-2' : ''}>
          {lines.map((line, lIdx) => {
            // Process bold formatting **text**
            const parts = line.split(/(\*\*.*?\*\*)/g);
            return (
              <span key={lIdx} className="block leading-relaxed">
                {parts.map((part, idx) => {
                  if (part.startsWith('**') && part.endsWith('**')) {
                    return (
                      <strong key={idx} className="font-semibold text-slate-900">
                        {part.slice(2, -2)}
                      </strong>
                    );
                  }
                  return part;
                })}
              </span>
            );
          })}
        </p>
      );
    });
  };

  return (
    <div className={`flex gap-3 my-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {/* Avatar for Assistant */}
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 text-white flex items-center justify-center shrink-0 shadow-sm mt-1">
          <Bot className="w-4 h-4" />
        </div>
      )}

      {/* Message Content Container */}
      <div className={`max-w-[85%] sm:max-w-[78%] flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
        {/* Header meta for bot messages: language badge and timestamp */}
        {!isUser && (
          <div className="flex items-center gap-2 mb-1.5 px-1 flex-wrap">
            <span className="text-xs font-semibold text-slate-700">MAIT Assistant</span>
            {message.detected_language && (
              <LanguageBadge language={message.detected_language} size="sm" />
            )}
            {message.latency_ms && (
              <span className="inline-flex items-center gap-0.5 text-[10px] text-slate-400 font-mono">
                <Zap className="w-3 h-3 text-amber-500" />
                {message.latency_ms}ms
              </span>
            )}
          </div>
        )}

        {/* Bubble Box */}
        <div
          className={`rounded-2xl px-4 py-3 text-sm shadow-xs ${
            isUser
              ? 'bg-blue-600 text-white rounded-br-xs'
              : 'bg-white border border-slate-200 text-slate-800 rounded-bl-xs'
          }`}
        >
          {/* Main message text */}
          <div className={isUser ? 'text-white' : 'text-slate-800'}>
            {renderFormattedText(message.content)}
          </div>

          {/* Render Escalation Card if query was escalated */}
          {!isUser && message.escalated && <EscalationCard />}

          {/* Render Citations Section if citations exist and not escalated */}
          {!isUser && !message.escalated && message.citations && message.citations.length > 0 && (
            <div className="mt-3.5 pt-3 border-t border-slate-100">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-700 tracking-wide uppercase">
                  Verified Notice Citations ({message.citations.length})
                </span>
                <span className="text-[10px] text-slate-400">Layer 2 Hybrid Retrieval</span>
              </div>
              <div className="grid grid-cols-1 gap-2">
                {message.citations.map((cit, idx) => (
                  <CitationCard key={idx} citation={cit} index={idx} />
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer info: timestamp and feedback */}
        <div className="flex items-center gap-2 mt-1 px-1 text-[11px] text-slate-400">
          <span>{message.timestamp}</span>

          {/* Bot Feedback Rating buttons */}
          {!isUser && (
            <div className="flex items-center gap-1 ml-2 border-l border-slate-200 pl-2">
              {feedbackState === null ? (
                <>
                  <button
                    type="button"
                    onClick={() => handleFeedback(1)}
                    disabled={submittingFeedback}
                    className="p-1 text-slate-400 hover:text-emerald-600 hover:bg-slate-100 rounded transition-colors"
                    title="Helpful response"
                  >
                    <ThumbsUp className="w-3.5 h-3.5" />
                  </button>
                  <button
                    type="button"
                    onClick={() => handleFeedback(0)}
                    disabled={submittingFeedback}
                    className="p-1 text-slate-400 hover:text-rose-600 hover:bg-slate-100 rounded transition-colors"
                    title="Not helpful / inaccurate"
                  >
                    <ThumbsDown className="w-3.5 h-3.5" />
                  </button>
                </>
              ) : (
                <span className="inline-flex items-center gap-1 text-[11px] text-emerald-600 font-medium">
                  <Check className="w-3 h-3" />
                  Feedback recorded
                </span>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Avatar for User */}
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-slate-700 text-white flex items-center justify-center shrink-0 shadow-sm mt-1">
          <User className="w-4 h-4" />
        </div>
      )}
    </div>
  );
}
