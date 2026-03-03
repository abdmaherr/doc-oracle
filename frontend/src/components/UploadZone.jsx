import { useState, useRef } from 'react';
import { Upload, FileUp, Loader2 } from 'lucide-react';

export default function UploadZone({ onUpload, isProcessing }) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef(null);

  function handleDrop(e) {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file?.type === 'application/pdf') onUpload(file);
  }

  function handleSelect(e) {
    const file = e.target.files[0];
    if (file) onUpload(file);
  }

  return (
    <div className="max-w-2xl mx-auto mt-24">
      <div className="text-center mb-8">
        <h2 className="font-serif text-3xl font-bold text-ink-white mb-2">
          Interrogate Your Documents
        </h2>
        <p className="text-ink-muted font-mono text-sm">
          Upload a PDF. Get an executive brief. Ask anything.
        </p>
      </div>

      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => !isProcessing && inputRef.current?.click()}
        className={`
          relative cursor-pointer border-2 border-dashed rounded-xl p-16
          transition-all duration-300 group
          ${isDragging
            ? 'border-safety-orange bg-safety-orange-glow'
            : 'border-charcoal-600 hover:border-charcoal-500 bg-charcoal-900/50'}
          ${isProcessing ? 'pointer-events-none opacity-60' : ''}
        `}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          onChange={handleSelect}
          className="hidden"
        />

        <div className="flex flex-col items-center gap-4">
          {isProcessing ? (
            <>
              <Loader2 size={40} className="text-safety-orange animate-spin" />
              <div>
                <p className="text-ink-white font-mono text-sm">Processing document...</p>
                <p className="text-ink-muted text-xs mt-1">Extracting, chunking, embedding, briefing</p>
              </div>
            </>
          ) : (
            <>
              <div className="w-16 h-16 border border-charcoal-600 rounded-xl flex items-center justify-center
                            group-hover:border-safety-orange/50 group-hover:bg-safety-orange/5 transition-all">
                {isDragging ? (
                  <FileUp size={28} className="text-safety-orange" />
                ) : (
                  <Upload size={28} className="text-charcoal-500 group-hover:text-safety-orange transition-colors" />
                )}
              </div>
              <div className="text-center">
                <p className="text-ink-white font-mono text-sm">
                  Drop a PDF here or <span className="text-safety-orange underline underline-offset-4">browse</span>
                </p>
                <p className="text-ink-muted text-xs mt-2 font-mono">
                  Powered by Claude &middot; Citations guaranteed
                </p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
