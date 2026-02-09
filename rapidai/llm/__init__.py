"""LLM providers for RapidAI."""

import os
from typing import Any, Optional, Union

from .base import BaseLLM, LLMConfig, MockLLM
from .anthropic import AnthropicLLM
from .openai import OpenAILLM
from ..exceptions import LLMError


def LLM(
    model: str,
    provider: Optional[str] = None,
    **kwargs: Any,
) -> BaseLLM:
    """Factory function to create LLM instances.

    This is the main entry point for creating LLM instances. It automatically
    detects the provider based on the model name or uses the specified provider.

    Args:
        model: Model name (e.g., "claude-sonnet-4", "gpt-4")
        provider: Provider name ("anthropic", "openai"). Auto-detected if not specified.
        **kwargs: Additional configuration parameters

    Returns:
        LLM instance

    Example:
        ```python
        # Auto-detect provider from model name
        llm = LLM("claude-sonnet-4")

        # Explicitly specify provider
        llm = LLM("gpt-4", provider="openai")

        # With custom parameters
        llm = LLM("claude-opus-4", temperature=0.9, max_tokens=8000)
        ```
    """
    # Auto-detect provider if not specified
    if provider is None:
        provider = _detect_provider(model)

    # Create provider instance
    if provider == "anthropic":
        return AnthropicLLM(model=model, **kwargs)
    elif provider == "openai":
        return OpenAILLM(model=model, **kwargs)
    elif provider == "mock":
        return MockLLM(config=LLMConfig(model=model, **kwargs))
    else:
        raise LLMError(f"Unknown provider: {provider}")


def _detect_provider(model: str) -> str:
    """Auto-detect provider from model name.

    Args:
        model: Model name

    Returns:
        Provider name

    Raises:
        LLMError: If provider cannot be detected
    """
    model_lower = model.lower()

    # Anthropic models
    if any(x in model_lower for x in ["claude", "sonnet", "opus", "haiku"]):
        return "anthropic"

    # OpenAI models
    if any(x in model_lower for x in ["gpt", "o1", "davinci", "curie"]):
        return "openai"

    # Check environment variable
    env_provider = os.getenv("RAPIDAI_LLM_PROVIDER")
    if env_provider:
        return env_provider

    raise LLMError(
        f"Could not detect provider for model '{model}'. "
        "Please specify provider explicitly or set RAPIDAI_LLM_PROVIDER environment variable."
    )


__all__ = [
    "BaseLLM",
    "LLMConfig",
    "MockLLM",
    "AnthropicLLM",
    "OpenAILLM",
    "LLM",
]
