# Getting Started with RapidAI

## ✅ Installation Complete!

Your RapidAI installation is working correctly with Python 3.9.6.

## 🔑 API Key Setup

Your Anthropic API key is configured and working with **Claude 3 Haiku**.

**Note:** Your API key currently only has access to:
- ✅ `claude-3-haiku-20240307` (fastest, most cost-effective)

If you need access to more powerful models like Claude 3 Sonnet or Opus, you'll need to upgrade your Anthropic account.

## 🚀 Quick Start

### 1. Run the Simple Chatbot

```bash
python3 examples/chatbot.py
```

Then in another terminal:
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me a joke!"}'
```

You should see streaming output like:
```
event: message
data: Why don't scientists trust atoms?

event: message
data: Because they make up everything!
```

### 2. Run the Stateful Chatbot (with memory)

```bash
python3 examples/stateful_chatbot.py
```

Test it:
```bash
# First message - introduce yourself
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "alice", "message": "My name is Alice"}'

# Second message - bot remembers context
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "alice", "message": "What is my name?"}'
```

### 3. Test with Python Code

Create a simple script:

```python
# test_rapidai.py
import asyncio
from rapidai import App, LLM

async def test():
    llm = LLM("claude-3-haiku-20240307")
    response = await llm.chat("Say hello in 3 words")
    print(f"Response: {response}")

if __name__ == "__main__":
    asyncio.run(test())
```

Run it:
```bash
python3 test_rapidai.py
```

## 📋 What's Working

✅ Core App class with routing
✅ Anthropic Claude 3 Haiku integration
✅ Streaming responses (SSE)
✅ Conversation memory
✅ Caching system
✅ Configuration management (.env loading)
✅ Type-safe API
✅ Full test suite

## 🎯 Next Steps

### 1. Upgrade Your Anthropic Account (Optional)

To use more powerful models like Claude 3.5 Sonnet:
1. Visit https://console.anthropic.com/settings/billing
2. Add payment method
3. Then you can use:
   - `claude-3-5-sonnet-20241022` (most powerful)
   - `claude-3-opus-20240229` (very capable)
   - `claude-3-sonnet-20240229` (balanced)

### 2. Try the Other Examples

```bash
# Multi-provider example (needs OpenAI key)
python3 examples/multi_provider.py

# Caching example
python3 examples/cached_responses.py
```

### 3. Build Your Own App

```python
from rapidai import App, LLM, stream

app = App()
llm = LLM("claude-3-haiku-20240307")

@app.route("/custom", methods=["POST"])
@stream
async def my_endpoint(prompt: str):
    response = await llm.chat(f"You are a helpful assistant. {prompt}", stream=True)
    async for chunk in response:
        yield chunk

if __name__ == "__main__":
    app.run(port=8002)
```

## 🐛 Troubleshooting

### Port Already in Use

If you get "address already in use", either:
- Kill the existing process: `lsof -ti:8001 | xargs kill`
- Use a different port: `app.run(port=8002)`

### Model Not Found Error

Make sure you're using `claude-3-haiku-20240307` (the only model your API key has access to).

### Import Errors

Reinstall dependencies:
```bash
python3 -m pip install -e ".[dev,anthropic,openai]"
```

## 📚 Documentation

- [QUICKSTART.md](QUICKSTART.md) - Detailed quick start guide
- [docs/API_EXAMPLES.md](docs/API_EXAMPLES.md) - More code examples
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Technical architecture
- [docs/ROADMAP.md](docs/ROADMAP.md) - Future features

## 💡 Tips

1. **Streaming is automatic** - Just use the `@stream` decorator
2. **Memory is per-user** - Use `app.memory(user_id)` to track conversations
3. **Caching saves money** - Use `@cache(ttl=3600)` on expensive operations
4. **Type hints help** - Full IDE autocomplete support

---

**You're all set! Happy building with RapidAI! 🚀**

For help or issues: https://github.com/shaungehring/rapidai/issues
