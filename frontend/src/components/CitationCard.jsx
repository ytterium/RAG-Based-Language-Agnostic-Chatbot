// WHAT: Clickable citation card component displaying verifiable source document provenance for generated claims.
// WHY: Implements Layer 2 & 4 citation linking to eliminate blind context trust and satisfy academic verification
//      standards, explicitly showing circular ID, file name, publication date, and page number.

import React, { useState } from 'react';
import { FileText, Calendar, Hash, ExternalLink, ChevronDown, ChevronUp, ShieldCheck } from 'lucide-react';

export default function CitationCard({ citation, index }) {
  const [expanded, setExpanded] = useState(false);

  if (!citation) return null;

  const sourceName = citation.source || 'Institutional Circular';
  const pageNum = citation.page || citation.page_number || null;
  const circularNum = citation.circular_number || null;
  const dateStr = citation.date || null;
  const ocrMethod = citation.ocr_method || null;

  return (
    <div className="bg-slate-50 hover:bg-slate-100/80 border border-slate-200 rounded-lg p-3 transition-all duration-150 shadow-2xs">
      <div
        className="flex items-start justify-between gap-2 cursor-pointer select-none"
        onClick={() => setExpanded(!expanded)}
        title="Click to view verified source metadata"
      >
        <div className="flex items-start gap-2.5 min-w-0">
          <div className="p-1.5 bg-blue-100 text-blue-700 rounded-md shrink-0 mt-0.5">
            <FileText className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className="text-xs font-semibold text-blue-700 uppercase tracking-wide">
                [{index + 1}] Source
              </span>
              {pageNum && (
                <span className="text-xs bg-slate-200 text-slate-700 font-medium px-1.5 py-0.2 rounded">
                  Page {pageNum}
                </span>
              )}
              {ocrMethod && (
                <span className="text-[10px] bg-indigo-50 text-indigo-600 border border-indigo-200 px-1 py-0.2 rounded">
                  OCR: {ocrMethod}
                </span>
              )}
            </div>
            <p className="text-xs font-medium text-slate-800 truncate mt-0.5" title={sourceName}>
              {sourceName}
            </p>
          </div>
        </div>

        <button
          type="button"
          className="text-slate-400 hover:text-slate-600 p-0.5 rounded transition-colors shrink-0"
          aria-label={expanded ? 'Collapse details' : 'Expand details'}
        >
          {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>

      {/* Expanded provenance metadata details */}
      {expanded && (
        <div className="mt-2.5 pt-2 border-t border-slate-200/80 text-xs text-slate-600 space-y-1.5">
          <div className="flex items-center gap-1.5 text-slate-500">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span className="font-medium text-slate-700">Verified Grounding Provenance:</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 pl-5">
            <div>
              <span className="text-slate-400">File: </span>
              <span className="font-mono text-[11px] text-slate-700">{sourceName}</span>
            </div>

            {pageNum && (
              <div>
                <span className="text-slate-400">Document Page: </span>
                <span className="font-semibold text-slate-700">{pageNum}</span>
              </div>
            )}

            {circularNum && (
              <div className="flex items-center gap-1">
                <Hash className="w-3 h-3 text-slate-400" />
                <span className="text-slate-400">Circular No: </span>
                <span className="font-mono font-medium text-slate-700">{circularNum}</span>
              </div>
            )}

            {dateStr && (
              <div className="flex items-center gap-1">
                <Calendar className="w-3 h-3 text-slate-400" />
                <span className="text-slate-400">Published Date: </span>
                <span className="text-slate-700">{dateStr}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
