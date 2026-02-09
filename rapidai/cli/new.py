"""Project scaffolding command for RapidAI CLI."""

import shutil
from pathlib import Path
from typing import Any, Dict

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


def get_template_files(template: str, project_name: str) -> Dict[str, str]:
    """Get template files for the specified template type.

    Args:
        template: Template type (chatbot, rag, agent, api)
        project_name: Name of the project

    Returns:
        Dictionary mapping file paths to file contents
    """
    templates: Dict[str, Dict[str, str]] = {
        "chatbot": {
            "app.py": f'''"""Simple chatbot application built with RapidAI."""

from rapidai import App, LLM
from rapidai.memory import ConversationMemory

app = App(title="{project_name}")
llm = LLM("claude-3-haiku-20240307")  # or "gpt-4o-mini"
memory = ConversationMemory()


@app.route("/chat", methods=["POST"])
async def chat(user_id: str, message: str):
    """Chat endpoint with conversation memory."""
    # Add user message to memory
    memory.add_message(user_id, "user", message)

    # Get conversation history
    history = memory.get_history(user_id)

    # Generate response
    response = await llm.chat(history)

    # Add assistant response to memory
    memory.add_message(user_id, "assistant", response)

    return {{"response": response}}


@app.route("/clear", methods=["POST"])
async def clear_history(user_id: str):
    """Clear conversation history for a user."""
    memory.clear(user_id)
    return {{"status": "cleared"}}


if __name__ == "__main__":
    app.run(port=8000)
''',
            ".env": '''# LLM Provider API Keys
ANTHROPIC_API_KEY=your-api-key-here
# OPENAI_API_KEY=your-api-key-here

# Application Settings
DEBUG=true
''',
            "requirements.txt": '''rapidai>=0.1.0
rapidai[anthropic]
# rapidai[openai]
python-dotenv>=1.0.0
''',
            "README.md": f'''# {project_name}

A chatbot application built with RapidAI.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your API key in `.env`:
```bash
ANTHROPIC_API_KEY=your-key-here
```

## Run

```bash
rapidai dev
# or
python app.py
```

## Test

```bash
curl -X POST http://localhost:8000/chat \\
  -H "Content-Type: application/json" \\
  -d '{{"user_id": "user123", "message": "Hello!"}}'
```

## Features

- Conversation memory per user
- Clear history endpoint
- Simple and extensible
''',
        },
        "rag": {
            "app.py": f'''"""RAG application built with RapidAI."""

from rapidai import App, LLM
from rapidai.rag import RAG

app = App(title="{project_name}")
llm = LLM("claude-3-haiku-20240307")
rag = RAG()


@app.on_startup
async def startup():
    """Initialize RAG system on startup."""
    await rag.initialize()
    console.print("[green]RAG system initialized[/green]")


@app.route("/upload", methods=["POST"])
async def upload_document(filepath: str):
    """Upload a document to the RAG system."""
    try:
        chunks = await rag.add_document(filepath)
        return {{
            "status": "success",
            "chunks": len(chunks),
            "source": filepath
        }}
    except Exception as e:
        return {{"error": str(e)}}, 400


@app.route("/ask", methods=["POST"])
async def ask_question(question: str):
    """Ask a question using RAG."""
    # Retrieve relevant context
    retrieval = await rag.retrieve(question, top_k=5)

    # Generate answer with context
    answer = await rag.query(question, llm=llm)

    return {{
        "question": question,
        "answer": answer,
        "sources": [s.metadata.get("source") for s in retrieval.sources],
        "context": retrieval.text[:500]  # First 500 chars
    }}


@app.route("/search", methods=["POST"])
async def search(query: str, top_k: int = 5):
    """Search for relevant documents."""
    result = await rag.retrieve(query, top_k=top_k)
    return {{
        "query": query,
        "results": [
            {{
                "content": chunk.content,
                "source": chunk.metadata.get("source"),
                "score": getattr(chunk, "score", None)
            }}
            for chunk in result.sources
        ]
    }}


if __name__ == "__main__":
    app.run(port=8000)
''',
            ".env": '''# LLM Provider API Keys
ANTHROPIC_API_KEY=your-api-key-here

# RAG Configuration
RAPIDAI_RAG_TOP_K=5
RAPIDAI_CHUNKING_CHUNK_SIZE=512
RAPIDAI_CHUNKING_CHUNK_OVERLAP=50

# Application Settings
DEBUG=true
''',
            "requirements.txt": '''rapidai>=0.1.0
rapidai[anthropic,rag]
python-dotenv>=1.0.0
''',
            "README.md": f'''# {project_name}

A RAG (Retrieval-Augmented Generation) application built with RapidAI.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your API key in `.env`:
```bash
ANTHROPIC_API_KEY=your-key-here
```

## Run

```bash
rapidai dev
```

## Usage

Upload a document:
```bash
curl -X POST http://localhost:8000/upload \\
  -H "Content-Type: application/json" \\
  -d '{{"filepath": "path/to/document.pdf"}}'
```

Ask a question:
```bash
curl -X POST http://localhost:8000/ask \\
  -H "Content-Type: application/json" \\
  -d '{{"question": "What is this document about?"}}'
```

## Features

- PDF, DOCX, TXT, HTML, Markdown support
- Semantic search with embeddings
- Context-aware answers
- ChromaDB vector storage
''',
            "docs/.gitkeep": "",
        },
        "agent": {
            "app.py": f'''"""AI agent application built with RapidAI."""

from rapidai import App, LLM
from rapidai.cache import cache

app = App(title="{project_name}")
llm = LLM("claude-3-haiku-20240307")


@app.route("/analyze", methods=["POST"])
@cache(ttl=3600)  # Cache for 1 hour
async def analyze_text(text: str):
    """Analyze text and extract insights."""
    prompt = f"""Analyze the following text and provide:
1. Summary (2-3 sentences)
2. Key topics (3-5 topics)
3. Sentiment (positive/negative/neutral)
4. Action items (if any)

Text: {{text}}

Analysis:"""

    response = await llm.complete(prompt)
    return {{"analysis": response}}


@app.route("/generate", methods=["POST"])
async def generate_content(topic: str, style: str = "professional"):
    """Generate content on a given topic."""
    prompt = f"""Generate a {{style}} article about: {{topic}}

Include:
- Introduction
- Main points
- Conclusion

Article:"""

    response = await llm.complete(prompt)
    return {{"content": response}}


@app.route("/chat", methods=["POST"])
async def agent_chat(message: str):
    """Interactive agent chat."""
    system_prompt = """You are a helpful AI agent that can:
- Answer questions
- Analyze information
- Generate content
- Provide recommendations

Always be concise and helpful."""

    response = await llm.complete(message, system_prompt=system_prompt)
    return {{"response": response}}


if __name__ == "__main__":
    app.run(port=8000)
''',
            ".env": '''# LLM Provider API Keys
ANTHROPIC_API_KEY=your-api-key-here

# Cache Settings
RAPIDAI_CACHE_BACKEND=memory
RAPIDAI_CACHE_TTL=3600

# Application Settings
DEBUG=true
''',
            "requirements.txt": '''rapidai>=0.1.0
rapidai[anthropic]
python-dotenv>=1.0.0
''',
            "README.md": f'''# {project_name}

An AI agent application built with RapidAI.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your API key in `.env`:
```bash
ANTHROPIC_API_KEY=your-key-here
```

## Run

```bash
rapidai dev
```

## Endpoints

Analyze text:
```bash
curl -X POST http://localhost:8000/analyze \\
  -H "Content-Type: application/json" \\
  -d '{{"text": "Your text here"}}'
```

Generate content:
```bash
curl -X POST http://localhost:8000/generate \\
  -H "Content-Type: application/json" \\
  -d '{{"topic": "AI in healthcare", "style": "professional"}}'
```

Chat with agent:
```bash
curl -X POST http://localhost:8000/chat \\
  -H "Content-Type: application/json" \\
  -d '{{"message": "What can you help me with?"}}'
```

## Features

- Text analysis with caching
- Content generation
- Interactive agent chat
- Extensible architecture
''',
        },
        "api": {
            "app.py": f'''"""REST API built with RapidAI."""

from rapidai import App, LLM
from rapidai.middleware import cors, api_key_auth

app = App(title="{project_name}")
llm = LLM("claude-3-haiku-20240307")

# Apply middleware
app.use(cors())
app.use(api_key_auth("your-api-key"))  # Change this!


@app.route("/", methods=["GET"])
async def root():
    """API root endpoint."""
    return {{
        "name": "{project_name}",
        "version": "1.0.0",
        "endpoints": [
            "/complete",
            "/chat",
            "/health"
        ]
    }}


@app.route("/complete", methods=["POST"])
async def complete(prompt: str, max_tokens: int = 1000):
    """Complete a prompt."""
    response = await llm.complete(prompt, max_tokens=max_tokens)
    return {{"completion": response}}


@app.route("/chat", methods=["POST"])
async def chat(messages: list):
    """Chat with the AI."""
    response = await llm.chat(messages)
    return {{"response": response}}


@app.route("/health", methods=["GET"])
async def health():
    """Health check endpoint."""
    return {{"status": "healthy"}}


if __name__ == "__main__":
    app.run(port=8000)
''',
            ".env": '''# LLM Provider API Keys
ANTHROPIC_API_KEY=your-api-key-here

# API Settings
API_KEY=your-api-key
CORS_ORIGINS=*

# Application Settings
DEBUG=true
''',
            "requirements.txt": '''rapidai>=0.1.0
rapidai[anthropic]
python-dotenv>=1.0.0
''',
            "README.md": f'''# {project_name}

A REST API built with RapidAI.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your API keys in `.env`:
```bash
ANTHROPIC_API_KEY=your-key-here
API_KEY=your-custom-api-key
```

## Run

```bash
rapidai dev
```

## API Usage

All endpoints require the `X-API-Key` header:

Get API info:
```bash
curl http://localhost:8000/
```

Complete a prompt:
```bash
curl -X POST http://localhost:8000/complete \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: your-api-key" \\
  -d '{{"prompt": "Write a haiku about coding"}}'
```

Chat:
```bash
curl -X POST http://localhost:8000/chat \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: your-api-key" \\
  -d '{{"messages": [{{"role": "user", "content": "Hello!"}}]}}'
```

## Features

- CORS enabled
- API key authentication
- Health check endpoint
- Clean REST design
''',
        },
    }

    return templates.get(template, templates["chatbot"])


