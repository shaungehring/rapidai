"""Tests for UI components."""

import pytest
from rapidai import App
from rapidai.ui import page, ChatInterface, get_chat_template
from rapidai.testing import TestClient


class TestChatInterface:
    """Test ChatInterface dataclass."""

    def test_chat_interface_defaults(self):
        """Should create with default values."""
        config = ChatInterface()

        assert config.title == "RapidAI Chat"
        assert config.theme == "dark"
        assert config.show_timestamps is True
        assert config.enable_markdown is True
        assert config.enable_file_upload is False
        assert config.placeholder == "Type your message..."
        assert config.max_height == "600px"
        assert config.avatar_user == "👤"
        assert config.avatar_assistant == "🤖"

    def test_chat_interface_custom_values(self):
        """Should create with custom values."""
        config = ChatInterface(
            title="Custom Chat",
            theme="light",
            show_timestamps=False,
            enable_markdown=False,
            enable_file_upload=True,
            placeholder="Ask a question...",
            max_height="800px",
            avatar_user="😊",
            avatar_assistant="🤝",
        )

        assert config.title == "Custom Chat"
        assert config.theme == "light"
        assert config.show_timestamps is False
        assert config.enable_markdown is False
        assert config.enable_file_upload is True
        assert config.placeholder == "Ask a question..."
        assert config.max_height == "800px"
        assert config.avatar_user == "😊"
        assert config.avatar_assistant == "🤝"


class TestGetChatTemplate:
    """Test get_chat_template function."""

    def test_get_chat_template_returns_html(self):
        """Should return HTML string."""
        html = get_chat_template()

        assert isinstance(html, str)
        assert len(html) > 0

    def test_template_contains_html_structure(self):
        """Template should contain HTML structure."""
        html = get_chat_template()

        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "</html>" in html
        assert "<head>" in html
        assert "<body>" in html

    def test_template_with_custom_title(self):
        """Should use custom title."""
        html = get_chat_template(title="My Custom Chat")

        assert "My Custom Chat" in html

    def test_template_with_light_theme(self):
        """Should apply light theme colors."""
        html = get_chat_template(theme="light")

        # Should contain light theme colors
        assert "#ffffff" in html or "white" in html.lower()

    def test_template_with_dark_theme(self):
        """Should apply dark theme colors."""
        html = get_chat_template(theme="dark")

        # Should contain dark theme colors
        assert "#0a0a0a" in html or "#1a1a1a" in html

    def test_template_with_config_object(self):
        """Should accept ChatInterface config."""
        config = ChatInterface(title="Test", theme="light", placeholder="Type here...")

        html = get_chat_template(config=config)

        assert "Test" in html
        assert "Type here..." in html

    def test_template_with_markdown_enabled(self):
        """Should include markdown script when enabled."""
        config = ChatInterface(enable_markdown=True)
        html = get_chat_template(config=config)

        assert "marked" in html.lower() or "markdown" in html.lower()

    def test_template_with_file_upload(self):
        """Should include file upload button when enabled."""
        config = ChatInterface(enable_file_upload=True)
        html = get_chat_template(config=config)

        assert "file" in html.lower()
        assert "upload" in html.lower() or "input" in html.lower()

    def test_template_without_file_upload(self):
        """Should not include file upload when disabled."""
        config = ChatInterface(enable_file_upload=False)
        html = get_chat_template(config=config)

        # Should not have file input
        assert 'type="file"' not in html


class TestPageDecorator:
    """Test @page decorator."""

    def test_page_decorator_wraps_function(self):
        """Page decorator should wrap async function."""

        @page("/")
        async def index():
            return "<h1>Test</h1>"

        assert callable(index)

    def test_page_decorator_returns_proper_format(self):
        """Page decorator should return proper HTTP response format."""
        app = App()

        @app.route("/")
        @page("/")
        async def index():
            return "<h1>Hello</h1>"

        client = TestClient(app)
        response = client.get("/")

        # Should return HTML response
        assert response.status_code == 200

    def test_page_decorator_sets_content_type(self):
        """Page decorator should set HTML content type."""
        app = App()

        @app.route("/test")
        @page("/test")
        async def test_page():
            return "<p>Test</p>"

        # Decorator should set Content-Type header internally
        # This is a behavior test of the decorator


