"""Background job system for RapidAI."""

import asyncio
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union

from .exceptions import RapidAIException


class JobError(RapidAIException):
    """Background job errors."""

    pass


class JobStatus(str, Enum):
    """Job status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class JobResult:
    """Result of a background job."""

    job_id: str
    status: JobStatus
    result: Any = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    attempts: int = 0
    max_retries: int = 3

    @property
    def duration(self) -> Optional[float]:
        """Get job duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def is_done(self) -> bool:
        """Check if job is in a terminal state."""
        return self.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED)


class JobQueue:
    """Base class for job queue backends."""

    async def enqueue(self, job_id: str, func: Callable, args: tuple, kwargs: dict, max_retries: int = 3) -> str:
        """Enqueue a job."""
        raise NotImplementedError

    async def get_result(self, job_id: str) -> Optional[JobResult]:
        """Get job result."""
        raise NotImplementedError

    async def cancel(self, job_id: str) -> bool:
        """Cancel a job."""
        raise NotImplementedError

    async def list_jobs(self, status: Optional[JobStatus] = None) -> List[JobResult]:
        """List jobs, optionally filtered by status."""
        raise NotImplementedError


class InMemoryQueue(JobQueue):
    """In-memory job queue implementation."""

    def __init__(self) -> None:
        """Initialize in-memory queue."""
        self._jobs: Dict[str, JobResult] = {}
        self._tasks: Dict[str, asyncio.Task] = {}

    async def enqueue(
        self,
        job_id: str,
        func: Callable,
        args: tuple,
        kwargs: dict,
        max_retries: int = 3,
    ) -> str:
        """Enqueue a job for execution.

        Args:
            job_id: Unique job identifier
            func: Function to execute
            args: Positional arguments
            kwargs: Keyword arguments
            max_retries: Maximum retry attempts

        Returns:
            Job ID
        """
        # Create job result
        result = JobResult(
            job_id=job_id,
            status=JobStatus.PENDING,
            max_retries=max_retries,
        )
        self._jobs[job_id] = result

        # Create and schedule task
        task = asyncio.create_task(self._execute_job(job_id, func, args, kwargs))
        self._tasks[job_id] = task

        return job_id

    async def _execute_job(
        self,
        job_id: str,
        func: Callable,
        args: tuple,
        kwargs: dict,
    ) -> None:
        """Execute a job with retry logic.

        Args:
            job_id: Job identifier
            func: Function to execute
            args: Positional arguments
            kwargs: Keyword arguments
        """
        result = self._jobs[job_id]
        result.status = JobStatus.RUNNING
        result.started_at = datetime.now()

        while result.attempts < result.max_retries:
            try:
                result.attempts += 1

                # Execute function
                if asyncio.iscoroutinefunction(func):
                    output = await func(*args, **kwargs)
                else:
                    output = func(*args, **kwargs)

                # Success
                result.status = JobStatus.COMPLETED
                result.result = output
                result.completed_at = datetime.now()
                break

            except asyncio.CancelledError:
                # Job was cancelled
                result.status = JobStatus.CANCELLED
                result.completed_at = datetime.now()
                break

            except Exception as e:
                # Error occurred
                result.error = str(e)

                if result.attempts >= result.max_retries:
                    # Max retries reached
                    result.status = JobStatus.FAILED
                    result.completed_at = datetime.now()
                else:
                    # Retry with exponential backoff
                    delay = 2 ** result.attempts
                    await asyncio.sleep(delay)

    async def get_result(self, job_id: str) -> Optional[JobResult]:
        """Get job result.

        Args:
            job_id: Job identifier

        Returns:
            Job result or None if not found
        """
        return self._jobs.get(job_id)

    async def cancel(self, job_id: str) -> bool:
        """Cancel a running job.

        Args:
            job_id: Job identifier

        Returns:
            True if cancelled, False if not found or already done
        """
        task = self._tasks.get(job_id)
        result = self._jobs.get(job_id)

        if task and result and not result.is_done:
            task.cancel()
            return True
        return False

    async def list_jobs(self, status: Optional[JobStatus] = None) -> List[JobResult]:
        """List jobs, optionally filtered by status.

        Args:
            status: Optional status filter

        Returns:
            List of job results
        """
        jobs = list(self._jobs.values())
        if status:
            jobs = [j for j in jobs if j.status == status]
        return sorted(jobs, key=lambda j: j.created_at, reverse=True)


