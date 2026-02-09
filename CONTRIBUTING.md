# Contributing to RapidAI

Thank you for your interest in contributing to RapidAI! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help create a welcoming environment for all contributors
- Assume good intentions

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report:
1. Check existing issues to avoid duplicates
2. Update to the latest version to see if the bug persists
3. Collect information about your environment

When filing a bug report, include:
- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- RapidAI version, Python version, OS
- Minimal code example that reproduces the issue
- Full error message and stack trace

**Example:**
```markdown
**Bug:** Streaming breaks with long responses

**Environment:**
- RapidAI: 0.1.0
- Python: 3.11.5
- OS: macOS 14.0

**To Reproduce:**
```python
from rapidai import App, LLM, stream

app = App()
llm = LLM("gpt-4")

@app.route("/chat")
@stream
async def chat(message: str):
    async for chunk in llm.chat(message):
        yield chunk
```

**Error:**
```
RuntimeError: generator didn't stop after throw()
...
```

**Expected:** Stream should complete cleanly
**Actual:** Throws exception after ~100 chunks
```

### Suggesting Features

We love feature suggestions! Please:
1. Check if it's already been suggested
2. Explain the use case clearly
3. Describe how it fits RapidAI's vision
4. Provide example API if possible

**Template:**
```markdown
**Feature:** Add support for Gemini models

**Use Case:** 
Many developers want to use Google's Gemini models for cost optimization.

**Proposed API:**
```python
llm = LLM("gemini-pro", api_key=...)
```

**Benefits:**
- More provider options
- Cost optimization
- Matches existing pattern
```

### Contributing Code

#### Getting Started

1. **Fork the repository**
```bash
git clone https://github.com/yourusername/rapidai.git
cd rapidai
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install development dependencies**
```bash
pip install -e ".[dev]"
```

4. **Install pre-commit hooks**
```bash
pre-commit install
```

#### Development Workflow

1. **Create a feature branch**
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

2. **Write tests first (TDD preferred)**
```python
# tests/test_your_feature.py
import pytest
from rapidai import App

@pytest.mark.asyncio
async def test_your_feature():
    app = App()
    # Test implementation
    assert True
```

3. **Implement your feature**
```python
# rapidai/your_feature.py
async def your_feature():
    """Your implementation."""
    pass
```

4. **Run tests**
```bash
pytest
pytest --cov=rapidai  # With coverage
```

5. **Type check**
```bash
mypy rapidai
```

6. **Lint and format**
```bash
ruff check rapidai
ruff format rapidai
```

7. **Commit with clear messages**
```bash
git add .
git commit -m "feat: add support for Gemini models

