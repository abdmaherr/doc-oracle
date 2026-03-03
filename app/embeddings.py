from sentence_transformers import SentenceTransformer

from app.config import settings


class EmbeddingClient:
    """Local embedding using sentence-transformers. No API calls, no cost."""

    def __init__(self, model_name: str = settings.EMBEDDING_MODEL):
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts. Returns list of embedding vectors."""
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()

    def embed_query(self, query: str) -> list[float]:
        """Embed a single query string."""
        embedding = self.model.encode([query], show_progress_bar=False)
        return embedding[0].tolist()
