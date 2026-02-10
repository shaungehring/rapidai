# Installation

## Requirements

!!! info "Python Version"
    RapidAI requires **Python 3.9 or higher**

## Install RapidAI

=== "pip"

    ```bash
    pip install rapidai
    ```

=== "With Anthropic"

    ```bash
    pip install rapidai[anthropic]
    ```

=== "With OpenAI"

    ```bash
    pip install rapidai[openai]
    ```

=== "With All Features"

    ```bash
    pip install rapidai[all]
    ```

=== "For Development"

    ```bash
    git clone https://github.com/shaungehring/rapidai.git
    cd rapidai
    pip install -e ".[dev]"
    ```

## Optional Dependencies

RapidAI has several optional dependency groups:

| Extra | Description | Install Command |
|-------|-------------|-----------------|
| `anthropic` | Anthropic Claude support | `pip install rapidai[anthropic]` |
| `openai` | OpenAI GPT support | `pip install rapidai[openai]` |
| `cohere` | Cohere support | `pip install rapidai[cohere]` |
| `rag` | RAG features (vector DB, embeddings) | `pip install rapidai[rag]` |
| `redis` | Redis cache/memory backend | `pip install rapidai[redis]` |
| `postgres` | PostgreSQL memory backend | `pip install rapidai[postgres]` |
| `all` | All optional features | `pip install rapidai[all]` |
| `dev` | Development tools | `pip install rapidai[dev]` |

## Setup API Keys

Create a `.env` file in your project root:

```bash title=".env"
# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# OpenAI (GPT)
OPENAI_API_KEY=sk-your-key-here

# Cohere
COHERE_API_KEY=your-key-here

# Optional: Default settings
RAPIDAI_LLM_PROVIDER=anthropic
RAPIDAI_LLM_MODEL=claude-3-haiku-20240307
RAPIDAI_LLM_TEMPERATURE=0.7
RAPIDAI_LLM_MAX_TOKENS=4000
```

!!! warning "Keep Your Keys Secret"
    Never commit `.env` files to version control. Add `.env` to your `.gitignore`.

## Verify Installation

```python title="test_install.py"
import rapidai

print(f"RapidAI version: {rapidai.__version__}")
print("✓ Installation successful!")
```

<div class="command">python test_install.py</div>

Expected output:
```
RapidAI version: 0.1.0
✓ Installation successful!
```

## Get API Keys

### Anthropic (Claude)

1. Visit [console.anthropic.com](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new API key
5. Copy and add to your `.env` file

### OpenAI (GPT)

1. Visit [platform.openai.com](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new API key
5. Copy and add to your `.env` file

### Cohere

1. Visit [dashboard.cohere.com](https://dashboard.cohere.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Copy your API key
5. Add to your `.env` file

## Troubleshooting

### ModuleNotFoundError

If you get `ModuleNotFoundError: No module named 'rapidai'`:

1. Check your Python version: `python --version`
2. Verify installation: `pip list | grep rapidai`
3. Try reinstalling: `pip install --force-reinstall rapidai`

### Import Errors

If you get import errors for optional dependencies:

```python
# ❌ This will fail if anthropic not installed
from rapidai import LLM
llm = LLM("claude-3-haiku-20240307")
```

Solution:
```bash
pip install rapidai[anthropic]
```

### API Key Not Found

If you get "API key not found" errors:

1. Check `.env` file exists in project root
2. Verify key names match: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`
3. No quotes around keys in `.env`
4. No spaces around `=` in `.env`

## Next Steps

- [First Steps](first-steps.html) - Create your first RapidAI app
- [Quick Start](quickstart.html) - Learn the basics
- [Tutorial](../tutorial/intro.html) - Step-by-step guide

---

!!! success "Ready to Go!"
    Installation complete! Let's build something amazing.
