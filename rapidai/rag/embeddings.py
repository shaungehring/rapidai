"""Embedding implementations for RAG."""

import asyncio
import os
from typing import List, Optional

from ..exceptions import EmbeddingError
from .base import BaseEmbedding
from .config import EmbeddingConfig
from .mocks import MockEmbedding


class SentenceTransformerEmbedding(BaseEmbedding):
    """sentence-transformers embedding provider."""

    def __init__(
        self, model: str = "all-MiniLM-L6-v2", batch_size: int = 32, **kwargs
    ):
        """Initialize sentence-transformers embedding.

        Args:
            model: Model name
            batch_size: Batch size for encoding
            **kwargs: Additional parameters
        """
        config = EmbeddingConfig(
            provider="sentence-transformers",
            model=model,
            batch_size=batch_size,
            **kwargs,
        )
        super().__init__(config)

        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(model)
        except ImportError:
            raise EmbeddingError(
                "sentence-transformers not installed. "
                "Install with: pip install rapidai-framework[rag]"
            )

    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        # Run in thread pool since sentence-transformers is sync
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(None, self.model.encode, text)
        return embedding.tolist()

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(None, self.model.encode, texts)
        return [emb.tolist() for emb in embeddings]

    @property
    def dimension(self) -> int:
        """Return embedding dimension."""
        return self.model.get_sentence_embedding_dimension()


class OpenAIEmbedding(BaseEmbedding):
    """OpenAI embedding provider."""

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_key: Optional[str] = None,
        **kwargs,
    ):
        """Initialize OpenAI embedding.

        Args:
            model: Model name
            api_key: API key (or use OPENAI_API_KEY env var)
            **kwargs: Additional parameters
        """
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EmbeddingError(
                "OpenAI API key not found. "
                "Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )

        config = EmbeddingConfig(
            provider="openai", model=model, api_key=api_key, **kwargs
        )
        super().__init__(config)

        try:
            from openai import AsyncOpenAI

            self.client = AsyncOpenAI(api_key=api_key)
        except ImportError:
            raise EmbeddingError(
                "openai not installed. Install with: pip install rapidai-framework[openai]"
            )

    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        try:
            response = await self.client.embeddings.create(
                model=self.config.model, input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise EmbeddingError(f"OpenAI embedding error: {str(e)}")

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        try:
            response = await self.client.embeddings.create(
                model=self.config.model, input=texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            raise EmbeddingError(f"OpenAI embedding error: {str(e)}")

    @property
    def dimension(self) -> int:
        """Return embedding dimension."""
        # text-embedding-3-small: 1536, text-embedding-3-large: 3072
        if "large" in self.config.model:
            return 3072
        return 1536


def Embedding(provider: str = "sentence-transformers", **kwargs) -> BaseEmbedding:
    """Factory function to create embedding instances.

    Args:
        provider: Embedding provider ("sentence-transformers", "openai", "mock")
        **kwargs: Additional parameters passed to embedding class

    Returns:
        Embedding instance

    Example:
        ```python
        # Sentence transformers (default)
        embedding = Embedding()

        # OpenAI
        embedding = Embedding(provider="openai", model="text-embedding-3-large")

        # Mock for testing
        embedding = Embedding(provider="mock", dimension=384)
        ```
    """
    if provider == "sentence-transformers":
        return SentenceTransformerEmbedding(**kwargs)
    elif provider == "openai":
        return OpenAIEmbedding(**kwargs)
    elif provider == "mock":
        return MockEmbedding(**kwargs)
    else:
        raise EmbeddingError(f"Unknown embedding provider: {provider}")
