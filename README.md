# RapidAI 🚀

**The Python framework for lightning-fast AI prototypes**

RapidAI is designed for one thing: getting from idea to deployed AI application in under an hour. When your boss asks you to POC the latest AI tool, this is the framework you reach for.

## Vision

A web framework that bridges the gap between Flask's simplicity and Django's batteries-included approach, but optimized specifically for modern AI development. Think of it as "the Rails of AI apps" - convention over configuration, but for LLM-powered applications.

## Core Differentiators

- **Zero-config LLM integration** - Built-in clients for OpenAI, Anthropic, Cohere, local models with unified interface
- **Streaming by default** - SSE/WebSocket streaming built into routes, not bolted on
- **Prompt management** - Version, test, and swap prompts without code changes
- **Smart caching** - LLM response caching that understands semantic similarity
- **Built-in eval tools** - A/B test prompts, track token usage, log conversations
- **Modern UI components** - Pre-built chat interfaces, streaming text displays, file upload handlers
- **RAG in minutes** - Document parsing, vector DB, and retrieval with 2-line setup

## Quick Start

```python
from rapidai import App, LLM, stream

app = App()
llm = LLM("claude-sonnet-4")

@app.route("/chat", methods=["POST"])
@stream
async def chat(message: str):
    async for chunk in llm.chat(message):
        yield chunk

if __name__ == "__main__":
    app.run()
```

## Installation

```bash
pip install rapidai
```

Or with specific extras:

```bash
# With Anthropic support
pip install rapidai[anthropic]

# With OpenAI support
pip install rapidai[openai]

# With all features
pip install rapidai[all]
```

## Project Status

🚧 **In Development** - This is a brand new project. We're building in public!

### Current Phase: Foundation
- [x] Project setup and structure
- [ ] Core App class and routing
- [ ] Unified LLM interface
- [ ] Streaming support
- [ ] Basic middleware system
- [ ] Configuration management

### Next Phase: AI Features
- [ ] Prompt management
- [ ] Conversation memory
- [ ] Smart caching
- [ ] RAG implementation
- [ ] Document loaders

### Future Phases
- [ ] Built-in UI components
- [ ] CLI tool
- [ ] Deployment templates
- [ ] Cost tracking & monitoring
- [ ] Plugin system

## Philosophy

1. **Convention over configuration** - Sensible defaults everywhere
2. **Provider agnostic** - Swap OpenAI for Anthropic with one line
3. **Async-first** - Everything uses async/await
4. **Type-safe** - Full type hints for great IDE support
5. **Batteries included** - But easy to replace any component

## Target Use Cases

- Rapid POCs for new AI features
- Internal tools and dashboards
- Chat interfaces and assistants
- RAG applications
- Document processing pipelines
- AI-powered APIs

## Development

```bash
# Clone the repository
git clone https://github.com/shaungehring/rapidai.git
cd rapidai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Type check
mypy rapidai

# Format code
ruff format rapidai
```

## Community

- 🐛 [Report bugs](https://github.com/shaungehring/rapidai/issues)
- 💡 [Request features](https://github.com/shaungehring/rapidai/discussions)
- 📖 [Read the docs](https://rapidai.dev) (coming soon)

## License

MIT License - see [LICENSE](LICENSE) file for details

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

Built with ❤️ for AI engineers who move fast
