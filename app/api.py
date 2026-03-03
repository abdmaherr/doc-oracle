import shutil
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings
from app.pdf_processor import process_pdf, extract_text_by_page
from app.embeddings import EmbeddingClient
from app.vectorstore import VectorStore
from app.retriever import Retriever
from app.llm import LLMClient

app = FastAPI(
    title="RAG PDF Chatbot API",
    description="Upload PDFs and ask questions using retrieval-augmented generation.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared instances (initialized once, reused across requests)
embedding_client = EmbeddingClient()
vectorstore = VectorStore()
retriever = Retriever(vectorstore=vectorstore, embedding_client=embedding_client)
llm_client = LLMClient()


# --- Request/Response Models ---


class QueryRequest(BaseModel):
    collection_name: str
    question: str
    chat_history: list[dict] = []


class SourceInfo(BaseModel):
    page: int
    text_snippet: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceInfo]
    chunks_used: int


class BriefResponse(BaseModel):
    bullets: list[str]
    bottom_line: str


class UploadResponse(BaseModel):
    collection_name: str
    total_pages: int
    total_chunks: int
    message: str
    brief: BriefResponse | None = None


# --- Endpoints ---


@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF for question answering."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    # Save to temp directory
    tmp_path = Path(settings.TMP_DIR) / file.filename
    with open(tmp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        # Extract raw pages for brief generation
        pages = extract_text_by_page(str(tmp_path))

        # Process PDF into chunks
        result = process_pdf(str(tmp_path), filename=file.filename)

        # Generate executive brief
        brief = None
        try:
            pages_for_brief = [
                {"page_number": p["page"], "text": p["text"]} for p in pages
            ]
            brief_data = llm_client.generate_brief(pages_for_brief)
            brief = BriefResponse(**brief_data)
        except Exception as e:
            brief = BriefResponse(
                bullets=[f"Brief generation failed: {str(e)}"],
                bottom_line="Please query the document directly.",
            )

        # Check if already ingested
        if not vectorstore.collection_exists(result["collection_name"]):
            # Generate embeddings
            texts = [chunk["text"] for chunk in result["chunks"]]
            embeddings = embedding_client.embed_texts(texts)

            # Store in ChromaDB
            vectorstore.add_documents(
                collection_name=result["collection_name"],
                chunks=result["chunks"],
                embeddings=embeddings,
            )

        return UploadResponse(
            collection_name=result["collection_name"],
            total_pages=result["total_pages"],
            total_chunks=result["total_chunks"],
            message="PDF processed and indexed successfully.",
            brief=brief,
        )
    finally:
        # Clean up temp file
        tmp_path.unlink(missing_ok=True)


@app.post("/query", response_model=QueryResponse)
async def query_document(request: QueryRequest):
    """Ask a question about an uploaded PDF."""
    if not vectorstore.collection_exists(request.collection_name):
        raise HTTPException(
            status_code=404,
            detail=f"Collection '{request.collection_name}' not found. Upload a PDF first.",
        )

    # Retrieve relevant chunks
    chunks = retriever.retrieve(request.collection_name, request.question)

    if not chunks:
        return QueryResponse(
            answer="I couldn't find any relevant information in the document for your question.",
            sources=[],
            chunks_used=0,
        )

    # Generate response
    try:
        response = llm_client.generate_response(
            query=request.question,
            context_chunks=chunks,
            chat_history=request.chat_history if request.chat_history else None,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=502, detail=f"LLM generation failed: {str(e)}"
        )

    return QueryResponse(
        answer=response["answer"],
        sources=[SourceInfo(**s) for s in response["sources"]],
        chunks_used=len(chunks),
    )


@app.get("/collections")
async def list_collections():
    """List all uploaded PDF collections."""
    return {"collections": vectorstore.list_collections()}


@app.delete("/collections/{name}")
async def delete_collection(name: str):
    """Delete a PDF collection from the vector store."""
    if not vectorstore.collection_exists(name):
        raise HTTPException(status_code=404, detail=f"Collection '{name}' not found.")
    vectorstore.delete_collection(name)
    return {"message": f"Collection '{name}' deleted."}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": settings.LLM_MODEL}
