"""Monitoring and observability for RapidAI."""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

from .exceptions import RapidAIException


class MonitoringError(RapidAIException):
    """Monitoring-related errors."""

    pass


@dataclass
class Metric:
    """Represents a metric measurement."""

    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class RequestMetrics:
    """Metrics for a single request."""

    endpoint: str
    method: str
    duration: float
    status_code: int
    timestamp: datetime = field(default_factory=datetime.now)
    tokens_used: Optional[int] = None
    model: Optional[str] = None
    cost: Optional[float] = None
    error: Optional[str] = None


@dataclass
class ModelUsage:
    """Token usage and cost for a model."""

    model: str
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_cost: float = 0.0
    request_count: int = 0

    def add_tokens(
        self,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        cost: float = 0.0,
    ) -> None:
        """Add token usage."""
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens
        self.total_tokens += prompt_tokens + completion_tokens
        self.total_cost += cost
        self.request_count += 1


# Pricing per 1M tokens (as of 2024)
MODEL_PRICING = {
    # Anthropic Claude
    "claude-3-opus-20240229": {"prompt": 15.00, "completion": 75.00},
    "claude-3-sonnet-20240229": {"prompt": 3.00, "completion": 15.00},
    "claude-3-haiku-20240307": {"prompt": 0.25, "completion": 1.25},
    "claude-3-5-sonnet-20241022": {"prompt": 3.00, "completion": 15.00},
    # OpenAI
    "gpt-4o": {"prompt": 5.00, "completion": 15.00},
    "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
    "gpt-4-turbo": {"prompt": 10.00, "completion": 30.00},
    "gpt-3.5-turbo": {"prompt": 0.50, "completion": 1.50},
}


def calculate_cost(
    model: str,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
) -> float:
    """Calculate cost for model usage.

    Args:
        model: Model name
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens

    Returns:
        Cost in USD
    """
    pricing = MODEL_PRICING.get(model, {"prompt": 0, "completion": 0})
    prompt_cost = (prompt_tokens / 1_000_000) * pricing["prompt"]
    completion_cost = (completion_tokens / 1_000_000) * pricing["completion"]
    return prompt_cost + completion_cost


