# RAG PDF Chatbot — Directive

## Business Problem
Users need to quickly extract answers from PDF documents without reading the entire document. Traditional keyword search misses semantic meaning. This system uses RAG to provide accurate, cited answers.

## Architecture
3-layer system per agents.md:
- **Directives**: This file and related SOPs
- **Orchestration**: FastAPI API layer routes between ingestion and query pipelines
- **Execution**: CLI scripts in `execution/` for standalone pipeline testing

## Pipeline
1. PDF upload → PyMuPDF extracts text by page
2. Text chunked (1000 chars, 200 overlap, recursive character split)
3. Chunks embedded locally with all-MiniLM-L6-v2 (384 dims)
4. Embeddings stored in ChromaDB (persistent, cosine similarity)
5. Query → embed → retrieve top-5 chunks → Gemini generates cited answer

## Known Constraints
- Gemini free tier: 15 RPM, 1M TPM — sufficient for demo/personal use
- ChromaDB: single-process, not suited for multi-server deployment
- Local embeddings: CPU-bound, ~1 second per batch on modern hardware
- PDF text extraction only — no OCR for scanned documents

## Learned Edge Cases
- (Update this section as issues are discovered during usage)
