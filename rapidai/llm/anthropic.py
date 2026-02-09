"""Anthropic (Claude) LLM provider."""

import os
from typing import Any, AsyncIterator, Dict, List, Optional, Union

from ..exceptions import LLMAuthenticationError, LLMError, LLMProviderError
from .base import BaseLLM, LLMConfig


class AnthropicLLM(BaseLLM):
    """Anthropic (Claude) LLM provider."""

    def __init__(
        self,
        model: str = "claude-sonnet-4",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs: Any,
    ):
        """Initialize Anthropic LLM.

        Args:
            model: Model name (e.g., "claude-sonnet-4", "claude-opus-4")
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional configuration parameters
        """
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise LLMAuthenticationError(
                "Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )

        config = LLMConfig(
            model=model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        super().__init__(config)

        try:
            from anthropic import AsyncAnthropic

            self.client = AsyncAnthropic(api_key=api_key)
        except ImportError:
            raise LLMError(
                "anthropic package not installed. Install with: pip install anthropic"
            )

    async def chat(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Union[str, AsyncIterator[str]]:
        """Send a chat message to Claude.

        Args:
            message: User message
            history: Optional conversation history
            stream: Whether to stream the response
            **kwargs: Additional parameters

        Returns:
            Response string or async iterator if streaming
        """
        messages = history or []
        messages = messages + [{"role": "user", "content": message}]

        try:
            if stream:
                return self._stream_chat(messages, **kwargs)
            else:
                response = await self.client.messages.create(
                    model=self.config.model,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    messages=messages,
                    **kwargs,
                )
                return response.content[0].text

        except Exception as e:
            raise LLMProviderError(f"Anthropic API error: {str(e)}")

    async def _stream_chat(
        self, messages: List[Dict[str, str]], **kwargs: Any
    ) -> AsyncIterator[str]:
        """Stream chat responses from Claude.

        Args:
            messages: Message history
            **kwargs: Additional parameters

        Yields:
            Response chunks
        """
        try:
            async with self.client.messages.stream(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=messages,
                **kwargs,
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            raise LLMProviderError(f"Anthropic streaming error: {str(e)}")

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
            **kwargs: Additional parameters

        Returns:
            Completion string or async iterator if streaming
        """
        # Claude uses chat format, so we convert the prompt to a message
        return await self.chat(message=prompt, stream=stream, **kwargs)

    async def embed(self, text: str, **kwargs: Any) -> List[float]:
        """Generate embeddings.

        Note: Anthropic doesn't provide embeddings. This raises an error.

        Args:
            text: Text to embed
            **kwargs: Additional parameters

        Raises:
            LLMError: Anthropic doesn't support embeddings
        """
        raise LLMError(
            "Anthropic doesn't provide embeddings. Use OpenAI or a dedicated embedding model."
        )
