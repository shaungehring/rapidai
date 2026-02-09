"""Prompt template management for RapidAI."""

import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
from functools import wraps
from dataclasses import dataclass, field
from datetime import datetime

from .exceptions import RapidAIException


class PromptError(RapidAIException):
    """Prompt-related errors."""

    pass


@dataclass
class PromptVersion:
    """Represents a version of a prompt template."""

    version: str
    template: str
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Prompt:
    """Represents a prompt template with version history."""

    name: str
    template: str
    variables: List[str] = field(default_factory=list)
    versions: List[PromptVersion] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Extract variables from template."""
        if not self.variables:
            self.variables = self._extract_variables(self.template)

    def _extract_variables(self, template: str) -> List[str]:
        """Extract variable names from Jinja2 template."""
        try:
            from jinja2 import Environment, meta

            env = Environment()
            ast = env.parse(template)
            return sorted(meta.find_undeclared_variables(ast))
        except ImportError:
            raise PromptError("jinja2 not installed. Install with: pip install jinja2")

    def render(self, **kwargs: Any) -> str:
        """Render the template with provided variables.

        Args:
            **kwargs: Variables to substitute in the template

        Returns:
            Rendered prompt string

        Raises:
            PromptError: If required variables are missing
        """
        try:
            from jinja2 import Template

            template = Template(self.template)
            return template.render(**kwargs)
        except ImportError:
            raise PromptError("jinja2 not installed. Install with: pip install jinja2")
        except Exception as e:
            raise PromptError(f"Template rendering error: {str(e)}")

    def add_version(self, version: str, template: str, metadata: Dict[str, Any] = None):
        """Add a new version of the prompt.

        Args:
            version: Version identifier
            template: New template string
            metadata: Optional metadata for this version
        """
        prompt_version = PromptVersion(
            version=version, template=template, metadata=metadata or {}
        )
        self.versions.append(prompt_version)

    def get_version(self, version: str) -> Optional[str]:
        """Get a specific version of the prompt template.

        Args:
            version: Version identifier

        Returns:
            Template string for that version, or None if not found
        """
        for v in self.versions:
            if v.version == version:
                return v.template
        return None


class PromptManager:
    """Manages prompt templates with loading, caching, and hot reloading."""

    def __init__(
        self,
        prompt_dir: Optional[Union[str, Path]] = None,
        auto_reload: bool = False,
        reload_interval: int = 5,
    ):
        """Initialize prompt manager.

        Args:
            prompt_dir: Directory containing prompt template files
            auto_reload: Enable hot reloading in development
            reload_interval: Seconds between reload checks
        """
        self.prompt_dir = Path(prompt_dir) if prompt_dir else Path("prompts")
        self.auto_reload = auto_reload
        self.reload_interval = reload_interval

        self._prompts: Dict[str, Prompt] = {}
        self._file_mtimes: Dict[str, float] = {}
        self._last_reload_check: float = 0

        # Load prompts from directory if it exists
        if self.prompt_dir.exists():
            self.load_all()

    def load_all(self) -> None:
        """Load all prompt templates from the prompt directory."""
        if not self.prompt_dir.exists():
            return

        for file_path in self.prompt_dir.glob("*.txt"):
            self.load_from_file(file_path)

        for file_path in self.prompt_dir.glob("*.md"):
            self.load_from_file(file_path)

    def load_from_file(self, file_path: Union[str, Path]) -> Prompt:
        """Load a prompt template from a file.

        Args:
            file_path: Path to the prompt file

        Returns:
            Loaded Prompt object

        File format supports YAML frontmatter for metadata:
            ---
            version: "1.0"
            description: "Customer support prompt"
            ---
            Hello {{ name }}, how can I help you today?
        """
        path = Path(file_path)
        if not path.exists():
            raise PromptError(f"Prompt file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse frontmatter if present
        metadata = {}
        template = content

        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    import yaml

                    metadata = yaml.safe_load(parts[1]) or {}
                    template = parts[2].strip()
                except ImportError:
                    # YAML not installed, just use content as-is
                    pass

        # Use filename (without extension) as prompt name
        name = path.stem

        prompt = Prompt(name=name, template=template, metadata=metadata)
        self._prompts[name] = prompt
        self._file_mtimes[str(path)] = path.stat().st_mtime

        return prompt

    def register(self, name: str, template: str, metadata: Dict[str, Any] = None) -> Prompt:
        """Register a prompt template programmatically.

        Args:
            name: Prompt name
            template: Template string
            metadata: Optional metadata

        Returns:
            Created Prompt object
        """
        prompt = Prompt(name=name, template=template, metadata=metadata or {})
        self._prompts[name] = prompt
        return prompt

    def get(self, name: str, version: Optional[str] = None) -> Optional[Prompt]:
        """Get a prompt by name.

        Args:
            name: Prompt name
            version: Optional specific version to retrieve

        Returns:
            Prompt object, or None if not found
        """
        # Check for hot reload
        if self.auto_reload:
            self._check_reload()

        prompt = self._prompts.get(name)

        if prompt and version:
            # Return a copy with the specific version template
            template = prompt.get_version(version)
            if template:
                return Prompt(
                    name=f"{name}@{version}",
                    template=template,
                    metadata=prompt.metadata,
                )

        return prompt

    def render(self, name: str, **kwargs: Any) -> str:
        """Render a prompt template by name.

        Args:
            name: Prompt name
            **kwargs: Variables to substitute

        Returns:
            Rendered prompt string

        Raises:
            PromptError: If prompt not found or rendering fails
        """
        prompt = self.get(name)
        if not prompt:
            raise PromptError(f"Prompt not found: {name}")

        return prompt.render(**kwargs)

    def _check_reload(self) -> None:
        """Check if any prompt files have been modified and reload them."""
        now = time.time()

        # Only check at the specified interval
        if now - self._last_reload_check < self.reload_interval:
            return

        self._last_reload_check = now

        # Check each tracked file
        for file_path, old_mtime in list(self._file_mtimes.items()):
            path = Path(file_path)
            if path.exists():
                current_mtime = path.stat().st_mtime
                if current_mtime > old_mtime:
                    # File modified, reload it
                    self.load_from_file(path)

    def list_prompts(self) -> List[str]:
        """List all registered prompt names.

        Returns:
            List of prompt names
        """
        return list(self._prompts.keys())


# Global prompt manager instance
_global_manager: Optional[PromptManager] = None


def get_prompt_manager(
    prompt_dir: Optional[Union[str, Path]] = None,
    auto_reload: bool = None,
) -> PromptManager:
    """Get or create the global prompt manager.

    Args:
        prompt_dir: Directory containing prompt templates
        auto_reload: Enable hot reloading (default: based on DEBUG env var)

    Returns:
        PromptManager instance
    """
    global _global_manager

    if _global_manager is None:
        # Auto-detect reload based on environment
        if auto_reload is None:
            auto_reload = os.getenv("DEBUG", "").lower() in ("true", "1", "yes")

        _global_manager = PromptManager(
            prompt_dir=prompt_dir, auto_reload=auto_reload
        )

    return _global_manager


def prompt(
    name: Optional[str] = None,
    template: Optional[str] = None,
    manager: Optional[PromptManager] = None,
) -> Callable:
    """Decorator to load and inject prompt templates into functions.

    Args:
        name: Prompt name (defaults to function name)
        template: Optional inline template string
        manager: Custom PromptManager (default: global manager)

    Returns:
        Decorator function

    Example:
        ```python
        @prompt(name="greeting")
        async def greet(user_name: str, prompt_template: str):
            # prompt_template is automatically injected
            filled_prompt = prompt_template.format(name=user_name)
            return await llm.complete(filled_prompt)

        # Or with inline template
        @prompt(template="Hello {{ name }}, welcome!")
        async def greet(name: str, prompt_template: str):
            return prompt_template
        ```
    """
    prompt_mgr = manager or get_prompt_manager()

    def decorator(func: Callable) -> Callable:
        # Determine prompt name
        prompt_name = name or func.__name__

        # Register inline template if provided
        if template:
            prompt_mgr.register(prompt_name, template)

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Get the prompt
            p = prompt_mgr.get(prompt_name)

            if not p:
                raise PromptError(
                    f"Prompt '{prompt_name}' not found. "
                    f"Create a file at {prompt_mgr.prompt_dir / prompt_name}.txt "
                    f"or pass template parameter to @prompt decorator."
                )

            # Inject prompt template into kwargs
            kwargs["prompt_template"] = p.template
            kwargs["prompt"] = p

            return await func(*args, **kwargs)

        return wrapper

    return decorator
