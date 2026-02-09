# CLI Tool

RapidAI includes a powerful CLI tool for scaffolding projects, running development servers, and deploying to cloud platforms.

## Installation

The CLI is installed automatically with RapidAI:

```bash
pip install rapidai
```

Verify installation:

```bash
rapidai --version
```

## Quick Start

Create a new chatbot project:

```bash
rapidai new my-chatbot
cd my-chatbot
pip install -r requirements.txt
rapidai dev
```

Your app is now running at `http://localhost:8000`!

## Commands

### `rapidai new`

Create a new RapidAI project from a template.

```bash
rapidai new <project-name> [OPTIONS]
```

**Arguments:**

- `project-name` - Name of the project to create

**Options:**

- `-t, --template` - Template to use (chatbot, rag, agent, api) [default: chatbot]
- `-d, --directory` - Directory to create project in [default: .]

**Examples:**

```bash
# Create a chatbot project
rapidai new my-bot

# Create a RAG project
rapidai new doc-qa --template rag

# Create in a specific directory
rapidai new my-api --template api --directory ~/projects
```

**Templates:**

1. **chatbot** - Simple chatbot with conversation memory
2. **rag** - RAG application with document upload and Q&A
3. **agent** - AI agent with analysis and generation endpoints
4. **api** - REST API with authentication and CORS

### `rapidai dev`

Run the development server with hot reload.

```bash
rapidai dev [OPTIONS]
```

**Options:**

- `-p, --port` - Port to run on [default: 8000]
- `-h, --host` - Host to bind to [default: 127.0.0.1]
- `--reload/--no-reload` - Enable/disable auto-reload [default: reload]
- `-a, --app` - Application module path [default: app:app]

**Examples:**

```bash
# Run on default port 8000
rapidai dev

# Run on custom port
rapidai dev --port 3000

# Disable hot reload
rapidai dev --no-reload

# Custom app module
rapidai dev --app myapp:application
```

**Features:**

- Auto-reload on file changes
- Colored console output
- Clear error messages
- Powered by Uvicorn

### `rapidai deploy`

Deploy your application to a cloud platform.

```bash
rapidai deploy <platform> [OPTIONS]
```

**Arguments:**

- `platform` - Cloud platform (fly, heroku, vercel, aws)

**Options:**

- `-n, --app-name` - Application name for deployment
- `-r, --region` - Region to deploy to

**Examples:**

```bash
# Deploy to Fly.io
rapidai deploy fly

# Deploy to Heroku with app name
rapidai deploy heroku --app-name my-app

# Deploy to Vercel
rapidai deploy vercel

# Deploy to AWS (shows instructions)
rapidai deploy aws
```

**Supported Platforms:**

1. **Fly.io** - Automatic deployment with generated fly.toml
2. **Heroku** - Git-based deployment with Procfile
3. **Vercel** - Serverless deployment with vercel.json
4. **AWS** - Manual deployment instructions

### `rapidai test`

Run tests for your application.

```bash
rapidai test [OPTIONS]
```

**Options:**

- `--coverage/--no-coverage` - Run with coverage [default: coverage]
- `-v, --verbose` - Verbose output

**Examples:**

```bash
# Run tests with coverage
rapidai test

# Run without coverage
rapidai test --no-coverage

# Verbose output
rapidai test --verbose
```

**Requirements:**

- pytest must be installed
- Tests should be in `tests/` directory

### `rapidai docs`

Generate and serve project documentation.

```bash
rapidai docs [OPTIONS]
```

**Options:**

- `--serve/--build` - Serve locally or build for production [default: serve]
- `-p, --port` - Port to serve docs on [default: 8001]

**Examples:**

```bash
# Serve docs locally
rapidai docs

# Build for production
rapidai docs --build

# Serve on custom port
rapidai docs --port 3000
```

**Requirements:**

- mkdocs and mkdocs-material must be installed
- Docs should be in `docs/` directory

## Project Templates

### Chatbot Template

A simple chatbot with conversation memory.

**Features:**

- Conversation memory per user
- Clear history endpoint
- Environment-based configuration
- Claude or GPT support

**Files created:**

```text
my-chatbot/
├── app.py              # Main application
├── .env                # Environment variables
├── requirements.txt    # Dependencies
├── README.md          # Project documentation
└── tests/             # Test directory
```

**Endpoints:**

- `POST /chat` - Chat with the bot
- `POST /clear` - Clear conversation history

### RAG Template

RAG application with document upload and Q&A.

**Features:**

- Upload PDFs, DOCX, TXT, HTML, Markdown
- Semantic search with embeddings
- Context-aware answers
- ChromaDB vector storage

**Files created:**

```text
my-rag/
├── app.py              # Main application
├── .env                # Environment variables
├── requirements.txt    # Dependencies (includes RAG extras)
├── README.md          # Project documentation
├── tests/             # Test directory
└── docs/              # Document storage
```

**Endpoints:**

- `POST /upload` - Upload documents
- `POST /ask` - Ask questions
- `POST /search` - Search documents

### Agent Template

AI agent with analysis and content generation.

**Features:**

