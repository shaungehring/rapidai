# Monitoring

RapidAI includes built-in monitoring and observability features for tracking token usage, costs, latency, and performance metrics.

## Quick Start

```python
from rapidai import App, LLM
from rapidai.monitoring import monitor, get_dashboard_html

app = App()
llm = LLM("claude-3-haiku-20240307")

@app.route("/chat", methods=["POST"])
@monitor(track_tokens=True, track_cost=True)
async def chat(message: str):
    response = await llm.complete(message)
    return {
        "response": response,
        "tokens_used": 150,  # Add if available
        "model": "claude-3-haiku-20240307"
    }

@app.route("/metrics")
async def metrics():
    # Serve built-in dashboard
    return get_dashboard_html()

if __name__ == "__main__":
    app.run(port=8000)
```

Visit `http://localhost:8000/metrics` to see the dashboard!

## Features

- **Token Tracking** - Monitor token usage per model
- **Cost Calculation** - Automatic cost tracking for all providers
- **Latency Metrics** - Request duration and performance
- **Error Tracking** - Success rates and error monitoring
- **Built-in Dashboard** - Beautiful HTML dashboard with auto-refresh
- **Metrics API** - Programmatic access to all metrics

## @monitor Decorator

### Basic Usage

```python
from rapidai.monitoring import monitor

@app.route("/endpoint", methods=["POST"])
@monitor()
async def my_endpoint(data: str):
    # Request metrics automatically tracked
    return {"result": "success"}
```

### With Token Tracking

```python
@app.route("/chat", methods=["POST"])
@monitor(track_tokens=True, track_cost=True)
async def chat(message: str):
    response = await llm.complete(message)

    # Include these fields for tracking
    return {
        "response": response,
        "tokens_used": 100,  # Total tokens
        "model": "claude-3-haiku-20240307"
    }
```

## Metrics Collector

### Recording Custom Metrics

```python
from rapidai.monitoring import get_collector

collector = get_collector()

# Record a metric
collector.record_metric(
    name="custom.metric",
    value=42.5,
    tags={"environment": "production"}
)
```

### Recording Requests

```python
collector.record_request(
    endpoint="/chat",
    method="POST",
    duration=0.523,  # seconds
    status_code=200,
    tokens_used=150,
    model="claude-3-haiku-20240307",
    error=None
)
```

### Getting Metrics

```python
# Get all metrics
metrics = collector.get_metrics()

# Get filtered metrics
recent_metrics = collector.get_metrics(
    name="custom.metric",
    since=datetime.now() - timedelta(hours=1)
)

# Get request metrics
requests = collector.get_requests(
    endpoint="/chat",
    since=datetime.now() - timedelta(minutes=30)
)
```

## Model Usage Tracking

### Automatic Tracking

When using `@monitor(track_tokens=True, track_cost=True)`, token usage and costs are automatically tracked:

```python
@monitor(track_tokens=True, track_cost=True)
async def generate_text(prompt: str):
    response = await llm.complete(prompt)
    return {
        "response": response,
        "tokens_used": 200,
        "model": "gpt-4o-mini"
    }
```

### Get Model Usage

```python
collector = get_collector()

# Get all model usage
usage = collector.get_model_usage()

for model, stats in usage.items():
    print(f"Model: {model}")
    print(f"  Total tokens: {stats.total_tokens}")
    print(f"  Total cost: ${stats.total_cost:.4f}")
    print(f"  Requests: {stats.request_count}")
```

### Get Specific Model

```python
# Get usage for specific model
claude_usage = collector.get_model_usage(model="claude-3-haiku-20240307")
```

## Cost Calculation

RapidAI includes pricing for major providers:

### Supported Models

**Anthropic Claude:**
- claude-3-opus-20240229: $15/$75 per 1M tokens
- claude-3-sonnet-20240229: $3/$15 per 1M tokens
- claude-3-haiku-20240307: $0.25/$1.25 per 1M tokens
- claude-3-5-sonnet-20241022: $3/$15 per 1M tokens

