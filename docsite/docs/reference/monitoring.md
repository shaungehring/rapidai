# Monitoring API Reference

Complete API reference for RapidAI's monitoring and observability system.

## Decorator

### monitor

```python
def monitor(
    track_tokens: bool = False,
    track_cost: bool = False
) -> Callable
```

Decorator to monitor endpoint performance.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `track_tokens` | `bool` | `False` | Track token usage (requires LLM integration) |
| `track_cost` | `bool` | `False` | Calculate and track costs |

**Returns:** Decorator function

**Example:**

```python
from rapidai.monitoring import monitor

@app.route("/chat", methods=["POST"])
@monitor(track_tokens=True, track_cost=True)
async def chat(message: str):
    response = await llm.complete(message)
    return {
        "response": response,
        "tokens_used": 150,
        "model": "claude-3-haiku-20240307"
    }
```

## Classes

### MetricsCollector

```python
class MetricsCollector:
    def __init__(self) -> None
```

Collects and stores metrics.

**Methods:**

#### `record_metric`

```python
def record_metric(
    self,
    name: str,
    value: float,
    tags: Optional[Dict[str, str]] = None
) -> None
```

Record a metric.

**Parameters:**

- `name` (`str`) - Metric name
- `value` (`float`) - Metric value
- `tags` (`Dict[str, str]`, optional) - Optional tags

**Example:**

```python
collector.record_metric(
    name="api.latency",
    value=0.523,
    tags={"endpoint": "/chat"}
)
```

#### `record_request`

```python
def record_request(
    self,
    endpoint: str,
    method: str,
    duration: float,
    status_code: int,
    tokens_used: Optional[int] = None,
    model: Optional[str] = None,
    error: Optional[str] = None
) -> None
```

Record request metrics.

**Parameters:**

- `endpoint` (`str`) - Request endpoint
- `method` (`str`) - HTTP method
- `duration` (`float`) - Duration in seconds
- `status_code` (`int`) - HTTP status code
- `tokens_used` (`int`, optional) - Total tokens used
- `model` (`str`, optional) - Model name
- `error` (`str`, optional) - Error message if any

#### `get_metrics`

```python
def get_metrics(
    self,
    name: Optional[str] = None,
    since: Optional[datetime] = None
) -> List[Metric]
```

Get recorded metrics.

**Parameters:**

- `name` (`str`, optional) - Optional metric name filter
- `since` (`datetime`, optional) - Optional time filter

**Returns:** `List[Metric]` - List of metrics

#### `get_requests`

```python
def get_requests(
    self,
    endpoint: Optional[str] = None,
    since: Optional[datetime] = None
) -> List[RequestMetrics]
```

Get request metrics.

**Parameters:**

- `endpoint` (`str`, optional) - Optional endpoint filter
- `since` (`datetime`, optional) - Optional time filter

**Returns:** `List[RequestMetrics]` - List of request metrics

#### `get_model_usage`

```python
def get_model_usage(
    self,
    model: Optional[str] = None
) -> Dict[str, ModelUsage]
```

Get model usage statistics.

**Parameters:**

- `model` (`str`, optional) - Optional model filter

**Returns:** `Dict[str, ModelUsage]` - Dictionary of model usage

#### `get_summary`

```python
def get_summary(self) -> Dict[str, Any]
```

Get summary statistics.

**Returns:** Dictionary with:

```python
{
    "uptime_seconds": float,
    "total_requests": int,
    "successful_requests": int,
    "failed_requests": int,
    "success_rate": float,
    "average_duration": float,
    "total_tokens": int,
    "total_cost": float,
    "models_used": int
}
```

#### `clear`

```python
def clear(self) -> None
```

Clear all metrics.

### Metric

```python
@dataclass
class Metric:
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str]
```

Represents a metric measurement.

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Metric name |
| `value` | `float` | Metric value |
| `timestamp` | `datetime` | When metric was recorded |
| `tags` | `Dict[str, str]` | Metric tags |

### RequestMetrics

```python
@dataclass
class RequestMetrics:
    endpoint: str
    method: str
    duration: float
    status_code: int
    timestamp: datetime
    tokens_used: Optional[int] = None
    model: Optional[str] = None
    cost: Optional[float] = None
    error: Optional[str] = None
```

