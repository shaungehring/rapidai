# RapidAI ⚡

<div class="hero">
  <h1>The Python Framework for Lightning-Fast AI Prototypes</h1>
  <p style="font-size: 1.3rem; color: var(--synthwave-cyan); margin: 2rem 0;">
    Build production-ready AI applications in under an hour. Zero-config LLM integration, streaming by default, batteries included.
  </p>
  <div style="margin-top: 2rem;">
    <a href="getting-started/installation.html" class="md-button md-button--primary" style="margin: 0.5rem;">Get Started</a>
    <a href="tutorial/intro.html" class="md-button" style="margin: 0.5rem;">View Tutorial</a>
    <a href="https://github.com/shaungehring/rapidai" class="md-button" style="margin: 0.5rem;">GitHub</a>
  </div>
</div>

## ✨ Features

<div class="feature-grid">
  <div class="feature-card">
    <h3>🚀 Zero-Config LLM Integration</h3>
    <p>Built-in clients for OpenAI, Anthropic, Cohere, and local models with a unified interface. Swap providers with one line of code.</p>
  </div>

  <div class="feature-card">
    <h3>📡 Streaming by Default</h3>
    <p>Server-Sent Events (SSE) and WebSocket streaming built into routes, not bolted on. Real-time AI responses out of the box.</p>
  </div>

  <div class="feature-card">
    <h3>🧠 Smart Memory</h3>
    <p>Conversation tracking per user with multiple backend options. Redis, PostgreSQL, or in-memory - you choose.</p>
  </div>

  <div class="feature-card">
    <h3>💾 Intelligent Caching</h3>
    <p>LLM response caching that understands semantic similarity. Save money and improve response times automatically.</p>
  </div>

  <div class="feature-card">
    <h3>📝 Prompt Management</h3>
    <p>Version, test, and swap prompts without code changes. Jinja2 templating with hot reloading in development.</p>
  </div>

  <div class="feature-card">
    <h3>🔍 RAG in Minutes</h3>
    <p>Document parsing, vector DB, and retrieval with 2-line setup. Built-in support for PDFs, DOCX, and more.</p>
  </div>
</div>

## 🎯 Quick Example

```python title="app.py"
from rapidai import App, LLM, stream

app = App()
llm = LLM("claude-3-haiku-20240307")

@app.route("/chat", methods=["POST"])
@stream
async def chat(message: str):
    """Stream a chat response."""
    response = await llm.chat(message, stream=True)
    async for chunk in response:
        yield chunk

if __name__ == "__main__":
    app.run()
```

<div class="command">python app.py</div>

```bash title="Test it"
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, AI!"}'
```

## 🌟 Why RapidAI?

!!! success "Convention over Configuration"
    Sensible defaults everywhere. Get started in minutes, not hours.

!!! success "Provider Agnostic"
    Never get locked into a single LLM provider. Switch between OpenAI, Anthropic, or local models with ease.

!!! success "Async-First"
    Built from the ground up with async/await for maximum performance.

!!! success "Type-Safe"
    Full type hints for excellent IDE support and fewer runtime errors.

!!! success "Production Ready"
    Error handling, rate limiting, monitoring, and deployment templates included.

## 📊 Perfect For

- 🚀 **Rapid POCs** - Test AI features in minutes
- 🏢 **Internal Tools** - Build dashboards and automation
- 💬 **Chat Interfaces** - Customer support and assistants
- 📚 **RAG Applications** - Document Q&A systems
- 🔄 **Document Processing** - Automated pipelines
- 🌐 **AI-Powered APIs** - Production-grade endpoints

## 🎓 Learn More

<div class="feature-grid">
  <div class="feature-card">
    <h3>📘 Tutorial</h3>
    <p>Step-by-step guide from simple chatbot to production deployment.</p>
    <a href="tutorial/intro.html">Start Learning →</a>
  </div>

  <div class="feature-card">
    <h3>📖 API Reference</h3>
    <p>Complete documentation of all classes, methods, and decorators.</p>
    <a href="reference/app.html">Browse Reference →</a>
  </div>

  <div class="feature-card">
    <h3>🚀 Deployment</h3>
    <p>Deploy to Docker, AWS, GCP, Azure, and more with confidence.</p>
    <a href="deployment/overview.html">Deploy Now →</a>
  </div>
</div>

## 🤝 Community

- 🐛 [Report Bugs](https://github.com/shaungehring/rapidai/issues)
- 💡 [Request Features](https://github.com/shaungehring/rapidai/discussions)
- 📣 [Join Discord](#) (Coming Soon)
- 🐦 [Follow on Twitter](https://twitter.com/rapidai)

## 📄 License

RapidAI is licensed under the MIT License. See [LICENSE](about/license.html) for details.

---

<div style="text-align: center; padding: 2rem; color: var(--synthwave-cyan);">
  <p style="font-size: 1.5rem; font-weight: 600;">Ready to build something amazing?</p>
  <a href="getting-started/installation.html" class="md-button md-button--primary" style="font-size: 1.2rem; padding: 1rem 2rem;">Get Started Now →</a>
</div>
