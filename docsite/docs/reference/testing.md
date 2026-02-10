# Testing API Reference

Complete API reference for RapidAI's testing utilities.

## Classes

### TestClient

```python
class TestClient:
    def __init__(self, app: App) -> None
```

Test client for making HTTP requests to RapidAI applications without running a server.

**Parameters:**

- `app` (`App`) - RapidAI application instance to test

**Example:**

```python
from rapidai import App
from rapidai.testing import TestClient

app = App()

@app.route("/hello")
async def hello():
    return {"message": "Hello!"}

client = TestClient(app)
response = client.get("/hello")
```

#### Methods

##### get

```python
def get(
    self,
    path: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> TestResponse
```

Send GET request to application.

**Parameters:**

- `path` (`str`) - Request path
- `params` (`Dict[str, Any]`, optional) - Query parameters
- `headers` (`Dict[str, str]`, optional) - Request headers

**Returns:** `TestResponse` - Response object

**Example:**

```python
# Simple GET
response = client.get("/users")

# With query params
response = client.get("/search", params={"q": "test", "limit": 10})

# With headers
response = client.get("/protected", headers={"Authorization": "Bearer token"})
```

##### post

```python
def post(
    self,
    path: str,
    json: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> TestResponse
```

Send POST request to application.

**Parameters:**

- `path` (`str`) - Request path
- `json` (`Dict[str, Any]`, optional) - JSON body
- `data` (`Dict[str, Any]`, optional) - Form data
- `headers` (`Dict[str, str]`, optional) - Request headers

**Returns:** `TestResponse` - Response object

**Example:**

```python
# JSON body
response = client.post("/users", json={"name": "Alice", "email": "alice@example.com"})

# Form data
response = client.post("/upload", data={"file": "data"})

# With headers
response = client.post("/api/data", json={"key": "value"}, headers={"Content-Type": "application/json"})
```

##### put

```python
def put(
    self,
    path: str,
    json: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> TestResponse
```

Send PUT request to application.

**Parameters:**

- `path` (`str`) - Request path
- `json` (`Dict[str, Any]`, optional) - JSON body
- `headers` (`Dict[str, str]`, optional) - Request headers

**Returns:** `TestResponse` - Response object

**Example:**

```python
response = client.put("/users/123", json={"name": "Bob"})
```

##### delete

```python
def delete(
    self,
    path: str,
    headers: Optional[Dict[str, str]] = None,
) -> TestResponse
```

Send DELETE request to application.

**Parameters:**

- `path` (`str`) - Request path
- `headers` (`Dict[str, str]`, optional) - Request headers

**Returns:** `TestResponse` - Response object

**Example:**

```python
response = client.delete("/users/123")
response = client.delete("/sessions/abc", headers={"Authorization": "Bearer token"})
```

### TestResponse

```python
class TestResponse:
    status_code: int
    headers: Dict[str, str]
```

Response object from test client requests.

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `status_code` | `int` | HTTP status code |
| `headers` | `Dict[str, str]` | Response headers |

**Methods:**

#### json

```python
def json(self) -> Any
```

Get JSON response body.

**Returns:** Parsed JSON data

**Example:**

```python
response = client.get("/api/data")
data = response.json()
assert data["key"] == "value"
```

#### text

```python
@property
def text(self) -> str
```

Get text response body.

**Returns:** `str` - Response as string

**Example:**

```python
response = client.get("/html")
html = response.text
assert "<h1>" in html
```

### MockLLM

```python
class MockLLM(BaseLLM):
    def __init__(
        self,
        response: str = "Mock response",
        model: str = "mock-model"
    ) -> None
```

Mock LLM for testing without API calls.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `response` | `str` | `"Mock response"` | Default response to return |
| `model` | `str` | `"mock-model"` | Model name |

**Attributes:**

- `calls` (`list`) - List of all method calls: `[(method, args, kwargs), ...]`
- `default_response` (`str`) - Default response text

**Example:**

```python
from rapidai.testing import MockLLM

llm = MockLLM(response="Test response", model="test-model")
result = await llm.complete("prompt")
assert result == "Test response"

# Verify calls
assert len(llm.calls) == 1
method, prompt, kwargs = llm.calls[0]
assert method == "complete"
assert prompt == "prompt"
```

#### Methods

##### chat

```python
async def chat(self, messages: list, **kwargs: Any) -> str
```

Mock chat method.

**Parameters:**

- `messages` (`list`) - Chat messages
- `**kwargs` - Additional arguments

**Returns:** `str` - Default response

**Tracking:** Adds `("chat", messages, kwargs)` to `calls`

**Example:**

```python
llm = MockLLM(response="Hello!")
result = await llm.chat([{"role": "user", "content": "Hi"}])
assert result == "Hello!"
assert llm.calls[0][0] == "chat"
```

##### complete

```python
async def complete(self, prompt: str, **kwargs: Any) -> str
```

Mock complete method.

**Parameters:**

