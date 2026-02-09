"""Rate limiting middleware for RapidAI."""

import time
from typing import Any, Callable, Dict
from collections import defaultdict


class RateLimiter:
    """In-memory rate limiter using sliding window algorithm."""

    def __init__(self, max_requests: int, window_seconds: int):
        """Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed.

        Args:
            key: Unique identifier for rate limiting (e.g., IP address)

        Returns:
            True if request is allowed
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old requests
        self.requests[key] = [
            timestamp for timestamp in self.requests[key] if timestamp > window_start
        ]

        # Check if under limit
        if len(self.requests[key]) < self.max_requests:
            self.requests[key].append(now)
            return True

        return False

    def get_remaining(self, key: str) -> int:
        """Get remaining requests in current window.

        Args:
            key: Unique identifier

        Returns:
            Number of remaining requests
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Count requests in current window
        current_requests = sum(
            1 for timestamp in self.requests[key] if timestamp > window_start
        )

        return max(0, self.max_requests - current_requests)


def rate_limit(
    max_requests: int = 100,
    window_seconds: int = 60,
    key_fn: Callable[[Dict[str, Any]], str] = None,
) -> Callable:
    """Rate limiting middleware factory.

    Args:
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds
        key_fn: Function to extract rate limit key from request (default: uses IP)

    Returns:
        Rate limiting middleware function

    Example:
        ```python
        from rapidai import App
        from rapidai.middleware import rate_limit

        app = App()

        # Default: 100 requests per minute per IP
        app.use(rate_limit())

        # Custom limits
        app.use(rate_limit(max_requests=10, window_seconds=60))

        # Custom key function (e.g., per user)
        def get_user_id(request):
            return request.get("headers", {}).get("x-user-id", "anonymous")

        app.use(rate_limit(key_fn=get_user_id))
        ```
    """
    limiter = RateLimiter(max_requests, window_seconds)

    if key_fn is None:

        def key_fn(request: Dict[str, Any]) -> str:
            """Default key function uses client IP."""
            return request.get("client", {}).get("host", "unknown")

    async def middleware(request: Dict[str, Any], next: Callable) -> Dict[str, Any]:
        """Rate limiting middleware function.

        Args:
            request: Request object
            next: Next middleware/handler

        Returns:
            Response or 429 Too Many Requests
        """
        key = key_fn(request)

        if not limiter.is_allowed(key):
            remaining = limiter.get_remaining(key)
            return {
                "status": 429,
                "headers": {
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Remaining": str(remaining),
                    "X-RateLimit-Reset": str(window_seconds),
                    "Retry-After": str(window_seconds),
                },
                "body": {
                    "error": "Too many requests",
                    "retry_after": window_seconds,
                },
            }

        response = await next()

        # Add rate limit headers to response
        if isinstance(response, dict):
            if "headers" not in response:
                response["headers"] = {}

            remaining = limiter.get_remaining(key)
            response["headers"].update(
                {
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Remaining": str(remaining),
                    "X-RateLimit-Reset": str(window_seconds),
                }
            )

        return response

    return middleware
