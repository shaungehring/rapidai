# UI Components

RapidAI includes pre-built UI components for rapid prototyping of AI applications. Get a beautiful chat interface running in minutes with zero frontend code.

## Quick Start

```python
from rapidai import App, LLM
from rapidai.ui import page, get_chat_template

app = App()
llm = LLM("claude-3-haiku-20240307")

@app.route("/")
@page("/")
async def index():
    return get_chat_template(
        title="My AI Chat",
        theme="dark"
    )

@app.route("/api/chat", methods=["POST"])
async def chat(message: str):
    response = await llm.complete(message)
    return {"response": response}

if __name__ == "__main__":
    app.run()
```

Visit `http://localhost:8000` to see your chat interface!

## Features

- **Zero Frontend Code** - Pure Python, no HTML/CSS/JS required
- **Beautiful Themes** - Dark and light themes out of the box
- **Markdown Support** - Render formatted responses
- **File Uploads** - Handle document uploads
- **Real-time Streaming** - Stream LLM responses
- **Mobile Responsive** - Works on all devices
- **Customizable** - Easy theming and branding

## Chat Interface

### Basic Chat

```python
from rapidai import App
from rapidai.ui import page, get_chat_template

app = App()

@app.route("/")
@page("/")
async def index():
    return get_chat_template()
```

**Default features:**
- Send messages with Enter key
- Markdown rendering
- Auto-scroll to latest message
- Message history
- Clear conversation button

### Custom Configuration

```python
from rapidai.ui import ChatInterface, get_chat_template

interface = ChatInterface(
    title="Customer Support Bot",
    theme="light",
    primary_color="#007bff",
    placeholder="How can I help you today?",
    enable_file_upload=True,
    max_file_size_mb=10,
    allowed_file_types=[".pdf", ".txt", ".docx"],
    show_timestamps=True,
    enable_markdown=True
)

@app.route("/")
@page("/")
async def index():
    return get_chat_template(config=interface)
```

### Themes

**Built-in themes:**

```python
# Dark theme (default)
get_chat_template(theme="dark")

# Light theme
get_chat_template(theme="light")
```

**Custom theme:**

```python
interface = ChatInterface(
    theme="custom",
    primary_color="#ff6b6b",
    background_color="#1a1a2e",
    text_color="#eee",
    user_message_color="#3a3a5e",
    bot_message_color="#2d2d4e"
)
```

## @page Decorator

The `@page` decorator serves HTML content with proper content type headers.

### Basic Usage

```python
from rapidai.ui import page

@app.route("/")
@page("/")
async def index():
    return "<h1>Hello, World!</h1>"
```

### With Templates

```python
from rapidai.ui import page, get_chat_template

@app.route("/chat")
@page("/chat")
async def chat_page():
    return get_chat_template(title="AI Chat")

@app.route("/dashboard")
@page("/dashboard")
async def dashboard():
    return get_dashboard_template()
```

### Response Format

The decorator automatically adds:

```python
{
    "status": 200,
    "headers": {"Content-Type": "text/html; charset=utf-8"},
    "body": html_content
}
```

## Chat API Integration

### Simple Chat Endpoint

```python
from rapidai import App, LLM
from rapidai.ui import page, get_chat_template

app = App()
llm = LLM("claude-3-haiku-20240307")

@app.route("/")
@page("/")
async def index():
    return get_chat_template()

@app.route("/api/chat", methods=["POST"])
async def chat(message: str):
    response = await llm.complete(message)
    return {"response": response}
```

### With Memory

```python
from rapidai import App, LLM
from rapidai.memory import ConversationMemory

app = App()
llm = LLM("claude-3-haiku-20240307")
memory = ConversationMemory()

@app.route("/api/chat", methods=["POST"])
async def chat(user_id: str, message: str):
    # Add user message
    memory.add_message(user_id, "user", message)

    # Get history
    history = memory.get_history(user_id)

    # Generate response
    response = await llm.chat(history)

    # Add assistant message
    memory.add_message(user_id, "assistant", response)

    return {"response": response}
```

### With RAG