- `prompt` (`str`) - Prompt text
- `**kwargs` - Additional arguments

**Returns:** `str` - Default response

**Tracking:** Adds `("complete", prompt, kwargs)` to `calls`

**Example:**

```python
llm = MockLLM(response="Completed")
result = await llm.complete("test prompt")
assert result == "Completed"
```

##### stream

```python
async def stream(self, prompt: str, **kwargs: Any)
```

Mock stream method.

**Parameters:**

- `prompt` (`str`) - Prompt text
- `**kwargs` - Additional arguments

**Yields:** Individual characters from default response

**Tracking:** Adds `("stream", prompt, kwargs)` to `calls`

**Example:**

```python
llm = MockLLM(response="ABC")
chunks = []
async for chunk in llm.stream("prompt"):
    chunks.append(chunk)
assert "".join(chunks) == "ABC"
```

##### embed

```python
async def embed(self, text: str) -> list
```

Mock embed method.

**Parameters:**

- `text` (`str`) - Text to embed

**Returns:** `list` - Fake embedding vector (384 dimensions, all 0.1)

**Tracking:** Adds `("embed", text)` to `calls`

**Example:**

```python
llm = MockLLM()
embedding = await llm.embed("text")
assert len(embedding) == 384
assert all(v == 0.1 for v in embedding)
```

##### reset

```python
def reset(self) -> None
```

Reset call history.

**Example:**

```python
llm = MockLLM()
await llm.complete("test")
assert len(llm.calls) == 1

llm.reset()
assert len(llm.calls) == 0
```

### MockMemory

```python
class MockMemory(ConversationMemory):
    def __init__(self) -> None
```

Mock conversation memory for testing.

**Attributes:**

- `calls` (`list`) - List of all method calls: `[(method, args...), ...]`

**Example:**

```python
from rapidai.testing import MockMemory

memory = MockMemory()
memory.add_message("user1", "user", "Hello")

assert len(memory.calls) == 1
method, user_id, role, content = memory.calls[0]
assert method == "add_message"
```

#### Methods

##### add_message

```python
def add_message(self, user_id: str, role: str, content: str) -> None
```

Add message to memory.

**Parameters:**

- `user_id` (`str`) - User identifier
- `role` (`str`) - Message role (user/assistant)
- `content` (`str`) - Message content

**Tracking:** Adds `("add_message", user_id, role, content)` to `calls`

**Example:**

```python
memory = MockMemory()
memory.add_message("user1", "user", "Hello")

# Verify call
assert memory.calls[0] == ("add_message", "user1", "user", "Hello")

# Check storage
history = memory.get_history("user1")
assert len(history) == 1
```

##### get_history

```python
def get_history(self, user_id: str, limit: Optional[int] = None) -> list
```

Get conversation history.

**Parameters:**

- `user_id` (`str`) - User identifier
- `limit` (`int`, optional) - Maximum messages to return

**Returns:** `list` - Message history

**Tracking:** Adds `("get_history", user_id, limit)` to `calls`

**Example:**

```python
memory = MockMemory()
memory.add_message("user1", "user", "Hi")
memory.add_message("user1", "assistant", "Hello")

history = memory.get_history("user1", limit=10)
assert len(history) == 2
assert memory.calls[-1] == ("get_history", "user1", 10)
```

##### clear

```python
def clear(self, user_id: str) -> None
```

Clear conversation history.

**Parameters:**

- `user_id` (`str`) - User identifier

**Tracking:** Adds `("clear", user_id)` to `calls`

**Example:**

```python
memory = MockMemory()
memory.add_message("user1", "user", "Hi")
memory.clear("user1")

assert memory.calls[-1] == ("clear", "user1")
history = memory.get_history("user1")
assert len(history) == 0
```

##### reset

```python
def reset(self) -> None
```

Reset call history (does not clear stored messages).

**Example:**

```python
memory = MockMemory()
memory.add_message("user1", "user", "Hi")

memory.reset()
assert len(memory.calls) == 0  # Calls cleared

# Messages still exist
history = memory.get_history("user1")
assert len(history) == 1
```

## Functions

### create_mock_app

```python
def create_mock_app() -> App
```

Create a mock application with basic routes for testing.

**Returns:** `App` - Mock application with `/health` and `/echo` endpoints

**Routes:**

- `GET /health` - Returns `{"status": "healthy"}`
- `POST /echo` - Returns `{"echo": message}`

**Example:**

```python
from rapidai.testing import create_mock_app, TestClient

app = create_mock_app()
client = TestClient(app)

# Test health endpoint
response = client.get("/health")
assert response.json() == {"status": "healthy"}

# Test echo endpoint
response = client.post("/echo", json={"message": "test"})
assert response.json() == {"echo": "test"}
```

### pytest_fixtures

```python
def pytest_fixtures() -> dict
```

Get pytest fixtures for RapidAI testing.

**Returns:** `dict` - Dictionary of pytest fixtures

**Fixtures:**

