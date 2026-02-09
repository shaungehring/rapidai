"""Exception classes for RapidAI."""


class RapidAIException(Exception):
    """Base exception for all RapidAI errors."""

    pass


class ConfigurationError(RapidAIException):
    """Raised when there's a configuration issue."""

    pass


class LLMError(RapidAIException):
    """Base exception for LLM-related errors."""

    pass


class LLMProviderError(LLMError):
    """Raised when there's an error with an LLM provider."""

    pass


class LLMAuthenticationError(LLMError):
    """Raised when LLM authentication fails."""

    pass


class LLMRateLimitError(LLMError):
    """Raised when rate limit is exceeded."""

    pass


class LLMTimeoutError(LLMError):
    """Raised when LLM request times out."""

    pass


class RouteError(RapidAIException):
    """Raised when there's a routing error."""

    pass


class MiddlewareError(RapidAIException):
    """Raised when there's a middleware error."""

    pass


class CacheError(RapidAIException):
    """Raised when there's a caching error."""

    pass


class MemoryError(RapidAIException):
    """Raised when there's a memory system error."""

    pass


class RAGError(RapidAIException):
    """Base exception for RAG-related errors."""

    pass


class DocumentLoaderError(RAGError):
    """Raised when document loading fails."""

    pass


class EmbeddingError(RAGError):
    """Raised when embedding fails."""

    pass


class VectorDBError(RAGError):
    """Raised when vector database operation fails."""

    pass
