import { FileText, Zap } from 'lucide-react';

export default function Header({ docName, status }) {
  return (
    <header className="border-b border-charcoal-700 bg-charcoal-900/80 backdrop-blur-sm sticky top-0 z-40">
      <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-safety-orange/10 border border-safety-orange/30 rounded-lg flex items-center justify-center">
            <FileText size={18} className="text-safety-orange" />
          </div>
          <div>
            <h1 className="font-serif text-xl font-bold tracking-tight text-ink-white">
              DOC<span className="text-safety-orange">.</span>ORACLE
            </h1>
            <p className="text-[11px] text-ink-muted font-mono tracking-widest uppercase">
              PDF Intelligence System
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {docName && (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-charcoal-800 border border-charcoal-600 rounded-md">
              <Zap size={12} className="text-safety-orange" />
              <span className="text-xs text-ink-muted font-mono truncate max-w-[200px]">
                {docName}
              </span>
            </div>
          )}
          <div className="flex items-center gap-1.5">
            <div className={`w-2 h-2 rounded-full ${
              status === 'ready' ? 'bg-green-500' :
              status === 'processing' ? 'bg-safety-orange pulse-glow' :
              'bg-charcoal-500'
            }`} />
            <span className="text-[11px] text-ink-muted font-mono uppercase tracking-wider">
              {status}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
