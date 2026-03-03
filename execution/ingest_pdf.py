"""
CLI script: Ingest a PDF into the vector store.

Usage:
    python -m execution.ingest_pdf path/to/document.pdf
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.pdf_processor import process_pdf
from app.embeddings import EmbeddingClient
from app.vectorstore import VectorStore


def main(pdf_path: str) -> None:
    if not Path(pdf_path).exists():
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)

    print(f"Processing: {pdf_path}")

    # Step 1: Parse and chunk PDF
    result = process_pdf(pdf_path)
    print(f"  Pages extracted: {result['total_pages']}")
    print(f"  Chunks created: {result['total_chunks']}")
    print(f"  Collection name: {result['collection_name']}")

    # Step 2: Generate embeddings
    print("Generating embeddings...")
    embedding_client = EmbeddingClient()
    texts = [chunk["text"] for chunk in result["chunks"]]
    embeddings = embedding_client.embed_texts(texts)
    print(f"  Embeddings generated: {len(embeddings)} x {len(embeddings[0])} dims")

    # Step 3: Store in ChromaDB
    print("Storing in vector database...")
    vectorstore = VectorStore()
    vectorstore.add_documents(
        collection_name=result["collection_name"],
        chunks=result["chunks"],
        embeddings=embeddings,
    )
    print(f"  Stored in collection: {result['collection_name']}")

    print("Done! PDF ingested successfully.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m execution.ingest_pdf <path_to_pdf>")
        sys.exit(1)
    main(sys.argv[1])