class MetricsCollector:
    """Collects and stores metrics."""

    def __init__(self) -> None:
        """Initialize metrics collector."""
        self._metrics: List[Metric] = []
        self._requests: List[RequestMetrics] = []
        self._model_usage: Dict[str, ModelUsage] = {}
        self._start_time = datetime.now()

    def record_metric(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a metric.

        Args:
            name: Metric name
            value: Metric value
            tags: Optional tags
        """
        metric = Metric(name=name, value=value, tags=tags or {})
        self._metrics.append(metric)

    def record_request(
        self,
        endpoint: str,
        method: str,
        duration: float,
        status_code: int,
        tokens_used: Optional[int] = None,
        model: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        """Record request metrics.

        Args:
            endpoint: Request endpoint
            method: HTTP method
            duration: Duration in seconds
            status_code: HTTP status code
            tokens_used: Total tokens used
            model: Model name
            error: Error message if any
        """
        # Calculate cost if model and tokens provided
        cost = None
        if model and tokens_used:
            # Estimate 50/50 split for prompt/completion
            prompt_tokens = tokens_used // 2
            completion_tokens = tokens_used - prompt_tokens
            cost = calculate_cost(model, prompt_tokens, completion_tokens)

        request = RequestMetrics(
            endpoint=endpoint,
            method=method,
            duration=duration,
            status_code=status_code,
            tokens_used=tokens_used,
            model=model,
            cost=cost,
            error=error,
        )
        self._requests.append(request)

        # Update model usage
        if model and tokens_used:
            if model not in self._model_usage:
                self._model_usage[model] = ModelUsage(model=model)
            self._model_usage[model].add_tokens(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                cost=cost or 0.0,
            )

    def get_metrics(
        self,
        name: Optional[str] = None,
        since: Optional[datetime] = None,
    ) -> List[Metric]:
        """Get recorded metrics.

        Args:
            name: Optional metric name filter
            since: Optional time filter

        Returns:
            List of metrics
        """
        metrics = self._metrics

        if name:
            metrics = [m for m in metrics if m.name == name]

        if since:
            metrics = [m for m in metrics if m.timestamp >= since]

        return metrics

    def get_requests(
        self,
        endpoint: Optional[str] = None,
        since: Optional[datetime] = None,
    ) -> List[RequestMetrics]:
        """Get request metrics.

        Args:
            endpoint: Optional endpoint filter
            since: Optional time filter

        Returns:
            List of request metrics
        """
        requests = self._requests

        if endpoint:
            requests = [r for r in requests if r.endpoint == endpoint]

        if since:
            requests = [r for r in requests if r.timestamp >= since]

        return requests

    def get_model_usage(self, model: Optional[str] = None) -> Dict[str, ModelUsage]:
        """Get model usage statistics.

        Args:
            model: Optional model filter

        Returns:
            Dictionary of model usage
        """
        if model:
            return {model: self._model_usage.get(model, ModelUsage(model=model))}
        return self._model_usage.copy()

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics.

        Returns:
            Summary dictionary
        """
        uptime = (datetime.now() - self._start_time).total_seconds()

        total_requests = len(self._requests)
        successful_requests = len([r for r in self._requests if r.status_code < 400])
        failed_requests = total_requests - successful_requests

        avg_duration = 0.0
        if self._requests:
            avg_duration = sum(r.duration for r in self._requests) / total_requests

        total_tokens = sum(u.total_tokens for u in self._model_usage.values())
        total_cost = sum(u.total_cost for u in self._model_usage.values())

        return {
            "uptime_seconds": uptime,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": successful_requests / total_requests if total_requests > 0 else 0.0,
            "average_duration": avg_duration,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "models_used": len(self._model_usage),
        }

    def clear(self) -> None:
        """Clear all metrics."""
        self._metrics.clear()
        self._requests.clear()
        self._model_usage.clear()
        self._start_time = datetime.now()


# Global metrics collector
_collector: Optional[MetricsCollector] = None


def get_collector() -> MetricsCollector:
    """Get or create global metrics collector.

    Returns:
        MetricsCollector instance
    """
    global _collector
    if _collector is None:
        _collector = MetricsCollector()
    return _collector


def monitor(track_tokens: bool = False, track_cost: bool = False) -> Callable:
    """Decorator to monitor endpoint performance.

    Args:
        track_tokens: Track token usage (requires LLM integration)
        track_cost: Calculate and track costs

    Returns:
        Decorator function

    Example:
        ```python
        @app.route("/chat", methods=["POST"])
        @monitor(track_tokens=True, track_cost=True)
        async def chat(message: str):
            response = await llm.complete(message)
            return {"response": response}
        ```
    """
    collector = get_collector()

    def decorator(func: Callable) -> Callable:
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            error = None
            status_code = 200
            tokens_used = None
            model = None

            try:
                # Execute function
                result = await func(*args, **kwargs)

                # Extract tokens and model if available
                if track_tokens and isinstance(result, dict):
                    tokens_used = result.get("tokens_used")
                    model = result.get("model")

                return result

            except Exception as e:
                error = str(e)
                status_code = 500
                raise

            finally:
                duration = time.time() - start_time

                # Record request
                collector.record_request(
                    endpoint=func.__name__,
                    method="POST",  # Default, could be extracted from request
                    duration=duration,
                    status_code=status_code,
                    tokens_used=tokens_used,
                    model=model,
                    error=error,
                )

        return wrapper

    return decorator


def get_dashboard_html() -> str:
    """Generate HTML dashboard for metrics.

    Returns:
        HTML string
    """
    collector = get_collector()
    summary = collector.get_summary()
    model_usage = collector.get_model_usage()

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>RapidAI Metrics Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: #fff;
            padding: 2rem;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ margin-bottom: 2rem; font-size: 2.5rem; }}
        .card {{
            background: #1a1a1a;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid #333;
        }}
        .card h2 {{ margin-bottom: 1rem; color: #00ffff; }}
        .metric {{
            display: flex;
            justify-content: space-between;
            padding: 0.75rem 0;
            border-bottom: 1px solid #333;
        }}
        .metric:last-child {{ border-bottom: none; }}
        .metric-label {{ color: #999; }}
        .metric-value {{ font-weight: bold; color: #00ffff; }}
        .success {{ color: #00ff00; }}
        .error {{ color: #ff0000; }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #333;
        }}
        th {{ color: #00ffff; }}
        .refresh {{
            background: #00ffff;
            color: #000;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            margin-bottom: 1rem;
        }}
        .refresh:hover {{ background: #00cccc; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 RapidAI Metrics</h1>

        <button class="refresh" onclick="location.reload()">↻ Refresh</button>

        <div class="card">
            <h2>Overview</h2>
            <div class="metric">
                <span class="metric-label">Uptime</span>
                <span class="metric-value">{summary['uptime_seconds']:.2f}s</span>
            </div>
            <div class="metric">
                <span class="metric-label">Total Requests</span>
                <span class="metric-value">{summary['total_requests']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Successful Requests</span>
                <span class="metric-value success">{summary['successful_requests']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Failed Requests</span>
                <span class="metric-value error">{summary['failed_requests']}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Success Rate</span>
                <span class="metric-value">{summary['success_rate']:.1%}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Average Duration</span>
                <span class="metric-value">{summary['average_duration']:.3f}s</span>
            </div>
        </div>

        <div class="card">
            <h2>LLM Usage</h2>
            <div class="metric">
                <span class="metric-label">Total Tokens</span>
                <span class="metric-value">{summary['total_tokens']:,}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Total Cost</span>
                <span class="metric-value">${summary['total_cost']:.4f}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Models Used</span>
                <span class="metric-value">{summary['models_used']}</span>
            </div>
        </div>

        <div class="card">
            <h2>Model Breakdown</h2>
            <table>
                <thead>
                    <tr>
                        <th>Model</th>
                        <th>Requests</th>
                        <th>Tokens</th>
                        <th>Cost</th>
                    </tr>
                </thead>
                <tbody>
"""

    for model, usage in model_usage.items():
        html += f"""
                    <tr>
                        <td>{model}</td>
                        <td>{usage.request_count}</td>
                        <td>{usage.total_tokens:,}</td>
                        <td>${usage.total_cost:.4f}</td>
                    </tr>
"""

    html += """
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>
"""

    return html
