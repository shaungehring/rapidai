# Caching

RapidAI provides built-in caching to reduce API calls, improve response times, and lower costs. Supports both standard caching and semantic caching for intelligent similarity matching.

## Quick Start

```python
from rapidai import App, LLM
from rapidai.cache import cache

app = App()
llm = LLM("claude-3-haiku-20240307")

@app.route("/chat", methods=["POST"])
@cache(ttl=3600)  # Cache for 1 hour
async def chat(message: str):
    response = await llm.complete(message)
    return {"response": response}
```

## Features

- **Automatic Caching** - Decorator-based caching
- **Multiple Backends** - In-memory or Redis
- **TTL Support** - Time-to-live configuration
- **Semantic Caching** - AI-powered similarity matching
- **Cache Keys** - Automatic key generation
- **Manual Control** - Direct cache access

## Cache Decorator

### Basic Usage

```python
from rapidai.cache import cache

@app.route("/expensive", methods=["POST"])
@cache(ttl=3600)
async def expensive_operation(data: str):
    # Expensive computation
    result = await process(data)
    return {"result": result}
```

**How it works:**

1. Request arrives with parameters
2. Cache key generated from function name + parameters
3. Check cache for existing result
4. If hit: return cached result
5. If miss: execute function, cache result, return

### With TTL

```python
from rapidai.cache import cache

# Cache for 1 hour
@cache(ttl=3600)
async def short_lived(data: str):
    return await process(data)

# Cache for 1 day
@cache(ttl=86400)
async def long_lived(data: str):
    return await process(data)

# Cache forever (until manual clear)
@cache(ttl=None)
async def permanent(data: str):
    return await process(data)
```

### With Redis Backend

```python
from rapidai.cache import cache, RedisCache

# Use Redis for persistence
redis_cache = RedisCache(url="redis://localhost:6379")

@cache(ttl=7200, backend=redis_cache)
async def persistent_cache(data: str):
    return await process(data)
```

## Semantic Caching

Semantic caching uses embeddings to find similar queries instead of exact matches.

### Basic Semantic Cache

```python
from rapidai.cache import cache

@app.route("/chat", methods=["POST"])
@cache(ttl=3600, semantic=True, threshold=0.85)
async def chat(message: str):
    response = await llm.complete(message)
    return {"response": response}
```

**Example:**

```python
# First request
response1 = await chat(message="What is Python?")
# Cache miss, calls LLM

# Similar request
response2 = await chat(message="Can you explain Python?")
# Cache hit! Returns cached response (similarity > 0.85)

# Different request
response3 = await chat(message="What is JavaScript?")
# Cache miss, different topic
```

### Similarity Threshold

Control how similar queries need to be:

```python
# Strict matching (default)
@cache(semantic=True, threshold=0.85)
async def strict(query: str):
    return await llm.complete(query)

# Loose matching
@cache(semantic=True, threshold=0.70)
async def loose(query: str):
    return await llm.complete(query)

# Very strict matching
@cache(semantic=True, threshold=0.95)
async def very_strict(query: str):
    return await llm.complete(query)
```

**Threshold guide:**

- `0.95+` - Nearly identical queries
- `0.85-0.94` - Similar questions (recommended)
- `0.70-0.84` - Related topics
- `<0.70` - Too loose, may return unrelated results

### Custom Embedding Model

```python
from rapidai.cache import SemanticCache

# Use custom model
semantic_cache = SemanticCache(
    model="all-mpnet-base-v2",  # Better accuracy
    threshold=0.85
)

@cache(backend=semantic_cache, ttl=3600)
async def chat(message: str):
    return await llm.complete(message)
```

## Cache Backends

### In-Memory Cache

Default backend, fast but not persistent:

```python
from rapidai.cache import InMemoryCache

cache_backend = InMemoryCache()

@cache(backend=cache_backend, ttl=3600)
async def my_function(data: str):
    return await process(data)
```

**Pros:**
- Very fast
- No external dependencies
- Simple setup

**Cons:**
- Lost on restart
- Single-server only
- Limited by RAM

