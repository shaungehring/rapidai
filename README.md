# RapidAI 🚀

[![PyPI version](https://badge.fury.io/py/rapidai.svg)](https://pypi.org/project/rapidai/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Production-ready Python framework for building AI applications fast**

RapidAI is designed for one thing: getting from idea to deployed AI application in under an hour. When your boss asks you to POC the latest AI tool, this is the framework you reach for.

## Vision

A web framework that bridges the gap between Flask's simplicity and Django's batteries-included approach, but optimized specifically for modern AI development. Think of it as "the Rails of AI apps" - convention over configuration, but for LLM-powered applications.

## ✨ Features

- **🤖 Zero-config LLM integration** - Built-in support for Anthropic Claude, OpenAI, Cohere with unified interface
- **📡 Streaming by default** - SSE/WebSocket streaming built into routes, not bolted on
- **🔄 Background jobs** - Async task processing with automatic retry and job tracking
- **📊 Built-in monitoring** - Token usage, cost tracking, and metrics dashboard
- **🎨 UI components** - Pre-built chat interfaces with customizable themes
- **📚 RAG system** - Document loading, embeddings, vector DB integration for retrieval
- **📝 Prompt management** - Version control and templating for prompts with Jinja2
- **💾 Smart caching** - Semantic caching using embedding similarity
- **🧪 Testing utilities** - TestClient, MockLLM, MockMemory for easy testing
- **⚡ CLI tool** - Project templates, dev server, deployment, and more

## 🚀 Quick Start

### Simple Chat Endpoint

```python
from rapidai import App, LLM

app = App()
llm = LLM("claude-3-haiku-20240307")

@app.route("/chat", methods=["POST"])
async def chat(message: str):
    response = await llm.complete(message)
    return {"response": response}

if __name__ == "__main__":
    app.run()
```

### With Streaming

```python
from rapidai import App, LLM

app = App()
llm = LLM("claude-3-haiku-20240307")

@app.route("/chat", methods=["POST"])
async def chat(message: str):
    async for chunk in llm.stream(message):
        yield chunk

if __name__ == "__main__":
    app.run()
```

### With Background Jobs

```python
from rapidai import App, background

app = App()

@background(max_retries=3)
async def process_document(doc_id: str):
    # Long-running task runs in background
    await analyze_document(doc_id)

@app.route("/process", methods=["POST"])
async def start_processing(doc_id: str):
    job = await process_document(doc_id)
    return {"job_id": job.id, "status": job.status}
```

### With Monitoring

```python
from rapidai import App, LLM, monitor

app = App()
llm = LLM("claude-3-haiku-20240307")

@app.route("/chat", methods=["POST"])
@monitor()  # Automatically tracks tokens and costs
async def chat(message: str):
    return await llm.complete(message)

@app.route("/metrics")
async def metrics():
    return app.get_metrics_html()  # Built-in dashboard
```

## 📦 Installation

```bash
pip install rapidai
```

### Optional Dependencies

Install with specific features:

```bash
# Anthropic Claude support
pip install "rapidai[anthropic]"

# OpenAI support
pip install "rapidai[openai]"

# RAG (document loading, embeddings, vector DB)
pip install "rapidai[rag]"

# Redis (for caching and memory)
pip install "rapidai[redis]"

# Everything
pip install "rapidai[all]"

# Development tools
pip install "rapidai[dev]"
```

## 📋 What's Included

### Core Framework

- ✅ **App class** - Fast async web server with routing
- ✅ **LLM clients** - Anthropic Claude, OpenAI, Cohere with unified interface
- ✅ **Streaming** - Built-in SSE support for real-time responses
- ✅ **Memory** - Conversation history (in-memory and Redis)
- ✅ **Caching** - Semantic caching with embedding similarity
- ✅ **Config** - Environment-based configuration with Pydantic

### Advanced Features

- ✅ **Background jobs** - `@background` decorator with retry logic and job tracking
- ✅ **Monitoring** - `@monitor` decorator with token/cost tracking and HTML dashboard
- ✅ **RAG system** - Document loading (PDF, DOCX, TXT, HTML, MD), embeddings, vector DB
- ✅ **Prompt management** - Template-based prompts with Jinja2 and versioning
- ✅ **UI components** - Pre-built chat interfaces with themes and customization
- ✅ **Testing utilities** - TestClient, MockLLM, MockMemory for easy testing

### Developer Tools

- ✅ **CLI tool** - `rapidai new`, `rapidai dev`, `rapidai deploy`, `rapidai test`
- ✅ **Project templates** - Chatbot, RAG, Agent, API templates
- ✅ **Type hints** - Full type coverage for IDE support
- ✅ **Documentation** - Complete guides and API references at [rapidai.dev](https://rapidai.dev)

## Status

**Version:** 1.0.0 - Production Ready 🎉

See [CHANGELOG.md](CHANGELOG.md) for release notes.

## 💡 Use Cases

Perfect for building:

- 🤖 **Chat applications** - Customer support bots, AI assistants
- 📚 **RAG systems** - Document Q&A, knowledge bases
- 🔧 **Internal tools** - AI-powered dashboards and workflows
- 📊 **Data processing** - Background jobs for document analysis
- 🌐 **AI APIs** - REST endpoints with LLM integration
- 🎯 **Rapid prototypes** - POCs and MVPs in under an hour

## 🎯 Philosophy

1. **Convention over configuration** - Sensible defaults, minimal boilerplate
2. **Provider agnostic** - Swap OpenAI for Anthropic with one line
3. **Async-first** - Built on modern async/await patterns
4. **Type-safe** - Full type hints for excellent IDE support
5. **Batteries included** - Everything you need, nothing you don't
6. **Production ready** - Monitoring, testing, deployment from day one

## 📚 Documentation

Complete documentation available at **[rapidai.dev](https://rapidai.dev)**

- [Getting Started Guide](https://rapidai.dev/tutorial/intro/)
- [LLM Integration](https://rapidai.dev/advanced/llm/)
- [Background Jobs](https://rapidai.dev/advanced/background/)
- [Monitoring & Metrics](https://rapidai.dev/advanced/monitoring/)
- [RAG System](https://rapidai.dev/advanced/rag/)
- [UI Components](https://rapidai.dev/advanced/ui/)
- [Testing Guide](https://rapidai.dev/advanced/testing/)
- [Deployment](https://rapidai.dev/deployment/overview/)
- [API Reference](https://rapidai.dev/reference/app/)

## 🛠️ CLI Tool

RapidAI includes a powerful CLI for project scaffolding and management:

```bash
# Create a new project from template
rapidai new my-chatbot --template chatbot

# Start development server with hot reload
rapidai dev

# Run tests
rapidai test

# Deploy to cloud platforms
rapidai deploy --platform vercel

# Generate documentation
rapidai docs
```

**Available templates:**

- `chatbot` - Simple chat application
- `rag` - RAG system with document Q&A
- `agent` - AI agent with tools
- `api` - REST API with LLM endpoints

## 👨‍💻 Development

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

# Run tests with coverage
pytest --cov=rapidai tests/

# Type check
mypy rapidai

# Lint and format
ruff check rapidai
ruff format rapidai
```

## 🤝 Community & Support

- 📖 **Documentation** - [rapidai.dev](https://rapidai.dev)
- 🐛 **Bug Reports** - [GitHub Issues](https://github.com/shaungehring/rapidai/issues)
- 💡 **Feature Requests** - [GitHub Discussions](https://github.com/shaungehring/rapidai/discussions)
- 📦 **PyPI Package** - [pypi.org/project/rapidai](https://pypi.org/project/rapidai/)
- 📋 **Changelog** - [CHANGELOG.md](CHANGELOG.md)

## 🚀 Publishing

RapidAI is available on PyPI. To publish a new version:

```bash
# Test on TestPyPI first
./scripts/publish.sh test

# Publish to production PyPI
./scripts/publish.sh prod
```

See [PUBLISHING.md](PUBLISHING.md) for complete publishing guide.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Contributing

We welcome contributions! Whether it's:

- 🐛 Bug fixes
- ✨ New features
- 📚 Documentation improvements
- 🧪 Test coverage
- 💡 Ideas and suggestions

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute.

## ⭐ Show Your Support

If you find RapidAI helpful, please consider:

- ⭐ Starring the [GitHub repository](https://github.com/shaungehring/rapidai)
- 📢 Sharing with your network
- 🐛 Reporting issues you encounter
- 💡 Suggesting new features

---

Built with ❤️ for AI engineers who move fast

**Version:** 1.0.0 | **Status:** Production Ready 🎉
