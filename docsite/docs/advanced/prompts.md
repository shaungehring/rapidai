# Prompt Management

RapidAI provides a powerful prompt management system with Jinja2 templating, version tracking, and hot reloading for development.

## Quick Start

```python
from rapidai import App, LLM
from rapidai.prompts import PromptManager

app = App()
llm = LLM("claude-3-haiku-20240307")

# Initialize prompt manager
prompts = PromptManager(prompt_dir="prompts", auto_reload=True)

@app.route("/greet", methods=["POST"])
async def greet(name: str):
    # Render prompt with variables
    prompt_text = prompts.render("greeting", name=name)
    response = await llm.complete(prompt_text)
    return {"response": response}
```

Create `prompts/greeting.txt`:

```jinja2
Hello {{ name }}! How can I assist you today?
```

## Features

- **Jinja2 Templates**: Full Jinja2 support with variables, loops, conditionals
- **Hot Reloading**: Auto-reload prompts in development when files change
- **Version Tracking**: Track and retrieve different versions of prompts
- **Frontmatter Metadata**: YAML frontmatter for prompt metadata
- **@prompt Decorator**: Automatic prompt injection into route handlers
- **Programmatic Registration**: Register prompts in code without files

## PromptManager

### Initialization

```python
from rapidai.prompts import PromptManager

# Basic usage
prompts = PromptManager()

# Custom directory with hot reloading
prompts = PromptManager(
    prompt_dir="my_prompts",
    auto_reload=True,           # Enable hot reloading
    reload_interval=5           # Check for changes every 5 seconds
)
```

### Loading from Files

The PromptManager automatically loads `.txt` and `.md` files from the prompt directory:

```text
prompts/
  ├── greeting.txt
  ├── analyze.txt
  └── support.md
```

Access prompts by filename (without extension):

```python
greeting_prompt = prompts.get("greeting")
analyze_prompt = prompts.get("analyze")
support_prompt = prompts.get("support")
```

### YAML Frontmatter

Add metadata to prompts using YAML frontmatter:

```yaml
---
version: "1.0"
description: "Customer support prompt"
author: "Support Team"
tags: ["support", "customer-service"]
---
Hello {{ customer_name }},

Thank you for contacting support. How can I help you today?
```

Access metadata:

```python
prompt = prompts.get("support")
print(prompt.metadata)
# {"version": "1.0", "description": "Customer support prompt", ...}
```

### Programmatic Registration

Register prompts in code without files:

```python
prompts.register(
    name="dynamic_prompt",
    template="Analyze this: {{ text }}",
    metadata={"type": "analysis"}
)

# Use it
result = prompts.render("dynamic_prompt", text="Sample content")
```

## Templates with Jinja2

### Variables

```python
template = "Hello {{ name }}, you have {{ count }} messages."

prompt = prompts.register("greeting", template)
result = prompt.render(name="Alice", count=5)
# "Hello Alice, you have 5 messages."
```

### Conditionals

```python
template = """
{% if premium %}
Welcome, premium member {{ name }}!
{% else %}
Welcome {{ name }}! Upgrade to premium for more features.
{% endif %}
"""

prompts.register("welcome", template)
result = prompts.render("welcome", name="Bob", premium=True)
```

### Loops

```python
template = """
Topics to cover:
{% for topic in topics %}
- {{ topic }}
{% endfor %}
"""

prompts.register("topics", template)
result = prompts.render("topics", topics=["AI", "ML", "NLP"])
```

### Filters

```python
template = "User: {{ name | upper }}"

prompts.register("user", template)
result = prompts.render("user", name="alice")
# "User: ALICE"
```

## Version Tracking

Track multiple versions of prompts:

```python
prompt = prompts.get("greeting")

# Add a new version
prompt.add_version(
    version="2.0",
    template="Hi {{ name }}! What can I do for you?",
    metadata={"changelog": "More casual tone"}
)

# Get specific version
v1_prompt = prompts.get("greeting", version="1.0")
v2_prompt = prompts.get("greeting", version="2.0")
```

## Hot Reloading

Enable hot reloading in development:

```python
prompts = PromptManager(
    prompt_dir="prompts",
    auto_reload=True,
    reload_interval=5  # Check every 5 seconds
)
```

When `auto_reload=True`, the manager checks for file changes at the specified interval and reloads modified prompts automatically.

Environment-based auto-reload:

```python
from rapidai.prompts import get_prompt_manager

# Auto-enables reload if DEBUG=true in environment
prompts = get_prompt_manager()
```

## @prompt Decorator

Automatically inject prompts into route handlers:

```python
from rapidai import App, LLM
from rapidai.prompts import prompt, PromptManager

app = App()
llm = LLM("claude-3-haiku-20240307")
prompt_manager = PromptManager(auto_reload=True)

# Using inline template
@app.route("/greet", methods=["POST"])
@prompt(template="Hello {{ name }}! How can I help?", manager=prompt_manager)
async def greet(name: str, prompt_template: str, prompt):
    # prompt_template and prompt are automatically injected
    filled = prompt.render(name=name)
    response = await llm.complete(filled)
    return {"response": response}

# Using file-based prompt
@app.route("/analyze", methods=["POST"])
@prompt(name="analyze", manager=prompt_manager)
async def analyze(text: str, prompt_template: str, prompt):
    filled = prompt.render(text=text)
    response = await llm.complete(filled)
    return {"analysis": response}
```

