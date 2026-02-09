"""Core application class for RapidAI."""

import asyncio
import json
import inspect
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass
from urllib.parse import parse_qs

from .config import RapidAIConfig
from .exceptions import RouteError
from .types import HTTPMethod, Middleware, RouteHandler
from .memory import MemoryManager
from .streaming import is_stream_handler, StreamingResponse


@dataclass
class Route:
    """Represents a route in the application."""

    path: str
    handler: RouteHandler
    methods: List[str]
    is_stream: bool = False


class App:
    """Main application class for RapidAI.

    This class provides the core ASGI application with routing,
    middleware support, and integration with LLM providers.

    Example:
        ```python
        app = App()

        @app.route("/hello", methods=["GET"])
        async def hello():
            return {"message": "Hello, World!"}

        if __name__ == "__main__":
            app.run()
        ```
    """

    def __init__(
        self,
        title: str = "RapidAI Application",
        version: str = "1.0.0",
        config: Optional[RapidAIConfig] = None,
    ):
        """Initialize the application.

        Args:
            title: Application title
            version: Application version
            config: Configuration object (optional, loads from env if not provided)
        """
        self.title = title
        self.version = version
        self.config = config or RapidAIConfig.load()

        self._routes: List[Route] = []
        self._middleware: List[Middleware] = []
        self._memory_manager = MemoryManager(backend=self.config.memory.backend)

    def route(
        self,
        path: str,
        methods: Optional[List[Union[str, HTTPMethod]]] = None,
    ) -> Callable[[RouteHandler], RouteHandler]:
        """Decorator to register a route.

        Args:
            path: URL path for the route
            methods: List of HTTP methods (default: ["GET"])

        Returns:
            Decorator function

        Example:
            ```python
            @app.route("/chat", methods=["POST"])
            async def chat(message: str):
                return {"response": "Hello!"}
            ```
        """
        if methods is None:
            methods = ["GET"]

        method_strs = [m.value if isinstance(m, HTTPMethod) else m.upper() for m in methods]

        def decorator(func: RouteHandler) -> RouteHandler:
            # Check if handler is a streaming function
            is_stream = is_stream_handler(func)
            route = Route(path=path, handler=func, methods=method_strs, is_stream=is_stream)
            self._routes.append(route)
            return func

        return decorator

    def use(self, middleware: Middleware) -> None:
        """Add middleware to the application.

        Middleware is executed in the order it's added.

        Args:
            middleware: Middleware function

        Example:
            ```python
            async def logging_middleware(request, next):
                print(f"Request: {request}")
                response = await next()
                print(f"Response: {response}")
                return response

            app.use(logging_middleware)
            ```
        """
        self._middleware.append(middleware)

    def memory(self, user_id: str) -> "ConversationMemory":
        """Get or create a conversation memory for a user.

        Args:
            user_id: User identifier

        Returns:
            ConversationMemory instance
        """
        return self._memory_manager.get(user_id)

    async def __call__(self, scope: Dict[str, Any], receive: Any, send: Any) -> None:
        """ASGI application entry point."""
        if scope["type"] == "http":
            await self._handle_http(scope, receive, send)
        elif scope["type"] == "lifespan":
            await self._handle_lifespan(scope, receive, send)

    async def _handle_lifespan(
        self, scope: Dict[str, Any], receive: Any, send: Any
    ) -> None:
        """Handle ASGI lifespan events."""
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                return

    async def _handle_http(self, scope: Dict[str, Any], receive: Any, send: Any) -> None:
        """Handle HTTP requests."""
        path = scope["path"]
        method = scope["method"]

        # Find matching route
        route = self._find_route(path, method)
        if not route:
            await self._send_json(
                send, {"error": "Not Found"}, status=404
            )
            return

        try:
            # Parse request body
            body = await self._receive_body(receive)
            request_data = self._parse_request(scope, body)

            # Extract handler parameters
            params = await self._extract_params(route.handler, request_data)

            # Execute handler through middleware chain
            response = await self._execute_with_middleware(
                route.handler, params, route.is_stream, send
            )

            # Send response if not streaming
            if not route.is_stream:
                await self._send_response(send, response)

        except Exception as e:
            await self._send_json(
                send, {"error": str(e)}, status=500
            )

    def _find_route(self, path: str, method: str) -> Optional[Route]:
        """Find a route matching the path and method."""
        for route in self._routes:
            if route.path == path and method in route.methods:
                return route
        return None

    async def _receive_body(self, receive: Any) -> bytes:
        """Receive the full request body."""
        body = b""
        while True:
            message = await receive()
            body += message.get("body", b"")
            if not message.get("more_body"):
                break
        return body

    def _parse_request(self, scope: Dict[str, Any], body: bytes) -> Dict[str, Any]:
        """Parse the request into a dictionary."""
        request_data = {}

        # Parse query parameters
        if scope.get("query_string"):
            query_params = parse_qs(scope["query_string"].decode())
            request_data.update(
                {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
            )

        # Parse JSON body
        if body:
            try:
                json_data = json.loads(body.decode())
                request_data.update(json_data)
            except json.JSONDecodeError:
                pass

        return request_data

    async def _extract_params(
        self, handler: RouteHandler, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract parameters for the handler from request data."""
        # If handler is wrapped (e.g., by @stream), get the original function's signature
        unwrapped = handler
        if hasattr(handler, "__wrapped__"):
            unwrapped = handler.__wrapped__

        sig = inspect.signature(unwrapped)
        params = {}

        for param_name, param in sig.parameters.items():
            if param_name in request_data:
                params[param_name] = request_data[param_name]
            elif param.default is not inspect.Parameter.empty:
                params[param_name] = param.default

        return params

    async def _execute_with_middleware(
        self,
        handler: RouteHandler,
        params: Dict[str, Any],
        is_stream: bool,
        send: Any,
    ) -> Any:
        """Execute handler through middleware chain."""
        # For streaming, handle separately
        if is_stream:
            # Call handler directly (middleware support for streaming can be added later)
            iterator = handler(**params)
            streaming_response = StreamingResponse(iterator)
            await streaming_response.send(send)
            return None

        if not self._middleware:
            return await handler(**params)

        # Build middleware chain
        async def final_handler() -> Any:
            result = await handler(**params)
            return result

        # Execute middleware in reverse order
        next_handler = final_handler
        for middleware in reversed(self._middleware):
            next_handler = self._wrap_middleware(middleware, next_handler, params)

        return await next_handler()

    def _wrap_middleware(
        self, middleware: Middleware, next_handler: Callable, params: Dict[str, Any]
    ) -> Callable:
        """Wrap middleware around the next handler."""

        async def wrapped() -> Any:
            return await middleware(params, next_handler)

        return wrapped

    async def _send_response(self, send: Any, response: Any) -> None:
        """Send an HTTP response."""
        if isinstance(response, dict):
            await self._send_json(send, response)
        elif isinstance(response, str):
            await self._send_text(send, response)
        else:
            await self._send_json(send, {"result": response})

    async def _send_json(
        self, send: Any, data: Dict[str, Any], status: int = 200
    ) -> None:
        """Send a JSON response."""
        body = json.dumps(data).encode()
        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": [
                    [b"content-type", b"application/json"],
                    [b"content-length", str(len(body)).encode()],
                ],
            }
        )
        await send({"type": "http.response.body", "body": body})

    async def _send_text(self, send: Any, text: str, status: int = 200) -> None:
        """Send a text response."""
        body = text.encode()
        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": [
                    [b"content-type", b"text/plain"],
                    [b"content-length", str(len(body)).encode()],
                ],
            }
        )
        await send({"type": "http.response.body", "body": body})

    def run(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        workers: Optional[int] = None,
    ) -> None:
        """Run the application with uvicorn.

        Args:
            host: Host to bind to (default from config)
            port: Port to bind to (default from config)
            workers: Number of workers (default from config)
        """
        import uvicorn

        uvicorn.run(
            self,
            host=host or self.config.server.host,
            port=port or self.config.server.port,
            workers=workers or self.config.server.workers,
            log_level="debug" if self.config.server.debug else "info",
        )


# For backwards compatibility and easier imports
from .memory import ConversationMemory  # noqa: E402
