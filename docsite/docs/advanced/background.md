# Background Jobs

RapidAI provides a powerful background job system for running long-running tasks asynchronously with automatic retry logic and status tracking.

## Quick Start

```python
from rapidai import App
from rapidai.background import background

app = App()

@background(max_retries=3)
async def process_document(doc_id: str, user_id: str):
    # Long-running task
    # Process document, call APIs, etc.
    return {"doc_id": doc_id, "status": "processed"}

@app.route("/process", methods=["POST"])
async def enqueue_processing(doc_id: str, user_id: str):
    # Enqueue the job
    job_id = await process_document.enqueue(doc_id=doc_id, user_id=user_id)
    return {"job_id": job_id, "status": "queued"}

@app.route("/status/<job_id>", methods=["GET"])
async def check_status(job_id: str):
    # Check job status
    result = await process_document.get_result(job_id)

    return {
        "job_id": result.job_id,
        "status": result.status,
        "result": result.result,
        "error": result.error,
        "duration": result.duration
    }
```

## Features

- **Async Execution** - Run tasks in the background
- **Automatic Retries** - Exponential backoff on failures
- **Status Tracking** - Monitor job progress
- **Multiple Backends** - In-memory or Redis
- **Job Cancellation** - Cancel running jobs
- **Result Retrieval** - Get job results when complete

## Job Decorator

### Basic Usage

```python
from rapidai.background import background

@background()
async def send_email(to: str, subject: str, body: str):
    # Send email via API
    await email_service.send(to, subject, body)
    return {"sent": True}

# Enqueue job
job_id = await send_email.enqueue(
    to="user@example.com",
    subject="Hello",
    body="Welcome!"
)
```

### With Retry Logic

```python
@background(max_retries=5)
async def call_external_api(url: str):
    # Will retry up to 5 times with exponential backoff
    response = await http_client.get(url)
    return response.json()

# Retry delays: 2s, 4s, 8s, 16s, 32s
```

### Custom Queue

```python
from rapidai.background import background, RedisQueue

# Use Redis queue for persistence
redis_queue = RedisQueue(url="redis://localhost:6379")

@background(max_retries=3, queue=redis_queue)
async def important_task(data: dict):
    # Task persists across restarts
    return process(data)
```

## Job Status

Jobs can be in one of five states:

| Status | Description |
|--------|-------------|
| `pending` | Job queued, waiting to start |
| `running` | Job currently executing |
| `completed` | Job finished successfully |
| `failed` | Job failed after all retries |
| `cancelled` | Job was cancelled |

### Checking Status

```python
@app.route("/jobs/<job_id>", methods=["GET"])
async def get_job_status(job_id: str):
    result = await my_task.get_result(job_id)

    if result is None:
        return {"error": "Job not found"}, 404

    response = {
        "job_id": result.job_id,
        "status": result.status,
        "created_at": result.created_at.isoformat(),
        "attempts": result.attempts,
        "max_retries": result.max_retries
    }

    if result.is_done:
        response["completed_at"] = result.completed_at.isoformat()
        response["duration"] = result.duration

        if result.status == "completed":
            response["result"] = result.result
        elif result.status == "failed":
            response["error"] = result.error

    return response
```

## Job Backends

### In-Memory Queue

Default backend, suitable for development and single-server deployments:

```python
from rapidai.background import InMemoryQueue

queue = InMemoryQueue()

@background(queue=queue)
async def my_task(data: str):
    return {"processed": data}
```

**Pros:**
- Fast
- No external dependencies
- Simple setup

**Cons:**
- Jobs lost on restart
- Single-server only
- No persistence

### Redis Queue

Production backend with persistence:

```python
from rapidai.background import RedisQueue

queue = RedisQueue(
    url="redis://localhost:6379",
    prefix="myapp:jobs:"
)

@background(queue=queue)
async def my_task(data: str):
    return {"processed": data}
```

**Pros:**
- Persistent storage
- Survives restarts
- Multi-server support
- Production-ready

**Cons:**
- Requires Redis
- Slightly slower

## Job Management

### Cancelling Jobs

```python
@app.route("/jobs/<job_id>/cancel", methods=["POST"])
async def cancel_job(job_id: str):
    cancelled = await my_task.cancel(job_id)

    if cancelled:
        return {"status": "cancelled"}
    else:
        return {"error": "Job not found or already completed"}, 404
```

### Listing Jobs

```python
from rapidai.background import get_queue, JobStatus

@app.route("/jobs", methods=["GET"])
async def list_jobs(status: str = None):
    queue = get_queue()

    # Filter by status if provided
    job_status = JobStatus(status) if status else None
    jobs = await queue.list_jobs(status=job_status)

    return {
        "jobs": [
            {
                "job_id": job.job_id,
                "status": job.status,
                "created_at": job.created_at.isoformat()
            }
            for job in jobs
        ]
    }
```

## Complete Example: Document Processing

