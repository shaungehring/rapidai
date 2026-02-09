# CLI API Reference

Complete API reference for the RapidAI CLI tool.

## Commands

### rapidai

Main CLI entry point.

```bash
rapidai [OPTIONS] COMMAND [ARGS]...
```

**Options:**

- `--version` - Show the version and exit
- `--help` - Show help message and exit

**Commands:**

- `new` - Create a new RapidAI project
- `dev` - Run development server
- `deploy` - Deploy to cloud platforms
- `test` - Run tests
- `docs` - Generate and serve documentation

## new

Create a new RapidAI project from a template.

```bash
rapidai new PROJECT_NAME [OPTIONS]
```

**Arguments:**

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `PROJECT_NAME` | string | Yes | Name of the project to create |

**Options:**

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--template` | `-t` | choice | `chatbot` | Template to use (chatbot\|rag\|agent\|api) |
| `--directory` | `-d` | path | `.` | Directory to create project in |

**Return Codes:**

- `0` - Success
- `1` - Error (invalid name, directory exists, etc.)

**Examples:**

```bash
# Create chatbot project
rapidai new my-bot

# Create RAG project in specific directory
rapidai new doc-qa -t rag -d ~/projects

# Create API project
rapidai new my-api --template api
```

**Template Details:**

#### chatbot

Creates a chatbot application with conversation memory.

**Generated Files:**

- `app.py` - Main application with chat endpoints
- `.env` - Environment variable template
- `requirements.txt` - Dependencies (rapidai, anthropic/openai)
- `README.md` - Project documentation
- `tests/` - Empty test directory

**Endpoints:**

- `POST /chat` - Chat with memory
- `POST /clear` - Clear conversation history

#### rag

Creates a RAG application with document upload and Q&A.

**Generated Files:**

- `app.py` - Main application with RAG endpoints
- `.env` - Environment variable template
- `requirements.txt` - Dependencies (rapidai[rag], anthropic/openai)
- `README.md` - Project documentation
- `tests/` - Empty test directory
- `docs/` - Document storage directory

**Endpoints:**

- `POST /upload` - Upload documents
- `POST /ask` - Ask questions
- `POST /search` - Search documents

#### agent

Creates an AI agent with analysis and generation capabilities.

**Generated Files:**

- `app.py` - Main application with agent endpoints
- `.env` - Environment variable template
- `requirements.txt` - Dependencies (rapidai, anthropic/openai)
- `README.md` - Project documentation
- `tests/` - Empty test directory

**Endpoints:**

- `POST /analyze` - Analyze text
- `POST /generate` - Generate content
- `POST /chat` - Agent chat

#### api

Creates a REST API with authentication and CORS.

**Generated Files:**

- `app.py` - Main application with API endpoints
- `.env` - Environment variable template
- `requirements.txt` - Dependencies (rapidai, anthropic/openai)
- `README.md` - Project documentation
- `tests/` - Empty test directory

**Endpoints:**

- `GET /` - API information
- `POST /complete` - Complete prompts
- `POST /chat` - Chat endpoint
- `GET /health` - Health check

## dev

Run the development server with hot reload.

```bash
rapidai dev [OPTIONS]
```

**Options:**

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--port` | `-p` | integer | `8000` | Port to run server on |
| `--host` | `-h` | string | `127.0.0.1` | Host to bind server to |
| `--reload` | - | flag | `True` | Enable auto-reload on file changes |
| `--no-reload` | - | flag | `False` | Disable auto-reload |
| `--app` | `-a` | string | `app:app` | Application module path |

**Return Codes:**

- `0` - Server stopped normally (Ctrl+C)
- `1` - Error (app file not found, uvicorn not installed, etc.)

**Examples:**

```bash
# Run with defaults
rapidai dev

# Custom port
rapidai dev -p 3000

# Custom host (allow external connections)
rapidai dev -h 0.0.0.0

# Disable auto-reload
rapidai dev --no-reload

# Custom app module
rapidai dev --app myapp:application
```

**Behavior:**

1. Checks if app file exists
2. Displays startup banner with URL and settings
3. Starts Uvicorn server with specified options
4. Watches files for changes if `--reload` is enabled
5. Stops on Ctrl+C

**File Watching:**

When `--reload` is enabled, watches:

- `*.py` files
- Excludes: `*.pyc`, `__pycache__`, `.git`

## deploy

Deploy application to a cloud platform.

```bash
rapidai deploy PLATFORM [OPTIONS]
```

**Arguments:**

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `PLATFORM` | choice | Yes | Cloud platform (fly\|heroku\|vercel\|aws) |

**Options:**

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--app-name` | `-n` | string | - | Application name for deployment |
| `--region` | `-r` | string | - | Region to deploy to |

**Return Codes:**

- `0` - Success
- `1` - Error (CLI not installed, deployment failed, etc.)

**Examples:**

```bash
# Deploy to Fly.io
rapidai deploy fly

# Deploy to Heroku with app name
rapidai deploy heroku -n my-app

