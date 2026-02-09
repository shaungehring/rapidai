"""Tests for prompt management system."""

import pytest
from pathlib import Path
import tempfile
import time

from rapidai.prompts import (
    Prompt,
    PromptManager,
    PromptError,
    prompt,
    get_prompt_manager,
)


def test_prompt_creation():
    """Test basic prompt creation."""
    p = Prompt(
        name="greeting",
        template="Hello {{ name }}, welcome to {{ app }}!",
    )

    assert p.name == "greeting"
    assert "name" in p.variables
    assert "app" in p.variables


def test_prompt_render():
    """Test prompt rendering."""
    p = Prompt(
        name="greeting",
        template="Hello {{ name }}, welcome to {{ app }}!",
    )

    result = p.render(name="Alice", app="RapidAI")
    assert result == "Hello Alice, welcome to RapidAI!"


def test_prompt_render_missing_variable():
    """Test rendering with missing variable."""
    p = Prompt(
        name="greeting",
        template="Hello {{ name }}!",
    )

    # Jinja2 doesn't error on missing variables by default, just renders empty
    result = p.render()
    assert result == "Hello !"


def test_prompt_versioning():
    """Test prompt version tracking."""
    p = Prompt(
        name="greeting",
        template="Hello {{ name }}!",
    )

    # Add versions
    p.add_version("1.0", "Hello {{ name }}!", metadata={"author": "Alice"})
    p.add_version("2.0", "Hi {{ name }}, welcome!", metadata={"author": "Bob"})

    # Get specific version
    v1_template = p.get_version("1.0")
    assert v1_template == "Hello {{ name }}!"

    v2_template = p.get_version("2.0")
    assert v2_template == "Hi {{ name }}, welcome!"

    # Non-existent version
    assert p.get_version("3.0") is None


def test_prompt_manager_register():
    """Test registering prompts programmatically."""
    manager = PromptManager()

    prompt_obj = manager.register(
        "greeting",
        "Hello {{ name }}!",
        metadata={"description": "Simple greeting"},
    )

    assert prompt_obj.name == "greeting"
    assert manager.get("greeting") is not None


def test_prompt_manager_render():
    """Test rendering via manager."""
    manager = PromptManager()
    manager.register("greeting", "Hello {{ name }}!")

    result = manager.render("greeting", name="Alice")
    assert result == "Hello Alice!"


def test_prompt_manager_render_not_found():
    """Test rendering non-existent prompt."""
    manager = PromptManager()

    with pytest.raises(PromptError, match="Prompt not found"):
        manager.render("nonexistent", name="Alice")


def test_prompt_manager_list():
    """Test listing prompts."""
    manager = PromptManager()
    manager.register("greeting", "Hello!")
    manager.register("farewell", "Goodbye!")

    prompts = manager.list_prompts()
    assert "greeting" in prompts
    assert "farewell" in prompts


def test_prompt_manager_load_from_file():
    """Test loading prompts from files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a prompt file
        prompt_file = Path(tmpdir) / "greeting.txt"
        prompt_file.write_text("Hello {{ name }}, welcome!")

        manager = PromptManager(prompt_dir=tmpdir)
        manager.load_all()

        prompt_obj = manager.get("greeting")
        assert prompt_obj is not None
        assert prompt_obj.template == "Hello {{ name }}, welcome!"


def test_prompt_manager_load_with_frontmatter():
    """Test loading prompts with YAML frontmatter."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a prompt file with frontmatter
        prompt_file = Path(tmpdir) / "greeting.txt"
        prompt_file.write_text("""---
version: "1.0"
description: "Customer greeting"
---
Hello {{ name }}, how can I help you today?""")

        manager = PromptManager(prompt_dir=tmpdir)
        manager.load_all()

        prompt_obj = manager.get("greeting")
        assert prompt_obj is not None
        assert prompt_obj.template == "Hello {{ name }}, how can I help you today?"
        assert prompt_obj.metadata.get("version") == "1.0"
        assert prompt_obj.metadata.get("description") == "Customer greeting"


def test_prompt_manager_hot_reload():
    """Test hot reloading of prompt files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create initial prompt file
        prompt_file = Path(tmpdir) / "greeting.txt"
        prompt_file.write_text("Hello {{ name }}!")

        manager = PromptManager(prompt_dir=tmpdir, auto_reload=True, reload_interval=1)
        manager.load_all()

        # Initial version
        prompt_obj = manager.get("greeting")
        assert prompt_obj.template == "Hello {{ name }}!"

        # Wait a bit and modify the file
        time.sleep(1.5)
        prompt_file.write_text("Hi {{ name }}, welcome!")

        # Force reload check
        manager._last_reload_check = 0
        prompt_obj = manager.get("greeting")
        assert prompt_obj.template == "Hi {{ name }}, welcome!"


@pytest.mark.asyncio
async def test_prompt_decorator():
    """Test @prompt decorator."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a prompt file
        prompt_file = Path(tmpdir) / "test_greeting.txt"
        prompt_file.write_text("Hello {{ name }}!")

        manager = PromptManager(prompt_dir=tmpdir)
        manager.load_all()

        @prompt(name="test_greeting", manager=manager)
        async def greet(name: str, prompt_template: str):
            return prompt_template

        result = await greet(name="Alice")
        assert "Hello" in result


@pytest.mark.asyncio
async def test_prompt_decorator_inline():
    """Test @prompt decorator with inline template."""
    manager = PromptManager()

    @prompt(template="Hello {{ name }}!", manager=manager)
    async def greet(name: str, prompt_template: str):
        from jinja2 import Template

        return Template(prompt_template).render(name=name)

    result = await greet(name="Alice")
    assert result == "Hello Alice!"


@pytest.mark.asyncio
async def test_prompt_decorator_not_found():
    """Test @prompt decorator with non-existent prompt."""
    manager = PromptManager()

    @prompt(name="nonexistent", manager=manager)
    async def greet(name: str, prompt_template: str):
        return prompt_template

    with pytest.raises(PromptError, match="Prompt 'nonexistent' not found"):
        await greet(name="Alice")


def test_get_global_prompt_manager():
    """Test getting global prompt manager."""
    manager1 = get_prompt_manager()
    manager2 = get_prompt_manager()

    # Should return the same instance
    assert manager1 is manager2
