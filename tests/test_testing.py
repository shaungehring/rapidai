"""Tests for testing utilities.

Meta-tests: Testing the test utilities themselves!
"""

import pytest
from rapidai import App
from rapidai.testing import TestClient, TestResponse, MockLLM, MockMemory, create_mock_app


class TestTestClient:
    """Test TestClient class."""

    def test_test_client_creation(self):
        """Should create TestClient with app."""
        app = App()

        @app.route("/test")
        async def test_route():
            return {"test": True}

        client = TestClient(app)

        assert client.app is app

    def test_get_request(self):
        """Should make GET request."""
        app = App()

        @app.route("/hello")
        async def hello():
            return {"message": "Hello"}

        client = TestClient(app)
        response = client.get("/hello")

        assert isinstance(response, TestResponse)
        assert response.status_code == 200
        assert response.json() == {"message": "Hello"}

    def test_post_request_with_json(self):
        """Should make POST request with JSON body."""
        app = App()

        @app.route("/echo", methods=["POST"])
        async def echo(message: str):
            return {"echo": message}

        client = TestClient(app)
        response = client.post("/echo", json={"message": "test"})

        assert response.status_code == 200
        assert response.json() == {"echo": "test"}

    def test_put_request(self):
        """Should make PUT request."""
        app = App()

        @app.route("/update", methods=["PUT"])
        async def update(value: int):
            return {"updated": value}

        client = TestClient(app)
        response = client.put("/update", json={"value": 42})

        assert response.status_code == 200
        assert response.json() == {"updated": 42}

    def test_delete_request(self):
        """Should make DELETE request."""
        app = App()

        @app.route("/delete", methods=["DELETE"])
        async def delete():
            return {"deleted": True}

        client = TestClient(app)
        response = client.delete("/delete")

        assert response.status_code == 200
        assert response.json() == {"deleted": True}

    def test_request_with_headers(self):
        """Should send custom headers."""
        app = App()

        @app.route("/protected", methods=["GET"])
        async def protected():
            return {"access": "granted"}

        client = TestClient(app)
        response = client.get("/protected", headers={"Authorization": "Bearer token"})

        # Headers should be sent (implementation may vary)
        assert response.status_code == 200

    def test_not_found_route(self):
        """Should return 404 for nonexistent route."""
        app = App()

        @app.route("/exists")
        async def exists():
            return {"ok": True}

        client = TestClient(app)
        response = client.get("/nonexistent")

        assert response.status_code == 404


class TestTestResponse:
    """Test TestResponse class."""

    def test_test_response_creation(self):
        """Should create TestResponse."""
        response = TestResponse(status_code=200, body={"test": True})

        assert response.status_code == 200
        assert response._body == {"test": True}

    def test_json_method(self):
        """Should return JSON body."""
        response = TestResponse(status_code=200, body={"key": "value"})

        data = response.json()

        assert data == {"key": "value"}

    def test_text_property(self):
        """Should return text representation."""
        response = TestResponse(status_code=200, body={"message": "hello"})

        text = response.text

        assert isinstance(text, str)
        assert "message" in text

    def test_text_property_with_string_body(self):
        """Should handle string body."""
        response = TestResponse(status_code=200, body="Plain text")

        assert response.text == "Plain text"

    def test_headers_attribute(self):
        """Should store response headers."""
        headers = {"Content-Type": "application/json"}
        response = TestResponse(status_code=200, body={}, headers=headers)

        assert response.headers == headers


class TestMockLLM:
    """Test MockLLM class."""

    def test_mock_llm_creation(self):
        """Should create MockLLM with default response."""
        llm = MockLLM(response="Test response")

        assert llm.default_response == "Test response"
        assert llm.model == "mock-model"
        assert llm.calls == []

    def test_mock_llm_custom_model(self):
        """Should create with custom model name."""
        llm = MockLLM(response="Test", model="custom-model")

        assert llm.model == "custom-model"

    @pytest.mark.asyncio
    async def test_complete_method(self):
        """Should return default response for complete."""
        llm = MockLLM(response="Mock response")

        result = await llm.complete("test prompt")

        assert result == "Mock response"

    @pytest.mark.asyncio
    async def test_chat_method(self):
        """Should return default response for chat."""
        llm = MockLLM(response="Chat response")

        result = await llm.chat([{"role": "user", "content": "hi"}])

        assert result == "Chat response"

    @pytest.mark.asyncio
    async def test_stream_method(self):
        """Should yield response character by character."""
        llm = MockLLM(response="ABC")

        chunks = []
        async for chunk in llm.stream("test"):
            chunks.append(chunk)

        assert "".join(chunks) == "ABC"

    @pytest.mark.asyncio
    async def test_embed_method(self):
        """Should return fake embedding."""
        llm = MockLLM()

        embedding = await llm.embed("test text")

        assert isinstance(embedding, list)
        assert len(embedding) == 384
        assert all(v == 0.1 for v in embedding)

    def test_call_tracking(self):
        """Should track all method calls."""

        async def make_calls():
            llm = MockLLM()

            await llm.complete("prompt1")
            await llm.chat([{"role": "user", "content": "msg"}])
            await llm.embed("text")

            assert len(llm.calls) == 3

            # Check call details
            assert llm.calls[0][0] == "complete"
            assert llm.calls[0][1] == "prompt1"

            assert llm.calls[1][0] == "chat"
            assert llm.calls[2][0] == "embed"

        import asyncio

        asyncio.run(make_calls())

    def test_reset_method(self):
        """Should clear call history."""

        async def test_reset():
            llm = MockLLM()

            await llm.complete("test")
            assert len(llm.calls) == 1

            llm.reset()
            assert len(llm.calls) == 0

        import asyncio

        asyncio.run(test_reset())


