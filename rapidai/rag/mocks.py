"""Mock implementations for RAG testing."""

from typing import Any, Dict, List, Optional
import hashlib

from ..types import DocumentChunk
from .base import BaseEmbedding, BaseVectorDB
from .config import EmbeddingConfig


class MockEmbedding(BaseEmbedding):
    """Mock embedding provider for testing."""

    def __init__(self, dimension: int = 384, **kwargs: Any):
        """Initialize mock embedding.

        Args:
            dimension: Embedding dimension
            **kwargs: Additional parameters
        """
        config = EmbeddingConfig(provider="mock", model="mock", **kwargs)
        super().__init__(config)
        self._dimension = dimension
        self.embed_calls = 0

    async def embed_text(self, text: str) -> List[float]:
        """Return mock embedding.

        Args:
            text: Text to embed

        Returns:
            Deterministic embedding based on text hash
        """
        self.embed_calls += 1
        # Return deterministic embedding based on text hash
        hash_val = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
        return [(hash_val % 100) / 100.0] * self._dimension

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Return mock embeddings for batch.

        Args:
            texts: List of texts to embed

        Returns:
            List of mock embeddings
        """
        return [await self.embed_text(text) for text in texts]

    @property
    def dimension(self) -> int:
        """Return embedding dimension."""
        return self._dimension


class MockVectorDB(BaseVectorDB):
    """Mock vector database for testing."""

    def __init__(self, **kwargs: Any):
        """Initialize mock vector database."""
        self.collections: Dict[str, List[DocumentChunk]] = {}

    async def create_collection(
        self, name: str, dimension: int, **kwargs: Any
    ) -> None:
        """Create a collection.

        Args:
            name: Collection name
            dimension: Embedding dimension
            **kwargs: Additional parameters
        """
        if name not in self.collections:
            self.collections[name] = []

    async def add_chunks(
        self, collection: str, chunks: List[DocumentChunk]
    ) -> None:
        """Add chunks to collection.

        Args:
            collection: Collection name
            chunks: List of chunks to add
        """
        if collection not in self.collections:
            self.collections[collection] = []
        self.collections[collection].extend(chunks)

    async def search(
        self,
        collection: str,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[DocumentChunk]:
        """Search for similar chunks (returns first top_k).

        Args:
            collection: Collection name
            query_embedding: Query embedding
            top_k: Number of results
            filter_metadata: Metadata filters

        Returns:
            First top_k chunks (mock doesn't do actual similarity)
        """
        if collection not in self.collections:
            return []

        chunks = self.collections[collection]

        # Apply metadata filter if provided
        if filter_metadata:
            chunks = [
                c
                for c in chunks
                if all(c.metadata.get(k) == v for k, v in filter_metadata.items())
            ]

        # Return top_k (mock doesn't do actual similarity)
        return chunks[:top_k]

    async def delete_collection(self, name: str) -> None:
        """Delete a collection.

        Args:
            name: Collection name
        """
        if name in self.collections:
            del self.collections[name]
