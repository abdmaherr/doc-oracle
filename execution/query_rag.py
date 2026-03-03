"""
CLI script: Query a PDF collection using RAG.

Usage:
    python -m execution.query_rag <collection_name> "Your question here"
    python -m execution.query_rag --list  # List available collections
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.retriever import Retriever
from app.llm import LLMClient
from app.vectorstore import VectorStore


def list_collections() -> None:
    vs = VectorStore()
    collections = vs.list_collections()
    if not collections:
        print("No collections found. Ingest a PDF first.")
        return
    print("Available collections:")
    for name in collections:
        print(f"  - {name}")


def query(collection_name: str, question: str) -> None:
    print(f"Collection: {collection_name}")
    print(f"Question: {question}\n")

    # Retrieve relevant chunks
    retriever = Retriever()
    chunks = retriever.retrieve(collection_name, question)

    if not chunks:
        print("No relevant chunks found.")
        return

    print(f"Retrieved {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks):
        page = chunk["metadata"].get("page_number", "?")
        dist = chunk["distance"]
        print(f"  [{i+1}] Page {page} (distance: {dist:.4f}): {chunk['text'][:100]}...")

    # Generate response
    print("\nGenerating answer...\n")
    llm = LLMClient()
    response = llm.generate_response(question, chunks)

    print(f"Answer:\n{response['answer']}\n")

    if response["sources"]:
        print("Sources:")
        for src in response["sources"]:
            print(f"  Page {src['page']}: {src['text_snippet'][:150]}...")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m execution.query_rag --list")
        print('  python -m execution.query_rag <collection_name> "question"')
        sys.exit(1)

    if sys.argv[1] == "--list":
        list_collections()
    elif len(sys.argv) >= 3:
        query(sys.argv[1], sys.argv[2])
    else:
        print("Provide both collection name and question.")
        sys.exit(1)
