from app.embeddings import EmbeddingClient
from app.vectorstore import VectorStore
from app.config import settings


class Retriever:
    """Orchestrates: query -> embed -> vector search -> ranked chunks."""

    def __init__(
        self,
        vectorstore: VectorStore | None = None,
        embedding_client: EmbeddingClient | None = None,
    ):
        self.vectorstore = vectorstore or VectorStore()
        self.embedding_client = embedding_client or EmbeddingClient()

    def retrieve(
        self,
        collection_name: str,
        query: str,
        top_k: int = settings.TOP_K,
    ) -> list[dict]:
        """
        Retrieve relevant chunks for a query.

        Returns list of dicts with keys: text, metadata, distance
        Sorted by relevance (lowest distance = most relevant).
        """
        query_embedding = self.embedding_client.embed_query(query)

        results = self.vectorstore.query(
            collection_name=collection_name,
            query_embedding=query_embedding,
            n_results=top_k,
        )

        # Unpack ChromaDB results into a clean list
        chunks = []
        if results["documents"] and results["documents"][0]:
            for i in range(len(results["documents"][0])):
                chunks.append(
                    {
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i],
                    }
                )

        return chunks
