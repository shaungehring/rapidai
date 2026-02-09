"""Tests for LLM functionality."""

import pytest
from rapidai import MockLLM
from rapidai.config import LLMConfig
from rapidai.llm import _detect_provider


@pytest.mark.asyncio
async def test_mock_llm_chat():
    """Test MockLLM chat functionality."""
    llm = MockLLM(config=LLMConfig(model="mock"))
    llm.set_responses(["Hello, world!"])

    response = await llm.chat("Test message")
    assert response == "Hello, world!"


@pytest.mark.asyncio
async def test_mock_llm_streaming():
    """Test MockLLM streaming."""
    llm = MockLLM(config=LLMConfig(model="mock"))
    llm.set_responses(["Hello world"])

    chunks = []
    async for chunk in await llm.chat("Test", stream=True):
        chunks.append(chunk)

    assert len(chunks) > 0
    assert "".join(chunks).strip() == "Hello world"


@pytest.mark.asyncio
async def test_mock_llm_complete():
    """Test MockLLM completion."""
    llm = MockLLM(config=LLMConfig(model="mock"))
    llm.set_responses(["Completion response"])

    response = await llm.complete("Test prompt")
    assert response == "Completion response"


@pytest.mark.asyncio
async def test_mock_llm_embed():
    """Test MockLLM embeddings."""
    llm = MockLLM(config=LLMConfig(model="mock"))

    embedding = await llm.embed("Test text")
    assert isinstance(embedding, list)
    assert len(embedding) == 1536  # OpenAI embedding size


def test_provider_detection():
    """Test automatic provider detection."""
    assert _detect_provider("claude-sonnet-4") == "anthropic"
    assert _detect_provider("claude-opus-4") == "anthropic"
    assert _detect_provider("gpt-4") == "openai"
    assert _detect_provider("gpt-4o") == "openai"


def test_provider_detection_failure():
    """Test provider detection with unknown model."""
    with pytest.raises(Exception):
        _detect_provider("unknown-model-xyz")