class RedisQueue(JobQueue):
    """Redis-backed job queue implementation."""

    def __init__(self, url: str = "redis://localhost:6379", prefix: str = "rapidai:jobs:") -> None:
        """Initialize Redis queue.

        Args:
            url: Redis connection URL
            prefix: Key prefix for Redis
        """
        try:
            import redis
        except ImportError:
            raise JobError("redis package not installed. Install with: pip install redis")

        self.client = redis.from_url(url, decode_responses=True)
        self.prefix = prefix

    def _key(self, job_id: str) -> str:
        """Get Redis key for job."""
        return f"{self.prefix}{job_id}"

    async def enqueue(
        self,
        job_id: str,
        func: Callable,
        args: tuple,
        kwargs: dict,
        max_retries: int = 3,
    ) -> str:
        """Enqueue a job (Redis implementation).

        Note: Redis implementation stores job metadata only.
        Actual execution happens via background workers.

        Args:
            job_id: Unique job identifier
            func: Function to execute (stored as reference)
            args: Positional arguments (serialized)
            kwargs: Keyword arguments (serialized)
            max_retries: Maximum retry attempts

        Returns:
            Job ID
        """
        import pickle

        result = JobResult(
            job_id=job_id,
            status=JobStatus.PENDING,
            max_retries=max_retries,
        )

        # Store job data
        data = {
            "job_id": job_id,
            "status": result.status.value,
            "created_at": result.created_at.isoformat(),
            "max_retries": max_retries,
            "attempts": 0,
            "func": pickle.dumps(func).hex(),
            "args": pickle.dumps(args).hex(),
            "kwargs": pickle.dumps(kwargs).hex(),
        }

        self.client.hset(self._key(job_id), mapping=data)
        self.client.lpush(f"{self.prefix}queue", job_id)

        return job_id

    async def get_result(self, job_id: str) -> Optional[JobResult]:
        """Get job result from Redis.

        Args:
            job_id: Job identifier

        Returns:
            Job result or None if not found
        """
        import pickle

        data = self.client.hgetall(self._key(job_id))
        if not data:
            return None

        # Reconstruct JobResult
        result = JobResult(
            job_id=data["job_id"],
            status=JobStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            attempts=int(data["attempts"]),
            max_retries=int(data["max_retries"]),
        )

        if "result" in data:
            result.result = pickle.loads(bytes.fromhex(data["result"]))
        if "error" in data:
            result.error = data["error"]
        if "started_at" in data:
            result.started_at = datetime.fromisoformat(data["started_at"])
        if "completed_at" in data:
            result.completed_at = datetime.fromisoformat(data["completed_at"])

        return result

    async def cancel(self, job_id: str) -> bool:
        """Cancel a job in Redis.

        Args:
            job_id: Job identifier

        Returns:
            True if cancelled, False otherwise
        """
        result = await self.get_result(job_id)
        if result and not result.is_done:
            self.client.hset(self._key(job_id), "status", JobStatus.CANCELLED.value)
            return True
        return False

    async def list_jobs(self, status: Optional[JobStatus] = None) -> List[JobResult]:
        """List jobs from Redis.

        Args:
            status: Optional status filter

        Returns:
            List of job results
        """
        # Get all job keys
        keys = self.client.keys(f"{self.prefix}*")
        keys = [k for k in keys if not k.endswith(":queue")]

        jobs = []
        for key in keys:
            job_id = key.replace(self.prefix, "")
            result = await self.get_result(job_id)
            if result:
                if status is None or result.status == status:
                    jobs.append(result)

        return sorted(jobs, key=lambda j: j.created_at, reverse=True)


# Global queue instance
_queue: Optional[JobQueue] = None


def get_queue(backend: str = "memory", **kwargs: Any) -> JobQueue:
    """Get or create job queue.

    Args:
        backend: Queue backend ('memory' or 'redis')
        **kwargs: Backend-specific arguments

    Returns:
        JobQueue instance
    """
    global _queue

    if _queue is None:
        if backend == "memory":
            _queue = InMemoryQueue()
        elif backend == "redis":
            _queue = RedisQueue(**kwargs)
        else:
            raise JobError(f"Unknown backend: {backend}")

    return _queue


def background(max_retries: int = 3, queue: Optional[JobQueue] = None) -> Callable:
    """Decorator to run a function as a background job.

    Args:
        max_retries: Maximum retry attempts on failure
        queue: Optional custom job queue

    Returns:
        Decorator function

    Example:
        ```python
        @background(max_retries=3)
        async def process_document(doc_id: str):
            # Long-running task
            ...

        # Enqueue job
        job_id = await process_document.enqueue(doc_id="123")

        # Check status
        result = await process_document.get_result(job_id)
        ```
    """
    job_queue = queue or get_queue()

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Direct execution (for testing)."""
            return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)

        async def enqueue(*args: Any, **kwargs: Any) -> str:
            """Enqueue job for background execution."""
            job_id = str(uuid.uuid4())
            return await job_queue.enqueue(job_id, func, args, kwargs, max_retries)

        async def get_result(job_id: str) -> Optional[JobResult]:
            """Get job result."""
            return await job_queue.get_result(job_id)

        async def cancel(job_id: str) -> bool:
            """Cancel job."""
            return await job_queue.cancel(job_id)

        # Attach helper methods
        wrapper.enqueue = enqueue  # type: ignore
        wrapper.get_result = get_result  # type: ignore
        wrapper.cancel = cancel  # type: ignore
        wrapper._original_func = func  # type: ignore

        return wrapper

    return decorator
