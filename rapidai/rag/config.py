"""RAG configuration for RapidAI."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EmbeddingConfig(BaseSettings):
    """Embedding configuration."""

    model_config = SettingsConfigDict(env_prefix="RAPIDAI_EMBEDDING_", extra="ignore")

    provider: str = "sentence-transformers"
    model: str = "all-MiniLM-L6-v2"
    batch_size: int = 32
    api_key: Optional[str] = None


class ChunkingConfig(BaseSettings):
    """Chunking configuration."""

    model_config = SettingsConfigDict(env_prefix="RAPIDAI_CHUNKING_", extra="ignore")

    strategy: str = "recursive"
    chunk_size: int = 512
    chunk_overlap: int = 50
    separator: str = "\n\n"


class VectorDBConfig(BaseSettings):
    """Vector database configuration."""

    model_config = SettingsConfigDict(env_prefix="RAPIDAI_VECTORDB_", extra="ignore")

    backend: str = "chromadb"
    persist_directory: str = "./chroma_data"
    collection_name: str = "rapidai_docs"


class RAGConfig(BaseSettings):
    """RAG configuration."""

    model_config = SettingsConfigDict(env_prefix="RAPIDAI_RAG_", extra="ignore")

    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    vectordb: VectorDBConfig = Field(default_factory=VectorDBConfig)
    top_k: int = 5
    enable_caching: bool = True
    cache_ttl: int = 3600
