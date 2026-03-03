import { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';

export default function ChatInput({ onSend, isLoading, disabled }) {
  const [value, setValue] = useState('');

  function handleSubmit(e) {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || isLoading || disabled) return;
    onSend(trimmed);
    setValue('');
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="border-t border-charcoal-700 bg-charcoal-900/90 backdrop-blur-sm p-4"
    >
      <div className="max-w-3xl mx-auto flex gap-3">
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder={disabled ? 'Upload a PDF first...' : 'Ask a question about the document...'}
          disabled={disabled || isLoading}
          className="flex-1 bg-charcoal-800 border border-charcoal-600 rounded-lg px-4 py-3
                     text-sm text-ink-white font-mono placeholder:text-charcoal-500
                     focus:outline-none focus:border-safety-orange/50 focus:ring-1 focus:ring-safety-orange/20
                     disabled:opacity-40 disabled:cursor-not-allowed
                     transition-all"
        />
        <button
          type="submit"
          disabled={!value.trim() || isLoading || disabled}
          className="px-4 py-3 bg-safety-orange text-charcoal-950 rounded-lg font-mono text-sm font-bold
                     hover:bg-safety-orange-dim active:scale-95
                     disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:bg-safety-orange
                     transition-all flex items-center gap-2"
        >
          {isLoading ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <Send size={16} />
          )}
        </button>
      </div>
    </form>
  );
}
