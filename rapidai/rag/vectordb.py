"""Vector database implementations for RAG."""

from typing import Any, Dict, List, Optional

from ..exceptions import VectorDBError
from ..types import DocumentChunk
from .base import BaseVectorDB
from .mocks import MockVectorDB


class ChromaDB(BaseVectorDB):
    """ChromaDB vector database implementation."""

    def __init__(self, persist_directory: str = "./chroma_data"):
        """Initialize ChromaDB.

        Args:
            persist_directory: Directory to persist database
        """
        try:
            import chromadb
        except ImportError:
            raise VectorDBError(
                "chromadb not installed. Install with: pip install rapidai[rag]"
            )

        self.client = chromadb.PersistentClient(path=persist_directory)

    async def create_collection(
        self, name: str, dimension: int, **kwargs: Any
    ) -> None:
        """Create a collection.

        Args:
            name: Collection name
            dimension: Embedding dimension
            **kwargs: Additional parameters
        """
        try:
            self.client.get_or_create_collection(
                name=name, metadata={"dimension": dimension}
            )
        except Exception as e:
            raise VectorDBError(f"Failed to create collection {name}: {str(e)}")

    async def add_chunks(
        self, collection: str, chunks: List[DocumentChunk]
    ) -> None:
        """Add chunks to collection.

        Args:
            collection: Collection name
            chunks: List of chunks with embeddings
        """
        try:
            coll = self.client.get_collection(collection)

            ids = []
            documents = []
            embeddings = []
            metadatas = []

            for i, chunk in enumerate(chunks):
                if chunk.embedding is None:
                    raise VectorDBError(f"Chunk {i} has no embedding")

                # Generate unique ID
                source = chunk.metadata.get("source", "unknown")
                chunk_idx = chunk.metadata.get("chunk_index", i)
                chunk_id = f"{source}_{chunk_idx}_{i}"

                ids.append(chunk_id)
                documents.append(chunk.content)
                embeddings.append(chunk.embedding)
                metadatas.append(chunk.metadata)

            coll.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
            )
        except Exception as e:
            raise VectorDBError(f"Failed to add chunks to {collection}: {str(e)}")

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
        try:
            coll = self.client.get_collection(collection)

            results = coll.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter_metadata,
            )

            chunks = []
            for i in range(len(results["documents"][0])):
                embedding = (
                    results["embeddings"][0][i] if results.get("embeddings") else None
                )

                chunk = DocumentChunk(
                    content=results["documents"][0][i],
                    metadata=results["metadatas"][0][i],
                    embedding=embedding,
                )
                chunks.append(chunk)

            return chunks
        except Exception as e:
            raise VectorDBError(f"Search failed in {collection}: {str(e)}")

    async def delete_collection(self, name: str) -> None:
        """Delete a collection.

        Args:
            name: Collection name
        """
        try:
            self.client.delete_collection(name)
        except Exception as e:
            raise VectorDBError(f"Failed to delete collection {name}: {str(e)}")


def VectorDB(backend: str = "chromadb", **kwargs) -> BaseVectorDB:
    """Factory function to create vector database.

    Args:
        backend: Vector database backend ("chromadb", "mock")
        **kwargs: Additional parameters for vector database

    Returns:
        Vector database instance

    Example:
        ```python
        # ChromaDB (default)
        vectordb = VectorDB()

        # ChromaDB with custom directory
        vectordb = VectorDB(backend="chromadb", persist_directory="./my_data")

        # Mock for testing
        vectordb = VectorDB(backend="mock")
        ```
    """
    if backend == "chromadb":
        return ChromaDB(**kwargs)
    elif backend == "mock":
        return MockVectorDB(**kwargs)
    else:
        raise VectorDBError(f"Unknown vector database backend: {backend}")
