# First Steps

Let's create your first RapidAI application in under 5 minutes! ⚡

## Create Your First App

Create a file called `app.py`:

```python title="app.py" linenums="1"
from rapidai import App, LLM, stream

# Create the app
app = App()

# Initialize LLM
llm = LLM("claude-3-haiku-20240307")

# Define a streaming chat endpoint
@app.route("/chat", methods=["POST"])
@stream
async def chat(message: str):
    """Stream a chat response."""
    response = await llm.chat(message, stream=True)
    async for chunk in response:
        yield chunk

# Run the server
if __name__ == "__main__":
    app.run(port=8000)
```

## Run Your App

<div class="command">python app.py</div>

You should see:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

!!! success "Server Running!"
    Your AI-powered API is now live at `http://localhost:8000`

## Test Your App

Open a new terminal and test your endpoint:

```bash title="Test with curl"
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello! Tell me a joke."}'
```

You'll see streaming output:

```
event: message
data: Why don't scientists trust atoms?

event: message
data: Because they make up everything!
```

## Understanding the Code

Let's break down what's happening:

### 1. Import Components

```python
from rapidai import App, LLM, stream
```

- `App` - The main application class
- `LLM` - Unified LLM interface
- `stream` - Decorator for streaming responses

### 2. Create App and LLM

```python
app = App()
llm = LLM("claude-3-haiku-20240307")
```

- `App()` creates your ASGI application
- `LLM()` auto-detects provider from model name

### 3. Define Routes

```python
@app.route("/chat", methods=["POST"])
@stream
async def chat(message: str):
    response = await llm.chat(message, stream=True)
    async for chunk in response:
        yield chunk
```

- `@app.route()` registers an endpoint
- `@stream` enables Server-Sent Events
- `async def` makes it asynchronous
- Parameters auto-extracted from request

### 4. Run the Server

```python
if __name__ == "__main__":
    app.run(port=8000)
```

Starts uvicorn ASGI server on port 8000

## Add a Health Check

Let's add a health check endpoint:

```python title="app.py" hl_lines="17-20"
from rapidai import App, LLM, stream

app = App()
llm = LLM("claude-3-haiku-20240307")

@app.route("/chat", methods=["POST"])
@stream
async def chat(message: str):
    """Stream a chat response."""
    response = await llm.chat(message, stream=True)
    async for chunk in response:
        yield chunk

# Add health check
@app.route("/health", methods=["GET"])
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}

if __name__ == "__main__":
    app.run(port=8000)
```

Test it:

```bash
curl http://localhost:8000/health
```

Output:
```json
{"status": "healthy", "version": "0.1.0"}
```

## Add Multiple Routes

Expand your app with more endpoints:

```python title="app.py"
from rapidai import App, LLM, stream

app = App()
llm = LLM("claude-3-haiku-20240307")

@app.route("/chat", methods=["POST"])
@stream
async def chat(message: str):
    """General chat."""
    response = await llm.chat(message, stream=True)
    async for chunk in response:
        yield chunk

@app.route("/summarize", methods=["POST"])
async def summarize(text: str):
    """Summarize text."""
    prompt = f"Summarize this concisely:\n\n{text}"
    response = await llm.chat(prompt)
    return {"summary": response}

@app.route("/translate", methods=["POST"])
async def translate(text: str, target_lang: str = "Spanish"):
    """Translate text."""
    prompt = f"Translate to {target_lang}:\n\n{text}"
    response = await llm.chat(prompt)
    return {"translation": response, "language": target_lang}

if __name__ == "__main__":
    app.run(port=8000)
```

Test the new endpoints:

```bash
# Summarize
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "Long article text here..."}'

# Translate
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, how are you?", "target_lang": "French"}'
```

## Next Steps

!!! tip "You're Ready!"
    You've created your first RapidAI application!

**Continue Learning:**

- [Quick Start Guide](quickstart.html) - Learn more features
- [Tutorial](../tutorial/intro.html) - Step-by-step walkthrough
- [Streaming](../tutorial/streaming.html) - Deep dive into streaming
- [Memory](../tutorial/memory.html) - Add conversation memory

**Try This:**

- Switch to a different LLM provider
- Add error handling
- Implement rate limiting
- Deploy to production

---

<div style="text-align: center; padding: 2rem;">
  <a href="quickstart.html" class="md-button md-button--primary">Continue to Quick Start →</a>
</div>
