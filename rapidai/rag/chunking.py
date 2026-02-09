"""Text chunking strategies for RAG."""

import re
from typing import List

from ..exceptions import RAGError
from ..types import Document, DocumentChunk
from .base import BaseChunker


class RecursiveChunker(BaseChunker):
    """Recursively split text using multiple separators."""

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        separators: List[str] = None,
    ):
        """Initialize recursive chunker.

        Args:
            chunk_size: Maximum chunk size in characters
            chunk_overlap: Number of overlapping characters between chunks
            separators: List of separators to try (hierarchical)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]

    def chunk(self, document: Document) -> List[DocumentChunk]:
        """Split document into chunks.

        Args:
            document: Document to chunk

        Returns:
            List of document chunks
        """
        chunks_text = self._recursive_split(document.content, self.separators)

        result = []
        for i, chunk_text in enumerate(chunks_text):
            metadata = {
                **document.metadata,
                "chunk_index": i,
                "chunk_size": len(chunk_text),
            }
            result.append(DocumentChunk(content=chunk_text, metadata=metadata))

        return result

    def _recursive_split(self, text: str, separators: List[str]) -> List[str]:
        """Recursively split text using separators.

        Args:
            text: Text to split
            separators: List of separators

        Returns:
            List of text chunks
        """
        if not separators:
            return self._split_by_length(text)

        separator = separators[0]
        remaining_separators = separators[1:]

        splits = text.split(separator) if separator else [text]

        chunks = []
        current_chunk = ""

        for split in splits:
            # Add separator back if it's not the last one
            test_chunk = current_chunk + split + (separator if separator else "")

            if len(test_chunk) <= self.chunk_size:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())

                if len(split) > self.chunk_size:
                    # Recursively split with next separator
                    chunks.extend(self._recursive_split(split, remaining_separators))
                    current_chunk = ""
                else:
                    current_chunk = split + (separator if separator else "")

        if current_chunk:
            chunks.append(current_chunk.strip())

        # Apply overlap
        return self._apply_overlap(chunks)

    def _split_by_length(self, text: str) -> List[str]:
        """Split text by fixed length.

        Args:
            text: Text to split

        Returns:
            List of text chunks
        """
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk = text[i : i + self.chunk_size]
            if chunk:
                chunks.append(chunk)
        return chunks

    def _apply_overlap(self, chunks: List[str]) -> List[str]:
        """Add overlap between chunks.

        Args:
            chunks: List of chunks

        Returns:
            List of chunks with overlap
        """
        if not chunks or self.chunk_overlap == 0:
            return chunks

        overlapped = []
        for i, chunk in enumerate(chunks):
            if i > 0:
                # Add end of previous chunk
                prev_end = chunks[i - 1][-self.chunk_overlap :]
                chunk = prev_end + " " + chunk
            overlapped.append(chunk)

        return overlapped


class SentenceChunker(BaseChunker):
    """Split by sentences using simple heuristics."""

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 1):
        """Initialize sentence chunker.

        Args:
            chunk_size: Maximum chunk size in characters
            chunk_overlap: Number of sentences to overlap
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap  # Number of sentences to overlap

    def chunk(self, document: Document) -> List[DocumentChunk]:
        """Split document into chunks.

        Args:
            document: Document to chunk

        Returns:
            List of document chunks
        """
        sentences = self._split_sentences(document.content)

        chunks = []
        current_chunk = []
        current_size = 0

        for sentence in sentences:
            sentence_len = len(sentence)

            if current_size + sentence_len > self.chunk_size and current_chunk:
                # Create chunk
                chunk_text = " ".join(current_chunk)
                chunks.append(chunk_text)

                # Keep overlap sentences
                current_chunk = (
                    current_chunk[-self.chunk_overlap :]
                    if self.chunk_overlap > 0
                    else []
                )
                current_size = sum(len(s) for s in current_chunk)

            current_chunk.append(sentence)
            current_size += sentence_len

        # Add final chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        result = []
        for i, chunk_text in enumerate(chunks):
            metadata = {
                **document.metadata,
                "chunk_index": i,
                "chunk_size": len(chunk_text),
            }
            result.append(DocumentChunk(content=chunk_text, metadata=metadata))

        return result

    def _split_sentences(self, text: str) -> List[str]:
        """Simple sentence splitting.

        Args:
            text: Text to split

        Returns:
            List of sentences
        """
        # Split on common sentence terminators
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]


def Chunker(strategy: str = "recursive", **kwargs) -> BaseChunker:
    """Factory function to create chunker.

    Args:
        strategy: Chunking strategy ("recursive", "sentence")
        **kwargs: Additional parameters for chunker

    Returns:
        Chunker instance

    Example:
        ```python
        # Recursive chunking (default)
        chunker = Chunker()

        # Sentence-based chunking
        chunker = Chunker(strategy="sentence", chunk_size=512, chunk_overlap=2)
        ```
    """
    if strategy == "recursive":
        return RecursiveChunker(**kwargs)
    elif strategy == "sentence":
        return SentenceChunker(**kwargs)
    else:
        raise RAGError(f"Unknown chunking strategy: {strategy}")
