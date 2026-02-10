# Simple Chatbot

Let's build your first AI chatbot with RapidAI!

## Goal

Create a basic chatbot that:

- ✅ Accepts messages via HTTP POST
- ✅ Responds using Claude or GPT
- ✅ Returns complete responses (non-streaming)

## Step 1: Create the File

Create `chatbot.py`:

```python title="chatbot.py" linenums="1"
from rapidai import App, LLM

# Initialize app and LLM
app = App()
llm = LLM("claude-3-haiku-20240307")

# Define chat endpoint
@app.route("/chat", methods=["POST"])
async def chat(message: str):
    """Process a chat message and return response."""
    response = await llm.chat(message)
    return {"response": response}

# Run the server
if __name__ == "__main__":
    app.run(port=8000)
```

!!! tip "Model Selection"
    You can use any supported model:

    - Anthropic: `claude-3-haiku-20240307`, `claude-3-sonnet-20240229`
    - OpenAI: `gpt-4o-mini`, `gpt-4o`, `gpt-4`

    RapidAI auto-detects the provider!

## Step 2: Run the Server

<div class="command">python chatbot.py</div>

You should see:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 3: Test Your Chatbot

### Using curl

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello! Can you introduce yourself?"}'
```

### Using Python

```python title="test_chatbot.py"
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={"message": "Hello! Can you introduce yourself?"}
)

print(response.json())
```

### Using httpie

```bash
http POST localhost:8000/chat message="Hello! Can you introduce yourself?"
```

## Step 4: Add Error Handling

Improve your chatbot with better error handling:

```python title="chatbot.py" hl_lines="14-20"
from rapidai import App, LLM

app = App()
llm = LLM("claude-3-haiku-20240307")

@app.route("/chat", methods=["POST"])
async def chat(message: str):
    """Process a chat message and return response."""
    # Validate input
    if not message or not message.strip():
        return {"error": "Message cannot be empty"}, 400

    try:
        response = await llm.chat(message)
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(port=8000)
```

## Step 5: Add Multiple Endpoints

Expand your chatbot with specialized endpoints:

```python title="chatbot.py"
from rapidai import App, LLM

app = App()
llm = LLM("claude-3-haiku-20240307")

@app.route("/chat", methods=["POST"])
async def chat(message: str):
    """General chat."""
    response = await llm.chat(message)
    return {"response": response}

@app.route("/joke", methods=["GET"])
async def joke():
    """Get a random joke."""
    response = await llm.chat("Tell me a short, funny joke.")
    return {"joke": response}

@app.route("/fact", methods=["GET"])
async def fact():
    """Get a random fact."""
    response = await llm.chat("Tell me an interesting fact.")
    return {"fact": response}

@app.route("/health", methods=["GET"])
async def health():
    """Health check."""
    return {"status": "healthy"}

if __name__ == "__main__":
    app.run(port=8000)
```

Test the new endpoints:

```bash
# Get a joke
curl http://localhost:8000/joke

# Get a fact
curl http://localhost:8000/fact

# Health check
curl http://localhost:8000/health
```

## Understanding the Code

### The App Object

```python
app = App()
```

Creates an ASGI application with:

- Automatic request parsing
- JSON response handling
- Error handling
- Middleware support

### The LLM Object

```python
llm = LLM("claude-3-haiku-20240307")
```

Creates a unified LLM client that:

- Auto-detects provider (Anthropic, OpenAI, etc.)
- Handles authentication
- Manages rate limits
- Provides consistent API

### Route Decorator

```python
@app.route("/chat", methods=["POST"])
async def chat(message: str):
    ...
```

- Registers endpoint at `/chat`
- Accepts POST requests
- Extracts `message` from JSON body
- Returns JSON response

### Async/Await

```python
response = await llm.chat(message)
```

All LLM calls are async for:

- Better performance
- Non-blocking I/O
- Concurrent requests

## Common Issues

### Port Already in Use

If port 8000 is taken:

```python
app.run(port=8001)  # Use different port
```

### API Key Not Found

Ensure `.env` file exists:

```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Import Errors

Install required dependencies:

```bash
pip install rapidai[anthropic]
```

## Next Steps

!!! success "Chatbot Complete!"
    You've built a working AI chatbot!

**Enhance Your Chatbot:**

- [Add Streaming](streaming.html) - Real-time responses
- [Add Memory](memory.html) - Remember conversations
- [Add Caching](caching.html) - Save money

**Or Explore:**

- [Multi-Provider Setup](multi-provider.html)
- [Error Handling](error-handling.html)
- [Testing](../advanced/testing.html)

---

<div style="text-align: center; padding: 2rem;">
  <a href="streaming.html" class="md-button md-button--primary">Next: Streaming Responses →</a>
</div>
