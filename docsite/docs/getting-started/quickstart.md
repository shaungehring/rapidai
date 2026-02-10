# Quick Start

This guide covers the essential features of RapidAI in 10 minutes.

## Table of Contents

1. [Basic Chatbot](#basic-chatbot)
2. [Streaming Responses](#streaming-responses)
3. [Conversation Memory](#conversation-memory)
4. [Caching](#caching)
5. [Multiple LLM Providers](#multiple-llm-providers)

## Basic Chatbot

The simplest possible chatbot:

```python
from rapidai import App, LLM

app = App()
llm = LLM("claude-3-haiku-20240307")

@app.route("/chat", methods=["POST"])
async def chat(message: str):
    return await llm.chat(message)

if __name__ == "__main__":
    app.run()
```

!!! tip "Non-Streaming"
    Without `@stream`, responses are returned all at once.

## Streaming Responses

Add real-time streaming with one decorator:

```python hl_lines="1 6"
from rapidai import App, LLM, stream

app = App()
llm = LLM("claude-3-haiku-20240307")

@app.route("/chat", methods=["POST"])
@stream
async def chat(message: str):
    response = await llm.chat(message, stream=True)
    async for chunk in response:
        yield chunk

if __name__ == "__main__":
    app.run()
```

!!! success "Streaming Enabled"
    Responses now stream via Server-Sent Events (SSE)

Test with curl:

```bash
curl -N -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me a story"}'
```

## Conversation Memory

Add stateful conversations:

```python hl_lines="8 9 13 14"
from rapidai import App, LLM, stream

app = App()
llm = LLM("claude-3-haiku-20240307")

@app.route("/chat", methods=["POST"])
@stream
async def chat(user_id: str, message: str):
    # Get user's conversation memory
    memory = app.memory(user_id)
    history = memory.to_dict_list()

    # Chat with context
    response = await llm.chat(message, history=history, stream=True)
    async for chunk in response:
        yield chunk

    # Save to memory
    memory.add("user", message)
    memory.add("assistant", "[full response here]")

if __name__ == "__main__":
    app.run()
```

Test context awareness:

```bash
# First message
curl -X POST http://localhost:8000/chat \
  -d '{"user_id": "alice", "message": "My name is Alice"}'

# Second message - bot remembers!
curl -X POST http://localhost:8000/chat \
  -d '{"user_id": "alice", "message": "What is my name?"}'
```

!!! info "Memory Backends"
    Default is in-memory. Use Redis or PostgreSQL for production.

## Caching

Save money and time with automatic caching:

```python hl_lines="1 6"
from rapidai import App, LLM, cache

app = App()
llm = LLM("claude-3-haiku-20240307")

@app.route("/summarize", methods=["POST"])
@cache(ttl=3600)  # Cache for 1 hour
async def summarize(text: str):
    prompt = f"Summarize: {text}"
    return await llm.chat(prompt)

if __name__ == "__main__":
    app.run()
```

!!! success "Smart Caching"
    Identical requests return cached results instantly!

## Multiple LLM Providers

Use different models for different tasks:

```python
from rapidai import App, LLM

app = App()

# Different models for different purposes
fast_llm = LLM("claude-3-haiku-20240307")  # Fast & cheap
smart_llm = LLM("claude-3-sonnet-20240229")  # More capable

@app.route("/quick", methods=["POST"])
async def quick_answer(question: str):
    """Fast responses for simple questions."""
    return await fast_llm.chat(question)

@app.route("/deep", methods=["POST"])
async def deep_analysis(question: str):
    """Detailed analysis for complex questions."""
    return await smart_llm.chat(question)

if __name__ == "__main__":
    app.run()
```

### Switch Providers Easily

```python
# Anthropic Claude
llm = LLM("claude-3-haiku-20240307")

# OpenAI GPT
llm = LLM("gpt-4o-mini")

# Cohere
llm = LLM("command-r")

# Auto-detection works!
```

## Complete Example

Put it all together:

```python title="production_app.py"
from rapidai import App, LLM, stream, cache

app = App(title="AI Assistant", version="1.0.0")
llm = LLM("claude-3-haiku-20240307")

# Streaming chat with memory
@app.route("/chat", methods=["POST"])
@stream
async def chat(user_id: str, message: str):
    memory = app.memory(user_id)
    history = memory.to_dict_list()

    response = await llm.chat(message, history=history, stream=True)
    async for chunk in response:
        yield chunk

    memory.add("user", message)
    memory.add("assistant", "[response]")

# Cached summarization
@app.route("/summarize", methods=["POST"])
@cache(ttl=3600)
async def summarize(text: str):
    return await llm.chat(f"Summarize: {text}")

# Health check
@app.route("/health", methods=["GET"])
async def health():
    return {"status": "healthy"}

# Clear user memory
@app.route("/clear", methods=["POST"])
async def clear(user_id: str):
    memory = app.memory(user_id)
    memory.clear()
    return {"status": "cleared"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

## Configuration

Create `rapidai.yaml` for advanced configuration:

```yaml title="rapidai.yaml"
app:
  name: my-ai-app
  debug: false

llm:
  default_provider: anthropic
  default_model: claude-3-haiku-20240307
  temperature: 0.7
  max_tokens: 4000

cache:
  enabled: true
  backend: redis
  ttl: 3600
  redis_url: redis://localhost:6379

memory:
  backend: redis
  max_history: 10
```

## Next Steps

!!! tip "Ready for More?"
    You now know the core features of RapidAI!

**Continue Learning:**

- [Tutorial](../tutorial/intro.html) - Comprehensive walkthrough
- [Streaming Deep Dive](../tutorial/streaming.html)
- [Memory Management](../tutorial/memory.html)
- [Advanced Features](../advanced/configuration.html)

**Deploy:**

- [Docker Deployment](../deployment/docker.html)
- [Cloud Platforms](../deployment/cloud.html)
- [Production Best Practices](../deployment/best-practices.html)

---

<div style="text-align: center; padding: 2rem;">
  <a href="../tutorial/intro.html" class="md-button md-button--primary">Start Tutorial →</a>
</div>
