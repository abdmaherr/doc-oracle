import { Bot } from 'lucide-react';

export default function TypingIndicator() {
  return (
    <div className="msg-reveal flex gap-3">
      <div className="w-8 h-8 rounded-lg bg-safety-orange/10 border border-safety-orange/30
                      flex items-center justify-center shrink-0">
        <Bot size={14} className="text-safety-orange" />
      </div>
      <div className="bg-charcoal-800 border border-charcoal-700 rounded-xl px-4 py-3">
        <p className="text-[10px] font-mono uppercase tracking-widest text-safety-orange mb-2">
          Oracle
        </p>
        <div className="flex gap-1.5">
          <span className="typing-dot w-2 h-2 rounded-full bg-safety-orange" />
          <span className="typing-dot w-2 h-2 rounded-full bg-safety-orange" />
          <span className="typing-dot w-2 h-2 rounded-full bg-safety-orange" />
        </div>
      </div>
    </div>
  );
}