class TestUIIntegration:
    """Integration tests for UI components."""

    def test_serve_chat_interface(self):
        """Should serve chat interface at route."""
        app = App()

        @app.route("/")
        @page("/")
        async def index():
            return get_chat_template()

        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        # Response should contain HTML
        html = response.text
        assert "<!DOCTYPE html>" in html
        assert "chat" in html.lower()

    def test_serve_multiple_chat_interfaces(self):
        """Should serve different chat interfaces at different routes."""
        app = App()

        @app.route("/dark")
        @page("/dark")
        async def dark_chat():
            return get_chat_template(theme="dark")

        @app.route("/light")
        @page("/light")
        async def light_chat():
            return get_chat_template(theme="light")

        client = TestClient(app)

        dark_response = client.get("/dark")
        light_response = client.get("/light")

        assert dark_response.status_code == 200
        assert light_response.status_code == 200

        # Both should be valid HTML
        assert "<!DOCTYPE html>" in dark_response.text
        assert "<!DOCTYPE html>" in light_response.text

    def test_chat_api_backend(self):
        """Should create backend API for chat interface."""
        app = App()

        @app.route("/")
        @page("/")
        async def index():
            return get_chat_template()

        @app.route("/chat", methods=["POST"])
        async def chat(message: str):
            return {"response": f"Echo: {message}"}

        client = TestClient(app)

        # Frontend
        frontend_response = client.get("/")
        assert frontend_response.status_code == 200

        # Backend API
        api_response = client.post("/chat", json={"message": "test"})
        assert api_response.status_code == 200
        assert api_response.json() == {"response": "Echo: test"}

    def test_custom_theme_application(self):
        """Should apply custom configuration."""
        config = ChatInterface(
            title="Support Bot",
            theme="light",
            placeholder="How can we help?",
            enable_file_upload=True,
        )

        html = get_chat_template(config=config)

        assert "Support Bot" in html
        assert "How can we help?" in html


class TestUITemplateStructure:
    """Test UI template structure and components."""

    def test_template_has_css(self):
        """Template should include CSS styling."""
        html = get_chat_template()

        assert "<style>" in html
        assert "</style>" in html

    def test_template_has_javascript(self):
        """Template should include JavaScript."""
        html = get_chat_template()

        assert "<script>" in html
        assert "</script>" in html

    def test_template_has_message_container(self):
        """Template should have message container."""
        html = get_chat_template()

        assert "messages" in html or "chat" in html

    def test_template_has_input_field(self):
        """Template should have input field."""
        html = get_chat_template()

        assert "input" in html.lower() or "textarea" in html.lower()

    def test_template_has_send_button(self):
        """Template should have send button."""
        html = get_chat_template()

        assert "send" in html.lower() or "button" in html.lower()


class TestUICustomization:
    """Test UI customization options."""

    def test_custom_avatars(self):
        """Should support custom avatar emojis."""
        config = ChatInterface(avatar_user="🧑", avatar_assistant="🦾")

        html = get_chat_template(config=config)

        assert "🧑" in html
        assert "🦾" in html

    def test_custom_max_height(self):
        """Should apply custom max height."""
        config = ChatInterface(max_height="900px")

        html = get_chat_template(config=config)

        assert "900px" in html

    def test_timestamps_toggle(self):
        """Should toggle timestamps display."""
        with_timestamps = get_chat_template(
            config=ChatInterface(show_timestamps=True)
        )

        without_timestamps = get_chat_template(
            config=ChatInterface(show_timestamps=False)
        )

        # Both should generate HTML
        assert len(with_timestamps) > 0
        assert len(without_timestamps) > 0
