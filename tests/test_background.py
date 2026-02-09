"""Tests for background jobs system."""

import pytest
import asyncio
from datetime import datetime, timedelta

from rapidai.background import (
    background,
    JobStatus,
    JobResult,
    InMemoryQueue,
    get_queue,
)


class TestJobDecorator:
    """Test @background decorator."""

    @pytest.mark.asyncio
    async def test_background_decorator_creates_job(self):
        """Background decorator should create enqueueable function."""

        @background(max_retries=3)
        async def test_job(data: str):
            return {"processed": data}

        # Should have enqueue method
        assert hasattr(test_job, "enqueue")
        assert hasattr(test_job, "get_result")
        assert hasattr(test_job, "cancel")

    @pytest.mark.asyncio
    async def test_enqueue_job(self):
        """Should enqueue job and return job ID."""

        @background(max_retries=2)
        async def test_job(value: int):
            await asyncio.sleep(0.1)
            return {"result": value * 2}

        job_id = await test_job.enqueue(value=5)

        assert job_id is not None
        assert isinstance(job_id, str)

    @pytest.mark.asyncio
    async def test_get_job_result(self):
        """Should retrieve job result."""

        @background(max_retries=1)
        async def test_job(x: int):
            return {"value": x + 1}

        job_id = await test_job.enqueue(x=10)

        # Wait for completion
        await asyncio.sleep(0.2)

        result = await test_job.get_result(job_id)

        assert result is not None
        assert result.status == JobStatus.COMPLETED
        assert result.result == {"value": 11}

    @pytest.mark.asyncio
    async def test_job_with_error_retries(self):
        """Failed jobs should retry with exponential backoff."""
        attempt_count = 0

        @background(max_retries=3)
        async def failing_job():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ValueError("Test error")
            return {"success": True}

        job_id = await failing_job.enqueue()

        # Wait for retries
        await asyncio.sleep(1.0)

        result = await failing_job.get_result(job_id)

        # Should succeed after retries
        assert result.status == JobStatus.COMPLETED
        assert result.attempts >= 2


class TestJobStatus:
    """Test JobStatus enum."""

    def test_job_status_values(self):
        """JobStatus should have all required states."""
        assert JobStatus.PENDING == "pending"
        assert JobStatus.RUNNING == "running"
        assert JobStatus.COMPLETED == "completed"
        assert JobStatus.FAILED == "failed"
        assert JobStatus.CANCELLED == "cancelled"


class TestJobResult:
    """Test JobResult dataclass."""

    def test_job_result_creation(self):
        """Should create JobResult with required fields."""
        result = JobResult(
            job_id="test-123",
            status=JobStatus.PENDING,
            created_at=datetime.now(),
            max_retries=3,
        )

        assert result.job_id == "test-123"
        assert result.status == JobStatus.PENDING
        assert result.attempts == 0
        assert result.max_retries == 3

    def test_is_done_property(self):
        """is_done should return True for terminal states."""
        completed = JobResult(
            job_id="1", status=JobStatus.COMPLETED, created_at=datetime.now(), max_retries=0
        )

        failed = JobResult(job_id="2", status=JobStatus.FAILED, created_at=datetime.now(), max_retries=0)

        cancelled = JobResult(
            job_id="3", status=JobStatus.CANCELLED, created_at=datetime.now(), max_retries=0
        )

        pending = JobResult(job_id="4", status=JobStatus.PENDING, created_at=datetime.now(), max_retries=0)

        assert completed.is_done is True
        assert failed.is_done is True
        assert cancelled.is_done is True
        assert pending.is_done is False

    def test_duration_calculation(self):
        """Duration should calculate time between created and completed."""
        created = datetime.now()
        completed = created + timedelta(seconds=5)

        result = JobResult(
            job_id="test",
            status=JobStatus.COMPLETED,
            created_at=created,
            completed_at=completed,
            max_retries=0,
        )

        assert result.duration == pytest.approx(5.0, rel=0.1)

    def test_duration_none_when_not_completed(self):
        """Duration should be None when job not completed."""
        result = JobResult(
            job_id="test", status=JobStatus.RUNNING, created_at=datetime.now(), max_retries=0
        )

        assert result.duration is None


