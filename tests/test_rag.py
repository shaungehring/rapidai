"""Tests for RAG system."""

import pytest
from pathlib import Path

from rapidai.types import Document, DocumentChunk
from rapidai.rag import (
    RAG,
    MockEmbedding,
    MockVectorDB,
    RecursiveChunker,
    SentenceChunker,
    rag,
)
from rapidai.llm import MockLLM


@pytest.mark.asyncio
async def test_mock_embedding():
    """Test mock embedding provider."""
    embedding = MockEmbedding(dimension=384)

    # Test single text
    result = await embedding.embed_text("test text")
    assert len(result) == 384
    assert all(isinstance(x, float) for x in result)
    assert embedding.embed_calls == 1

    # Test batch
    results = await embedding.embed_batch(["text1", "text2", "text3"])
    assert len(results) == 3
    assert all(len(r) == 384 for r in results)
    assert embedding.embed_calls == 4  # 1 + 3


@pytest.mark.asyncio
async def test_mock_vectordb():
    """Test mock vector database."""
    vectordb = MockVectorDB()

    # Create collection
    await vectordb.create_collection("test", dimension=384)
    assert "test" in vectordb.collections

    # Add chunks
    chunks = [
        DocumentChunk(
            content="chunk 1",
            metadata={"source": "test.txt", "chunk_index": 0},
            embedding=[0.1] * 384,
        ),
        DocumentChunk(
            content="chunk 2",
            metadata={"source": "test.txt", "chunk_index": 1},
            embedding=[0.2] * 384,
        ),
    ]
    await vectordb.add_chunks("test", chunks)
    assert len(vectordb.collections["test"]) == 2

    # Search
    results = await vectordb.search("test", query_embedding=[0.15] * 384, top_k=1)
    assert len(results) == 1
    assert results[0].content == "chunk 1"

    # Delete collection
    await vectordb.delete_collection("test")
    assert "test" not in vectordb.collections


def test_recursive_chunker():
    """Test recursive chunking strategy."""
    chunker = RecursiveChunker(chunk_size=50, chunk_overlap=10)

    doc = Document(
        content="This is a test document.\n\nIt has multiple paragraphs.\n\nAnd some more text here.",
        metadata={"source": "test.txt"},
    )

    chunks = chunker.chunk(doc)
    assert len(chunks) > 0
    assert all(isinstance(c, DocumentChunk) for c in chunks)
    assert all(c.metadata["source"] == "test.txt" for c in chunks)
    assert all("chunk_index" in c.metadata for c in chunks)


def test_sentence_chunker():
    """Test sentence chunking strategy."""
    chunker = SentenceChunker(chunk_size=100, chunk_overlap=1)

    doc = Document(
        content="First sentence. Second sentence. Third sentence. Fourth sentence.",
        metadata={"source": "test.txt"},
    )

    chunks = chunker.chunk(doc)
    assert len(chunks) > 0
    assert all(isinstance(c, DocumentChunk) for c in chunks)


@pytest.mark.asyncio
async def test_rag_pipeline():
    """Test full RAG pipeline with mocks."""
    # Setup
    embedding = MockEmbedding(dimension=384)
    vectordb = MockVectorDB()
    chunker = RecursiveChunker(chunk_size=100, chunk_overlap=20)

    rag_system = RAG(embedding=embedding, vectordb=vectordb, chunker=chunker)

    # Create test document
    doc = Document(
        content="RapidAI is a Python framework for building AI applications. "
        "It supports RAG, streaming, and caching. "
        "RAG stands for Retrieval-Augmented Generation.",
        metadata={"source": "test.txt", "type": "txt", "filename": "test.txt"},
    )

    # Add document
    chunks = await rag_system.add_document(doc)
    assert len(chunks) > 0
    assert all(chunk.embedding is not None for chunk in chunks)
    assert all(len(chunk.embedding) == 384 for chunk in chunks)

    # Retrieve
    result = await rag_system.retrieve("What is RAG?", top_k=3)
    assert result.text
    assert len(result.sources) <= 3
    assert len(result.sources) > 0


@pytest.mark.asyncio
async def test_rag_add_multiple_documents():
    """Test adding multiple documents."""
    embedding = MockEmbedding(dimension=128)
    vectordb = MockVectorDB()
    rag_system = RAG(embedding=embedding, vectordb=vectordb)

    docs = [
        Document(content="Document 1 content", metadata={"source": "doc1.txt"}),
        Document(content="Document 2 content", metadata={"source": "doc2.txt"}),
        Document(content="Document 3 content", metadata={"source": "doc3.txt"}),
    ]

    all_chunks = await rag_system.add_documents(docs)
    assert len(all_chunks) == 3
    assert all(len(chunks) > 0 for chunks in all_chunks)


@pytest.mark.asyncio
async def test_rag_query_with_llm():
    """Test RAG query with LLM generation."""
    # Setup RAG
    embedding = MockEmbedding(dimension=128)
    vectordb = MockVectorDB()
    rag_system = RAG(embedding=embedding, vectordb=vectordb)

    # Setup LLM
    llm = MockLLM()
    llm.set_responses(["The answer is 42."])

    # Add document
    doc = Document(
        content="The answer to life, the universe, and everything is 42.",
        metadata={"source": "guide.txt"},
    )
    await rag_system.add_document(doc)

    # Query
    answer = await rag_system.query(
        "What is the answer?", llm=llm, top_k=1
    )
    assert answer == "The answer is 42."


@pytest.mark.asyncio
async def test_rag_metadata_filtering():
    """Test retrieval with metadata filtering."""
    embedding = MockEmbedding(dimension=128)
    vectordb = MockVectorDB()
    rag_system = RAG(embedding=embedding, vectordb=vectordb)

    # Add documents with different types
    docs = [
        Document(content="PDF content", metadata={"source": "doc1.pdf", "type": "pdf"}),
        Document(content="Text content", metadata={"source": "doc2.txt", "type": "txt"}),
    ]
    await rag_system.add_documents(docs)

    # Retrieve with filter
    result = await rag_system.retrieve(
        "content",
        top_k=5,
        filter_metadata={"type": "pdf"}
    )

    # All sources should be PDF
    assert all(chunk.metadata.get("type") == "pdf" for chunk in result.sources)


@pytest.mark.asyncio
async def test_rag_decorator_basic():
    """Test @rag decorator basic functionality."""
    embedding = MockEmbedding(dimension=128)
    vectordb = MockVectorDB()

    # Create decorator with mock components
    from rapidai.rag.decorator import rag as rag_decorator
    from rapidai.rag.config import RAGConfig

    @rag_decorator(top_k=3)
    async def ask(query: str, rag_context):
        assert rag_context is not None
        return {"context": rag_context.text}

    # Note: Full decorator test would require app integration
    # This tests the decorator wrapping
    assert callable(ask)
