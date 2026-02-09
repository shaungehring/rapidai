"""Page decorator for serving HTML in RapidAI."""

from functools import wraps
from typing import Any, Callable


def page(route: str) -> Callable:
    """Decorator to serve an HTML page at a route.

    Args:
        route: Route path (e.g., "/", "/chat")

    Returns:
        Decorator function

    Example:
        ```python
        from rapidai import App
        from rapidai.ui import page, get_chat_template

        app = App()

        @app.route("/")
        @page("/")
        async def index():
            return get_chat_template()
        ```
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> dict:
            # Get HTML content
            html = await func(*args, **kwargs) if callable(func) else func

            # Return as HTTP response with HTML content type
            return {
                "status": 200,
                "headers": {"Content-Type": "text/html; charset=utf-8"},
                "body": html,
            }

        return wrapper

    return decorator