class TestInMemoryQueue:
    """Test in-memory job queue."""

    @pytest.fixture
    def queue(self):
        """Create fresh queue for each test."""
        return InMemoryQueue()

    @pytest.mark.asyncio
    async def test_enqueue_job(self, queue):
        """Should enqueue job and return job ID."""

        async def test_func():
            return {"test": True}

        job_id = await queue.enqueue("test_func", test_func, {}, max_retries=3)

        assert job_id is not None
        result = await queue.get_result(job_id)
        assert result is not None
        assert result.status == JobStatus.PENDING

    @pytest.mark.asyncio
    async def test_get_nonexistent_job(self, queue):
        """Should return None for nonexistent job."""
        result = await queue.get_result("nonexistent-id")

        assert result is None

    @pytest.mark.asyncio
    async def test_cancel_job(self, queue):
        """Should cancel pending job."""

        async def slow_job():
            await asyncio.sleep(10)
            return {"done": True}

        job_id = await queue.enqueue("slow_job", slow_job, {}, max_retries=0)

        # Cancel before it runs
        cancelled = await queue.cancel(job_id)

        assert cancelled is True

        result = await queue.get_result(job_id)
        assert result.status == JobStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_list_jobs(self, queue):
        """Should list all jobs."""

        async def job1():
            return 1

        async def job2():
            return 2

        id1 = await queue.enqueue("job1", job1, {}, max_retries=0)
        id2 = await queue.enqueue("job2", job2, {}, max_retries=0)

        jobs = await queue.list_jobs()

        assert len(jobs) >= 2
        job_ids = [j.job_id for j in jobs]
        assert id1 in job_ids
        assert id2 in job_ids

    @pytest.mark.asyncio
    async def test_list_jobs_filtered_by_status(self, queue):
        """Should filter jobs by status."""

        async def quick_job():
            return "done"

        job_id = await queue.enqueue("quick", quick_job, {}, max_retries=0)

        # Wait for completion
        await asyncio.sleep(0.2)

        # Get only completed jobs
        completed_jobs = await queue.list_jobs(status=JobStatus.COMPLETED)

        assert len(completed_jobs) > 0
        assert all(j.status == JobStatus.COMPLETED for j in completed_jobs)


class TestQueueFactory:
    """Test get_queue factory function."""

    def test_get_queue_returns_singleton(self):
        """get_queue should return same instance."""
        queue1 = get_queue()
        queue2 = get_queue()

        assert queue1 is queue2

    def test_get_queue_returns_in_memory_by_default(self):
        """get_queue should return InMemoryQueue by default."""
        queue = get_queue()

        assert isinstance(queue, InMemoryQueue)


class TestBackgroundJobIntegration:
    """Integration tests for complete background job workflow."""

    @pytest.mark.asyncio
    async def test_complete_job_workflow(self):
        """Test complete job lifecycle."""

        @background(max_retries=2)
        async def process_data(value: int):
            await asyncio.sleep(0.1)
            return {"processed": value * 2, "timestamp": "2024-01-01"}

        # Enqueue job
        job_id = await process_data.enqueue(value=21)
        assert job_id is not None

        # Check initial status
        result = await process_data.get_result(job_id)
        assert result.status in [JobStatus.PENDING, JobStatus.RUNNING]

        # Wait for completion
        await asyncio.sleep(0.3)

        # Check final status
        result = await process_data.get_result(job_id)
        assert result.status == JobStatus.COMPLETED
        assert result.result["processed"] == 42
        assert result.is_done is True
        assert result.duration is not None

    @pytest.mark.asyncio
    async def test_job_cancellation_workflow(self):
        """Test cancelling a job."""

        @background(max_retries=0)
        async def long_running_job():
            await asyncio.sleep(5)
            return {"done": True}

        # Enqueue
        job_id = await long_running_job.enqueue()

        # Cancel immediately
        cancelled = await long_running_job.cancel(job_id)
        assert cancelled is True

        # Verify cancelled
        result = await long_running_job.get_result(job_id)
        assert result.status == JobStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_parallel_jobs(self):
        """Multiple jobs should run in parallel."""

        @background(max_retries=1)
        async def parallel_job(job_num: int):
            await asyncio.sleep(0.1)
            return {"job": job_num}

        # Enqueue multiple jobs
        job_ids = []
        for i in range(5):
            job_id = await parallel_job.enqueue(job_num=i)
            job_ids.append(job_id)

        # Wait for all to complete
        await asyncio.sleep(0.5)

        # All should be completed
        for job_id in job_ids:
            result = await parallel_job.get_result(job_id)
            assert result.status == JobStatus.COMPLETED
