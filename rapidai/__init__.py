"""RapidAI - The Python framework for lightning-fast AI prototypes."""

__version__ = "1.0.1"

from .app import App
from .llm import LLM, BaseLLM, AnthropicLLM, OpenAILLM, MockLLM
from .streaming import stream
from .cache import cache
from .memory import ConversationMemory
from .config import RapidAIConfig
from .types import Message, ConversationHistory, Document, DocumentChunk
from .exceptions import (
    RapidAIException,
    ConfigurationError,
    LLMError,
    LLMProviderError,
    LLMAuthenticationError,
    RouteError,
    CacheError,
    MemoryError,
)

# v1.0 Features
from .background import background, JobStatus, get_queue
from .monitoring import monitor, get_collector, get_dashboard_html, calculate_cost
from .prompts import PromptManager, prompt, get_prompt_manager

__all__ = [
    # Core
    "App",
    # LLM
    "LLM",
    "BaseLLM",
    "AnthropicLLM",
    "OpenAILLM",
    "MockLLM",
    # Decorators
    "stream",
    "cache",
    # Memory
    "ConversationMemory",
    # Config
    "RapidAIConfig",
    # Types
    "Message",
    "ConversationHistory",
    "Document",
    "DocumentChunk",
    # Exceptions
    "RapidAIException",
    "ConfigurationError",
    "LLMError",
    "LLMProviderError",
    "LLMAuthenticationError",
    "RouteError",
    "CacheError",
    "MemoryError",
    # Background Jobs
    "background",
    "JobStatus",
    "get_queue",
    # Monitoring
    "monitor",
    "get_collector",
    "get_dashboard_html",
    "calculate_cost",
    # Prompts
    "PromptManager",
    "prompt",
    "get_prompt_manager",
]
