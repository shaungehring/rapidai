"""RAG retriever and orchestrator."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..llm.base import BaseLLM
from ..types import Document, DocumentChunk, RetrievalResult
from .base import BaseChunker, BaseEmbedding, BaseVectorDB
from .chunking import Chunker
from .config import RAGConfig
from .embeddings import Embedding
from .loaders import DocumentLoader
from .vectordb import VectorDB


class RAG:
    """Main RAG orchestrator that ties everything together."""

    def __init__(
        self,
        embedding: Optional[BaseEmbedding] = None,
        vectordb: Optional[BaseVectorDB] = None,
        chunker: Optional[BaseChunker] = None,
        config: Optional[RAGConfig] = None,
    ):
        """Initialize RAG system.

        Args:
            embedding: Embedding provider (auto-created if None)
            vectordb: Vector database (auto-created if None)
            chunker: Chunker (auto-created if None)
            config: RAG configuration (loads from env if None)
        """
        self.config = config or RAGConfig()

        # Initialize components
        self.embedding = embedding or Embedding(
            provider=self.config.embedding.provider,
            model=self.config.embedding.model,
        )

        self.vectordb = vectordb or VectorDB(
            backend=self.config.vectordb.backend,
            persist_directory=self.config.vectordb.persist_directory,
        )

        self.chunker = chunker or Chunker(
            strategy=self.config.chunking.strategy,
            chunk_size=self.config.chunking.chunk_size,
            chunk_overlap=self.config.chunking.chunk_overlap,
        )

        self._collection_initialized = False

    async def initialize(self) -> None:
        """Initialize vector database collection."""
        if not self._collection_initialized:
            await self.vectordb.create_collection(
                name=self.config.vectordb.collection_name,
                dimension=self.embedding.dimension,
            )
            self._collection_initialized = True

    async def add_document(
        self, source: Union[str, Path, Document]
    ) -> List[DocumentChunk]:
        """Add a document to the RAG system.

        Args:
            source: File path or Document object

        Returns:
            List of created chunks

        Example:
            ```python
            rag = RAG()
            chunks = await rag.add_document("docs/manual.pdf")
            print(f"Added {len(chunks)} chunks")
            ```
        """
        await self.initialize()

        # Load document if needed
        if isinstance(source, (str, Path)):
            loader = DocumentLoader(source)
            document = await loader.load(source)
        else:
            document = source

        # Chunk document
        chunks = self.chunker.chunk(document)

        # Generate embeddings
        texts = [chunk.content for chunk in chunks]
        embeddings = await self.embedding.embed_batch(texts)

        # Attach embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding

        # Store in vector DB
        await self.vectordb.add_chunks(
            collection=self.config.vectordb.collection_name,
            chunks=chunks,
        )

        return chunks

    async def add_documents(
        self, sources: List[Union[str, Path, Document]]
    ) -> List[List[DocumentChunk]]:
        """Add multiple documents.

        Args:
            sources: List of file paths or Document objects

        Returns:
            List of chunk lists (one per document)

        Example:
            ```python
            rag = RAG()
            all_chunks = await rag.add_documents([
                "doc1.pdf",
                "doc2.md",
                "doc3.txt"
            ])
            ```
        """
        results = []
        for source in sources:
            chunks = await self.add_document(source)
            results.append(chunks)
        return results

    async def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> RetrievalResult:
        """Retrieve relevant chunks for a query.

        Args:
            query: Search query
            top_k: Number of results (default from config)
            filter_metadata: Metadata filters

        Returns:
            RetrievalResult with text and sources

        Example:
            ```python
            rag = RAG()
            result = await rag.retrieve("How do I install?", top_k=5)
            print(result.text)
            for chunk in result.sources:
                print(f"Source: {chunk.metadata['filename']}")
            ```
        """
        await self.initialize()

        k = top_k or self.config.top_k

        # Generate query embedding
        query_embedding = await self.embedding.embed_text(query)

        # Search vector DB
        chunks = await self.vectordb.search(
            collection=self.config.vectordb.collection_name,
            query_embedding=query_embedding,
            top_k=k,
            filter_metadata=filter_metadata,
        )

        # Combine chunk texts
        combined_text = "\n\n".join(
            [
                f"[Source: {chunk.metadata.get('filename', 'unknown')}]\n{chunk.content}"
                for chunk in chunks
            ]
        )

        return RetrievalResult(
            text=combined_text,
            sources=chunks,
            score=None,  # Could add relevance scoring
        )

    async def query(
        self,
        query: str,
        llm: BaseLLM,
        system_prompt: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> str:
        """Full RAG query: retrieve + generate.

        Args:
            query: User query
            llm: LLM instance to use for generation
            system_prompt: Optional system prompt
            top_k: Number of chunks to retrieve

        Returns:
            Generated response

        Example:
            ```python
            from rapidai import LLM
            from rapidai.rag import RAG

            llm = LLM("claude-3-haiku-20240307")
            rag = RAG()

            await rag.add_document("docs/manual.pdf")
            answer = await rag.query("How do I install?", llm=llm)
            print(answer)
            ```
        """
        # Retrieve relevant context
        retrieval = await self.retrieve(query, top_k=top_k)

        # Build prompt
        context = retrieval.text
        default_system = (
            "You are a helpful assistant. Answer the user's question based on the "
            "provided context. If the answer is not in the context, say so."
        )
        system = system_prompt or default_system

        prompt = f"""{system}

Context:
{context}

Question: {query}

Answer:"""

        # Generate response
        response = await llm.complete(prompt)
        return response
