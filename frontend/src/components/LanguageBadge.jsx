// WHAT: Visual badge component displaying the detected query language (English, Hindi, or Hinglish).
// WHY: Provides immediate visual confirmation of Layer 3 linguistic classification and Layer 4 Node 5
//      language consistency enforcement, transparently showing the student that their regional phrasing was understood.

import React from 'react';
import { Globe, Sparkles } from 'lucide-react';

export default function LanguageBadge({ language = 'en', size = 'sm' }) {
  // Normalize language key
  const langKey = (language || 'en').toLowerCase().trim();

  let label = 'English (EN)';
  let bgClass = 'bg-blue-50 text-blue-700 border-blue-200';
  let dotClass = 'bg-blue-500';

  if (langKey === 'hi' || langKey === 'hindi') {
    label = 'Hindi (HI)';
    bgClass = 'bg-emerald-50 text-emerald-700 border-emerald-200';
    dotClass = 'bg-emerald-500';
  } else if (langKey === 'hinglish' || langKey === 'hi-latn') {
    label = 'Hinglish (HI-Latn)';
    bgClass = 'bg-purple-50 text-purple-700 border-purple-200';
    dotClass = 'bg-purple-500';
  }

  const paddingClass = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-medium rounded-full border shadow-2xs transition-colors ${bgClass} ${paddingClass}`}
      title={`Language detected by Layer 3 Linguistic Router: ${label}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${dotClass} animate-pulse`} />
      <Globe className="w-3 h-3 opacity-75" />
      <span>{label}</span>
    </span>
  );
}
