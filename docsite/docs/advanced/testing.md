# Testing

RapidAI includes comprehensive testing utilities for building reliable AI applications. Test your endpoints, mock LLMs, and verify behavior without making real API calls.

## Quick Start

```python
from rapidai import App, LLM
from rapidai.testing import TestClient, MockLLM

app = App()

@app.route("/hello")
async def hello():
    return {"message": "Hello, World!"}

# Test
def test_hello():
    client = TestClient(app)
    response = client.get("/hello")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}
```

## Features

- **TestClient** - Test HTTP endpoints without running a server
- **MockLLM** - Mock language models for testing
- **MockMemory** - Mock conversation memory
- **Call Tracking** - Verify mock calls and arguments
- **Pytest Fixtures** - Ready-to-use pytest fixtures
- **No API Costs** - Test without making real API calls

## TestClient

### Basic Usage

```python
from rapidai import App
from rapidai.testing import TestClient

app = App()

@app.route("/echo", methods=["POST"])
async def echo(message: str):
    return {"echo": message}

def test_echo():
    client = TestClient(app)
    response = client.post("/echo", json={"message": "hello"})

    assert response.status_code == 200
    assert response.json() == {"echo": "hello"}
```

### HTTP Methods

```python
from rapidai.testing import TestClient

client = TestClient(app)

# GET request
response = client.get("/users")
response = client.get("/users/123")
response = client.get("/search", params={"q": "test"})

# POST request
response = client.post("/users", json={"name": "Alice"})
response = client.post("/upload", data={"file": "data"})

# PUT request
response = client.put("/users/123", json={"name": "Bob"})

# DELETE request
response = client.delete("/users/123")
```

### Request Headers

```python
response = client.get(
    "/protected",
    headers={"Authorization": "Bearer token"}
)

response = client.post(
    "/api/data",
    json={"key": "value"},
    headers={"Content-Type": "application/json"}
)
```

### Response Object

```python
response = client.get("/api/data")

# Status code
assert response.status_code == 200

# JSON body
data = response.json()
assert data["key"] == "value"

# Text body
text = response.text
assert "success" in text

# Headers
assert response.headers.get("Content-Type") == "application/json"
```

## MockLLM

### Basic Usage

```python
from rapidai.testing import MockLLM

# Create mock with default response
llm = MockLLM(response="This is a mock response")

# Use like regular LLM
result = await llm.complete("test prompt")
assert result == "This is a mock response"
```

### With TestClient

```python
from rapidai import App
from rapidai.testing import TestClient, MockLLM

# Create app with mock LLM
mock_llm = MockLLM(response="Mocked answer")
app = App()

@app.route("/chat", methods=["POST"])
async def chat(message: str):
    response = await mock_llm.complete(message)
    return {"response": response}

# Test
def test_chat():
    client = TestClient(app)
    response = client.post("/chat", json={"message": "hello"})

    assert response.status_code == 200
    assert response.json() == {"response": "Mocked answer"}
```

### Tracking Calls

```python
from rapidai.testing import MockLLM

llm = MockLLM()

# Make calls
await llm.complete("first prompt")
await llm.complete("second prompt")
await llm.chat([{"role": "user", "content": "hello"}])

# Verify calls
assert len(llm.calls) == 3

# Check specific calls
method, prompt, kwargs = llm.calls[0]
assert method == "complete"
assert prompt == "first prompt"

# Reset call history
llm.reset()
assert len(llm.calls) == 0
```

### Mock Methods

```python
from rapidai.testing import MockLLM

llm = MockLLM(response="Mock response")

# Complete
result = await llm.complete("prompt")
assert result == "Mock response"

# Chat
result = await llm.chat([{"role": "user", "content": "hi"}])
assert result == "Mock response"

# Stream
chunks = []
async for chunk in llm.stream("prompt"):
    chunks.append(chunk)
assert "".join(chunks) == "Mock response"

# Embed
embedding = await llm.embed("text")
assert len(embedding) == 384  # Fake embedding
```

## MockMemory

### Basic Usage

```python
from rapidai.testing import MockMemory

memory = MockMemory()

# Use like regular memory
memory.add_message("user1", "user", "Hello")
memory.add_message("user1", "assistant", "Hi!")

history = memory.get_history("user1")
assert len(history) == 2

# Verify calls
assert len(memory.calls) == 3  # 2 add + 1 get
```

### With TestClient

```python
from rapidai import App
from rapidai.testing import TestClient, MockLLM, MockMemory

mock_llm = MockLLM(response="Mocked response")
mock_memory = MockMemory()
app = App()

@app.route("/chat", methods=["POST"])
async def chat(user_id: str, message: str):
    mock_memory.add_message(user_id, "user", message)
    history = mock_memory.get_history(user_id)

    response = await mock_llm.chat(history)
    mock_memory.add_message(user_id, "assistant", response)

    return {"response": response}

def test_chat_with_memory():
    client = TestClient(app)

    # First message
    response = client.post("/chat", json={"user_id": "123", "message": "Hi"})
    assert response.status_code == 200

    # Verify memory was used
    assert len(mock_memory.calls) > 0

    # Check add_message was called
    method, user_id, role, content = mock_memory.calls[0]
    assert method == "add_message"
    assert user_id == "123"
    assert role == "user"
    assert content == "Hi"
```

