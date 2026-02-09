"""Tests for streaming functionality."""

import pytest
from rapidai.streaming import stream, is_stream_handler


@pytest.mark.asyncio
async def test_stream_decorator():
    """Test stream decorator."""

    @stream
    async def test_handler():
        yield "chunk1"
        yield "chunk2"
        yield "chunk3"

    # Check that decorator marks function
    assert is_stream_handler(test_handler)

    # Check that streaming works
    chunks = []
    async for chunk in test_handler():
        chunks.append(chunk)

    assert chunks == ["chunk1", "chunk2", "chunk3"]


@pytest.mark.asyncio
async def test_stream_with_params():
    """Test streaming with parameters."""

    @stream
    async def test_handler(message: str):
        words = message.split()
        for word in words:
            yield word

    chunks = []
    async for chunk in test_handler("hello world test"):
        chunks.append(chunk)

    assert chunks == ["hello", "world", "test"]


def test_is_stream_handler():
    """Test stream handler detection."""

    @stream
    async def stream_handler():
        yield "test"

    async def normal_handler():
        return "test"

    assert is_stream_handler(stream_handler) is True
    assert is_stream_handler(normal_handler) is False
