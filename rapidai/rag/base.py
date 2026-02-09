"""Base classes for RAG components."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from ..types import Document, DocumentChunk
from .config import EmbeddingConfig


class BaseEmbedding(ABC):
    """Base class for embedding providers.

    Separate from BaseLLM because:
    - Anthropic doesn't support embeddings
    - Embeddings and chat completion are different operations
    - Allows mixing: Anthropic LLM + OpenAI embeddings
    """

    def __init__(self, config: EmbeddingConfig):
        """Initialize embedding provider.

        Args:
            config: Embedding configuration
        """
        self.config = config

    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text.

        Args:
            text: Text to embed

        Returns:
            List of embedding values
        """
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return embedding dimension."""
        pass


class BaseDocumentLoader(ABC):
    """Base class for document loaders."""

    @abstractmethod
    async def load(self, source: Union[str, Path]) -> Document:
        """Load a document from source.

        Args:
            source: File path to load

        Returns:
            Loaded document
        """
        pass

    async def load_batch(self, sources: List[Union[str, Path]]) -> List[Document]:
        """Load multiple documents.

        Args:
            sources: List of file paths

        Returns:
            List of loaded documents
        """
        documents = []
        for source in sources:
            doc = await self.load(source)
            documents.append(doc)
        return documents


class BaseChunker(ABC):
    """Base class for text chunking strategies."""

    @abstractmethod
    def chunk(self, document: Document) -> List[DocumentChunk]:
        """Split document into chunks.

        Args:
            document: Document to chunk

        Returns:
            List of document chunks
        """
        pass


class BaseVectorDB(ABC):
    """Base class for vector database backends."""

    @abstractmethod
    async def create_collection(
        self, name: str, dimension: int, **kwargs: Any
    ) -> None:
        """Create a collection/index.

        Args:
            name: Collection name
            dimension: Embedding dimension
            **kwargs: Additional backend-specific parameters
        """
        pass

    @abstractmethod
    async def add_chunks(
        self, collection: str, chunks: List[DocumentChunk]
    ) -> None:
        """Add chunks to collection.

        Args:
            collection: Collection name
            chunks: List of chunks with embeddings
        """
        pass

    @abstractmethod
    async def search(
        self,
        collection: str,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[DocumentChunk]:
        """Search for similar chunks.

        Args:
            collection: Collection name
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filter_metadata: Optional metadata filters

        Returns:
            List of similar chunks
        """
        pass

    @abstractmethod
    async def delete_collection(self, name: str) -> None:
        """Delete a collection.

        Args:
            name: Collection name
        """
        pass