def new_command(project_name: str, template: str, directory: str) -> None:
    """Create a new RapidAI project.

    Args:
        project_name: Name of the project
        template: Template type to use
        directory: Directory to create project in
    """
    # Validate project name
    if not project_name.replace("-", "").replace("_", "").isalnum():
        console.print("[red]Error: Project name must be alphanumeric (with - or _ allowed)[/red]")
        return

    # Create project directory
    project_path = Path(directory) / project_name
    if project_path.exists():
        console.print(f"[red]Error: Directory {project_path} already exists[/red]")
        return

    console.print(f"[cyan]Creating new RapidAI project: {project_name}[/cyan]")
    console.print(f"[cyan]Template: {template}[/cyan]")
    console.print()

    try:
        # Create directory structure
        project_path.mkdir(parents=True)

        # Get template files
        files = get_template_files(template, project_name)

        # Create files
        for file_path, content in files.items():
            full_path = project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            console.print(f"  [green]✓[/green] Created {file_path}")

        # Create additional directories
        (project_path / "tests").mkdir(exist_ok=True)
        console.print(f"  [green]✓[/green] Created tests/")

        # Success message
        console.print()
        console.print(Panel.fit(
            f"[green]✓ Project created successfully![/green]\n\n"
            f"[cyan]Next steps:[/cyan]\n"
            f"1. cd {project_name}\n"
            f"2. pip install -r requirements.txt\n"
            f"3. Set your API key in .env\n"
            f"4. rapidai dev\n",
            title=f"🚀 {project_name}",
            border_style="green"
        ))

        # Show app.py preview
        app_content = files.get("app.py", "")
        if app_content:
            console.print("\n[cyan]Preview of app.py:[/cyan]")
            syntax = Syntax(app_content[:500] + "...", "python", theme="monokai", line_numbers=True)
            console.print(syntax)

    except Exception as e:
        console.print(f"[red]Error creating project: {e}[/red]")
        # Cleanup on error
        if project_path.exists():
            shutil.rmtree(project_path)