The decorator automatically injects:

- `prompt_template`: The raw template string
- `prompt`: The Prompt object with `render()` method and metadata

## Working with Prompts

### Extract Variables

```python
prompt = prompts.get("greeting")
print(prompt.variables)
# ["name", "count"]
```

Variables are automatically extracted from Jinja2 templates.

### Render with Variables

```python
prompt = prompts.get("greeting")
result = prompt.render(name="Alice", count=5)
```

Missing required variables will raise a `PromptError`.

### List Available Prompts

```python
prompt_names = prompts.list_prompts()
print(prompt_names)
# ["greeting", "analyze", "support"]
```

## Complete Example: Customer Support Bot

```python
from rapidai import App, LLM
from rapidai.prompts import prompt, PromptManager

app = App(title="Support Bot")
llm = LLM("claude-3-haiku-20240307")
prompts = PromptManager(prompt_dir="prompts", auto_reload=True)

@app.route("/support/greeting", methods=["POST"])
@prompt(
    template="""Hello {{ customer_name }}!

I'm here to help with your {{ product }} inquiry.
{% if is_premium %}
As a premium customer, you have priority support access.
{% endif %}

How can I assist you today?""",
    manager=prompts
)
async def support_greeting(
    customer_name: str,
    product: str,
    is_premium: bool = False,
    prompt_template: str = None,
    prompt = None
):
    filled = prompt.render(
        customer_name=customer_name,
        product=product,
        is_premium=is_premium
    )
    response = await llm.complete(filled)
    return {"greeting": response}

@app.route("/support/analyze", methods=["POST"])
@prompt(
    template="""Analyze this customer support ticket and provide:
1. Issue category (technical/billing/general)
2. Urgency level (low/medium/high)
3. Suggested response approach

Ticket: {{ ticket_text }}

Analysis:""",
    manager=prompts
)
async def analyze_ticket(ticket_text: str, prompt_template: str, prompt):
    filled = prompt.render(ticket_text=ticket_text)
    analysis = await llm.complete(filled)
    return {"analysis": analysis}

if __name__ == "__main__":
    app.run(port=8000)
```

Test the support bot:

```bash
# Greeting
curl -X POST http://localhost:8000/support/greeting \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Alice",
    "product": "RapidAI Premium",
    "is_premium": true
  }'

# Analyze ticket
curl -X POST http://localhost:8000/support/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_text": "I cannot access my account after updating my password"
  }'
```

## Best Practices

### 1. Organize Prompts by Purpose

```text
prompts/
  ├── greetings/
  │   ├── welcome.txt
  │   └── farewell.txt
  ├── analysis/
  │   ├── sentiment.txt
  │   └── topics.txt
  └── support/
      ├── ticket_analysis.txt
      └── response_template.txt
```

### 2. Use Metadata for Tracking

```yaml
---
version: "2.1"
created: "2024-01-15"
modified: "2024-02-01"
author: "AI Team"
performance: "95% satisfaction"
---
Your prompt template here
```

### 3. Version Control Prompts

```python
# Track changes
prompt.add_version(
    version="2.0",
    template=new_template,
    metadata={
        "changelog": "Improved clarity",
        "tested_on": "2024-02-01"
    }
)
```

### 4. Use Hot Reload in Development Only

```python
import os

prompts = PromptManager(
    auto_reload=os.getenv("ENV") == "development"
)
```

### 5. Validate Variables

```python
prompt = prompts.get("greeting")

# Check required variables
required_vars = prompt.variables
print(f"Required: {required_vars}")

# Ensure all are provided
user_vars = {"name": "Alice"}
missing = set(required_vars) - set(user_vars.keys())
if missing:
    raise ValueError(f"Missing variables: {missing}")
```

### 6. Cache Rendered Prompts

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_rendered_prompt(name: str, **kwargs):
    prompt = prompts.get(name)
    return prompt.render(**kwargs)
```

### 7. Use Descriptive Names

```python
# Good
prompts.register("customer_support_greeting", template)
prompts.register("sentiment_analysis_system_prompt", template)

# Avoid
prompts.register("p1", template)
prompts.register("temp", template)
```

## Configuration

Configure prompts via environment variables:

```bash
# Prompt directory
export RAPIDAI_PROMPT_DIR="./my_prompts"

# Enable auto-reload
export DEBUG=true
```

Or in code:

```python
from rapidai.prompts import PromptManager

prompts = PromptManager(
    prompt_dir="prompts",
    auto_reload=True,
    reload_interval=10
)
```

## Error Handling

```python
from rapidai.prompts import PromptError

try:
    prompt = prompts.get("missing_prompt")
    if not prompt:
        raise PromptError("Prompt not found")

    result = prompt.render(name="Alice")
except PromptError as e:
    print(f"Prompt error: {e}")
```

## Next Steps

- See [API Reference](../reference/prompts.html) for complete API documentation
- Check [examples/prompt_decorator.py](https://github.com/yourusername/rapidai/blob/main/examples/prompt_decorator.py) for more examples
- Learn about [RAG](rag.html) for combining prompts with retrieved context
