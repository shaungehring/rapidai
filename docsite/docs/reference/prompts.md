# Prompts API Reference

Complete API reference for RapidAI's prompt management system.

## Classes

### PromptManager

Manages prompt templates with loading, caching, and hot reloading.

```python
class PromptManager:
    def __init__(
        self,
        prompt_dir: Optional[Union[str, Path]] = None,
        auto_reload: bool = False,
        reload_interval: int = 5,
    )
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt_dir` | `str \| Path` | `"prompts"` | Directory containing prompt template files |
| `auto_reload` | `bool` | `False` | Enable hot reloading in development |
| `reload_interval` | `int` | `5` | Seconds between reload checks |

**Methods:**

#### `load_all()`

Load all prompt templates from the prompt directory.

```python
prompts.load_all()
```

Loads all `.txt` and `.md` files from `prompt_dir`.

#### `load_from_file(file_path)`

Load a prompt template from a file.

```python
prompt = prompts.load_from_file("prompts/greeting.txt")
```

**Parameters:**

- `file_path` (`str | Path`) - Path to the prompt file

**Returns:** `Prompt` - Loaded Prompt object

**File Format:**

Supports YAML frontmatter for metadata:

```yaml
---
version: "1.0"
description: "Customer support prompt"
---
Hello {{ name }}, how can I help?
```

#### `register(name, template, metadata)`

Register a prompt template programmatically.

```python
prompt = prompts.register(
    name="greeting",
    template="Hello {{ name }}!",
    metadata={"version": "1.0"}
)
```

**Parameters:**

- `name` (`str`) - Prompt name
- `template` (`str`) - Template string
- `metadata` (`Dict[str, Any]`, optional) - Optional metadata

**Returns:** `Prompt` - Created Prompt object

#### `get(name, version)`

Get a prompt by name.

```python
prompt = prompts.get("greeting")
versioned_prompt = prompts.get("greeting", version="2.0")
```

**Parameters:**

- `name` (`str`) - Prompt name
- `version` (`str`, optional) - Optional specific version to retrieve

**Returns:** `Prompt | None` - Prompt object, or None if not found

If `auto_reload=True`, checks for file changes before retrieving.

#### `render(name, **kwargs)`

Render a prompt template by name.

```python
result = prompts.render("greeting", name="Alice", count=5)
```

**Parameters:**

- `name` (`str`) - Prompt name
- `**kwargs` - Variables to substitute in the template

**Returns:** `str` - Rendered prompt string

**Raises:** `PromptError` - If prompt not found or rendering fails

#### `list_prompts()`

List all registered prompt names.

```python
names = prompts.list_prompts()
# ["greeting", "analyze", "support"]
```

**Returns:** `List[str]` - List of prompt names

### Prompt

Represents a prompt template with version history.

```python
@dataclass
class Prompt:
    name: str
    template: str
    variables: List[str]
    versions: List[PromptVersion]
    metadata: Dict[str, Any]
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Prompt name |
| `template` | `str` | Template string |
| `variables` | `List[str]` | Extracted variable names from template |
| `versions` | `List[PromptVersion]` | Version history |
| `metadata` | `Dict[str, Any]` | Metadata dictionary |

**Methods:**

#### `render(**kwargs)`

Render the template with provided variables.

```python
prompt = prompts.get("greeting")
result = prompt.render(name="Alice", count=5)
```

**Parameters:**

- `**kwargs` - Variables to substitute in the template

**Returns:** `str` - Rendered prompt string

**Raises:** `PromptError` - If required variables are missing or rendering fails

#### `add_version(version, template, metadata)`

Add a new version of the prompt.

```python
prompt.add_version(
    version="2.0",
    template="Hi {{ name }}! What's up?",
    metadata={"changelog": "More casual"}
)
```

**Parameters:**

- `version` (`str`) - Version identifier
- `template` (`str`) - New template string
- `metadata` (`Dict[str, Any]`, optional) - Optional metadata for this version

#### `get_version(version)`

Get a specific version of the prompt template.

```python
template = prompt.get_version("2.0")
```

**Parameters:**

- `version` (`str`) - Version identifier

**Returns:** `str | None` - Template string for that version, or None if not found

### PromptVersion

Represents a version of a prompt template.

```python
@dataclass
class PromptVersion:
    version: str
    template: str
    created_at: datetime
    metadata: Dict[str, Any]
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `version` | `str` | Version identifier |
| `template` | `str` | Template string for this version |
| `created_at` | `datetime` | Creation timestamp |
| `metadata` | `Dict[str, Any]` | Version-specific metadata |

## Functions

### get_prompt_manager(prompt_dir, auto_reload)

Get or create the global prompt manager.

```python
from rapidai.prompts import get_prompt_manager

prompts = get_prompt_manager()
```

**Parameters:**

- `prompt_dir` (`str | Path`, optional) - Directory containing prompt templates
- `auto_reload` (`bool`, optional) - Enable hot reloading (default: based on `DEBUG` env var)