- `mock_llm` - MockLLM instance
- `mock_memory` - MockMemory instance
- `test_app` - Mock app instance
- `test_client` - TestClient instance

**Usage:**

Add to `conftest.py`:

```python
from rapidai.testing import pytest_fixtures

# Register fixtures
fixtures = pytest_fixtures()
```

Or define manually:

```python
import pytest
from rapidai.testing import MockLLM, MockMemory, create_mock_app, TestClient

@pytest.fixture
def mock_llm():
    return MockLLM()

@pytest.fixture
def mock_memory():
    return MockMemory()

@pytest.fixture
def test_app():
    return create_mock_app()

@pytest.fixture
def test_client(test_app):
    return TestClient(test_app)
```

## Complete Testing Example

```python
# app.py
from rapidai import App, LLM
from rapidai.memory import ConversationMemory

app = App()
llm = LLM("claude-3-haiku-20240307")
memory = ConversationMemory()

@app.route("/health")
async def health():
    return {"status": "healthy"}

@app.route("/chat", methods=["POST"])
async def chat(user_id: str, message: str):
    memory.add_message(user_id, "user", message)
    history = memory.get_history(user_id)
    response = await llm.chat(history)
    memory.add_message(user_id, "assistant", response)
    return {"response": response}

# test_app.py
import pytest
from rapidai.testing import TestClient, MockLLM, MockMemory
from app import app

@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)

@pytest.fixture
def mock_llm():
    """Mock LLM fixture."""
    return MockLLM(response="Test response")

@pytest.fixture
def mock_memory():
    """Mock memory fixture."""
    return MockMemory()

def test_health_endpoint(client):
    """Test health check."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_chat_endpoint(client):
    """Test chat endpoint."""
    response = client.post(
        "/chat",
        json={"user_id": "test123", "message": "Hello"}
    )

    assert response.status_code == 200
    assert "response" in response.json()

def test_mock_llm_tracking(mock_llm):
    """Test mock LLM call tracking."""
    # Make calls
    await mock_llm.complete("first")
    await mock_llm.complete("second")

    # Verify tracking
    assert len(mock_llm.calls) == 2
    assert mock_llm.calls[0][1] == "first"
    assert mock_llm.calls[1][1] == "second"

    # Reset
    mock_llm.reset()
    assert len(mock_llm.calls) == 0

def test_mock_memory_tracking(mock_memory):
    """Test mock memory call tracking."""
    # Use memory
    mock_memory.add_message("u1", "user", "Hi")
    mock_memory.get_history("u1")
    mock_memory.clear("u1")

    # Verify all calls tracked
    assert len(mock_memory.calls) == 3
    assert mock_memory.calls[0][0] == "add_message"
    assert mock_memory.calls[1][0] == "get_history"
    assert mock_memory.calls[2][0] == "clear"

@pytest.mark.asyncio
async def test_async_operations(mock_llm):
    """Test async mock operations."""
    # Complete
    result = await mock_llm.complete("test")
    assert result == mock_llm.default_response

    # Stream
    chunks = []
    async for chunk in mock_llm.stream("test"):
        chunks.append(chunk)
    assert "".join(chunks) == mock_llm.default_response

    # Embed
    embedding = await mock_llm.embed("text")
    assert len(embedding) == 384
```

## Best Practices

### 1. Always Use Mocks

```python
# ✅ Good
from rapidai.testing import MockLLM

llm = MockLLM(response="Test")
result = await llm.complete("prompt")

# ❌ Avoid
from rapidai import LLM

llm = LLM("claude-3-haiku-20240307")
result = await llm.complete("prompt")  # Real API call!
```

### 2. Track and Verify Calls

```python
llm = MockLLM()
await llm.complete("test")

# Verify the call was made
assert len(llm.calls) == 1
method, prompt, kwargs = llm.calls[0]
assert method == "complete"
assert prompt == "test"
```

### 3. Reset Between Tests

```python
@pytest.fixture
def mock_llm():
    llm = MockLLM()
    yield llm
    llm.reset()  # Clean up after each test
```

### 4. Test Error Cases

```python
@app.route("/divide", methods=["POST"])
async def divide(a: int, b: int):
    if b == 0:
        return {"error": "Division by zero"}, 400
    return {"result": a / b}

def test_error_handling(client):
    response = client.post("/divide", json={"a": 10, "b": 0})
    assert response.status_code == 400
    assert "error" in response.json()
```

### 5. Use Fixtures for DRY

```python
@pytest.fixture
def authenticated_client(client):
    """Pre-configured authenticated client."""
    client.headers = {"Authorization": "Bearer test-token"}
    return client

def test_protected_route(authenticated_client):
    response = authenticated_client.get("/protected")
    assert response.status_code == 200
```

## See Also

- [Testing Guide](../advanced/testing.html) - Complete testing guide
- [Monitoring Reference](monitoring.html) - Test monitoring integration
- [Background Jobs Reference](background.html) - Test background jobs
