"""Testing utilities for RapidAI applications."""

import asyncio
import json
from typing import Any, Dict, Optional
from unittest.mock import AsyncMock

from .app import App
from .llm.base import BaseLLM
from .memory import ConversationMemory, InMemoryStorage


class TestClient:
    """Test client for RapidAI applications."""

    def __init__(self, app: App) -> None:
        """Initialize test client.

        Args:
            app: RapidAI application instance

        Example:
            ```python
            from rapidai import App
            from rapidai.testing import TestClient

            app = App()

            @app.route("/hello")
            async def hello():
                return {"message": "Hello, World!"}

            def test_hello():
                client = TestClient(app)
                response = client.get("/hello")
                assert response.status_code == 200
                assert response.json() == {"message": "Hello, World!"}
            ```
        """
        self.app = app

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> "TestResponse":
        """Send GET request.

        Args:
            path: Request path
            params: Query parameters
            headers: Request headers

        Returns:
            Test response
        """
        return self._request("GET", path, params=params, headers=headers)

    def post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> "TestResponse":
        """Send POST request.

        Args:
            path: Request path
            json: JSON body
            data: Form data
            headers: Request headers

        Returns:
            Test response
        """
        return self._request("POST", path, json=json, data=data, headers=headers)

    def put(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> "TestResponse":
        """Send PUT request.

        Args:
            path: Request path
            json: JSON body
            headers: Request headers

        Returns:
            Test response
        """
        return self._request("PUT", path, json=json, headers=headers)

    def delete(
        self,
        path: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> "TestResponse":
        """Send DELETE request.

        Args:
            path: Request path
            headers: Request headers

        Returns:
            Test response
        """
        return self._request("DELETE", path, headers=headers)

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> "TestResponse":
        """Send HTTP request to app.

        Args:
            method: HTTP method
            path: Request path
            params: Query parameters
            json: JSON body
            data: Form data
            headers: Request headers

        Returns:
            Test response
        """
        # Build request
        request = {
            "type": "http",
            "method": method,
            "path": path,
            "query_string": self._encode_params(params) if params else b"",
            "headers": self._encode_headers(headers or {}),
            "body": self._encode_body(json, data),
        }

        # Find matching route
        handler = None
        for route in self.app.routes:
            if route["path"] == path and method in route["methods"]:
                handler = route["handler"]
                break

        if not handler:
            return TestResponse(status_code=404, body={"error": "Not Found"})

        # Execute handler
        try:
            if json:
                result = asyncio.run(handler(**json))
            elif data:
                result = asyncio.run(handler(**data))
            else:
                result = asyncio.run(handler())

            return TestResponse(status_code=200, body=result)
        except Exception as e:
            return TestResponse(status_code=500, body={"error": str(e)})

    def _encode_params(self, params: Dict[str, Any]) -> bytes:
        """Encode query parameters."""
        from urllib.parse import urlencode

        return urlencode(params).encode()

    def _encode_headers(self, headers: Dict[str, str]) -> list:
        """Encode headers."""
        return [(k.lower().encode(), v.encode()) for k, v in headers.items()]

    def _encode_body(
        self,
        json_data: Optional[Dict[str, Any]],
        form_data: Optional[Dict[str, Any]],
    ) -> bytes:
        """Encode request body."""
        if json_data:
            return json.dumps(json_data).encode()
        elif form_data:
            from urllib.parse import urlencode

            return urlencode(form_data).encode()
        return b""


class TestResponse:
    """Test response object."""

    def __init__(self, status_code: int, body: Any, headers: Optional[Dict[str, str]] = None) -> None:
        """Initialize test response.

        Args:
            status_code: HTTP status code
            body: Response body
            headers: Response headers
        """
        self.status_code = status_code
        self._body = body
        self.headers = headers or {}

    def json(self) -> Any:
        """Get JSON response body.

        Returns:
            Parsed JSON data
        """
        return self._body

    @property
    def text(self) -> str:
        """Get text response body.

        Returns:
            Response as string
        """
        if isinstance(self._body, str):
            return self._body
        return json.dumps(self._body)


class MockLLM(BaseLLM):
    """Mock LLM for testing."""

    def __init__(self, response: str = "Mock response", model: str = "mock-model") -> None:
        """Initialize mock LLM.

        Args:
            response: Default response to return
            model: Model name

        Example:
            ```python
            from rapidai.testing import MockLLM

            llm = MockLLM(response="Test response")
            result = await llm.complete("test prompt")
            assert result == "Test response"
            ```
        """
        super().__init__(model=model)
        self.default_response = response
        self.calls: list = []

    async def chat(self, messages: list, **kwargs: Any) -> str:
        """Mock chat method."""
        self.calls.append(("chat", messages, kwargs))
        return self.default_response

    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """Mock complete method."""
        self.calls.append(("complete", prompt, kwargs))
        return self.default_response

    async def stream(self, prompt: str, **kwargs: Any):
        """Mock stream method."""
        self.calls.append(("stream", prompt, kwargs))
        for char in self.default_response:
            yield char

    async def embed(self, text: str) -> list:
        """Mock embed method."""
        self.calls.append(("embed", text))
        # Return fake embedding
        return [0.1] * 384

    def reset(self) -> None:
        """Reset call history."""
        self.calls.clear()


class MockMemory(ConversationMemory):
    """Mock memory for testing."""

    def __init__(self) -> None:
        """Initialize mock memory."""
        super().__init__(storage=InMemoryStorage())
        self.calls: list = []

    def add_message(self, user_id: str, role: str, content: str) -> None:
        """Mock add_message."""
        self.calls.append(("add_message", user_id, role, content))
        super().add_message(user_id, role, content)

    def get_history(self, user_id: str, limit: Optional[int] = None) -> list:
        """Mock get_history."""
        self.calls.append(("get_history", user_id, limit))
        return super().get_history(user_id, limit)

    def clear(self, user_id: str) -> None:
        """Mock clear."""
        self.calls.append(("clear", user_id))
        super().clear(user_id)

    def reset(self) -> None:
        """Reset call history."""
        self.calls.clear()


def create_mock_app() -> App:
    """Create a mock app for testing.

    Returns:
        App instance with mock routes

    Example:
        ```python
        from rapidai.testing import create_mock_app

        app = create_mock_app()
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        ```
    """
    app = App(title="Mock App")

    @app.route("/health", methods=["GET"])
    async def health():
        return {"status": "healthy"}

    @app.route("/echo", methods=["POST"])
    async def echo(message: str):
        return {"echo": message}

    return app


# Fixtures for pytest
def pytest_fixtures():
    """Pytest fixtures for RapidAI testing.

    Add to conftest.py:
        ```python
        from rapidai.testing import pytest_fixtures
        pytest_fixtures()
        ```
    """
    try:
        import pytest
    except ImportError:
        return

    @pytest.fixture
    def mock_llm():
        """Mock LLM fixture."""
        return MockLLM()

    @pytest.fixture
    def mock_memory():
        """Mock memory fixture."""
        return MockMemory()

    @pytest.fixture
    def test_app():
        """Test app fixture."""
        return create_mock_app()

    @pytest.fixture
    def test_client(test_app):
        """Test client fixture."""
        return TestClient(test_app)

    return {
        "mock_llm": mock_llm,
        "mock_memory": mock_memory,
        "test_app": test_app,
        "test_client": test_client,
    }