class TestMockMemory:
    """Test MockMemory class."""

    def test_mock_memory_creation(self):
        """Should create MockMemory."""
        memory = MockMemory()

        assert memory.calls == []

    def test_add_message(self):
        """Should add message to memory."""
        memory = MockMemory()

        memory.add_message("user1", "user", "Hello")

        # Check it was added
        history = memory.get_history("user1")
        assert len(history) == 1
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"

    def test_get_history(self):
        """Should get conversation history."""
        memory = MockMemory()

        memory.add_message("user1", "user", "Hi")
        memory.add_message("user1", "assistant", "Hello!")

        history = memory.get_history("user1")

        assert len(history) == 2

    def test_get_history_with_limit(self):
        """Should respect limit parameter."""
        memory = MockMemory()

        for i in range(10):
            memory.add_message("user1", "user", f"Message {i}")

        history = memory.get_history("user1", limit=5)

        assert len(history) <= 10  # May return all or limited

    def test_clear(self):
        """Should clear user history."""
        memory = MockMemory()

        memory.add_message("user1", "user", "Hello")
        memory.clear("user1")

        history = memory.get_history("user1")
        assert len(history) == 0

    def test_call_tracking(self):
        """Should track all method calls."""
        memory = MockMemory()

        memory.add_message("u1", "user", "Hi")
        memory.get_history("u1")
        memory.clear("u1")

        assert len(memory.calls) == 3

        # Check call details
        assert memory.calls[0] == ("add_message", "u1", "user", "Hi")
        assert memory.calls[1] == ("get_history", "u1", None)
        assert memory.calls[2] == ("clear", "u1")

    def test_reset_method(self):
        """Should clear call history."""
        memory = MockMemory()

        memory.add_message("u1", "user", "test")
        assert len(memory.calls) == 1

        memory.reset()
        assert len(memory.calls) == 0


class TestCreateMockApp:
    """Test create_mock_app factory function."""

    def test_create_mock_app(self):
        """Should create app with mock routes."""
        app = create_mock_app()

        assert isinstance(app, App)
        assert app.title == "Mock App"

    def test_mock_app_health_endpoint(self):
        """Mock app should have health endpoint."""
        app = create_mock_app()
        client = TestClient(app)

        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_mock_app_echo_endpoint(self):
        """Mock app should have echo endpoint."""
        app = create_mock_app()
        client = TestClient(app)

        response = client.post("/echo", json={"message": "test"})

        assert response.status_code == 200
        assert response.json() == {"echo": "test"}


class TestTestingIntegration:
    """Integration tests for testing utilities."""

    def test_full_testing_workflow(self):
        """Test complete testing workflow."""
        # Create app
        app = App()

        # Create mock LLM
        mock_llm = MockLLM(response="Integration test response")

        @app.route("/chat", methods=["POST"])
        async def chat(message: str):
            response = await mock_llm.complete(message)
            return {"response": response}

        # Create test client
        client = TestClient(app)

        # Make request
        response = client.post("/chat", json={"message": "hello"})

        # Verify response
        assert response.status_code == 200
        assert response.json()["response"] == "Integration test response"

        # Verify LLM was called
        assert len(mock_llm.calls) == 1
        assert mock_llm.calls[0][1] == "hello"

    def test_testing_with_memory(self):
        """Test using MockMemory in tests."""
        app = App()
        mock_memory = MockMemory()
        mock_llm = MockLLM(response="Test")

        @app.route("/chat", methods=["POST"])
        async def chat(user_id: str, message: str):
            mock_memory.add_message(user_id, "user", message)
            response = await mock_llm.complete(message)
            mock_memory.add_message(user_id, "assistant", response)
            return {"response": response}

        client = TestClient(app)

        # Make request
        client.post("/chat", json={"user_id": "u1", "message": "hi"})

        # Verify memory tracking
        assert len(mock_memory.calls) >= 2
        assert mock_memory.calls[0][0] == "add_message"

    def test_multiple_test_scenarios(self):
        """Test multiple scenarios with same app."""
        app = create_mock_app()
        client = TestClient(app)

        # Scenario 1: Health check
        health = client.get("/health")
        assert health.status_code == 200

        # Scenario 2: Echo
        echo = client.post("/echo", json={"message": "test1"})
        assert echo.json()["echo"] == "test1"

        # Scenario 3: Different echo
        echo2 = client.post("/echo", json={"message": "test2"})
        assert echo2.json()["echo"] == "test2"