### Redis Cache

Production backend with persistence:

```python
from rapidai.cache import RedisCache

cache_backend = RedisCache(
    url="redis://localhost:6379",
    prefix="myapp:cache:"
)

@cache(backend=cache_backend, ttl=7200)
async def my_function(data: str):
    return await process(data)
```

**Pros:**
- Persistent storage
- Survives restarts
- Multi-server support
- Production-ready

**Cons:**
- Requires Redis
- Slightly slower than in-memory

## Manual Cache Control

### Direct Cache Access

```python
from rapidai.cache import get_cache

cache = get_cache()

# Set value
await cache.set("key", {"data": "value"}, ttl=3600)

# Get value
result = await cache.get("key")

# Delete value
await cache.delete("key")

# Clear all
await cache.clear()
```

### With Custom Keys

```python
from rapidai.cache import get_cache

cache = get_cache()

@app.route("/user/<user_id>", methods=["GET"])
async def get_user(user_id: str):
    # Try cache first
    cache_key = f"user:{user_id}"
    cached = await cache.get(cache_key)

    if cached:
        return cached

    # Fetch from database
    user = await db.get_user(user_id)

    # Cache for 1 hour
    await cache.set(cache_key, user, ttl=3600)

    return user
```

## Cache Key Generation

### Automatic Keys

The decorator generates keys from function name and arguments:

```python
@cache(ttl=3600)
async def get_weather(city: str, units: str = "metric"):
    return await fetch_weather(city, units)

# Calls with same arguments use same cache
result1 = await get_weather("NYC", "metric")
# Key: get_weather:NYC:metric

result2 = await get_weather("NYC", "metric")
# Same key, cache hit!

result3 = await get_weather("NYC", "imperial")
# Different key: get_weather:NYC:imperial
```

### Custom Keys

```python
from rapidai.cache import cache

@cache(ttl=3600, key=lambda city, units: f"weather:{city}")
async def get_weather(city: str, units: str = "metric"):
    return await fetch_weather(city, units)

# Both use same cache key (units ignored)
result1 = await get_weather("NYC", "metric")
result2 = await get_weather("NYC", "imperial")
# Both hit same cache!
```

## Complete Examples

### Cached Chat Application

```python
from rapidai import App, LLM
from rapidai.cache import cache
from rapidai.memory import ConversationMemory

app = App()
llm = LLM("claude-3-haiku-20240307")
memory = ConversationMemory()

@app.route("/chat", methods=["POST"])
@cache(ttl=3600, semantic=True, threshold=0.85)
async def chat(message: str):
    """Chat with semantic caching."""
    response = await llm.complete(message)
    return {"response": response, "cached": False}

@app.route("/chat/user", methods=["POST"])
async def chat_with_memory(user_id: str, message: str):
    """Chat with memory (no caching - each conversation unique)."""
    memory.add_message(user_id, "user", message)
    history = memory.get_history(user_id)

    response = await llm.chat(history)

    memory.add_message(user_id, "assistant", response)

    return {"response": response}

if __name__ == "__main__":
    app.run()
```

### Cached RAG System

```python
from rapidai import App, LLM
from rapidai.rag import RAG
from rapidai.cache import cache

app = App()
llm = LLM("claude-3-haiku-20240307")
rag = RAG()

@app.on_startup
async def load_docs():
    await rag.add_document("docs/manual.pdf")
    await rag.add_document("docs/faq.txt")

@cache(ttl=7200, semantic=True, threshold=0.85)
async def cached_retrieval(query: str):
    """Cache RAG retrievals - similar questions use cached context."""
    return await rag.retrieve(query, top_k=3)

@app.route("/ask", methods=["POST"])
async def ask(question: str):
    # Use cached retrieval
    retrieval = await cached_retrieval(question)

    # Build prompt
    prompt = f"""Context:
{retrieval.text}

Question: {question}

Answer:"""

    # Generate response
    response = await llm.complete(prompt)

    return {
        "response": response,
        "sources": [s["source"] for s in retrieval.sources]
    }
```

### Multi-Tier Caching

