"""RAG (Retrieval-Augmented Generation) system for RapidAI."""

from .base import BaseChunker, BaseDocumentLoader, BaseEmbedding, BaseVectorDB
from .chunking import Chunker, RecursiveChunker, SentenceChunker
from .config import ChunkingConfig, EmbeddingConfig, RAGConfig, VectorDBConfig
from .decorator import rag
from .embeddings import Embedding, OpenAIEmbedding, SentenceTransformerEmbedding
from .loaders import (
    DOCXLoader,
    DocumentLoader,
    HTMLLoader,
    MarkdownLoader,
    PDFLoader,
    TextLoader,
)
from .mocks import MockEmbedding, MockVectorDB
from .retriever import RAG
from .vectordb import ChromaDB, VectorDB

__all__ = [
    # Main classes
    "RAG",
    "rag",
    # Factories
    "Embedding",
    "DocumentLoader",
    "Chunker",
    "VectorDB",
    # Base classes
    "BaseEmbedding",
    "BaseDocumentLoader",
    "BaseChunker",
    "BaseVectorDB",
    # Embeddings
    "SentenceTransformerEmbedding",
    "OpenAIEmbedding",
    # Loaders
    "PDFLoader",
    "DOCXLoader",
    "TextLoader",
    "MarkdownLoader",
    "HTMLLoader",
    # Chunkers
    "RecursiveChunker",
    "SentenceChunker",
    # Vector DBs
    "ChromaDB",
    # Mocks
    "MockEmbedding",
    "MockVectorDB",
    # Config
    "RAGConfig",
    "EmbeddingConfig",
    "ChunkingConfig",
    "VectorDBConfig",
]