- Text analysis with caching
- Content generation
- Interactive agent chat
- Configurable styles

**Files created:**

```text
my-agent/
├── app.py              # Main application
├── .env                # Environment variables
├── requirements.txt    # Dependencies
├── README.md          # Project documentation
└── tests/             # Test directory
```

**Endpoints:**

- `POST /analyze` - Analyze text
- `POST /generate` - Generate content
- `POST /chat` - Interactive chat

### API Template

REST API with authentication and CORS.

**Features:**

- API key authentication
- CORS enabled
- Health check endpoint
- Clean REST design

**Files created:**

```text
my-api/
├── app.py              # Main application
├── .env                # Environment variables
├── requirements.txt    # Dependencies
├── README.md          # Project documentation
└── tests/             # Test directory
```

**Endpoints:**

- `GET /` - API information
- `POST /complete` - Complete prompts
- `POST /chat` - Chat endpoint
- `GET /health` - Health check

## Deployment Guide

### Fly.io Deployment

1. Install flyctl:

```bash
curl -L https://fly.io/install.sh | sh
```

2. Login:

```bash
flyctl auth login
```

3. Deploy:

```bash
rapidai deploy fly
```

**What happens:**

- Generates `fly.toml` configuration
- Creates or updates Fly.io app
- Deploys using Paketo buildpacks
- Configures health checks
- Provides deployment URL

**Environment variables:**

Set secrets with:

```bash
flyctl secrets set ANTHROPIC_API_KEY=your-key
```

### Heroku Deployment

1. Install Heroku CLI:

```bash
# macOS
brew install heroku/brew/heroku

# Or download from https://devcenter.heroku.com/articles/heroku-cli
```

2. Login:

```bash
heroku login
```

3. Deploy:

```bash
rapidai deploy heroku --app-name my-app
```

4. Push code:

```bash
git remote add heroku https://git.heroku.com/my-app.git
git push heroku main
```

**What happens:**

- Generates `Procfile`
- Creates Heroku app
- Sets Python buildpack
- Provides deployment instructions

**Environment variables:**

```bash
heroku config:set ANTHROPIC_API_KEY=your-key -a my-app
```

### Vercel Deployment

1. Install Vercel CLI:

```bash
npm install -g vercel
```

2. Login:

```bash
vercel login
```

3. Deploy:

```bash
rapidai deploy vercel
```

**What happens:**

- Generates `vercel.json` configuration
- Deploys as serverless function
- Provides deployment URL

**Environment variables:**

Set in Vercel dashboard or:

```bash
vercel env add ANTHROPIC_API_KEY
```

### AWS Deployment

AWS deployment is manual. Use:

```bash
rapidai deploy aws
```

This provides instructions for:

- AWS Lambda + API Gateway (serverless)
- AWS ECS/Fargate (containers)
- AWS Elastic Beanstalk (platform)

## Development Workflow

### 1. Create Project

```bash
rapidai new my-project --template chatbot
cd my-project
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Edit `.env`:

```bash
ANTHROPIC_API_KEY=your-api-key-here
DEBUG=true
```

### 4. Run Development Server

```bash
rapidai dev
```

### 5. Test

```bash
rapidai test
```

### 6. Deploy

```bash
rapidai deploy fly
```

## Best Practices

### Project Structure

```text
my-project/
├── app.py              # Main application
├── .env                # Environment variables (gitignored)
├── .env.example        # Example environment variables
├── requirements.txt    # Dependencies
├── README.md          # Documentation
├── tests/             # Tests
│   ├── __init__.py
│   └── test_app.py
├── prompts/           # Prompt templates (optional)
└── docs/              # Documents for RAG (optional)
```

### Environment Variables

Always use `.env` for secrets:

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
DEBUG=true
```

Add `.env.example` for documentation:

```bash
# .env.example
ANTHROPIC_API_KEY=your-api-key-here
DEBUG=true
```

### Testing

Create tests in `tests/`:

```python
# tests/test_app.py
import pytest
from rapidai.testing import TestClient

def test_chat():
    from app import app
    client = TestClient(app)
    response = client.post("/chat", json={"user_id": "test", "message": "hi"})
    assert response.status_code == 200
```

Run tests:

```bash
rapidai test
```

### Documentation

Keep README.md updated:

```markdown
# My Project

## Setup

1. Install dependencies
2. Set environment variables
3. Run the dev server

## Endpoints

- POST /chat - Description
- GET /health - Description
```

## Troubleshooting

### Port Already in Use

```bash
# Use a different port
rapidai dev --port 3000
```

### Module Not Found

```bash
# Make sure you're in the project directory
cd my-project

# Specify the module path
rapidai dev --app app:app
```

### Deployment Fails

```bash
# Check requirements.txt
cat requirements.txt

# Ensure all files are committed
git status
git add .
git commit -m "Deploy"
```

### Missing Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# For development
pip install rapidai[dev]
```

## Next Steps

- See [API Reference](../reference/cli.md) for complete CLI API documentation
- Check [Configuration](configuration.md) for environment variables
- Learn about [Deployment](../tutorial/deployment.md) best practices