```python
from rapidai import App, LLM
from rapidai.rag import RAG
from rapidai.ui import page, get_chat_template

app = App()
llm = LLM("claude-3-haiku-20240307")
rag = RAG()

@app.route("/")
@page("/")
async def index():
    return get_chat_template(
        title="Document Q&A",
        placeholder="Ask a question about your documents..."
    )

@app.route("/api/chat", methods=["POST"])
async def chat(message: str):
    # Retrieve relevant context
    retrieval = await rag.retrieve(message, top_k=3)

    # Build prompt with context
    prompt = f"""Context:
{retrieval.text}

Question: {message}

Answer:"""

    response = await llm.complete(prompt)

    return {
        "response": response,
        "sources": [s["source"] for s in retrieval.sources]
    }
```

### Streaming Responses

```python
from rapidai import App, LLM
from rapidai.ui import page, get_chat_template

app = App()
llm = LLM("claude-3-haiku-20240307")

@app.route("/")
@page("/")
async def index():
    return get_chat_template(enable_streaming=True)

@app.route("/api/chat/stream", methods=["POST"])
async def chat_stream(message: str):
    async def generate():
        async for chunk in llm.stream(message):
            yield f"data: {chunk}\n\n"

    return {
        "type": "stream",
        "generator": generate(),
        "headers": {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache"
        }
    }
```

## File Upload Integration

### Enable File Uploads

```python
from rapidai.ui import ChatInterface, get_chat_template

interface = ChatInterface(
    enable_file_upload=True,
    max_file_size_mb=10,
    allowed_file_types=[".pdf", ".txt", ".docx"]
)

@app.route("/")
@page("/")
async def index():
    return get_chat_template(config=interface)
```

### Handle Uploads

```python
from rapidai.rag import RAG

rag = RAG()

@app.route("/api/upload", methods=["POST"])
async def upload(file: UploadFile):
    # Save file
    filepath = f"./uploads/{file.filename}"
    with open(filepath, "wb") as f:
        f.write(await file.read())

    # Process with RAG
    chunks = await rag.add_document(filepath)

    return {
        "message": "File uploaded successfully",
        "chunks": len(chunks),
        "filename": file.filename
    }

@app.route("/api/chat", methods=["POST"])
async def chat(message: str):
    # Query RAG
    retrieval = await rag.retrieve(message)
    prompt = f"Context: {retrieval.text}\n\nQuestion: {message}"
    response = await llm.complete(prompt)

    return {"response": response}
```

## Custom Templates

### Create Custom HTML

```python
from rapidai.ui import page

def get_custom_template():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Custom App</title>
        <style>
            body {
                font-family: system-ui;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
        </style>
    </head>
    <body>
        <h1>My Custom AI App</h1>
        <div id="chat"></div>
        <input type="text" id="input" placeholder="Type a message..." />
        <button onclick="send()">Send</button>

        <script>
            async function send() {
                const input = document.getElementById('input');
                const message = input.value;

                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message})
                });

                const data = await response.json();
                document.getElementById('chat').innerHTML +=
                    `<p><strong>You:</strong> ${message}</p>` +
                    `<p><strong>Bot:</strong> ${data.response}</p>`;

                input.value = '';
            }
        </script>
    </body>
    </html>
    """

@app.route("/")
@page("/")
async def index():
    return get_custom_template()
```

### Extend Chat Template

```python
from rapidai.ui import get_chat_template

def get_enhanced_chat():
    base = get_chat_template()

    # Add custom CSS
    custom_css = """
    <style>
        .custom-header {
            background: linear-gradient(to right, #667eea, #764ba2);
            padding: 20px;
            color: white;
        }
    </style>
    """

    # Inject before </head>
    return base.replace("</head>", f"{custom_css}</head>")

@app.route("/")
@page("/")
async def index():
    return get_enhanced_chat()
```

## Complete Example: Support Bot

