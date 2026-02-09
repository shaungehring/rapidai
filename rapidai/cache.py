"""Caching system for RapidAI."""

import hashlib
import json
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
from functools import wraps

from .exceptions import CacheError


class CacheBackend:
    """Base class for cache backends."""

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        raise NotImplementedError

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set value in cache with TTL."""
        raise NotImplementedError

    def delete(self, key: str) -> None:
        """Delete value from cache."""
        raise NotImplementedError

    def clear(self) -> None:
        """Clear all cache entries."""
        raise NotImplementedError


class InMemoryCache(CacheBackend):
    """In-memory cache backend."""

    def __init__(self) -> None:
        self._cache: Dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key in self._cache:
            value, expiry = self._cache[key]
            if time.time() < expiry:
                return value
            else:
                del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set value in cache with TTL."""
        expiry = time.time() + ttl
        self._cache[key] = (value, expiry)

    def delete(self, key: str) -> None:
        """Delete value from cache."""
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()


class RedisCache(CacheBackend):
    """Redis cache backend."""

    def __init__(self, url: str = "redis://localhost:6379", prefix: str = "rapidai:"):
        """Initialize Redis cache.

        Args:
            url: Redis connection URL
            prefix: Key prefix for namespacing
        """
        try:
            import redis
        except ImportError:
            raise CacheError(
                "redis not installed. Install with: pip install redis"
            )

        self.prefix = prefix
        self.client = redis.from_url(url, decode_responses=False)

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = self.client.get(self.prefix + key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            raise CacheError(f"Redis get error: {str(e)}")

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set value in cache with TTL."""
        try:
            serialized = json.dumps(value)
            self.client.setex(self.prefix + key, ttl, serialized)
        except Exception as e:
            raise CacheError(f"Redis set error: {str(e)}")

    def delete(self, key: str) -> None:
        """Delete value from cache."""
        try:
            self.client.delete(self.prefix + key)
        except Exception as e:
            raise CacheError(f"Redis delete error: {str(e)}")

    def clear(self) -> None:
        """Clear all cache entries with prefix."""
        try:
            # Delete all keys with the prefix
            keys = self.client.keys(self.prefix + "*")
            if keys:
                self.client.delete(*keys)
        except Exception as e:
            raise CacheError(f"Redis clear error: {str(e)}")


class SemanticCache(CacheBackend):
    """Semantic cache using embeddings for similarity matching."""

    def __init__(self, threshold: float = 0.85, embedding_model: str = "all-MiniLM-L6-v2") -> None:
        """Initialize semantic cache.

        Args:
            threshold: Similarity threshold (0.0 to 1.0)
            embedding_model: Sentence transformer model name
        """
        self.threshold = threshold
        self._cache: Dict[str, Tuple[Any, float, List[float]]] = {}  # key: (value, expiry, embedding)

        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise CacheError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )

        self.model = SentenceTransformer(embedding_model)

    def _cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score (0.0 to 1.0)
        """
        import numpy as np

        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    def _embed(self, text: str) -> List[float]:
        """Generate embedding for text.

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        embedding = self.model.encode(text)
        return embedding.tolist()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache using semantic similarity.

        Args:
            key: Search query (will be embedded and compared)

        Returns:
            Cached value if similar match found, None otherwise
        """
        # Generate embedding for query
        query_embedding = self._embed(key)

        # Find most similar cached item
        best_match = None
        best_similarity = 0.0

        current_time = time.time()

        for cache_key, (value, expiry, embedding) in list(self._cache.items()):
            # Skip expired entries
            if current_time >= expiry:
                del self._cache[cache_key]
                continue

            # Calculate similarity
            similarity = self._cosine_similarity(query_embedding, embedding)

            if similarity > best_similarity and similarity >= self.threshold:
                best_similarity = similarity
                best_match = value

        return best_match

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set value in cache with embedding.

        Args:
            key: Cache key (will be embedded)
            value: Value to cache
            ttl: Time-to-live in seconds
        """
        expiry = time.time() + ttl
        embedding = self._embed(key)
        self._cache[key] = (value, expiry, embedding)

    def delete(self, key: str) -> None:
        """Delete value from cache.

        Args:
            key: Cache key
        """
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()


class CacheManager:
    """Manages caching for the application."""

    def __init__(self, backend: str = "memory", ttl: int = 3600):
        """Initialize cache manager.

        Args:
            backend: Cache backend ("memory", "redis")
            ttl: Default time-to-live in seconds
        """
        self.ttl = ttl
        self.backend = self._create_backend(backend)

    def _create_backend(self, backend: str) -> CacheBackend:
        """Create cache backend instance."""
        if backend == "memory":
            return InMemoryCache()
        elif backend == "redis":
            from .config import RapidAIConfig
            config = RapidAIConfig.load()
            redis_url = config.cache.redis_url or "redis://localhost:6379"
            return RedisCache(url=redis_url)
        else:
            raise CacheError(f"Unknown backend: {backend}")

    def _make_key(self, *args: Any, **kwargs: Any) -> str:
        """Generate cache key from function arguments."""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        return self.backend.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        self.backend.set(key, value, ttl or self.ttl)

    def delete(self, key: str) -> None:
        """Delete value from cache."""
        self.backend.delete(key)

    def clear(self) -> None:
        """Clear all cache entries."""
        self.backend.clear()


def cache(
    ttl: int = 3600,
    semantic: bool = False,
    threshold: float = 0.85,
    embedding_model: str = "all-MiniLM-L6-v2",
) -> Callable:
    """Decorator to cache function results.

    Args:
        ttl: Time-to-live in seconds
        semantic: Use semantic similarity for cache lookup
        threshold: Similarity threshold for semantic caching (0.0 to 1.0)
        embedding_model: Sentence transformer model for embeddings

    Returns:
        Decorator function

    Example:
        ```python
        @cache(ttl=3600)
        async def expensive_operation(param: str):
            return await llm.complete(param)

        # Semantic caching
        @cache(ttl=3600, semantic=True, threshold=0.9)
        async def ask_llm(question: str):
            return await llm.complete(question)
        ```
    """
    # Create appropriate backend
    if semantic:
        backend = SemanticCache(threshold=threshold, embedding_model=embedding_model)
    else:
        cache_manager = CacheManager(ttl=ttl)
        backend = cache_manager.backend

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # For semantic caching, use first string argument as key
            if semantic:
                # Find first string argument to use as semantic key
                cache_key = None
                for arg in args:
                    if isinstance(arg, str):
                        cache_key = arg
                        break
                if cache_key is None:
                    for value in kwargs.values():
                        if isinstance(value, str):
                            cache_key = value
                            break

                if cache_key is None:
                    # No string argument, fall back to regular caching
                    cache_manager = CacheManager(ttl=ttl)
                    cache_key = cache_manager._make_key(func.__name__, *args, **kwargs)
                    cached_value = cache_manager.get(cache_key)
                else:
                    # Use semantic cache
                    cached_value = backend.get(cache_key)

                if cached_value is not None:
                    return cached_value

                # Call function
                result = await func(*args, **kwargs)

                # Cache result
                backend.set(cache_key, result, ttl)

                return result
            else:
                # Regular caching
                cache_manager = CacheManager(ttl=ttl)
                cache_key = cache_manager._make_key(func.__name__, *args, **kwargs)

                # Check cache
                cached_value = cache_manager.get(cache_key)
                if cached_value is not None:
                    return cached_value

                # Call function
                result = await func(*args, **kwargs)

                # Cache result
                cache_manager.set(cache_key, result, ttl)

                return result

        return wrapper

    return decorator
