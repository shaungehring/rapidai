# Changelog

All notable changes to RapidAI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-XX

### Added

**Background Jobs**
- Async task processing with `@background` decorator
- Automatic retry logic with exponential backoff
- Job status tracking (pending, running, completed, failed, cancelled)
- In-memory and Redis queue backends
- Job cancellation support

**Monitoring & Observability**
- `@monitor` decorator for automatic metrics collection
- Token usage and cost tracking for all LLM providers
- Built-in HTML metrics dashboard with auto-refresh
- Model usage statistics and breakdown
- Custom metrics recording
- Integration with Prometheus and CloudWatch

**UI Components**
- Pre-built chat interface with dark and light themes
- `@page` decorator for serving HTML
- Customizable `ChatInterface` with themes, avatars, and styling
- Markdown rendering support
- File upload integration
- Mobile-responsive design

**RAG System (Retrieval-Augmented Generation)**
- Document loading for PDF, DOCX, TXT, HTML, Markdown
- Multiple chunking strategies (recursive, sentence-based)
- Embedding support (Sentence Transformers, OpenAI)
- ChromaDB vector database integration
- `@rag` decorator for automatic document retrieval
- Metadata filtering and source tracking

**Prompt Management**
- Template-based prompt organization
- Jinja2 templating support
- `@prompt` decorator for prompt injection
- Prompt versioning and management

**Testing Utilities**
- `TestClient` for endpoint testing without running server
- `MockLLM` for testing without API calls
- `MockMemory` for conversation memory testing
- Call tracking and verification
- Pytest fixture integration

**CLI Tool**
- `rapidai new` - Create new projects from templates
- `rapidai dev` - Development server with hot reload
- `rapidai deploy` - Deploy to cloud platforms (Vercel, Railway, Render, AWS Lambda)
- `rapidai test` - Run test suite
- `rapidai docs` - Generate and serve documentation
- Four project templates: chatbot, rag, agent, api

**Semantic Caching**
- AI-powered response caching using embedding similarity
- Configurable similarity thresholds
- Reduces redundant LLM calls for similar queries

**Documentation**
- Complete user guides for all features (18 pages)
- Comprehensive API references
- Deployment tutorials for major platforms
- Working examples for all features (9+ examples)
- Full mkdocs documentation site

**Developer Experience**
- Comprehensive test coverage (300+ tests)
- Type hints throughout codebase
- Pre-commit hooks configuration
- Development tools (ruff, mypy, pytest)

### Changed

- Version bumped to 1.0.0 - production ready
- Development Status classifier updated to "Production/Stable"
- Enhanced cache system to support semantic caching
- Improved error messages and validation
- Better async/await patterns throughout

### Fixed

- All documentation links now valid
- Consistent version numbering across package
- Proper module exports in `__init__.py` files

### Breaking Changes

None - this is the first stable release.

## [0.1.0] - 2024-XX-XX

### Added

- Initial framework release
- Core `App` class with routing
- LLM support (Anthropic Claude, OpenAI, Cohere)
- Streaming responses
- Conversation memory (in-memory and Redis)
- Basic caching (in-memory and Redis)
- Configuration management
- Basic examples and documentation

---

## Release Notes

### v1.0.0 - Production Release 🚀

RapidAI v1.0.0 marks the first production-ready release! This version includes everything you need to build production AI applications:

**What's New:**
- 🔄 Background job processing with automatic retry
- 📊 Built-in monitoring and cost tracking
- 🎨 Pre-built UI components with chat interfaces
- 📚 RAG system for document Q&A
- 🧪 Comprehensive testing utilities
- ⚙️ CLI tool with project templates
- 📝 Prompt management system
- 💾 Semantic caching for intelligent response reuse

**Installation:**
```bash
pip install rapidai
```

**Quick Start:**
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

**Documentation:**
https://rapidai.dev

**Feedback:**
https://github.com/shaungehring/rapidai/issues

Thank you to all contributors and early adopters! 🎉

---

[1.0.0]: https://github.com/shaungehring/rapidai/releases/tag/v1.0.0
[0.1.0]: https://github.com/shaungehring/rapidai/releases/tag/v0.1.0
