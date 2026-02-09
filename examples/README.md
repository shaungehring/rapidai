# RapidAI Examples

This directory contains example applications demonstrating various features of RapidAI.

## Prerequisites

Before running any examples, make sure you have:

1. Installed RapidAI with dependencies:
   ```bash
   pip install -e ".[anthropic,openai]"
   ```

2. Set up your API keys in `.env`:
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

## Examples

### 1. Simple Chatbot ([chatbot.py](chatbot.py))

The most basic example - a streaming chatbot endpoint.

**Features:**
- Single streaming endpoint
- No conversation history
- Health check endpoint

**Run:**
```bash
python examples/chatbot.py
```

**Test:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

---

### 2. Stateful Chatbot ([stateful_chatbot.py](stateful_chatbot.py))

Chatbot with conversation memory that maintains context across requests.

**Features:**
- Conversation history per user
- Context-aware responses
- Clear history endpoint

**Run:**
```bash
python examples/stateful_chatbot.py
```

**Test:**
```bash
# First message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "alice", "message": "My name is Alice"}'

# Second message - bot remembers context
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "alice", "message": "What is my name?"}'

# Clear history
curl -X POST http://localhost:8000/clear \
  -H "Content-Type: application/json" \
  -d '{"user_id": "alice"}'
```

---

### 3. Multi-Provider ([multi_provider.py](multi_provider.py))

Demonstrates using multiple LLM providers for different tasks.

**Features:**
- Cost optimization (cheap vs expensive models)
- Side-by-side comparison
- Multiple providers in one app

**Run:**
```bash
python examples/multi_provider.py
```

**Test:**
```bash
# Quick answer with GPT-4o-mini
curl -X POST http://localhost:8000/quick-answer \
  -H "Content-Type: application/json" \
  -d '{"question": "What is 2+2?"}'

# Deep analysis with Claude Opus
curl -X POST http://localhost:8000/deep-analysis \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain quantum computing in simple terms"}'

# Compare both models
curl -X POST http://localhost:8000/compare \
  -H "Content-Type: application/json" \
  -d '{"question": "What is artificial intelligence?"}'
```

---

### 4. Cached Responses ([cached_responses.py](cached_responses.py))

Shows how caching can dramatically reduce LLM API costs.

**Features:**
- Automatic response caching
- TTL configuration
- Cost savings on repeated queries

**Run:**
```bash
python examples/cached_responses.py
```

**Test:**
```bash
# First request - calls LLM
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "Artificial intelligence is transforming the world..."}'

# Second identical request - returns cached result (much faster!)
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "Artificial intelligence is transforming the world..."}'
```

---

## Tips

### Debugging

Enable debug mode in your `.env`:
```bash
RAPIDAI_DEBUG=true
```

### Custom Configuration

Create a `rapidai.yaml` for advanced configuration:
```yaml
app:
  name: my-ai-app
  port: 8000
  debug: true

llm:
  default_provider: anthropic
  default_model: claude-sonnet-4
  temperature: 0.7
  max_tokens: 4000

cache:
  enabled: true
  backend: memory
  ttl: 3600
```

### Testing with httpie

For better formatted output, use [httpie](https://httpie.io/):

```bash
pip install httpie

http POST localhost:8000/chat message="Hello!"
```

## Next Steps

- Read the [main README](../README.md) for more features
- Check the [API documentation](../docs/API_EXAMPLES.md)
- Explore [architecture details](../docs/ARCHITECTURE.md)
- See the [roadmap](../docs/ROADMAP.md) for upcoming features