# Deploy to Vercel in specific region
rapidai deploy vercel -r us-east-1

# AWS deployment instructions
rapidai deploy aws
```

**Platform Details:**

### fly

Deploy to Fly.io.

**Requirements:**

- `flyctl` CLI installed
- Fly.io account

**Behavior:**

1. Checks for `flyctl` installation
2. Prompts for app name if not provided
3. Generates `fly.toml` if not present
4. Runs `flyctl deploy`
5. Displays deployment URL

**Generated Files:**

- `fly.toml` - Fly.io configuration

**Configuration:**

```toml
app = "app-name"
primary_region = "iad"  # if --region specified

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8080"

[[services]]
  internal_port = 8080
  protocol = "tcp"
```

### heroku

Deploy to Heroku.

**Requirements:**

- `heroku` CLI installed
- Heroku account
- Git repository

**Behavior:**

1. Checks for `heroku` CLI installation
2. Prompts for app name if not provided
3. Generates `Procfile` if not present
4. Creates Heroku app
5. Sets Python buildpack
6. Displays git push instructions

**Generated Files:**

- `Procfile` - Heroku process configuration

**Configuration:**

```
web: uvicorn app:app --host 0.0.0.0 --port $PORT
```

### vercel

Deploy to Vercel.

**Requirements:**

- `vercel` CLI installed (npm)
- Vercel account

**Behavior:**

1. Checks for `vercel` CLI installation
2. Generates `vercel.json` if not present
3. Runs `vercel --prod`
4. Displays deployment URL

**Generated Files:**

- `vercel.json` - Vercel configuration

**Configuration:**

```json
{
  "builds": [{"src": "app.py", "use": "@vercel/python"}],
  "routes": [{"src": "/(.*)", "dest": "app.py"}]
}
```

### aws

AWS deployment instructions.

**Behavior:**

Displays manual deployment guide for:

- AWS Lambda + API Gateway (serverless)
- AWS ECS/Fargate (containers)
- AWS Elastic Beanstalk (platform)

No automatic deployment.

## test

Run tests for the application.

```bash
rapidai test [OPTIONS]
```

**Options:**

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--coverage` | - | flag | `True` | Run with coverage reporting |
| `--no-coverage` | - | flag | `False` | Disable coverage reporting |
| `--verbose` | `-v` | flag | `False` | Verbose output |

**Return Codes:**

- `0` - All tests passed
- `1` - Tests failed or pytest not found

**Examples:**

```bash
# Run with coverage
rapidai test

# Run without coverage
rapidai test --no-coverage

# Verbose output
rapidai test -v

# Combine options
rapidai test --no-coverage --verbose
```

**Behavior:**

1. Checks for `pytest` installation
2. Builds pytest command with options
3. Runs tests
4. Returns pytest exit code

**Command Generated:**

```bash
# With coverage (default)
pytest --cov=. --cov-report=term-missing

# Without coverage
pytest

# Verbose
pytest -v
```

## docs

Generate and serve project documentation.

```bash
rapidai docs [OPTIONS]
```

**Options:**

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--serve` | - | flag | `True` | Serve documentation locally |
| `--build` | - | flag | `False` | Build for production |
| `--port` | `-p` | integer | `8001` | Port to serve docs on |

**Return Codes:**

- `0` - Success
- `1` - Error (mkdocs not installed, build failed, etc.)

**Examples:**

```bash
# Serve locally
rapidai docs

# Build for production
rapidai docs --build

# Custom port
rapidai docs -p 3000
```

**Behavior:**

1. Checks for `mkdocs` installation
2. Creates basic docs structure if missing
3. Either serves or builds documentation
4. Displays URL or build location

**Serve Mode:**

- Runs `mkdocs serve`
- Hot reloads on changes
- Accessible at `http://localhost:{port}`

**Build Mode:**

- Runs `mkdocs build`
- Generates static site in `site/`
- Ready for deployment

## Configuration

### Environment Variables

The CLI respects these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `false` |
| `RAPIDAI_*` | Any RapidAI configuration | - |

### Config Files

Generated config files:

- `fly.toml` - Fly.io configuration
- `Procfile` - Heroku configuration
- `vercel.json` - Vercel configuration

## Error Handling

### Common Errors

**"Application file not found"**

```bash
# Solution: Make sure you're in the project directory
cd my-project
rapidai dev
```

**"pytest not found"**

```bash
# Solution: Install pytest
pip install pytest pytest-cov
```

**"mkdocs not found"**

```bash
# Solution: Install mkdocs
pip install mkdocs mkdocs-material
```

**"Directory already exists"**

```bash
# Solution: Choose a different name or directory
rapidai new my-project-v2
# or
rm -rf my-project  # if you want to overwrite
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error |
| 2 | Invalid usage |

## See Also

- [CLI Guide](../advanced/cli.md) - Complete usage guide with examples
- [Configuration](configuration.md) - Environment variable configuration
- [Deployment](../tutorial/deployment.md) - Deployment best practices
