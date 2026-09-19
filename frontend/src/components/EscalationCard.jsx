// WHAT: Escalation contact card rendered when the backend returns `escalated: true`.
// WHY: Implements Layer 4 Node 2 / escalation node fallback. Halts speculative LLM generation when facts
//      cannot be verified in published circulars, preventing hallucinations and providing physical administrative contacts.

import React, { useState } from 'react';
import { AlertTriangle, Building2, Clock, Mail, Check, Copy, ShieldAlert } from 'lucide-react';

export default function EscalationCard() {
  const [copied, setCopied] = useState(false);
  const helpdeskEmail = 'admin@mait.ac.in';

  const handleCopyEmail = () => {
    navigator.clipboard.writeText(helpdeskEmail);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="mt-3 border-2 border-amber-300 bg-amber-50/90 rounded-xl p-4 text-slate-800 shadow-sm">
      <div className="flex items-start gap-3">
        <div className="p-2 bg-amber-100 text-amber-800 rounded-lg shrink-0 mt-0.5">
          <AlertTriangle className="w-5 h-5" />
        </div>
        <div className="space-y-2 flex-1">
          <div>
            <div className="flex items-center gap-2">
              <h4 className="text-sm font-bold text-amber-900">
                Official Administrative Office Escalation
              </h4>
              <span className="text-[10px] font-semibold bg-amber-200 text-amber-900 px-2 py-0.5 rounded-full uppercase tracking-wider">
                Staff Review Queued
              </span>
            </div>
            <p className="text-xs text-amber-800/90 mt-1 leading-relaxed">
              We could not verify a definitive answer for this query in the current published circulars and notices.
              To prevent misinformation, please consult the administrative department directly:
            </p>
          </div>

          {/* Contact Details Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1 text-xs">
            <div className="flex items-center gap-2 bg-white/80 p-2 rounded-lg border border-amber-200/80">
              <Building2 className="w-4 h-4 text-amber-700 shrink-0" />
              <div>
                <p className="font-semibold text-slate-700">Office Location</p>
                <p className="text-slate-600">Room 101, Administrative Block</p>
              </div>
            </div>

            <div className="flex items-center gap-2 bg-white/80 p-2 rounded-lg border border-amber-200/80">
              <Clock className="w-4 h-4 text-amber-700 shrink-0" />
              <div>
                <p className="font-semibold text-slate-700">In-Person Hours</p>
                <p className="text-slate-600">9:00 AM – 5:00 PM (Mon – Fri)</p>
              </div>
            </div>
          </div>

          {/* Email Helpdesk Row */}
          <div className="flex items-center justify-between gap-2 bg-white/90 p-2.5 rounded-lg border border-amber-200">
            <div className="flex items-center gap-2 text-xs">
              <Mail className="w-4 h-4 text-amber-700 shrink-0" />
              <div>
                <span className="text-slate-500">Official Helpdesk: </span>
                <span className="font-mono font-semibold text-slate-800">{helpdeskEmail}</span>
              </div>
            </div>
            <button
              type="button"
              onClick={handleCopyEmail}
              className="inline-flex items-center gap-1 text-xs bg-amber-100 hover:bg-amber-200 text-amber-900 font-medium px-2.5 py-1 rounded transition-colors"
              title="Copy helpdesk email address"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-600" />
                  <span className="text-emerald-700">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span>Copy</span>
                </>
              )}
            </button>
          </div>

          <div className="flex items-center gap-1.5 text-[11px] text-amber-700/80 pt-0.5">
            <ShieldAlert className="w-3.5 h-3.5 shrink-0" />
            <span>
              Ticket automatically logged to SQLite audit log with status <code>PENDING_STAFF_REVIEW</code>.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
