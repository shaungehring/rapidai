# Deployment Tutorial

Learn how to deploy your RapidAI applications to production environments.

## Overview

RapidAI applications can be deployed to various platforms:

- **Vercel** - Serverless deployment with zero config
- **Railway** - Container deployment with automatic HTTPS
- **Render** - Web services with persistent storage
- **AWS Lambda** - Serverless with Mangum adapter

This tutorial covers deployment strategies, configuration, and best practices.

## Prerequisites

Before deploying, ensure:

- Your application works locally
- Dependencies are specified in `requirements.txt`
- Environment variables are documented
- Tests pass successfully

## Quick Deploy with CLI

The RapidAI CLI provides one-command deployment:

```bash
# Deploy to Vercel
rapidai deploy --platform vercel

# Deploy to Railway
rapidai deploy --platform railway

# Deploy to Render
rapidai deploy --platform render

# Deploy to AWS Lambda
rapidai deploy --platform lambda
```

## Platform-Specific Guides

### Vercel Deployment

**Step 1: Install Vercel CLI**

```bash
npm install -g vercel
```

**Step 2: Create vercel.json**

```json
{
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

**Step 3: Deploy**

```bash
vercel --prod
```

**Or use CLI:**

```bash
rapidai deploy --platform vercel
```

**Environment Variables:**

Set in Vercel dashboard or via CLI:

```bash
vercel env add RAPIDAI_LLM_API_KEY
vercel env add RAPIDAI_CACHE_REDIS_URL
```

### Railway Deployment

**Step 1: Install Railway CLI**

```bash
npm install -g @railway/cli
```

**Step 2: Initialize Project**

```bash
railway login
railway init
```

**Step 3: Configure Start Command**

Create `Procfile`:

```
web: python app.py
```

Or set in railway.toml:

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python app.py"
numReplicas = 1
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

**Step 4: Deploy**

```bash
railway up
```

**Or use CLI:**

```bash
rapidai deploy --platform railway
```

**Environment Variables:**

```bash
railway variables set RAPIDAI_LLM_API_KEY=sk-...
railway variables set RAPIDAI_APP_PORT=8000
```

### Render Deployment

**Step 1: Create render.yaml**

```yaml
services:
  - type: web
    name: rapidai-app
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
    envVars:
      - key: RAPIDAI_LLM_API_KEY
        sync: false
      - key: RAPIDAI_APP_PORT
        value: 8000
```

**Step 2: Connect Git Repository**

1. Push code to GitHub
2. Go to Render dashboard
3. Create new Web Service
4. Connect repository

**Step 3: Deploy**

Render automatically deploys on push.

**Or use CLI:**

```bash
rapidai deploy --platform render
```

**Environment Variables:**

Set in Render dashboard under Environment tab.

### AWS Lambda Deployment

**Step 1: Install AWS CLI**

```bash
pip install awscli
aws configure
```

**Step 2: Create Lambda Handler**

```python
# lambda_handler.py
from mangum import Mangum
from app import app

handler = Mangum(app.asgi_app)
```

**Step 3: Package Dependencies**

```bash
pip install -r requirements.txt -t package/
cd package
zip -r ../deployment.zip .
cd ..
zip -g deployment.zip lambda_handler.py app.py
```

**Step 4: Create Lambda Function**

```bash
aws lambda create-function \
  --function-name rapidai-app \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT:role/lambda-role \
  --handler lambda_handler.handler \
  --zip-file fileb://deployment.zip \
  --timeout 30 \
  --memory-size 512
```

**Or use CLI:**

```bash
rapidai deploy --platform lambda
```

**Environment Variables:**

```bash
aws lambda update-function-configuration \
  --function-name rapidai-app \
  --environment Variables={RAPIDAI_LLM_API_KEY=sk-...}
```

## Production Configuration

### Environment Variables

**Required:**

```bash
# LLM Configuration
export RAPIDAI_LLM_PROVIDER=anthropic
export RAPIDAI_LLM_MODEL=claude-3-haiku-20240307
export RAPIDAI_LLM_API_KEY=sk-ant-...

# App Configuration
export RAPIDAI_APP_DEBUG=false
export RAPIDAI_APP_HOST=0.0.0.0
export RAPIDAI_APP_PORT=8000
```

**Optional (Production):**

```bash
# Redis for caching
export RAPIDAI_CACHE_BACKEND=redis
export RAPIDAI_CACHE_REDIS_URL=redis://redis:6379

# Redis for memory
export RAPIDAI_MEMORY_BACKEND=redis
export RAPIDAI_MEMORY_REDIS_URL=redis://redis:6379

# Redis for background jobs
export RAPIDAI_BACKGROUND_BACKEND=redis
export RAPIDAI_BACKGROUND_REDIS_URL=redis://redis:6379
```

### Configuration File

Create `config.production.yaml`:

```yaml
app:
  title: Production App
  debug: false
  host: 0.0.0.0
  port: 8000

llm:
  provider: anthropic
  model: claude-3-haiku-20240307
  temperature: 0.7
  max_tokens: 2048

cache:
  backend: redis
  ttl: 7200
  redis_url: ${REDIS_URL}

memory:
  backend: redis
  max_messages: 500
  redis_url: ${REDIS_URL}

rag:
  top_k: 10
  vectordb:
    persist_directory: /data/chroma
```

**Load in app:**

```python
from rapidai import App
from rapidai.config import load_config
import os

env = os.getenv("ENVIRONMENT", "development")
config = load_config(f"config.{env}.yaml")