- Add GeminiAdapter class
- Update LLM factory to support gemini-pro
- Add tests for Gemini integration
- Update documentation
"
```

#### Commit Message Convention

We use conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `chore:` Maintenance tasks

**Examples:**
```
feat: add semantic caching support
fix: resolve streaming timeout issue
docs: update RAG example in API_EXAMPLES.md
test: add integration tests for memory system
refactor: simplify LLM adapter interface
```

#### Pull Request Process

1. **Update documentation**
   - Add docstrings to new functions/classes
   - Update relevant .md files
   - Add examples if introducing new features

2. **Ensure tests pass**
   ```bash
   pytest
   mypy rapidai
   ruff check rapidai
   ```

3. **Update CHANGELOG.md**
   ```markdown
   ## [Unreleased]
   ### Added
   - Support for Gemini models
   
   ### Fixed
   - Streaming timeout issue (#123)
   ```

4. **Create pull request**
   - Clear title describing the change
   - Reference related issues
   - Describe what was changed and why
   - Include screenshots/examples if relevant

5. **PR Template:**
   ```markdown
   ## Description
   Adds support for Google's Gemini models.
   
   ## Related Issues
   Closes #45
   
   ## Changes
   - Added GeminiAdapter class
   - Updated LLM factory
   - Added tests
   - Updated docs
   
   ## Testing
   - [x] Unit tests pass
   - [x] Integration tests pass
   - [x] Manual testing completed
   
   ## Checklist
   - [x] Tests added/updated
   - [x] Documentation updated
   - [x] CHANGELOG.md updated
   - [x] Type hints added
   - [x] Code formatted
   ```

## Development Guidelines

### Code Style

- Follow PEP 8
- Use type hints everywhere
- Maximum line length: 100 characters
- Use async/await for IO operations
- Prefer explicit over implicit

**Good:**
```python
async def chat(
    message: str,
    history: list[dict[str, str]] | None = None,
    temperature: float = 0.7
) -> str:
    """Generate a chat response.
    
    Args:
        message: User message
        history: Previous conversation
        temperature: Sampling temperature
        
    Returns:
        Generated response
    """
    if history is None:
        history = []
    
    # Implementation
    return response
```

**Bad:**
```python
def chat(msg, hist=None, temp=0.7):  # Missing async, types, docstring
    hist = hist or []
    return response
```

### Testing Guidelines

- Write tests for all new code
- Aim for >80% coverage
- Use descriptive test names
- Test both success and failure cases
- Mock external API calls

**Structure:**
```python
# tests/test_feature.py
import pytest
from unittest.mock import AsyncMock, patch
from rapidai import YourFeature

@pytest.fixture
def feature():
    """Create feature instance for testing."""
    return YourFeature()

@pytest.mark.asyncio
async def test_feature_success(feature):
    """Test successful operation."""
    result = await feature.do_something()
    assert result == expected

@pytest.mark.asyncio
async def test_feature_failure(feature):
    """Test error handling."""
    with pytest.raises(ValueError):
        await feature.do_something(invalid_input)

@pytest.mark.asyncio
@patch("rapidai.external_api")
async def test_with_mock(mock_api, feature):
    """Test with mocked external dependency."""
    mock_api.return_value = AsyncMock(return_value="mocked")
    result = await feature.do_something()
    assert result == "mocked"
```

### Documentation Guidelines

Every public function/class needs:

```python
async def function_name(param: str, optional: int = 0) -> dict[str, Any]:
    """One-line summary.
    
    Longer description explaining what this does, why it exists,
    and any important details about behavior.
    
    Args:
        param: Description of param
        optional: Description of optional param (default: 0)
    
    Returns:
        Dictionary containing result data
        
    Raises:
        ValueError: If param is invalid
        APIError: If API call fails
        
    Example:
        >>> result = await function_name("test")
        >>> print(result["key"])
        'value'
    """
```

### Architecture Principles

When adding features, follow these principles:

1. **Keep it simple** - Prefer simple solutions over clever ones
2. **Async by default** - All IO should be async
3. **Type safe** - Use Pydantic for validation
4. **Testable** - Design for easy testing
5. **Documented** - Code should be self-documenting
6. **Provider agnostic** - Don't lock into specific vendors

### Adding New LLM Providers

To add a new provider:

1. **Create adapter class**
```python
# rapidai/llm/newprovider.py
from rapidai.llm.base import BaseLLM

class NewProviderLLM(BaseLLM):
    async def chat(self, message: str, **kwargs) -> str:
        # Implementation
        pass
    
    async def complete(self, prompt: str, **kwargs) -> str:
        # Implementation
        pass
```

2. **Register in factory**
```python
# rapidai/llm/__init__.py
def create_llm(provider: str, **kwargs) -> BaseLLM:
    providers = {
        "openai": OpenAILLM,
        "anthropic": AnthropicLLM,
        "newprovider": NewProviderLLM,  # Add here
    }
    return providers[provider](**kwargs)
```

3. **Add tests**
```python
# tests/llm/test_newprovider.py
@pytest.mark.asyncio
async def test_newprovider_chat():
    llm = NewProviderLLM(api_key="test")
    response = await llm.chat("Hello")
    assert isinstance(response, str)
```

4. **Update docs**
```markdown
# docs/providers.md
## NewProvider

```python
from rapidai import LLM

llm = LLM("newprovider-model", api_key="...")
```
```

## Review Process

Maintainers will review PRs for:
- Code quality and style
- Test coverage
- Documentation completeness
- Performance implications
- Breaking changes
- Security considerations

We aim to review PRs within 2-3 days. If urgent, mention in PR description.

## Questions?

- Open a discussion on GitHub
- Check existing issues and discussions
- Read documentation at rapidai.dev

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to RapidAI! 🚀
