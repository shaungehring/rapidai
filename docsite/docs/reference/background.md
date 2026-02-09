# Background Jobs API Reference

Complete API reference for RapidAI's background job system.

## Decorator

### background

```python
def background(
    max_retries: int = 3,
    queue: Optional[JobQueue] = None
) -> Callable
```

Decorator to run a function as a background job.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_retries` | `int` | `3` | Maximum retry attempts on failure |
| `queue` | `JobQueue` | `None` | Custom job queue (uses default if None) |

**Returns:** Decorated function with `enqueue()`, `get_result()`, and `cancel()` methods

**Example:**

```python
from rapidai.background import background

@background(max_retries=5)
async def process_task(data: str):
    return {"processed": data}

# Enqueue
job_id = await process_task.enqueue(data="test")

# Get result
result = await process_task.get_result(job_id)

# Cancel
cancelled = await process_task.cancel(job_id)
```

## Classes

### JobResult

```python
@dataclass
class JobResult:
    job_id: str
    status: JobStatus
    result: Any = None
    error: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    attempts: int = 0
    max_retries: int = 3
```

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `job_id` | `str` | Unique job identifier |
| `status` | `JobStatus` | Current job status |
| `result` | `Any` | Job result (if completed) |
| `error` | `str` | Error message (if failed) |
| `created_at` | `datetime` | When job was created |
| `started_at` | `datetime` | When job started running |
| `completed_at` | `datetime` | When job finished |
| `attempts` | `int` | Number of execution attempts |
| `max_retries` | `int` | Maximum retry attempts |

**Methods:**

#### `duration`

```python
@property
def duration(self) -> Optional[float]
```

Get job duration in seconds.

**Returns:** `float` - Duration in seconds, or `None` if not completed

#### `is_done`

```python
@property
def is_done(self) -> bool
```

Check if job is in a terminal state.

**Returns:** `bool` - True if completed, failed, or cancelled

### JobStatus

```python
class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

**Values:**

- `PENDING` - Job queued, waiting to start
- `RUNNING` - Job currently executing
- `COMPLETED` - Job finished successfully
- `FAILED` - Job failed after all retries
- `CANCELLED` - Job was cancelled

### JobQueue

```python
class JobQueue:
    async def enqueue(
        self,
        job_id: str,
        func: Callable,
        args: tuple,
        kwargs: dict,
        max_retries: int = 3
    ) -> str

    async def get_result(self, job_id: str) -> Optional[JobResult]

    async def cancel(self, job_id: str) -> bool

    async def list_jobs(
        self,
        status: Optional[JobStatus] = None
    ) -> List[JobResult]
```

Base class for job queue backends.

### InMemoryQueue

```python
class InMemoryQueue(JobQueue):
    def __init__(self) -> None
```

In-memory job queue implementation.

**Features:**
- Fast execution
- No external dependencies
- Jobs lost on restart
- Single-server only

**Example:**

```python
from rapidai.background import InMemoryQueue

queue = InMemoryQueue()
```

### RedisQueue

```python
class RedisQueue(JobQueue):
    def __init__(
        self,
        url: str = "redis://localhost:6379",
        prefix: str = "rapidai:jobs:"
    ) -> None
```

Redis-backed job queue implementation.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | `"redis://localhost:6379"` | Redis connection URL |
| `prefix` | `str` | `"rapidai:jobs:"` | Key prefix for namespacing |

**Features:**
- Persistent storage
- Survives restarts
- Multi-server support
- Production-ready

**Example:**

```python
from rapidai.background import RedisQueue

queue = RedisQueue(
    url="redis://localhost:6379",
    prefix="myapp:jobs:"
)
```

## Functions

### get_queue

```python
def get_queue(
    backend: str = "memory",
    **kwargs: Any
) -> JobQueue
```

Get or create job queue.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `backend` | `str` | `"memory"` | Queue backend ("memory" or "redis") |
| `**kwargs` | `Any` | - | Backend-specific arguments |

**Returns:** `JobQueue` - Queue instance

**Example:**

```python
from rapidai.background import get_queue

# In-memory queue
queue = get_queue(backend="memory")

# Redis queue
queue = get_queue(
    backend="redis",
    url="redis://localhost:6379"
)
```

## Exceptions

### JobError

```python
class JobError(RapidAIException):
    """Background job errors."""
```

Raised for job-related errors.

## Complete Example

```python
from rapidai import App
from rapidai.background import background, get_queue, JobStatus

app = App()

# Configure Redis queue for production
queue = get_queue(
    backend="redis",
    url="redis://localhost:6379"
)

@background(max_retries=3, queue=queue)
async def process_data(data_id: str):
    """Process data with automatic retries."""
    # Simulate processing
    result = await external_api.process(data_id)
    return {"data_id": data_id, "result": result}

@app.route("/process", methods=["POST"])
async def start_processing(data_id: str):
    """Start background processing."""
    job_id = await process_data.enqueue(data_id=data_id)
    return {
        "job_id": job_id,
        "status": "queued",
        "check_url": f"/jobs/{job_id}"
    }

@app.route("/jobs/<job_id>", methods=["GET"])
async def get_job_status(job_id: str):
    """Get job status and result."""
    result = await process_data.get_result(job_id)

    if not result:
        return {"error": "Job not found"}, 404

    response = {
        "job_id": result.job_id,
        "status": result.status.value,
        "created_at": result.created_at.isoformat(),
        "attempts": result.attempts
    }

    if result.is_done:
        response["completed_at"] = result.completed_at.isoformat()
        response["duration"] = result.duration

        if result.status == JobStatus.COMPLETED:
            response["result"] = result.result
        elif result.status == JobStatus.FAILED:
            response["error"] = result.error

    return response

@app.route("/jobs/<job_id>", methods=["DELETE"])
async def cancel_job(job_id: str):
    """Cancel a running job."""
    cancelled = await process_data.cancel(job_id)

    if cancelled:
        return {"status": "cancelled"}
    else:
        return {"error": "Cannot cancel job"}, 400

@app.route("/jobs", methods=["GET"])
async def list_all_jobs(status: str = None):
    """List all jobs, optionally filtered by status."""
    job_status = JobStatus(status) if status else None
    jobs = await queue.list_jobs(status=job_status)

    return {
        "jobs": [
            {
                "job_id": job.job_id,
                "status": job.status.value,
                "created_at": job.created_at.isoformat()
            }
            for job in jobs
        ]
    }
```

## See Also

- [Background Jobs Guide](../advanced/background.md) - Complete usage guide
- [Monitoring](monitoring.md) - Track job performance
- [Testing](testing.md) - Test background jobs
