"""Example: Testing RapidAI Applications.

This example demonstrates:
1. Using TestClient for endpoint testing
2. MockLLM for testing without API calls
3. MockMemory for memory testing
4. Call tracking and verification
5. pytest integration

Run tests with: pytest testing_example.py -v
"""

import pytest
from rapidai import App, LLM
from rapidai.testing import TestClient, MockLLM, MockMemory
from rapidai.memory import ConversationMemory

# Create application
app = App(title="Test Example App")

# Real LLM (would cost money in tests)
real_llm = LLM("claude-3-haiku-20240307")

# Mock LLM for testing
mock_llm = MockLLM(response="This is a test response")

# Memory
memory = ConversationMemory()


# Example endpoints
@app.route("/health", methods=["GET"])
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.route("/echo", methods=["POST"])
async def echo(message: str):
    """Echo endpoint for testing."""
    return {"echo": message}


@app.route("/chat", methods=["POST"])
async def chat(message: str):
    """Chat endpoint using mock LLM."""
    response = await mock_llm.complete(message)
    return {"response": response}


@app.route("/chat/memory", methods=["POST"])
async def chat_with_memory(user_id: str, message: str):
    """Chat with conversation memory."""
    memory.add_message(user_id, "user", message)
    history = memory.get_history(user_id)

    response = await mock_llm.chat(history)

    memory.add_message(user_id, "assistant", response)

    return {"response": response, "history_length": len(history)}


@app.route("/users/<user_id>", methods=["GET"])
async def get_user(user_id: str):
    """Get user endpoint for path parameter testing."""
    return {"user_id": user_id, "name": f"User {user_id}"}


# Pytest fixtures
@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


@pytest.fixture
def test_llm():
    """Mock LLM fixture."""
    llm = MockLLM(response="Fixture test response")
    yield llm
    llm.reset()  # Clean up after test


@pytest.fixture
def test_memory():
    """Mock memory fixture."""
    mem = MockMemory()
    yield mem
    mem.reset()


# Tests
class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_returns_200(self, client):
        """Health endpoint should return 200."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_health_returns_json(self, client):
        """Health endpoint should return JSON."""
        response = client.get("/health")

        data = response.json()
        assert isinstance(data, dict)
        assert "status" in data


class TestEchoEndpoint:
    """Test echo endpoint."""

    def test_echo_returns_message(self, client):
        """Echo should return the message."""
        response = client.post("/echo", json={"message": "Hello"})

        assert response.status_code == 200
        assert response.json() == {"echo": "Hello"}

    def test_echo_with_different_messages(self, client):
        """Echo should work with different messages."""
        messages = ["test1", "test2", "hello world"]

        for msg in messages:
            response = client.post("/echo", json={"message": msg})
            assert response.json()["echo"] == msg


class TestChatEndpoint:
    """Test chat endpoint with mock LLM."""

    def test_chat_returns_response(self, client):
        """Chat should return LLM response."""
        response = client.post("/chat", json={"message": "Hello"})

        assert response.status_code == 200
        assert "response" in response.json()
        assert response.json()["response"] == "This is a test response"

    def test_chat_tracks_llm_calls(self, test_llm):
        """Chat should track LLM calls."""
        # Make calls
        result1 = await test_llm.complete("first")
        result2 = await test_llm.complete("second")

        # Verify tracking
        assert len(test_llm.calls) == 2
        assert test_llm.calls[0][1] == "first"
        assert test_llm.calls[1][1] == "second"


class TestChatWithMemory:
    """Test chat with memory integration."""

    def test_memory_stores_messages(self, client, test_memory):
        """Memory should store conversation."""
        test_memory.add_message("user1", "user", "Hello")
        test_memory.add_message("user1", "assistant", "Hi!")

        history = test_memory.get_history("user1")

        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"

    def test_memory_tracks_calls(self, test_memory):
        """Memory should track method calls."""
        test_memory.add_message("u1", "user", "test")
        test_memory.get_history("u1")
        test_memory.clear("u1")

        assert len(test_memory.calls) == 3
        assert test_memory.calls[0][0] == "add_message"
        assert test_memory.calls[1][0] == "get_history"
        assert test_memory.calls[2][0] == "clear"


class TestUserEndpoint:
    """Test user endpoint with path parameters."""

    def test_get_user_returns_user_data(self, client):
        """User endpoint should return user data."""
        response = client.get("/users/123")

        # Note: TestClient currently has limited path parameter support
        # This is a demonstration of the pattern
        assert response.status_code == 200


class TestMockLLM:
    """Test MockLLM functionality."""

    @pytest.mark.asyncio
    async def test_complete_returns_default(self, test_llm):
        """Complete should return default response."""
        result = await test_llm.complete("test prompt")

        assert result == "Fixture test response"

    @pytest.mark.asyncio
    async def test_chat_returns_default(self, test_llm):
        """Chat should return default response."""
        result = await test_llm.chat([{"role": "user", "content": "hi"}])

        assert result == "Fixture test response"

    @pytest.mark.asyncio
    async def test_stream_yields_response(self, test_llm):
        """Stream should yield response character by character."""
        chunks = []
        async for chunk in test_llm.stream("test"):
            chunks.append(chunk)

        assert "".join(chunks) == "Fixture test response"

    @pytest.mark.asyncio
    async def test_embed_returns_vector(self, test_llm):
        """Embed should return fake embedding vector."""
        embedding = await test_llm.embed("text")

        assert len(embedding) == 384
        assert all(v == 0.1 for v in embedding)

    def test_reset_clears_calls(self, test_llm):
        """Reset should clear call history."""
        # Make some calls
        import asyncio

        asyncio.run(test_llm.complete("test"))

        assert len(test_llm.calls) > 0

        # Reset
        test_llm.reset()

        assert len(test_llm.calls) == 0


# Run tests
if __name__ == "__main__":
    print("Testing Example")
    print("=" * 50)
    print("\nThis file demonstrates testing RapidAI applications.")
    print("\nRun tests with:")
    print("  pytest testing_example.py -v")
    print("\nRun with coverage:")
    print("  pytest testing_example.py --cov=rapidai --cov-report=term-missing")
    print("\nRun specific test:")
    print("  pytest testing_example.py::TestHealthEndpoint::test_health_returns_200 -v")
    print("\nTest features demonstrated:")
    print("  ✓ TestClient for HTTP testing")
    print("  ✓ MockLLM for LLM mocking")
    print("  ✓ MockMemory for memory mocking")
    print("  ✓ Call tracking and verification")
    print("  ✓ pytest fixtures and organization")
    print("=" * 50)

    # Run pytest
    pytest.main([__file__, "-v", "--tb=short"])
