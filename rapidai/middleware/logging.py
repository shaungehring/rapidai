"""Logging middleware for RapidAI."""

import time
import logging
from typing import Any, Callable, Dict, Optional

# Configure default logger
logger = logging.getLogger("rapidai")


def logging_middleware(
    logger_instance: Optional[logging.Logger] = None,
    log_request: bool = True,
    log_response: bool = True,
    log_duration: bool = True,
) -> Callable:
    """Logging middleware factory.

    Args:
        logger_instance: Custom logger instance (default: uses rapidai logger)
        log_request: Log request details
        log_response: Log response details
        log_duration: Log request duration

    Returns:
        Logging middleware function

    Example:
        ```python
        from rapidai import App
        from rapidai.middleware import logging_middleware
        import logging

        app = App()

        # Default logging
        app.use(logging_middleware())

        # Custom logger
        custom_logger = logging.getLogger("myapp")
        app.use(logging_middleware(logger_instance=custom_logger))

        # Only log requests
        app.use(logging_middleware(log_response=False))
        ```
    """
    log = logger_instance or logger

    async def middleware(request: Dict[str, Any], next: Callable) -> Dict[str, Any]:
        """Logging middleware function.

        Args:
            request: Request object
            next: Next middleware/handler

        Returns:
            Response
        """
        start_time = time.time()

        # Log request
        if log_request:
            method = request.get("method", "UNKNOWN")
            path = request.get("path", "/")
            client = request.get("client", {}).get("host", "unknown")
            log.info(f"{method} {path} from {client}")

        # Process request
        try:
            response = await next()

            # Log response
            if log_response:
                status = response.get("status", 200) if isinstance(response, dict) else 200
                log.info(f"Response status: {status}")

            # Log duration
            if log_duration:
                duration = (time.time() - start_time) * 1000  # Convert to ms
                log.info(f"Request completed in {duration:.2f}ms")

            return response

        except Exception as e:
            # Log error
            duration = (time.time() - start_time) * 1000
            log.error(
                f"Request failed after {duration:.2f}ms: {type(e).__name__}: {str(e)}"
            )
            raise

    return middleware


def structured_logging(
    logger_instance: Optional[logging.Logger] = None,
    include_headers: bool = False,
    include_body: bool = False,
) -> Callable:
    """Structured logging middleware with detailed request/response info.

    Args:
        logger_instance: Custom logger instance
        include_headers: Include headers in logs
        include_body: Include request body in logs (be careful with sensitive data!)

    Returns:
        Structured logging middleware function

    Example:
        ```python
        from rapidai import App
        from rapidai.middleware import structured_logging

        app = App()
        app.use(structured_logging(include_headers=True))
        ```
    """
    log = logger_instance or logger

    async def middleware(request: Dict[str, Any], next: Callable) -> Dict[str, Any]:
        """Structured logging middleware function.

        Args:
            request: Request object
            next: Next middleware/handler

        Returns:
            Response
        """
        start_time = time.time()

        # Build log context
        log_context = {
            "method": request.get("method", "UNKNOWN"),
            "path": request.get("path", "/"),
            "client": request.get("client", {}).get("host", "unknown"),
        }

        if include_headers:
            log_context["headers"] = request.get("headers", {})

        if include_body:
            log_context["body"] = request.get("body", {})

        log.info(f"Request started: {log_context}")

        # Process request
        try:
            response = await next()
            duration = (time.time() - start_time) * 1000

            # Build response log context
            response_context = {
                "duration_ms": f"{duration:.2f}",
                "status": response.get("status", 200) if isinstance(response, dict) else 200,
            }

            log.info(f"Request completed: {response_context}")

            return response

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            error_context = {
                "duration_ms": f"{duration:.2f}",
                "error_type": type(e).__name__,
                "error_message": str(e),
            }

            log.error(f"Request failed: {error_context}")
            raise

    return middleware
