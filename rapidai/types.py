"""Type definitions for RapidAI."""

from typing import Any, AsyncIterator, Awaitable, Callable, Dict, List, Optional, Union
from enum import Enum
from dataclasses import dataclass


# Request/Response types
Request = Dict[str, Any]
Response = Dict[str, Any]
StreamResponse = AsyncIterator[str]

# Middleware type
Middleware = Callable[[Request, Callable[[], Awaitable[Response]]], Awaitable[Response]]

# Route handler types
RouteHandler = Callable[..., Awaitable[Union[Response, str, Dict[str, Any]]]]
StreamHandler = Callable[..., AsyncIterator[str]]


class HTTPMethod(str, Enum):
    """HTTP methods supported by RapidAI."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


@dataclass
class Message:
    """Represents a chat message."""

    role: str  # "user", "assistant", "system"
    content: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ConversationHistory:
    """Represents a conversation history."""

    messages: List[Message]
    user_id: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class Document:
    """Represents a document for RAG."""

    content: str
    metadata: Dict[str, Any]
    chunks: Optional[List["DocumentChunk"]] = None


@dataclass
class DocumentChunk:
    """Represents a chunk of a document."""

    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


@dataclass
class RetrievalResult:
    """Result from RAG retrieval."""

    text: str
    sources: List[DocumentChunk]
    score: Optional[float] = None
