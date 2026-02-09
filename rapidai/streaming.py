"""Streaming support for RapidAI."""

import asyncio
import json
from typing import Any, AsyncIterator, Callable
from functools import wraps

from .types import StreamHandler


def stream(func: StreamHandler) -> StreamHandler:
    """Decorator to enable Server-Sent Events (SSE) streaming for a route.

    This decorator automatically handles SSE setup including proper headers
    and formatting of the event stream.

    Example:
        ```python
        @app.route("/chat", methods=["POST"])
        @stream
        async def chat(message: str):
            async for chunk in llm.chat(message, stream=True):
                yield chunk
        ```

    Args:
        func: Async generator function that yields chunks

    Returns:
        Wrapped function that handles SSE streaming
    """
    func._is_stream = True  # type: ignore

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> AsyncIterator[str]:
        """Wrapper that handles SSE streaming."""
        async for chunk in func(*args, **kwargs):
            yield chunk

    return wrapper  # type: ignore


async def send_sse_event(
    send: Any,
    data: str,
    event: str = "message",
    id: str = None,
    retry: int = None,
) -> None:
    """Send a Server-Sent Event.

    Args:
        send: ASGI send callable
        data: Event data
        event: Event name (default: "message")
        id: Event ID (optional)
        retry: Retry time in milliseconds (optional)
    """
    message = ""

    if event:
        message += f"event: {event}\n"

    if id:
        message += f"id: {id}\n"

    if retry:
        message += f"retry: {retry}\n"

    message += f"data: {data}\n\n"

    await send(
        {
            "type": "http.response.body",
            "body": message.encode(),
            "more_body": True,
        }
    )


async def send_sse_start(send: Any) -> None:
    """Send SSE response headers.

    Args:
        send: ASGI send callable
    """
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [
                [b"content-type", b"text/event-stream"],
                [b"cache-control", b"no-cache"],
                [b"connection", b"keep-alive"],
            ],
        }
    )


async def send_sse_end(send: Any) -> None:
    """Send SSE response end.

    Args:
        send: ASGI send callable
    """
    await send(
        {
            "type": "http.response.body",
            "body": b"",
            "more_body": False,
        }
    )


class StreamingResponse:
    """Wrapper for streaming responses.

    This class handles the conversion of async iterators into
    proper SSE responses.
    """

    def __init__(self, iterator: AsyncIterator[str], event: str = "message"):
        """Initialize streaming response.

        Args:
            iterator: Async iterator that yields chunks
            event: SSE event name
        """
        self.iterator = iterator
        self.event = event

    async def send(self, send: Any) -> None:
        """Send the streaming response.

        Args:
            send: ASGI send callable
        """
        await send_sse_start(send)

        try:
            async for chunk in self.iterator:
                await send_sse_event(send, chunk, event=self.event)

        except Exception as e:
            # Send error event
            error_data = json.dumps({"error": str(e)})
            await send_sse_event(send, error_data, event="error")

        finally:
            await send_sse_end(send)


def is_stream_handler(func: Callable) -> bool:
    """Check if a function is a stream handler.

    Args:
        func: Function to check

    Returns:
        True if function is decorated with @stream
    """
    return getattr(func, "_is_stream", False)