```python
from rapidai import App, LLM
from rapidai.background import background
from rapidai.rag import RAG

app = App()
llm = LLM("claude-3-haiku-20240307")
rag = RAG()

@background(max_retries=3)
async def process_document(filepath: str, user_id: str):
    """Process document in background with RAG."""
    try:
        # Load and chunk document
        chunks = await rag.add_document(filepath)

        # Generate summary
        summary_prompt = f"Summarize this document: {chunks[0].content[:1000]}"
        summary = await llm.complete(summary_prompt)

        return {
            "filepath": filepath,
            "chunks": len(chunks),
            "summary": summary,
            "user_id": user_id
        }
    except Exception as e:
        raise Exception(f"Processing failed: {str(e)}")

@app.route("/upload", methods=["POST"])
async def upload_document(filepath: str, user_id: str):
    """Upload and process document."""
    job_id = await process_document.enqueue(
        filepath=filepath,
        user_id=user_id
    )

    return {
        "job_id": job_id,
        "message": "Document processing started",
        "status_url": f"/jobs/{job_id}"
    }

@app.route("/jobs/<job_id>", methods=["GET"])
async def get_job(job_id: str):
    """Get job status and result."""
    result = await process_document.get_result(job_id)

    if not result:
        return {"error": "Job not found"}, 404

    response = {
        "job_id": result.job_id,
        "status": result.status,
        "attempts": result.attempts
    }

    if result.status == "completed":
        response["result"] = result.result
        response["duration"] = result.duration
    elif result.status == "failed":
        response["error"] = result.error

    return response

if __name__ == "__main__":
    app.run(port=8000)
```

## Best Practices

### 1. Make Tasks Idempotent

Ensure tasks can be safely retried:

```python
@background(max_retries=3)
async def process_order(order_id: str):
    # Check if already processed
    if await db.is_processed(order_id):
        return {"already_processed": True}

    # Process order
    result = await process(order_id)

    # Mark as processed
    await db.mark_processed(order_id)

    return result
```

### 2. Use Appropriate Retry Counts

```python
# Quick tasks - few retries
@background(max_retries=2)
async def send_notification(user_id: str):
    ...

# Critical tasks - more retries
@background(max_retries=5)
async def process_payment(order_id: str):
    ...

# Best-effort tasks - no retries
@background(max_retries=0)
async def log_analytics(event: dict):
    ...
```

### 3. Handle Errors Gracefully

```python
@background(max_retries=3)
async def risky_task(data: dict):
    try:
        result = await external_api.call(data)
        return {"success": True, "result": result}
    except TemporaryError as e:
        # Retry on temporary errors
        raise
    except PermanentError as e:
        # Don't retry on permanent errors
        return {"success": False, "error": str(e)}
```

### 4. Provide Status Endpoints

```python
@app.route("/jobs/<job_id>", methods=["GET"])
async def job_status(job_id: str):
    result = await my_task.get_result(job_id)

    # Provide clear status information
    return {
        "job_id": job_id,
        "status": result.status,
        "progress": calculate_progress(result),
        "estimated_completion": estimate_time(result)
    }
```

### 5. Use Redis in Production

```python
import os

# Use in-memory for development, Redis for production
backend = "redis" if os.getenv("PRODUCTION") else "memory"

from rapidai.background import get_queue

queue = get_queue(
    backend=backend,
    url=os.getenv("REDIS_URL") if backend == "redis" else None
)
```

### 6. Monitor Job Metrics

```python
from rapidai.monitoring import get_collector

@background(max_retries=3)
async def monitored_task(data: dict):
    collector = get_collector()
    collector.record_metric("jobs.started", 1)

    try:
        result = await process(data)
        collector.record_metric("jobs.completed", 1)
        return result
    except Exception as e:
        collector.record_metric("jobs.failed", 1)
        raise
```

## Troubleshooting

### Jobs Not Processing

```python
# Ensure job is actually queued
job_id = await my_task.enqueue(data="test")
result = await my_task.get_result(job_id)
print(f"Status: {result.status}")  # Should be "running" or "completed"
```

### Redis Connection Issues

```python
from rapidai.background import RedisQueue

try:
    queue = RedisQueue(url="redis://localhost:6379")
except Exception as e:
    print(f"Redis connection failed: {e}")
    # Fall back to in-memory
    queue = InMemoryQueue()
```

### Job Stuck in Running State

```python
# Check if job is actually running
result = await my_task.get_result(job_id)

if result.status == "running":
    # Check how long it's been running
    import datetime
    running_time = datetime.datetime.now() - result.started_at

    if running_time.seconds > 300:  # 5 minutes
        # Consider cancelling and retrying
        await my_task.cancel(job_id)
```

## Next Steps

- See [API Reference](../reference/background.html) for complete API documentation
- Learn about [Monitoring](monitoring.html) to track job performance
- Check [Testing](testing.html) for testing background jobs
