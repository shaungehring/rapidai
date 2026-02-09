"""Tests for caching system."""

import pytest
import asyncio
from rapidai.cache import InMemoryCache, CacheManager, cache


def test_in_memory_cache():
    """Test in-memory cache backend."""
    cache_backend = InMemoryCache()

    # Test set and get
    cache_backend.set("key1", "value1", ttl=60)
    assert cache_backend.get("key1") == "value1"

    # Test non-existent key
    assert cache_backend.get("nonexistent") is None

    # Test delete
    cache_backend.delete("key1")
    assert cache_backend.get("key1") is None


def test_cache_expiry():
    """Test cache TTL expiry."""
    import time

    cache_backend = InMemoryCache()

    # Set with very short TTL
    cache_backend.set("key1", "value1", ttl=1)
    assert cache_backend.get("key1") == "value1"

    # Wait for expiry
    time.sleep(1.1)
    assert cache_backend.get("key1") is None


def test_cache_clear():
    """Test clearing cache."""
    cache_backend = InMemoryCache()

    cache_backend.set("key1", "value1")
    cache_backend.set("key2", "value2")

    assert cache_backend.get("key1") is not None
    assert cache_backend.get("key2") is not None

    cache_backend.clear()

    assert cache_backend.get("key1") is None
    assert cache_backend.get("key2") is None


@pytest.mark.asyncio
async def test_cache_decorator():
    """Test cache decorator."""
    call_count = 0

    @cache(ttl=60)
    async def expensive_function(x: int):
        nonlocal call_count
        call_count += 1
        return x * 2

    # First call
    result1 = await expensive_function(5)
    assert result1 == 10
    assert call_count == 1

    # Second call with same argument - should use cache
    result2 = await expensive_function(5)
    assert result2 == 10
    assert call_count == 1  # Should not increment

    # Call with different argument - should call function
    result3 = await expensive_function(10)
    assert result3 == 20
    assert call_count == 2


@pytest.mark.asyncio
async def test_cache_decorator_different_args():
    """Test cache with different arguments."""
    call_count = 0

    @cache(ttl=60)
    async def add(a: int, b: int):
        nonlocal call_count
        call_count += 1
        return a + b

    await add(1, 2)
    await add(1, 2)  # Same args - cached
    await add(2, 3)  # Different args - not cached

    assert call_count == 2
