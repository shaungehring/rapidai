># RapidAI Quick Start Guide

Get started with RapidAI in under 5 minutes!

## Installation

### 1. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install RapidAI

For development (editable install):
```bash
pip install -e ".[dev,anthropic,openai]"
```

Or install from PyPI (when published):
```bash
pip install rapidai[anthropic,openai]
```

### 3. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```bash
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

## Your First App

### Create `app.py`:

```python
from rapidai import App, LLM, stream

app = App()
llm = LLM("claude-sonnet-4")

@app.route("/chat", methods=["POST"])
@stream
async def chat(message: str):
    async for chunk in llm.chat(message, stream=True):
        yield chunk

if __name__ == "__main__":
    app.run()
```

### Run the app:

```bash
python app.py
```

Your app is now running at `http://localhost:8000`!

### Test it:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello! Tell me a joke."}'
```

## Next Steps

### Add Conversation Memory

```python
@app.route("/chat", methods=["POST"])
@stream
async def chat(user_id: str, message: str):
    memory = app.memory(user_id)
    history = memory.to_dict_list()

    async for chunk in llm.chat(message, history=history, stream=True):
        yield chunk

    memory.add("user", message)
    memory.add("assistant", "[response]")  # Accumulate in production
```

### Add Caching

```python
from rapidai import cache

@app.route("/summarize", methods=["POST"])
@cache(ttl=3600)  # Cache for 1 hour
async def summarize(text: str):
    return await llm.complete(f"Summarize: {text}")
```

### Use Multiple Providers

```python
from rapidai import LLM

cheap_llm = LLM("gpt-4o-mini")
smart_llm = LLM("claude-opus-4")

@app.route("/quick", methods=["POST"])
async def quick(question: str):
    return await cheap_llm.chat(question)

@app.route("/deep", methods=["POST"])
async def deep(question: str):
    return await smart_llm.chat(question)
```

## Run Examples

Check out the examples directory:

```bash
# Simple chatbot
python examples/chatbot.py

# Stateful chatbot with memory
python examples/stateful_chatbot.py

# Multi-provider setup
python examples/multi_provider.py

# Cached responses
python examples/cached_responses.py
```

## Development

### Run tests:

```bash
pytest
```

### Type checking:

```bash
mypy rapidai
```

### Format code:

```bash
ruff format rapidai
```

### Lint:

```bash
ruff check rapidai
```

## Common Issues

### Import Error: anthropic/openai not found

Install the provider:
```bash
pip install anthropic  # or openai
```

### API Key Not Found

Make sure your `.env` file has the correct API key:
```bash
ANTHROPIC_API_KEY=sk-ant-...
# or
OPENAI_API_KEY=sk-...
```

### Port Already in Use

Change the port:
```python
app.run(port=8001)
```

## Documentation

- [API Examples](docs/API_EXAMPLES.md) - More code examples
- [Architecture](docs/ARCHITECTURE.md) - How RapidAI works
- [Roadmap](docs/ROADMAP.md) - Upcoming features
- [Contributing](docs/CONTRIBUTING.md) - How to contribute

## Need Help?

- 🐛 [Report bugs](https://github.com/shaungehring/rapidai/issues)
- 💡 [Request features](https://github.com/shaungehring/rapidai/discussions)
- 📖 [Read the docs](https://rapidai.dev) (coming soon)

---

Happy building! 🚀
