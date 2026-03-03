# DOC.ORACLE — PDF Intelligence System

A production-grade RAG application with a React/Tailwind "Cyber-Monochrome" frontend. Upload PDFs, get an AI-generated executive brief, then interrogate the document with cited answers powered by Claude.

## Architecture

```
┌──────────────────┐     ┌──────────────┐     ┌──────────────────┐
│  React + Tailwind│────▶│   FastAPI    │────▶│  PDF Processor   │
│  Cyber-Monochrome│◀────│   REST API   │     │  (PyMuPDF)       │
│  Frontend (Vite) │     └──────┬───────┘     └────────┬─────────┘
└──────────────────┘            │                      │
                         ┌──────▼───────┐     ┌────────▼─────────┐
                         │  Retriever   │────▶│  Embedding Client│
                         │  (top-k=5)   │     │  (MiniLM-L6-v2)  │
                         └──────┬───────┘     └──────────────────┘
                                │
                         ┌──────▼───────┐     ┌──────────────────┐
                         │   ChromaDB   │     │  Claude Sonnet   │
                         │  Vector Store│     │  (Anthropic API) │
                         └──────────────┘     └──────────────────┘
```

**Flow:** PDF → Parse pages → Executive Brief (Claude) → Chunk (1000 chars, 200 overlap) → Embed locally → Store in ChromaDB → Query → Retrieve top-5 → Claude generates cited answer with TL;DR

## Key Design Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| No LangChain | Direct SDKs | Cleaner, more debuggable, fewer abstractions |
| Local embeddings | sentence-transformers | Zero API cost, no rate limits, ~80MB model |
| Claude Sonnet | Anthropic API | Superior instruction-following, reliable citations |
| ChromaDB | Persistent local | Zero infrastructure, easy to swap later |
| React + Tailwind | Vite frontend | Fast dev, modern stack, custom aesthetic |

## Tech Stack

**Backend:**
- Python 3.11, FastAPI, Anthropic SDK (Claude)
- sentence-transformers/all-MiniLM-L6-v2 (local embeddings)
- ChromaDB (vector store), PyMuPDF (PDF extraction)

**Frontend:**
- React 19, Tailwind CSS v4, Vite
- Playfair Display (serif headings) + JetBrains Mono (data)
- Cyber-Monochrome theme: charcoal + white + Safety Orange (#FF6B00)

## Quick Start

### 1. Backend Setup

```bash
cd rag-pdf-chatbot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
# Get your key: https://console.anthropic.com/
```

### 3. Start Backend

```bash
uvicorn app.api:app --reload --port 8000
```

### 4. Start Frontend (separate terminal)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — upload a PDF, read the executive brief, and start chatting.

### 5. CLI Usage (no UI needed)

```bash
# Ingest a PDF
python -m execution.ingest_pdf path/to/document.pdf

# Query it
python -m execution.query_rag <collection_name> "What is this document about?"

# List collections
python -m execution.query_rag --list
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload PDF → returns brief + collection info |
| POST | `/query` | Ask a question with chat history |
| GET | `/collections` | List uploaded PDFs |
| DELETE | `/collections/{name}` | Remove a PDF |
| GET | `/health` | Health check |

Full interactive docs at `http://localhost:8000/docs`.

## Project Structure

```
rag-pdf-chatbot/
├── app/                    # Backend source
│   ├── config.py           # Settings (Pydantic)
│   ├── pdf_processor.py    # PDF parsing + chunking
│   ├── embeddings.py       # Local embedding wrapper
│   ├── vectorstore.py      # ChromaDB wrapper
│   ├── retriever.py        # Retrieval pipeline
│   ├── llm.py              # Claude response generation
│   └── api.py              # FastAPI endpoints + CORS
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Header, UploadZone, ExecutiveBrief, ChatMessage, etc.
│   │   ├── api.js          # API client functions
│   │   ├── App.jsx         # Main application
│   │   └── index.css       # Tailwind + Cyber-Monochrome theme
│   └── vite.config.js      # Vite + proxy to backend
├── execution/              # CLI scripts
├── tests/                  # Test suite
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Features

- **Executive Brief**: Auto-generated 3-5 bullet summary on PDF upload
- **Cited Answers**: Every response includes [Page N] citations with expandable source text
- **Missing Info Handling**: Explicitly states when information isn't in the document
- **Chat Memory**: Maintains conversation context across multiple questions
- **Staggered Animations**: CSS animation-delay for smooth message reveals
- **Grain Overlay**: Subtle noise texture + CSS grid background for depth

## Scaling Path

| Bottleneck | Solution |
|-----------|----------|
| Many concurrent users | Add Redis for sessions, gunicorn workers |
| 100K+ chunks | Migrate to Pinecone or Qdrant |
| Large PDF processing | Background task queue (Celery) |
| Better retrieval quality | Add Cohere reranker |
| Streaming responses | Use Claude streaming API + SSE to frontend |
