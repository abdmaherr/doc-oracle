import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Groq (free tier - very fast inference)
    GROQ_API_KEY: str = ""

    # LLM
    LLM_MODEL: str = "llama-3.3-70b-versatile"

    # Embeddings (local sentence-transformers - no API key needed)
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # Chunking
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # Retrieval
    TOP_K: int = 5

    # ChromaDB
    CHROMA_PERSIST_DIR: str = str(
        Path(__file__).resolve().parent.parent / "chroma_data"
    )

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Temp directory
    TMP_DIR: str = str(Path(__file__).resolve().parent.parent / ".tmp")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

# Ensure directories exist
os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
os.makedirs(settings.TMP_DIR, exist_ok=True)
