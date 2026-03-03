import os
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """Embedding client with automatic backend selection.

    Uses sentence-transformers locally (better quality) if available,
    falls back to chromadb's built-in embeddings (lighter, no PyTorch).
    """

    def __init__(self, model_name: str = settings.EMBEDDING_MODEL):
        self._model = None
        self._use_lightweight = os.environ.get("LIGHTWEIGHT_EMBEDDINGS", "").lower() == "true"

        if self._use_lightweight:
            logger.info("Using ChromaDB default embeddings (lightweight mode)")
        else:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(model_name)
                logger.info(f"Loaded sentence-transformers model: {model_name}")
            except Exception as e:
                logger.warning(f"sentence-transformers unavailable ({e}), using lightweight embeddings")
                self._use_lightweight = True

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts. Returns list of embedding vectors."""
        if self._use_lightweight:
            return self._lightweight_embed(texts)
        embeddings = self._model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()

    def embed_query(self, query: str) -> list[float]:
        """Embed a single query string."""
        if self._use_lightweight:
            return self._lightweight_embed([query])[0]
        embedding = self._model.encode([query], show_progress_bar=False)
        return embedding[0].tolist()

    def _lightweight_embed(self, texts: list[str]) -> list[list[float]]:
        """Use chromadb's built-in embedding function (onnxruntime, no PyTorch)."""
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
        if not hasattr(self, '_default_ef'):
            self._default_ef = DefaultEmbeddingFunction()
        return [list(e) for e in self._default_ef(texts)]