```python
from rapidai import App, LLM
from rapidai.memory import ConversationMemory
from rapidai.rag import RAG
from rapidai.ui import page, ChatInterface, get_chat_template

app = App(title="Customer Support Bot")
llm = LLM("claude-3-haiku-20240307")
memory = ConversationMemory()
rag = RAG()

# Load knowledge base
async def load_docs():
    docs = ["faq.pdf", "manual.pdf", "policies.txt"]
    for doc in docs:
        await rag.add_document(doc)

@app.on_startup
async def startup():
    await load_docs()

# Serve UI
interface = ChatInterface(
    title="Customer Support",
    theme="light",
    primary_color="#0066cc",
    placeholder="How can we help you today?",
    show_timestamps=True
)

@app.route("/")
@page("/")
async def index():
    return get_chat_template(config=interface)

# Chat endpoint
@app.route("/api/chat", methods=["POST"])
async def chat(user_id: str, message: str):
    # Add to memory
    memory.add_message(user_id, "user", message)

    # Retrieve relevant docs
    retrieval = await rag.retrieve(message, top_k=3)

    # Get conversation history
    history = memory.get_history(user_id, limit=10)

    # Build context-aware prompt
    system = f"""You are a helpful customer support agent.
Use the following knowledge base to answer questions:

{retrieval.text}

Be concise, friendly, and helpful."""

    messages = [{"role": "system", "content": system}] + history

    # Generate response
    response = await llm.chat(messages)

    # Add to memory
    memory.add_message(user_id, "assistant", response)

    return {
        "response": response,
        "sources": [s["source"] for s in retrieval.sources]
    }

# Clear conversation
@app.route("/api/clear", methods=["POST"])
async def clear(user_id: str):
    memory.clear(user_id)
    return {"message": "Conversation cleared"}

if __name__ == "__main__":
    app.run(port=8000)
```

## Best Practices

### 1. Use Semantic HTML

```python
# ✅ Good
return get_chat_template(title="My App")

# ❌ Avoid
return "<h1>My App</h1><div>...</div>"  # Rebuild entire UI
```

### 2. Separate UI and API

```python
# UI routes
@app.route("/")
@page("/")
async def index():
    return get_chat_template()

# API routes
@app.route("/api/chat", methods=["POST"])
async def chat(message: str):
    return {"response": await llm.complete(message)}
```

### 3. Handle Errors Gracefully

```python
@app.route("/api/chat", methods=["POST"])
async def chat(message: str):
    try:
        response = await llm.complete(message)
        return {"response": response}
    except Exception as e:
        return {
            "error": "Sorry, something went wrong. Please try again.",
            "details": str(e)
        }, 500
```

### 4. Add Loading States

```python
# Frontend automatically shows loading spinner
# Just ensure timely responses

@app.route("/api/chat", methods=["POST"])
async def chat(message: str):
    # Long-running task
    response = await llm.complete(message)  # User sees loading...
    return {"response": response}
```

### 5. Validate Input

```python
@app.route("/api/chat", methods=["POST"])
async def chat(message: str):
    if not message or len(message) < 1:
        return {"error": "Message cannot be empty"}, 400

    if len(message) > 1000:
        return {"error": "Message too long (max 1000 chars)"}, 400

    response = await llm.complete(message)
    return {"response": response}
```

## Troubleshooting

### Template Not Rendering

```python
# Ensure @page decorator is applied
@app.route("/")
@page("/")  # ✅ Correct
async def index():
    return get_chat_template()

# Missing decorator
@app.route("/")  # ❌ Returns HTML as JSON
async def index():
    return get_chat_template()
```

### File Upload Not Working

```python
# Ensure file upload is enabled
interface = ChatInterface(
    enable_file_upload=True,  # Must be True
    max_file_size_mb=10
)

# Handle upload endpoint
@app.route("/api/upload", methods=["POST"])
async def upload(file: UploadFile):
    # Process file
    return {"message": "Uploaded"}
```

### Styling Issues

```python
# Use custom CSS for fine-tuning
interface = ChatInterface(
    theme="custom",
    primary_color="#your-color",
    background_color="#your-bg"
)

# Or extend template with custom CSS
```

## Next Steps

- [UI API Reference](../reference/ui.md) - Complete UI API
- [Testing](testing.md) - Test your UI endpoints
- [Deployment Tutorial](../tutorial/deployment.md) - Deploy your UI
