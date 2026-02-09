"""Example: Background Jobs with RapidAI.

This example demonstrates:
1. Using @background decorator for async tasks
2. Job status tracking
3. Retry logic with exponential backoff
4. Redis backend for persistence
"""

import asyncio
from rapidai import App, LLM, background, JobStatus, get_queue

app = App(title="Background Jobs Example")
llm = LLM("claude-3-haiku-20240307")


# Define background job with retry logic
@background(max_retries=3)
async def process_document(doc_id: str, content: str):
    """Process document in background with automatic retries."""
    print(f"Processing document {doc_id}...")

    # Simulate processing
    await asyncio.sleep(2)

    # Generate summary using LLM
    summary = await llm.complete(f"Summarize this text in one sentence:\n\n{content}")

    return {"doc_id": doc_id, "summary": summary, "status": "completed"}


@background(max_retries=5)
async def send_email(to: str, subject: str, body: str):
    """Send email in background with high retry count."""
    print(f"Sending email to {to}...")

    # Simulate email sending
    await asyncio.sleep(1)

    return {"to": to, "sent": True, "timestamp": "2024-01-01T00:00:00Z"}


# API endpoints
@app.route("/documents/process", methods=["POST"])
async def enqueue_processing(doc_id: str, content: str):
    """Enqueue document for background processing."""
    # Enqueue the job
    job_id = await process_document.enqueue(doc_id=doc_id, content=content)

    return {"job_id": job_id, "status": "queued", "message": "Document queued for processing"}


@app.route("/jobs/<job_id>", methods=["GET"])
async def get_job_status(job_id: str):
    """Get status of a background job."""
    # Get job result
    result = await process_document.get_result(job_id)

    if not result:
        return {"error": "Job not found"}, 404

    response = {
        "job_id": result.job_id,
        "status": result.status,
        "created_at": result.created_at.isoformat(),
        "attempts": result.attempts,
        "max_retries": result.max_retries,
    }

    if result.is_done:
        response["completed_at"] = result.completed_at.isoformat()
        response["duration"] = result.duration

        if result.status == JobStatus.COMPLETED:
            response["result"] = result.result
        elif result.status == JobStatus.FAILED:
            response["error"] = result.error

    return response


@app.route("/jobs/<job_id>/cancel", methods=["POST"])
async def cancel_job(job_id: str):
    """Cancel a running job."""
    cancelled = await process_document.cancel(job_id)

    if cancelled:
        return {"status": "cancelled", "job_id": job_id}
    else:
        return {"error": "Job not found or already completed"}, 404


@app.route("/email/send", methods=["POST"])
async def send_email_async(to: str, subject: str, body: str):
    """Send email asynchronously."""
    job_id = await send_email.enqueue(to=to, subject=subject, body=body)

    return {"job_id": job_id, "message": "Email queued for sending"}


@app.route("/jobs", methods=["GET"])
async def list_jobs(status: str = None):
    """List all jobs, optionally filtered by status."""
    queue = get_queue()

    # Filter by status if provided
    job_status = JobStatus(status) if status else None
    jobs = await queue.list_jobs(status=job_status)

    return {
        "jobs": [
            {"job_id": job.job_id, "status": job.status, "created_at": job.created_at.isoformat()}
            for job in jobs
        ],
        "total": len(jobs),
    }


@app.route("/health", methods=["GET"])
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "background-jobs-example"}


if __name__ == "__main__":
    print("Background Jobs Example")
    print("=" * 50)
    print("\nEndpoints:")
    print("  POST /documents/process - Queue document for processing")
    print("  GET  /jobs/<job_id>     - Get job status")
    print("  POST /jobs/<job_id>/cancel - Cancel a job")
    print("  POST /email/send        - Send email asynchronously")
    print("  GET  /jobs              - List all jobs")
    print("\nExample usage:")
    print('  curl -X POST http://localhost:8000/documents/process \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"doc_id": "doc-123", "content": "RapidAI is a Python framework..."}\'')
    print("\n  curl http://localhost:8000/jobs/<job_id>")
    print("\nStarting server on http://localhost:8000")
    print("=" * 50)

    app.run(port=8000)