**Returns:** `PromptManager` - PromptManager instance

Auto-detects reload based on environment:

```python
# Auto-enables if DEBUG=true, DEBUG=1, or DEBUG=yes
prompts = get_prompt_manager()
```

## Decorators

### @prompt(name, template, manager)

Decorator to load and inject prompt templates into functions.

```python
from rapidai.prompts import prompt

@prompt(name="greeting")
async def greet(user_name: str, prompt_template: str, prompt):
    # prompt_template and prompt are automatically injected
    filled = prompt.render(name=user_name)
    return await llm.complete(filled)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | Function name | Prompt name (defaults to function name) |
| `template` | `str` | `None` | Optional inline template string |
| `manager` | `PromptManager` | Global manager | Custom PromptManager instance |

**Injected Parameters:**

The decorator injects two parameters into the wrapped function:

- `prompt_template` (`str`) - The raw template string
- `prompt` (`Prompt`) - The Prompt object with `render()` method and metadata

**Usage Examples:**

**With inline template:**

```python
@prompt(template="Hello {{ name }}!")
async def greet(name: str, prompt_template: str, prompt):
    return prompt.render(name=name)
```

**With file-based prompt:**

```python
@prompt(name="analyze")  # Loads from prompts/analyze.txt
async def analyze(text: str, prompt_template: str, prompt):
    return prompt.render(text=text)
```

**With custom manager:**

```python
custom_manager = PromptManager(prompt_dir="my_prompts")

@prompt(manager=custom_manager)
async def process(data: str, prompt_template: str, prompt):
    return prompt.render(data=data)
```

## Exceptions

### PromptError

Base exception for prompt-related errors.

```python
from rapidai.prompts import PromptError

try:
    result = prompts.render("missing", name="test")
except PromptError as e:
    print(f"Error: {e}")
```

Raised in these scenarios:

- Prompt not found
- Template rendering error
- Required variables missing
- Jinja2 not installed

## Configuration

### Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `RAPIDAI_PROMPT_DIR` | `str` | `"./prompts"` | Prompt directory path |
| `DEBUG` | `bool` | `False` | Enable auto-reload (accepts: `true`, `1`, `yes`) |

**Example:**

```bash
export RAPIDAI_PROMPT_DIR="./my_prompts"
export DEBUG=true
```

## Type Definitions

### Template Variables

Variables in Jinja2 templates are automatically extracted:

```python
template = "Hello {{ name }}, you have {{ count }} messages"
prompt = Prompt(name="greeting", template=template)

print(prompt.variables)
# ["count", "name"]  # Alphabetically sorted
```

### Metadata Structure

```python
metadata = {
    "version": "1.0",
    "description": "Customer greeting",
    "author": "Support Team",
    "tags": ["greeting", "support"],
    "created": "2024-01-15",
    "performance": {"satisfaction": 0.95}
}
```

## Complete Example

```python
from rapidai import App, LLM
from rapidai.prompts import PromptManager, prompt, PromptError

# Initialize
app = App()
llm = LLM("claude-3-haiku-20240307")
prompts = PromptManager(prompt_dir="prompts", auto_reload=True)

# Register programmatic prompt
prompts.register(
    name="analyze",
    template="""Analyze: {{ text }}
Provide:
1. Summary
2. Key points
3. Sentiment""",
    metadata={"type": "analysis"}
)

# File-based prompt with decorator
@app.route("/greet", methods=["POST"])
@prompt(template="Hello {{ name }}! How can I help?", manager=prompts)
async def greet(name: str, prompt_template: str, prompt):
    try:
        filled = prompt.render(name=name)
        response = await llm.complete(filled)
        return {
            "response": response,
            "variables": prompt.variables,
            "metadata": prompt.metadata
        }
    except PromptError as e:
        return {"error": str(e)}, 400

# Programmatic usage
@app.route("/analyze", methods=["POST"])
async def analyze(text: str):
    try:
        prompt_obj = prompts.get("analyze")
        if not prompt_obj:
            return {"error": "Prompt not found"}, 404

        filled = prompt_obj.render(text=text)
        response = await llm.complete(filled)

        return {
            "analysis": response,
            "prompt_vars": prompt_obj.variables
        }
    except PromptError as e:
        return {"error": str(e)}, 400

# Version management
@app.route("/prompt/version", methods=["POST"])
async def add_prompt_version(name: str, version: str, template: str):
    prompt_obj = prompts.get(name)
    if not prompt_obj:
        return {"error": "Prompt not found"}, 404

    prompt_obj.add_version(version, template)
    return {"success": True, "versions": len(prompt_obj.versions)}

if __name__ == "__main__":
    app.run(port=8000)
```

## See Also

- [Prompt Management Guide](../advanced/prompts.md) - Comprehensive usage guide
- [RAG API Reference](rag.md) - Combine prompts with retrieval
- [LLM API Reference](llm.md) - LLM integration