## Testing Patterns

### Test Endpoints

```python
from rapidai import App
from rapidai.testing import TestClient

app = App()

@app.route("/add", methods=["POST"])
async def add(a: int, b: int):
    return {"result": a + b}

def test_add():
    client = TestClient(app)

    # Test successful case
    response = client.post("/add", json={"a": 2, "b": 3})
    assert response.status_code == 200
    assert response.json() == {"result": 5}

    # Test with different values
    response = client.post("/add", json={"a": 10, "b": 20})
    assert response.json() == {"result": 30}
```

### Test with Fixtures

```python
import pytest
from rapidai import App
from rapidai.testing import TestClient, MockLLM

@pytest.fixture
def app():
    return App()

@pytest.fixture
def client(app):
    return TestClient(app)

@pytest.fixture
def mock_llm():
    return MockLLM(response="Test response")

def test_chat_endpoint(client, mock_llm):
    # Use fixtures in test
    response = client.post("/chat", json={"message": "hello"})
    assert response.status_code == 200
```

### Test Error Handling

```python
from rapidai import App
from rapidai.testing import TestClient

app = App()

@app.route("/divide", methods=["POST"])
async def divide(a: int, b: int):
    if b == 0:
        return {"error": "Division by zero"}, 400
    return {"result": a / b}

def test_divide_by_zero():
    client = TestClient(app)

    response = client.post("/divide", json={"a": 10, "b": 0})

    assert response.status_code == 400
    assert response.json() == {"error": "Division by zero"}
```

### Test RAG System

```python
from rapidai.rag import RAG
from rapidai.rag.mocks import MockEmbedding, MockVectorDB
from rapidai.types import Document

async def test_rag_pipeline():
    # Create RAG with mocks
    embedding = MockEmbedding(dimension=384)
    vectordb = MockVectorDB()
    rag = RAG(embedding=embedding, vectordb=vectordb)

    # Add document
    doc = Document(
        content="RapidAI is a Python framework.",
        metadata={"source": "test.txt"}
    )
    chunks = await rag.add_document(doc)

    assert len(chunks) > 0
    assert all(chunk.embedding is not None for chunk in chunks)

    # Query
    result = await rag.retrieve("What is RapidAI?", top_k=1)

    assert result.text
    assert len(result.sources) > 0
```

### Test Background Jobs

```python
from rapidai.background import background

@background(max_retries=2)
async def process_data(data: str):
    return {"processed": data}

async def test_background_job():
    # Enqueue job
    job_id = await process_data.enqueue(data="test")

    # Wait for completion
    result = await process_data.get_result(job_id)

    assert result.status == "completed"
    assert result.result == {"processed": "test"}
```

### Test Monitoring

```python
from rapidai import App
from rapidai.monitoring import monitor, get_collector
from rapidai.testing import TestClient, MockLLM

app = App()
mock_llm = MockLLM()

@app.route("/chat", methods=["POST"])
@monitor(track_tokens=True, track_cost=True)
async def chat(message: str):
    response = await mock_llm.complete(message)
    return {
        "response": response,
        "tokens_used": 100,
        "model": "mock-model"
    }

def test_monitoring():
    client = TestClient(app)
    collector = get_collector()

    # Clear previous metrics
    collector.clear()

    # Make request
    response = client.post("/chat", json={"message": "hello"})
    assert response.status_code == 200

    # Verify metrics
    summary = collector.get_summary()
    assert summary["total_requests"] >= 1
```

## Pytest Integration

### Setup Fixtures

Create `conftest.py`:

```python
import pytest
from rapidai import App
from rapidai.testing import TestClient, MockLLM, MockMemory

@pytest.fixture
def app():
    """Create test app."""
    return App(title="Test App")

@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)

@pytest.fixture
def mock_llm():
    """Create mock LLM."""
    return MockLLM(response="Test response")

@pytest.fixture
def mock_memory():
    """Create mock memory."""
    return MockMemory()
```

### Write Tests

Create `test_app.py`:

```python
def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_chat_endpoint(client, mock_llm):
    """Test chat endpoint with mock LLM."""
    response = client.post("/chat", json={"message": "hello"})

    assert response.status_code == 200
    assert "response" in response.json()

def test_memory_integration(mock_memory):
    """Test memory integration."""
    mock_memory.add_message("user1", "user", "Hello")

    history = mock_memory.get_history("user1")

    assert len(history) == 1
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"
```

### Run Tests

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_app.py::test_health_endpoint

# Run with coverage
pytest --cov=rapidai tests/

# Run with verbose output
pytest -v
```

## Complete Example: Testing Chat App

```python
# app.py
from rapidai import App, LLM
from rapidai.memory import ConversationMemory
from rapidai.monitoring import monitor

app = App()
llm = LLM("claude-3-haiku-20240307")
memory = ConversationMemory()

@app.route("/health")
async def health():
    return {"status": "healthy"}

