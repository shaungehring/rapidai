# App Reference

The `App` class is the core of RapidAI, providing routing, middleware, and application lifecycle management.

## Class: `App`

```python
from rapidai import App

app = App(
    title="My AI App",
    version="1.0.0",
    config=None
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `title` | `str` | `"RapidAI Application"` | Application title |
| `version` | `str` | `"1.0.0"` | Application version |
| `config` | `RapidAIConfig` | `None` | Configuration object (auto-loaded if None) |

### Example

```python
from rapidai import App

# Simple initialization
app = App()

# With custom title and version
app = App(title="AI Assistant", version="2.0.0")

# With custom configuration
from rapidai import RapidAIConfig
config = RapidAIConfig.load("config.yaml")
app = App(config=config)
```

## Methods

### `route()`

Register a route handler.

```python
@app.route(path: str, methods: List[str] = None)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | `str` | Required | URL path |
| `methods` | `List[str]` | `["GET"]` | HTTP methods |

#### Example

```python
@app.route("/chat", methods=["POST"])
async def chat(message: str):
    return {"response": "Hello!"}

@app.route("/health", methods=["GET"])
async def health():
    return {"status": "healthy"}
```

### `use()`

Add middleware to the application.

```python
app.use(middleware: Middleware)
```

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `middleware` | `Middleware` | Middleware function |

#### Example

```python
async def logging_middleware(request, next):
    print(f"Request: {request}")
    response = await next()
    print(f"Response: {response}")
    return response

app.use(logging_middleware)
```

### `memory()`

Get conversation memory for a user.

```python
app.memory(user_id: str) -> ConversationMemory
```

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `user_id` | `str` | User identifier |

#### Returns

`ConversationMemory` - Memory instance for the user

#### Example

```python
@app.route("/chat", methods=["POST"])
async def chat(user_id: str, message: str):
    memory = app.memory(user_id)
    history = memory.get()
    # Use history...
```

### `run()`

Run the application server.

```python
app.run(
    host: str = None,
    port: int = None,
    workers: int = None
)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `host` | `str` | `"0.0.0.0"` | Host to bind to |
| `port` | `int` | `8000` | Port to bind to |
| `workers` | `int` | `1` | Number of workers |

#### Example

```python
if __name__ == "__main__":
    # Default settings
    app.run()

    # Custom port
    app.run(port=3000)

    # Production settings
    app.run(host="0.0.0.0", port=8000, workers=4)
```

## Attributes

### `title`

Application title.

```python
app.title -> str
```

### `version`

Application version.

```python
app.version -> str
```

### `config`

Application configuration.

```python
app.config -> RapidAIConfig
```

## Full Example

```python
from rapidai import App, LLM, stream, cache

# Initialize
app = App(title="AI Assistant", version="1.0.0")
llm = LLM("claude-3-haiku-20240307")

# Middleware
async def auth_middleware(request, next):
    # Add authentication logic
    return await next()

app.use(auth_middleware)

# Routes
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

@app.route("/summarize", methods=["POST"])
@cache(ttl=3600)
async def summarize(text: str):
    return await llm.chat(f"Summarize: {text}")

@app.route("/health")
async def health():
    return {"status": "healthy"}

# Run
if __name__ == "__main__":
    app.run(port=8000)
```

## See Also

- [LLM Reference](llm.md)
- [Streaming Reference](streaming.md)
- [Memory Reference](memory.md)
- [Cache Reference](cache.md)