app = App(title=config.app.title, debug=config.app.debug)
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "app.py"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - RAPIDAI_LLM_API_KEY=${RAPIDAI_LLM_API_KEY}
      - RAPIDAI_CACHE_BACKEND=redis
      - RAPIDAI_CACHE_REDIS_URL=redis://redis:6379
      - RAPIDAI_MEMORY_BACKEND=redis
      - RAPIDAI_MEMORY_REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

### Build and Run

```bash
# Build image
docker build -t rapidai-app .

# Run container
docker run -p 8000:8000 \
  -e RAPIDAI_LLM_API_KEY=sk-... \
  rapidai-app

# Or use docker-compose
docker-compose up -d
```

## Health Checks

Add health check endpoint:

```python
from rapidai import App

app = App()

@app.route("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

@app.route("/ready")
async def ready():
    """Readiness check endpoint."""
    # Check dependencies
    try:
        # Test Redis connection
        cache = get_cache()
        await cache.get("health_check")
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}, 503
```

**Configure in platforms:**

Vercel:
```json
{
  "healthCheck": {
    "path": "/health"
  }
}
```

Railway:
```toml
[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 10
```

Render:
```yaml
services:
  - type: web
    healthCheckPath: /health
```

## Monitoring

### Add Monitoring Endpoint

```python
from rapidai.monitoring import get_collector, get_dashboard_html

@app.route("/metrics")
async def metrics():
    """Metrics dashboard."""
    return get_dashboard_html()

@app.route("/metrics/json")
async def metrics_json():
    """Metrics as JSON."""
    collector = get_collector()
    return collector.get_summary()
```

### External Monitoring

**Prometheus:**

```python
@app.route("/metrics/prometheus")
async def prometheus():
    """Prometheus metrics."""
    collector = get_collector()
    summary = collector.get_summary()

    metrics = []
    metrics.append("# HELP rapidai_requests_total Total requests")
    metrics.append("# TYPE rapidai_requests_total counter")
    metrics.append(f"rapidai_requests_total {summary['total_requests']}")

    return {"body": "\n".join(metrics), "headers": {"Content-Type": "text/plain"}}
```

**CloudWatch:**

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

@app.on_interval(seconds=60)
async def push_metrics():
    """Push metrics to CloudWatch."""
    collector = get_collector()
    summary = collector.get_summary()

    cloudwatch.put_metric_data(
        Namespace='RapidAI',
        MetricData=[
            {
                'MetricName': 'Requests',
                'Value': summary['total_requests'],
                'Unit': 'Count'
            },
            {
                'MetricName': 'ErrorRate',
                'Value': 1 - summary['success_rate'],
                'Unit': 'Percent'
            }
        ]
    )
```

## Scaling Strategies

### Horizontal Scaling

**Multiple Instances:**

Railway:
```toml
[deploy]
numReplicas = 3
```

Render:
```yaml
services:
  - type: web
    numInstances: 3
```

**Load Balancing:**

All platforms provide automatic load balancing across replicas.

### Vertical Scaling

**Memory Limits:**

Railway:
```bash
railway service settings --memory 2048
```

Render:
```yaml
services:
  - type: web
    plan: standard  # 512 MB RAM
```

Lambda:
```bash
aws lambda update-function-configuration \
  --function-name rapidai-app \
  --memory-size 1024
```

### Caching Strategy

Use Redis for shared caching:

```python
from rapidai.cache import cache

@app.route("/chat")
@cache(ttl=3600, backend="redis")
async def chat(message: str):
    # Shared cache across instances
    return await llm.complete(message)
```

## Security Best Practices

### API Keys

**Never commit API keys:**

```python
# ❌ Don't do this
llm = LLM(api_key="sk-ant-...")

# ✅ Use environment variables
llm = LLM()  # Reads from RAPIDAI_LLM_API_KEY
```

**Use secrets management:**

Vercel:
```bash
vercel secrets add rapidai-api-key sk-...
```

Railway:
```bash
railway variables set RAPIDAI_LLM_API_KEY=sk-...
```

### HTTPS

All platforms provide automatic HTTPS:

- Vercel: Automatic with *.vercel.app
- Railway: Automatic with *.railway.app
- Render: Automatic with *.onrender.com
- Lambda: Use API Gateway with custom domain

### Rate Limiting

```python
from rapidai.middleware import RateLimiter

app.add_middleware(
    RateLimiter,
    requests_per_minute=60,
    burst_size=10
)
```

### CORS

```python
from rapidai.middleware import CORS

app.add_middleware(
    CORS,
    allow_origins=["https://myapp.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"]
)
```

## Troubleshooting

### Build Failures

**Check Python version:**

```toml
# railway.toml
[build]
nixpacksPython = "3.11"
```

```yaml
# render.yaml
services:
  - type: web
    runtime: python3.11
```

**Missing dependencies:**

Ensure all dependencies in `requirements.txt`:

```bash
pip freeze > requirements.txt
```

### Timeout Issues

**Increase timeouts:**

Railway:
```toml
[deploy]
healthcheckTimeout = 30
```

Lambda:
```bash
aws lambda update-function-configuration \
  --timeout 60
```

### Memory Issues

**Monitor memory usage:**

```python
import psutil

@app.route("/stats")
async def stats():
    memory = psutil.Process().memory_info()
    return {
        "memory_mb": memory.rss / 1024 / 1024,
        "percent": psutil.virtual_memory().percent
    }
```

**Increase memory:**

See Vertical Scaling section above.

## Next Steps

- [CLI Reference](../reference/cli.html) - CLI deployment commands
- [Configuration Reference](../reference/configuration.html) - All configuration options
- [Monitoring](../advanced/monitoring.html) - Production monitoring setup
- [Testing](../advanced/testing.html) - Test before deploying
