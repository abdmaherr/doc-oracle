import { useState } from 'react';
import { ChevronDown, ChevronUp, Sparkles } from 'lucide-react';

export default function ExecutiveBrief({ brief, docName, totalPages, totalChunks }) {
  const [expanded, setExpanded] = useState(true);

  if (!brief) return null;

  return (
    <div className="msg-reveal border border-charcoal-700 rounded-xl bg-charcoal-900/80 overflow-hidden">
      {/* Header bar */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-5 py-3.5 hover:bg-charcoal-800/50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 bg-safety-orange/10 rounded-md flex items-center justify-center">
            <Sparkles size={14} className="text-safety-orange" />
          </div>
          <span className="font-serif text-base font-bold text-ink-white">
            Executive Brief
          </span>
          <span className="text-[11px] text-ink-muted font-mono bg-charcoal-800 px-2 py-0.5 rounded">
            {totalPages} pages &middot; {totalChunks} chunks
          </span>
        </div>
        {expanded ? (
          <ChevronUp size={16} className="text-ink-muted" />
        ) : (
          <ChevronDown size={16} className="text-ink-muted" />
        )}
      </button>

      {/* Content */}
      {expanded && (
        <div className="px-5 pb-5 border-t border-charcoal-700/50">
          <ul className="mt-4 space-y-2.5">
            {brief.bullets.map((bullet, i) => (
              <li
                key={i}
                className="msg-reveal flex gap-3 text-sm text-ink-white/90 font-mono leading-relaxed"
                style={{ animationDelay: `${i * 100}ms` }}
              >
                <span className="text-safety-orange mt-0.5 shrink-0 font-bold">
                  {String(i + 1).padStart(2, '0')}
                </span>
                <span>{bullet}</span>
              </li>
            ))}
          </ul>

          {brief.bottom_line && (
            <div className="mt-4 pt-3 border-t border-charcoal-700/50">
              <p className="text-xs text-ink-muted font-mono uppercase tracking-wider mb-1">
                Bottom Line
              </p>
              <p className="text-sm text-safety-orange font-mono leading-relaxed">
                {brief.bottom_line}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
