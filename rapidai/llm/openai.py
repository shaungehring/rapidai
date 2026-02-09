"""OpenAI LLM provider."""

import os
from typing import Any, AsyncIterator, Dict, List, Optional, Union

from ..exceptions import LLMAuthenticationError, LLMError, LLMProviderError
from .base import BaseLLM, LLMConfig


class OpenAILLM(BaseLLM):
    """OpenAI LLM provider."""

    def __init__(
        self,
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs: Any,
    ):
        """Initialize OpenAI LLM.

        Args:
            model: Model name (e.g., "gpt-4", "gpt-4o", "gpt-4o-mini")
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional configuration parameters
        """
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise LLMAuthenticationError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
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
            from openai import AsyncOpenAI

            self.client = AsyncOpenAI(api_key=api_key)
        except ImportError:
            raise LLMError("openai package not installed. Install with: pip install openai")

    async def chat(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Union[str, AsyncIterator[str]]:
        """Send a chat message to OpenAI.

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
                response = await self.client.chat.completions.create(
                    model=self.config.model,
                    messages=messages,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    **kwargs,
                )
                return response.choices[0].message.content or ""

        except Exception as e:
            raise LLMProviderError(f"OpenAI API error: {str(e)}")

    async def _stream_chat(
        self, messages: List[Dict[str, str]], **kwargs: Any
    ) -> AsyncIterator[str]:
        """Stream chat responses from OpenAI.

        Args:
            messages: Message history
            **kwargs: Additional parameters

        Yields:
            Response chunks
        """
        try:
            stream = await self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                stream=True,
                **kwargs,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise LLMProviderError(f"OpenAI streaming error: {str(e)}")

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
        return await self.chat(message=prompt, stream=stream, **kwargs)

    async def embed(self, text: str, model: str = "text-embedding-3-small", **kwargs: Any) -> List[float]:
        """Generate embeddings for text.

        Args:
            text: Text to embed
            model: Embedding model name
            **kwargs: Additional parameters

        Returns:
            List of embedding values
        """
        try:
            response = await self.client.embeddings.create(
                model=model, input=text, **kwargs
            )
            return response.data[0].embedding

        except Exception as e:
            raise LLMProviderError(f"OpenAI embedding error: {str(e)}")