```python
from rapidai import App, LLM
from rapidai.cache import cache, InMemoryCache, RedisCache

app = App()
llm = LLM("claude-3-haiku-20240307")

# Fast in-memory cache for common queries
memory_cache = InMemoryCache()

# Persistent Redis cache for all queries
redis_cache = RedisCache(url="redis://localhost:6379")

@app.route("/chat/fast", methods=["POST"])
@cache(backend=memory_cache, ttl=300)  # 5 min memory cache
async def fast_chat(message: str):
    """Frequent queries cached in memory."""
    return {"response": await llm.complete(message)}

@app.route("/chat/persistent", methods=["POST"])
@cache(backend=redis_cache, ttl=86400)  # 1 day Redis cache
async def persistent_chat(message: str):
    """All queries cached in Redis."""
    return {"response": await llm.complete(message)}

@app.route("/chat/semantic", methods=["POST"])
@cache(semantic=True, threshold=0.85, ttl=3600)
async def semantic_chat(message: str):
    """Similar queries share cache."""
    return {"response": await llm.complete(message)}
```

## Best Practices

### 1. Choose Appropriate TTL

```python
# Short TTL for changing data
@cache(ttl=300)  # 5 minutes
async def get_stock_price(symbol: str):
    return await fetch_price(symbol)

# Long TTL for static data
@cache(ttl=86400)  # 1 day
async def get_company_info(symbol: str):
    return await fetch_info(symbol)

# No TTL for permanent data
@cache(ttl=None)
async def get_currency_codes():
    return ["USD", "EUR", "GBP"]
```

### 2. Use Semantic Caching for LLM Calls

```python
# ✅ Good - semantic caching for similar questions
@cache(semantic=True, threshold=0.85, ttl=3600)
async def chat(message: str):
    return await llm.complete(message)

# ❌ Avoid - exact matching misses similar queries
@cache(ttl=3600)  # Only caches identical messages
async def chat(message: str):
    return await llm.complete(message)
```

### 3. Use Redis in Production

```python
import os

# Development: in-memory
# Production: Redis
backend = "redis" if os.getenv("PRODUCTION") else "memory"

from rapidai.cache import get_cache

cache_backend = get_cache(backend=backend)
```

### 4. Cache Expensive Operations Only

```python
# ✅ Good - cache LLM calls
@cache(ttl=3600)
async def generate_summary(text: str):
    return await llm.complete(f"Summarize: {text}")

# ❌ Avoid - don't cache trivial operations
@cache(ttl=3600)
async def add_numbers(a: int, b: int):
    return {"result": a + b}  # Too fast to benefit
```

### 5. Monitor Cache Hit Rates

```python
from rapidai.cache import get_cache
from rapidai.monitoring import get_collector

@app.route("/stats")
async def cache_stats():
    cache = get_cache()
    collector = get_collector()

    # Track cache metrics
    collector.record_metric("cache.size", len(cache._cache))

    return {
        "cache_size": len(cache._cache),
        "metrics": collector.get_summary()
    }
```

## Troubleshooting

### Cache Not Working

```python
# Ensure decorator is applied correctly
@cache(ttl=3600)  # ✅ Correct
async def my_function():
    pass

async def my_function():  # ❌ Missing decorator
    pass
```

### Semantic Cache Misses

```python
# Threshold may be too high
@cache(semantic=True, threshold=0.95)  # Too strict
async def chat(message: str):
    pass

# Try lower threshold
@cache(semantic=True, threshold=0.80)  # More permissive
async def chat(message: str):
    pass
```

### Redis Connection Issues

```python
from rapidai.cache import RedisCache

try:
    cache = RedisCache(url="redis://localhost:6379")
except Exception as e:
    print(f"Redis connection failed: {e}")
    # Fall back to in-memory
    from rapidai.cache import InMemoryCache
    cache = InMemoryCache()
```

## Next Steps

- [Performance Guide](performance.html) - Optimize with caching
- [Monitoring](monitoring.html) - Track cache performance
- [Testing](testing.html) - Test cached endpoints