@app.route("/chat", methods=["POST"])
@monitor(track_tokens=True)
async def chat(user_id: str, message: str):
    memory.add_message(user_id, "user", message)
    history = memory.get_history(user_id)

    response = await llm.chat(history)

    memory.add_message(user_id, "assistant", response)

    return {
        "response": response,
        "tokens_used": 100,
        "model": llm.model
    }

@app.route("/clear", methods=["POST"])
async def clear(user_id: str):
    memory.clear(user_id)
    return {"message": "Cleared"}

# test_app.py
import pytest
from rapidai.testing import TestClient, MockLLM, MockMemory
from rapidai.monitoring import get_collector
from app import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_llm():
    return MockLLM(response="Test response")

@pytest.fixture
def mock_memory():
    return MockMemory()

def test_health(client):
    """Test health endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_chat(client):
    """Test chat endpoint."""
    response = client.post(
        "/chat",
        json={"user_id": "test123", "message": "Hello"}
    )

    assert response.status_code == 200
    assert "response" in response.json()
    assert "model" in response.json()

def test_chat_with_mocks(client, mock_llm, mock_memory):
    """Test chat with mocks."""
    response = client.post(
        "/chat",
        json={"user_id": "user1", "message": "Hi"}
    )

    assert response.status_code == 200

    # Verify LLM was called
    assert len(mock_llm.calls) > 0

    # Verify memory was used
    assert len(mock_memory.calls) > 0

def test_clear(client):
    """Test clear endpoint."""
    response = client.post("/clear", json={"user_id": "user1"})

    assert response.status_code == 200
    assert response.json() == {"message": "Cleared"}

def test_monitoring(client):
    """Test monitoring integration."""
    collector = get_collector()
    collector.clear()

    # Make request
    client.post("/chat", json={"user_id": "u1", "message": "test"})

    # Check metrics
    summary = collector.get_summary()
    assert summary["total_requests"] >= 1

def test_conversation_flow(client):
    """Test multi-turn conversation."""
    user_id = "test_user"

    # First message
    r1 = client.post("/chat", json={"user_id": user_id, "message": "Hello"})
    assert r1.status_code == 200

    # Second message
    r2 = client.post("/chat", json={"user_id": user_id, "message": "How are you?"})
    assert r2.status_code == 200

    # Clear
    r3 = client.post("/clear", json={"user_id": user_id})
    assert r3.status_code == 200
```

## Best Practices

### 1. Use Mocks for External Services

```python
# ✅ Good - use mocks
from rapidai.testing import MockLLM

mock_llm = MockLLM(response="Test")
result = await mock_llm.complete("test")

# ❌ Avoid - real API calls in tests
llm = LLM("claude-3-haiku-20240307")
result = await llm.complete("test")  # Costs money!
```

### 2. Test Happy and Error Paths

```python
def test_divide_success(client):
    """Test successful division."""
    response = client.post("/divide", json={"a": 10, "b": 2})
    assert response.status_code == 200
    assert response.json() == {"result": 5}

def test_divide_by_zero(client):
    """Test division by zero error."""
    response = client.post("/divide", json={"a": 10, "b": 0})
    assert response.status_code == 400
    assert "error" in response.json()
```

### 3. Use Fixtures for Reusable Components

```python
@pytest.fixture
def authenticated_client(client):
    """Client with authentication."""
    client.headers = {"Authorization": "Bearer test-token"}
    return client

def test_protected_endpoint(authenticated_client):
    response = authenticated_client.get("/protected")
    assert response.status_code == 200
```

### 4. Clean Up After Tests

```python
@pytest.fixture
def collector():
    """Metrics collector fixture."""
    from rapidai.monitoring import get_collector

    collector = get_collector()
    collector.clear()  # Start clean

    yield collector

    collector.clear()  # Clean up after
```

### 5. Test Realistic Scenarios

```python
def test_complete_chat_flow(client, mock_llm):
    """Test complete user interaction."""
    user_id = "user123"

    # Start conversation
    response = client.post("/chat", json={
        "user_id": user_id,
        "message": "I need help with Python"
    })
    assert response.status_code == 200

    # Follow-up question
    response = client.post("/chat", json={
        "user_id": user_id,
        "message": "Can you explain decorators?"
    })
    assert response.status_code == 200

    # Clear conversation
    response = client.post("/clear", json={"user_id": user_id})
    assert response.status_code == 200
```

## Troubleshooting

### Tests Not Running

```bash
# Ensure pytest is installed
pip install pytest

# Run from project root
cd /path/to/project
pytest
```

### Import Errors

```python
# Add project to path in conftest.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
```

### Async Test Errors

```python
# Use pytest-asyncio for async tests
pip install pytest-asyncio

# Mark async tests
@pytest.mark.asyncio
async def test_async_function():
    result = await async_func()
    assert result == expected
```

## Next Steps

- [Testing API Reference](../reference/testing.md) - Complete testing API
- [Monitoring](monitoring.md) - Test monitoring integration
- [Deployment Tutorial](../tutorial/deployment.md) - Test before deploying