**OpenAI:**
- gpt-4o: $5/$15 per 1M tokens
- gpt-4o-mini: $0.15/$0.60 per 1M tokens
- gpt-4-turbo: $10/$30 per 1M tokens
- gpt-3.5-turbo: $0.50/$1.50 per 1M tokens

### Manual Cost Calculation

```python
from rapidai.monitoring import calculate_cost

cost = calculate_cost(
    model="claude-3-haiku-20240307",
    prompt_tokens=100,
    completion_tokens=50
)
print(f"Cost: ${cost:.6f}")
```

## Dashboard

### Built-in HTML Dashboard

```python
from rapidai.monitoring import get_dashboard_html

@app.route("/metrics")
async def metrics_dashboard():
    html = get_dashboard_html()
    return {"body": html, "headers": {"Content-Type": "text/html"}}
```

**Dashboard Features:**
- Real-time metrics with auto-refresh (30s)
- Overview statistics
- LLM usage breakdown
- Model-specific metrics
- Request counts and success rates
- Average latency
- Total costs

### Custom Dashboard

```python
from rapidai.monitoring import get_collector

@app.route("/api/metrics")
async def api_metrics():
    collector = get_collector()
    summary = collector.get_summary()

    return {
        "uptime": summary["uptime_seconds"],
        "total_requests": summary["total_requests"],
        "success_rate": summary["success_rate"],
        "avg_duration": summary["average_duration"],
        "total_tokens": summary["total_tokens"],
        "total_cost": summary["total_cost"]
    }
```

## Summary Statistics

```python
collector = get_collector()
summary = collector.get_summary()

# Returns:
# {
#     "uptime_seconds": 3600.0,
#     "total_requests": 150,
#     "successful_requests": 145,
#     "failed_requests": 5,
#     "success_rate": 0.967,
#     "average_duration": 0.523,
#     "total_tokens": 15000,
#     "total_cost": 0.45,
#     "models_used": 2
# }
```

## Complete Example: Monitored Chat Application

```python
from rapidai import App, LLM
from rapidai.monitoring import monitor, get_collector, get_dashboard_html
from rapidai.memory import ConversationMemory

app = App(title="Monitored Chat")
llm = LLM("claude-3-haiku-20240307")
memory = ConversationMemory()

@app.route("/chat", methods=["POST"])
@monitor(track_tokens=True, track_cost=True)
async def chat(user_id: str, message: str):
    """Chat endpoint with monitoring."""
    # Add to memory
    memory.add_message(user_id, "user", message)

    # Get history
    history = memory.get_history(user_id)

    # Generate response
    response = await llm.chat(history)

    # Add response to memory
    memory.add_message(user_id, "assistant", response)

    # Return with tracking info
    return {
        "response": response,
        "tokens_used": 150,  # Would come from LLM
        "model": "claude-3-haiku-20240307"
    }

@app.route("/metrics/dashboard")
async def dashboard():
    """Serve metrics dashboard."""
    return get_dashboard_html()

@app.route("/metrics/api")
async def metrics_api():
    """Get metrics as JSON."""
    collector = get_collector()

    return {
        "summary": collector.get_summary(),
        "model_usage": {
            model: {
                "tokens": usage.total_tokens,
                "cost": usage.total_cost,
                "requests": usage.request_count
            }
            for model, usage in collector.get_model_usage().items()
        }
    }

@app.route("/metrics/clear", methods=["POST"])
async def clear_metrics():
    """Clear all metrics."""
    collector = get_collector()
    collector.clear()
    return {"status": "cleared"}

if __name__ == "__main__":
    print("Dashboard: http://localhost:8000/metrics/dashboard")
    print("API: http://localhost:8000/metrics/api")
    app.run(port=8000)
```

## Best Practices

### 1. Monitor All LLM Endpoints

```python
# Always use @monitor for LLM endpoints
@app.route("/generate", methods=["POST"])
@monitor(track_tokens=True, track_cost=True)
async def generate(prompt: str):
    ...
```

### 2. Include Token Information

```python
@monitor(track_tokens=True, track_cost=True)
async def chat(message: str):
    response = await llm.complete(message)

    # Always return token info if available
    return {
        "response": response,
        "tokens_used": response.usage.total_tokens,  # From LLM
        "model": llm.model
    }
```

