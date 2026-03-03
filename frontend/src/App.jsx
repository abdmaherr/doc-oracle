import { useState, useRef, useEffect } from 'react';
import Header from './components/Header';
import UploadZone from './components/UploadZone';
import ExecutiveBrief from './components/ExecutiveBrief';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import TypingIndicator from './components/TypingIndicator';
import { uploadPDF, queryDocument } from './api';

export default function App() {
  const [status, setStatus] = useState('idle');          // idle | processing | ready | error
  const [docName, setDocName] = useState(null);
  const [collectionName, setCollectionName] = useState(null);
  const [brief, setBrief] = useState(null);
  const [docMeta, setDocMeta] = useState({ pages: 0, chunks: 0 });
  const [messages, setMessages] = useState([]);
  const [isQuerying, setIsQuerying] = useState(false);
  const [error, setError] = useState(null);
  const scrollRef = useRef(null);

  // Auto-scroll on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isQuerying]);

  async function handleUpload(file) {
    setStatus('processing');
    setError(null);
    setDocName(file.name);
    setMessages([]);
    setBrief(null);

    try {
      const data = await uploadPDF(file);
      setCollectionName(data.collection_name);
      setDocMeta({ pages: data.total_pages, chunks: data.total_chunks });
      if (data.brief) {
        setBrief(data.brief);
      }
      setStatus('ready');
    } catch (err) {
      setError(err.message);
      setStatus('error');
    }
  }

  async function handleSend(question) {
    // Build chat history for context
    const history = messages.map((m) => ({
      role: m.role,
      content: m.content,
    }));

    // Add user message immediately
    setMessages((prev) => [...prev, { role: 'user', content: question }]);
    setIsQuerying(true);
    setError(null);

    try {
      const data = await queryDocument(collectionName, question, history);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.answer,
          sources: data.sources,
          chunksUsed: data.chunks_used,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `**Error:** ${err.message}`,
          sources: [],
        },
      ]);
    } finally {
      setIsQuerying(false);
    }
  }

  const hasDocument = status === 'ready' && collectionName;

  return (
    <div className="grid-bg min-h-screen flex flex-col">
      <Header docName={docName} status={status} />

      {/* Main content */}
      <main ref={scrollRef} className="flex-1 overflow-y-auto">
        {!hasDocument && status !== 'processing' ? (
          <UploadZone onUpload={handleUpload} isProcessing={status === 'processing'} />
        ) : status === 'processing' ? (
          <UploadZone onUpload={handleUpload} isProcessing={true} />
        ) : (
          <div className="max-w-3xl mx-auto px-4 py-6 space-y-6 pb-4">
            {/* Executive Brief */}
            <ExecutiveBrief
              brief={brief}
              docName={docName}
              totalPages={docMeta.pages}
              totalChunks={docMeta.chunks}
            />

            {/* New document upload hint */}
            <div className="flex items-center justify-between">
              <p className="text-[11px] text-ink-muted font-mono">
                Ask anything about <span className="text-safety-orange">{docName}</span>
              </p>
              <label className="text-[11px] text-ink-muted font-mono hover:text-safety-orange
                               cursor-pointer transition-colors underline underline-offset-4">
                Upload different PDF
                <input
                  type="file"
                  accept=".pdf"
                  className="hidden"
                  onChange={(e) => e.target.files[0] && handleUpload(e.target.files[0])}
                />
              </label>
            </div>

            {/* Chat messages */}
            <div className="space-y-5">
              {messages.map((msg, i) => (
                <ChatMessage key={i} message={msg} index={i} />
              ))}
              {isQuerying && <TypingIndicator />}
            </div>

            {/* Spacer for scroll */}
            <div className="h-4" />
          </div>
        )}

        {/* Error toast */}
        {error && (
          <div className="fixed bottom-24 left-1/2 -translate-x-1/2 z-50
                          bg-red-950/90 border border-red-800 text-red-200
                          px-5 py-3 rounded-lg font-mono text-sm msg-reveal
                          flex items-center gap-3">
            <span>{error}</span>
            <button
              onClick={() => setError(null)}
              className="text-red-400 hover:text-red-200 font-bold"
            >
              &times;
            </button>
          </div>
        )}
      </main>

      {/* Chat input — always visible */}
      <ChatInput
        onSend={handleSend}
        isLoading={isQuerying}
        disabled={!hasDocument}
      />
    </div>
  );
}
