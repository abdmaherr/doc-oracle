import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { User, Bot, ChevronDown, ChevronUp, FileText } from 'lucide-react';

export default function ChatMessage({ message, index }) {
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const isUser = message.role === 'user';

  return (
    <div
      className="msg-reveal"
      style={{ animationDelay: `${index * 80}ms` }}
    >
      <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
        {/* Avatar */}
        <div className={`
          w-8 h-8 rounded-lg flex items-center justify-center shrink-0 mt-1
          ${isUser
            ? 'bg-charcoal-700 border border-charcoal-600'
            : 'bg-safety-orange/10 border border-safety-orange/30'}
        `}>
          {isUser
            ? <User size={14} className="text-ink-muted" />
            : <Bot size={14} className="text-safety-orange" />
          }
        </div>

        {/* Bubble */}
        <div className={`
          max-w-[85%] rounded-xl px-4 py-3
          ${isUser
            ? 'bg-charcoal-700 border border-charcoal-600'
            : 'bg-charcoal-800 border border-charcoal-700'}
        `}>
          {/* Label */}
          <p className={`text-[10px] font-mono uppercase tracking-widest mb-1.5 ${
            isUser ? 'text-ink-muted text-right' : 'text-safety-orange'
          }`}>
            {isUser ? 'You' : 'Oracle'}
          </p>

          {/* Content */}
          {isUser ? (
            <p className="text-sm text-ink-white font-mono leading-relaxed">
              {message.content}
            </p>
          ) : (
            <div className="md-content text-sm font-mono leading-relaxed">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}

          {/* Sources */}
          {!isUser && message.sources?.length > 0 && (
            <div className="mt-3 pt-2 border-t border-charcoal-700/50">
              <button
                onClick={() => setSourcesOpen(!sourcesOpen)}
                className="flex items-center gap-1.5 text-[11px] text-ink-muted hover:text-safety-orange
                           font-mono transition-colors"
              >
                <FileText size={11} />
                {message.sources.length} source{message.sources.length > 1 ? 's' : ''}
                {sourcesOpen ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
              </button>

              {sourcesOpen && (
                <div className="mt-2 space-y-2">
                  {message.sources.map((src, i) => (
                    <div
                      key={i}
                      className="msg-reveal bg-charcoal-900 border border-charcoal-700 rounded-lg p-3"
                      style={{ animationDelay: `${i * 60}ms` }}
                    >
                      <span className="text-[10px] text-safety-orange font-mono font-bold">
                        PAGE {src.page}
                      </span>
                      <p className="text-xs text-ink-muted font-mono mt-1 leading-relaxed">
                        {src.text_snippet}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