### 3. Set Up Alerts

```python
from rapidai.monitoring import get_collector

@app.route("/health")
async def health_check():
    collector = get_collector()
    summary = collector.get_summary()

    # Alert if error rate too high
    if summary["success_rate"] < 0.95:
        # Send alert
        await send_alert("High error rate!")

    # Alert if costs too high
    if summary["total_cost"] > 10.0:
        await send_alert("High costs!")

    return {"status": "healthy", "metrics": summary}
```

### 4. Export Metrics

```python
@app.route("/metrics/export")
async def export_metrics():
    """Export metrics for external monitoring."""
    collector = get_collector()

    return {
        "timestamp": datetime.now().isoformat(),
        "metrics": collector.get_summary(),
        "models": collector.get_model_usage()
    }
```

### 5. Track Custom Business Metrics

```python
from rapidai.monitoring import get_collector

@app.route("/purchase", methods=["POST"])
async def process_purchase(amount: float):
    collector = get_collector()

    # Track business metrics
    collector.record_metric("revenue", amount)
    collector.record_metric("purchases", 1)

    return {"status": "success"}
```

### 6. Use Tags for Filtering

```python
collector.record_metric(
    name="api.latency",
    value=0.523,
    tags={
        "endpoint": "/chat",
        "environment": "production",
        "region": "us-east-1"
    }
)
```

## Integration with External Services

### Prometheus Export

```python
@app.route("/metrics/prometheus")
async def prometheus_metrics():
    """Export metrics in Prometheus format."""
    collector = get_collector()
    summary = collector.get_summary()

    metrics = []
    metrics.append(f"# HELP rapidai_requests_total Total number of requests")
    metrics.append(f"# TYPE rapidai_requests_total counter")
    metrics.append(f"rapidai_requests_total {summary['total_requests']}")

    metrics.append(f"# HELP rapidai_tokens_total Total tokens used")
    metrics.append(f"# TYPE rapidai_tokens_total counter")
    metrics.append(f"rapidai_tokens_total {summary['total_tokens']}")

    metrics.append(f"# HELP rapidai_cost_total Total cost in USD")
    metrics.append(f"# TYPE rapidai_cost_total counter")
    metrics.append(f"rapidai_cost_total {summary['total_cost']}")

    return {"body": "\\n".join(metrics), "headers": {"Content-Type": "text/plain"}}
```

### CloudWatch Integration

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

@app.on_interval(seconds=60)
async def push_to_cloudwatch():
    """Push metrics to AWS CloudWatch every minute."""
    collector = get_collector()
    summary = collector.get_summary()

    cloudwatch.put_metric_data(
        Namespace='RapidAI',
        MetricData=[
            {
                'MetricName': 'TotalTokens',
                'Value': summary['total_tokens'],
                'Unit': 'Count'
            },
            {
                'MetricName': 'TotalCost',
                'Value': summary['total_cost'],
                'Unit': 'None'
            }
        ]
    )
```

## Troubleshooting

### Metrics Not Showing

```python
# Ensure decorator is applied
@monitor(track_tokens=True)  # ✅ Correct
async def endpoint():
    ...

# Not decorated
async def endpoint():  # ❌ Won't track
    ...
```

### Token Costs Incorrect

```python
# Ensure you return the correct model name
@monitor(track_tokens=True, track_cost=True)
async def chat(message: str):
    return {
        "response": response,
        "tokens_used": 100,
        "model": llm.model  # ✅ Use actual model
    }
```

### Dashboard Not Loading

```python
# Ensure correct content type
@app.route("/metrics")
async def metrics():
    html = get_dashboard_html()
    # Return with HTML content type
    return {
        "body": html,
        "headers": {"Content-Type": "text/html; charset=utf-8"}
    }
```

## Next Steps

- See [API Reference](../reference/monitoring.html) for complete API documentation
- Learn about [Background Jobs](background.html) to monitor async tasks
- Check [Testing](testing.html) for testing monitored endpoints
