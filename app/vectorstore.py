import chromadb

from app.config import settings


class VectorStore:
    """ChromaDB wrapper with persistent local storage."""

    def __init__(self, persist_directory: str = settings.CHROMA_PERSIST_DIR):
        self.client = chromadb.PersistentClient(path=persist_directory)

    def get_or_create_collection(self, name: str) -> chromadb.Collection:
        """Get existing collection or create a new one."""
        return self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(
        self,
        collection_name: str,
        chunks: list[dict],
        embeddings: list[list[float]],
    ) -> None:
        """Store chunks with their embeddings and metadata."""
        collection = self.get_or_create_collection(collection_name)
        ids = [f"{collection_name}_{i}" for i in range(len(chunks))]
        documents = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]

        # ChromaDB has a batch limit, process in batches of 500
        batch_size = 500
        for i in range(0, len(ids), batch_size):
            end = i + batch_size
            collection.add(
                ids=ids[i:end],
                documents=documents[i:end],
                embeddings=embeddings[i:end],
                metadatas=metadatas[i:end],
            )

    def query(
        self,
        collection_name: str,
        query_embedding: list[float],
        n_results: int = settings.TOP_K,
    ) -> dict:
        """Query collection for similar documents."""
        collection = self.get_or_create_collection(collection_name)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
        return results

    def list_collections(self) -> list[str]:
        """List all collection names."""
        return [col.name for col in self.client.list_collections()]

    def delete_collection(self, name: str) -> None:
        """Delete a collection."""
        self.client.delete_collection(name)

    def collection_exists(self, name: str) -> bool:
        """Check if a collection exists."""
        return name in self.list_collections()