Metrics for a single request.

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `endpoint` | `str` | Request endpoint |
| `method` | `str` | HTTP method |
| `duration` | `float` | Request duration in seconds |
| `status_code` | `int` | HTTP status code |
| `timestamp` | `datetime` | Request timestamp |
| `tokens_used` | `int` | Total tokens used |
| `model` | `str` | Model name |
| `cost` | `float` | Request cost in USD |
| `error` | `str` | Error message if any |

### ModelUsage

```python
@dataclass
class ModelUsage:
    model: str
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_cost: float = 0.0
    request_count: int = 0
```

Token usage and cost for a model.

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `model` | `str` | Model name |
| `total_tokens` | `int` | Total tokens used |
| `prompt_tokens` | `int` | Prompt tokens |
| `completion_tokens` | `int` | Completion tokens |
| `total_cost` | `float` | Total cost in USD |
| `request_count` | `int` | Number of requests |

**Methods:**

#### `add_tokens`

```python
def add_tokens(
    self,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    cost: float = 0.0
) -> None
```

Add token usage.

## Functions

### get_collector

```python
def get_collector() -> MetricsCollector
```

Get or create global metrics collector.

**Returns:** `MetricsCollector` - Global collector instance

**Example:**

```python
from rapidai.monitoring import get_collector

collector = get_collector()
summary = collector.get_summary()
```

### calculate_cost

```python
def calculate_cost(
    model: str,
    prompt_tokens: int = 0,
    completion_tokens: int = 0
) -> float
```

Calculate cost for model usage.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | `str` | - | Model name |
| `prompt_tokens` | `int` | `0` | Number of prompt tokens |
| `completion_tokens` | `int` | `0` | Number of completion tokens |

**Returns:** `float` - Cost in USD

**Example:**

```python
from rapidai.monitoring import calculate_cost

cost = calculate_cost(
    model="claude-3-haiku-20240307",
    prompt_tokens=100,
    completion_tokens=50
)
# Returns: 0.0000875
```

### get_dashboard_html

```python
def get_dashboard_html() -> str
```

Generate HTML dashboard for metrics.

**Returns:** `str` - HTML string

**Example:**

```python
from rapidai.monitoring import get_dashboard_html

@app.route("/metrics")
async def dashboard():
    return get_dashboard_html()
```

## Model Pricing

Pricing per 1M tokens (prompt/completion):

**Anthropic Claude:**

| Model | Prompt | Completion |
|-------|--------|------------|
| claude-3-opus-20240229 | $15.00 | $75.00 |
| claude-3-sonnet-20240229 | $3.00 | $15.00 |
| claude-3-haiku-20240307 | $0.25 | $1.25 |
| claude-3-5-sonnet-20241022 | $3.00 | $15.00 |

**OpenAI:**

| Model | Prompt | Completion |
|-------|--------|------------|
| gpt-4o | $5.00 | $15.00 |
| gpt-4o-mini | $0.15 | $0.60 |
| gpt-4-turbo | $10.00 | $30.00 |
| gpt-3.5-turbo | $0.50 | $1.50 |

## Complete Example

```python
from rapidai import App, LLM
from rapidai.monitoring import (
    monitor,
    get_collector,
    get_dashboard_html,
    calculate_cost
)

app = App()
llm = LLM("claude-3-haiku-20240307")

@app.route("/chat", methods=["POST"])
@monitor(track_tokens=True, track_cost=True)
async def chat(message: str):
    """Monitored chat endpoint."""
    response = await llm.complete(message)
    return {
        "response": response,
        "tokens_used": 150,
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
        "models": {
            model: {
                "tokens": usage.total_tokens,
                "cost": usage.total_cost,
                "requests": usage.request_count
            }
            for model, usage in collector.get_model_usage().items()
        }
    }

@app.route("/metrics/cost")
async def cost_estimate(
    model: str,
    prompt_tokens: int,
    completion_tokens: int
):
    """Estimate cost for token usage."""
    cost = calculate_cost(model, prompt_tokens, completion_tokens)
    return {
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "cost": cost,
        "cost_formatted": f"${cost:.6f}"
    }

@app.route("/metrics/custom")
async def custom_metric():
    """Record custom metric."""
    collector = get_collector()
    collector.record_metric(
        name="custom.event",
        value=1.0,
        tags={"type": "important"}
    )
    return {"recorded": True}
```

## See Also

- [Monitoring Guide](../advanced/monitoring.html) - Complete usage guide
- [Background Jobs](background.html) - Monitor async tasks
- [Testing](testing.html) - Test monitored endpoints
