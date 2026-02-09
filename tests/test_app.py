"""Tests for the App class."""

import pytest
from rapidai import App


@pytest.mark.asyncio
async def test_app_initialization():
    """Test app initialization."""
    app = App(title="Test App", version="1.0.0")
    assert app.title == "Test App"
    assert app.version == "1.0.0"
    assert app.config is not None


@pytest.mark.asyncio
async def test_route_registration():
    """Test route registration."""
    app = App()

    @app.route("/test", methods=["GET"])
    async def test_route():
        return {"message": "test"}

    # Check that route was registered
    assert len(app._routes) == 1
    assert app._routes[0].path == "/test"
    assert "GET" in app._routes[0].methods


@pytest.mark.asyncio
async def test_multiple_routes():
    """Test multiple route registration."""
    app = App()

    @app.route("/route1", methods=["GET"])
    async def route1():
        return {"route": "1"}

    @app.route("/route2", methods=["POST"])
    async def route2():
        return {"route": "2"}

    assert len(app._routes) == 2


@pytest.mark.asyncio
async def test_memory_manager():
    """Test memory manager access."""
    app = App()
    memory = app.memory("user123")

    assert memory is not None
    assert memory.user_id == "user123"

    # Test that same user gets same memory instance
    memory2 = app.memory("user123")
    assert memory is memory2
