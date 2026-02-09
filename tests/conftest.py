"""Pytest configuration and fixtures."""

import pytest
from rapidai import App, MockLLM
from rapidai.config import LLMConfig


@pytest.fixture
def app():
    """Create a test application instance."""
    return App(title="Test App", version="1.0.0")


@pytest.fixture
def mock_llm():
    """Create a mock LLM instance."""
    llm = MockLLM(config=LLMConfig(model="mock"))
    llm.set_responses(["This is a test response", "Another response"])
    return llm


@pytest.fixture
async def test_client(app):
    """Create a test client for the app."""
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
