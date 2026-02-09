"""Base LLM interface for RapidAI."""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional, Union
from dataclasses import dataclass


@dataclass
class LLMConfig:
    """Configuration for LLM providers."""

    model: str
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout: int = 30


class BaseLLM(ABC):
    """Base class for all LLM providers.

    This provides a unified interface for interacting with different
    LLM providers (OpenAI, Anthropic, Cohere, etc.).
    """

    def __init__(self, config: LLMConfig):
        """Initialize the LLM provider.

        Args:
            config: LLM configuration
        """
        self.config = config

    @abstractmethod
    async def chat(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Union[str, AsyncIterator[str]]:
        """Send a chat message and get a response.

        Args:
            message: User message
            history: Optional conversation history
            stream: Whether to stream the response
            **kwargs: Additional provider-specific parameters

        Returns:
            Response string or async iterator of chunks if streaming
        """
        pass

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        stream: bool = False,
        **kwargs: Any,
    ) -> Union[str, AsyncIterator[str]]:
        """Generate a completion for a prompt.

        Args:
            prompt: The prompt to complete
            stream: Whether to stream the response
            **kwargs: Additional provider-specific parameters

        Returns:
            Completion string or async iterator of chunks if streaming
        """
        pass

    @abstractmethod
    async def embed(self, text: str, **kwargs: Any) -> List[float]:
        """Generate embeddings for text.

        Args:
            text: Text to embed
            **kwargs: Additional provider-specific parameters

        Returns:
            List of embedding values
        """
        pass


class MockLLM(BaseLLM):
    """Mock LLM for testing purposes."""

    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize mock LLM.

        Args:
            config: LLM configuration (optional)
        """
        super().__init__(config or LLMConfig(model="mock"))
        self.responses: List[str] = []
        self.call_count = 0

    def set_responses(self, responses: List[str]) -> None:
        """Set mock responses.

        Args:
            responses: List of responses to return
        """
        self.responses = responses
        self.call_count = 0

    async def chat(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Union[str, AsyncIterator[str]]:
        """Return mock chat response."""
        if stream:
            return self._stream_response(self._get_response())
        return self._get_response()

    async def complete(
        self,
        prompt: str,
        stream: bool = False,
        **kwargs: Any,
    ) -> Union[str, AsyncIterator[str]]:
        """Return mock completion."""
        if stream:
            return self._stream_response(self._get_response())
        return self._get_response()

    async def embed(self, text: str, **kwargs: Any) -> List[float]:
        """Return mock embeddings."""
        return [0.1] * 1536  # OpenAI embedding size

    def _get_response(self) -> str:
        """Get next mock response."""
        if not self.responses:
            return "Mock response"

        response = self.responses[self.call_count % len(self.responses)]
        self.call_count += 1
        return response

    async def _stream_response(self, text: str) -> AsyncIterator[str]:
        """Stream a mock response."""
        words = text.split()
        for word in words:
            yield word + " "
