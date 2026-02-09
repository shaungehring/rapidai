"""Example: Monitoring and Metrics with RapidAI.

This example demonstrates:
1. Using @monitor decorator for automatic metrics
2. Token usage and cost tracking
3. Built-in metrics dashboard
4. Custom metrics
5. Model usage statistics
"""

from rapidai import App, LLM, monitor, get_collector, get_dashboard_html, calculate_cost
from rapidai.memory import ConversationMemory

app = App(title="Monitoring Dashboard Example")
llm = LLM("claude-3-haiku-20240307")
memory = ConversationMemory()


# Monitored chat endpoint with token tracking
@app.route("/chat", methods=["POST"])
@monitor(track_tokens=True, track_cost=True)
async def chat(user_id: str, message: str):
    """Chat endpoint with automatic monitoring."""
    # Add to memory
    memory.add_message(user_id, "user", message)

    # Get history
    history = memory.get_history(user_id)

    # Generate response
    response = await llm.chat(history)

    # Add to memory
    memory.add_message(user_id, "assistant", response)

    # Return with tracking info (required for token tracking)
    return {
        "response": response,
        "tokens_used": 150,  # In real app, get from LLM response
        "model": llm.model,
    }


# Basic monitored endpoint
@app.route("/summarize", methods=["POST"])
@monitor(track_tokens=True, track_cost=True)
async def summarize(text: str):
    """Summarize text with monitoring."""
    summary = await llm.complete(f"Summarize this in one sentence:\n\n{text}")

    return {"summary": summary, "tokens_used": 100, "model": llm.model}


# Metrics dashboard
@app.route("/metrics/dashboard", methods=["GET"])
async def metrics_dashboard():
    """Serve interactive metrics dashboard."""
    html = get_dashboard_html()
    return {"body": html, "headers": {"Content-Type": "text/html; charset=utf-8"}}


# Metrics API
@app.route("/metrics/api", methods=["GET"])
async def metrics_api():
    """Get metrics as JSON."""
    collector = get_collector()

    return {
        "summary": collector.get_summary(),
        "models": {
            model: {
                "total_tokens": usage.total_tokens,
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_cost": usage.total_cost,
                "request_count": usage.request_count,
            }
            for model, usage in collector.get_model_usage().items()
        },
    }


# Model usage stats
@app.route("/metrics/models", methods=["GET"])
async def model_stats():
    """Get detailed model usage statistics."""
    collector = get_collector()
    usage = collector.get_model_usage()

    stats = []
    for model, model_usage in usage.items():
        stats.append(
            {
                "model": model,
                "total_tokens": model_usage.total_tokens,
                "total_cost": f"${model_usage.total_cost:.4f}",
                "requests": model_usage.request_count,
                "avg_tokens_per_request": (
                    model_usage.total_tokens / model_usage.request_count
                    if model_usage.request_count > 0
                    else 0
                ),
            }
        )

    return {"models": stats, "total": len(stats)}


# Cost estimation
@app.route("/cost/estimate", methods=["GET"])
async def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int):
    """Estimate cost for token usage."""
    cost = calculate_cost(model=model, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)

    return {
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "cost": cost,
        "cost_formatted": f"${cost:.6f}",
    }


# Custom metrics
@app.route("/custom/metric", methods=["POST"])
async def record_custom_metric(name: str, value: float, tags: dict = None):
    """Record a custom metric."""
    collector = get_collector()
    collector.record_metric(name=name, value=value, tags=tags or {})

    return {"recorded": True, "metric": name, "value": value}


# Clear metrics
@app.route("/metrics/clear", methods=["POST"])
async def clear_metrics():
    """Clear all metrics (use with caution!)."""
    collector = get_collector()
    collector.clear()

    return {"status": "cleared", "message": "All metrics have been cleared"}


# Health check
@app.route("/health", methods=["GET"])
async def health():
    """Health check with basic metrics."""
    collector = get_collector()
    summary = collector.get_summary()

    return {
        "status": "healthy",
        "uptime": summary["uptime_seconds"],
        "total_requests": summary["total_requests"],
        "success_rate": summary["success_rate"],
    }


if __name__ == "__main__":
    print("Monitoring Dashboard Example")
    print("=" * 50)
    print("\nEndpoints:")
    print("  POST /chat                   - Monitored chat endpoint")
    print("  POST /summarize              - Monitored summarization")
    print("  GET  /metrics/dashboard      - Interactive dashboard")
    print("  GET  /metrics/api            - Metrics as JSON")
    print("  GET  /metrics/models         - Model usage stats")
    print("  GET  /cost/estimate          - Estimate costs")
    print("  POST /custom/metric          - Record custom metric")
    print("  POST /metrics/clear          - Clear all metrics")
    print("\nDashboard:")
    print("  http://localhost:8000/metrics/dashboard")
    print("\nExample usage:")
    print('  curl -X POST http://localhost:8000/chat \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"user_id": "user123", "message": "Hello!"}\'')
    print("\n  curl http://localhost:8000/metrics/api")
    print("\nStarting server on http://localhost:8000")
    print("=" * 50)

    app.run(port=8000)
