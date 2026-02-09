"""CORS middleware for RapidAI."""

from typing import Any, Callable, Dict, List, Optional


def cors(
    allow_origins: List[str] = None,
    allow_methods: List[str] = None,
    allow_headers: List[str] = None,
    allow_credentials: bool = False,
    max_age: int = 600,
) -> Callable:
    """CORS middleware factory.

    Args:
        allow_origins: List of allowed origins (default: ["*"])
        allow_methods: List of allowed HTTP methods (default: ["GET", "POST", "PUT", "DELETE", "OPTIONS"])
        allow_headers: List of allowed headers (default: ["*"])
        allow_credentials: Allow credentials
        max_age: Preflight cache time in seconds

    Returns:
        CORS middleware function

    Example:
        ```python
        from rapidai import App
        from rapidai.middleware import cors

        app = App()

        # Allow all origins
        app.use(cors())

        # Specific origins
        app.use(cors(
            allow_origins=["https://example.com"],
            allow_methods=["GET", "POST"],
            allow_credentials=True
        ))
        ```
    """
    if allow_origins is None:
        allow_origins = ["*"]
    if allow_methods is None:
        allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    if allow_headers is None:
        allow_headers = ["*"]

    async def middleware(request: Dict[str, Any], next: Callable) -> Dict[str, Any]:
        """CORS middleware function.

        Args:
            request: Request object
            next: Next middleware/handler

        Returns:
            Response with CORS headers
        """
        # Handle preflight requests
        if request.get("method") == "OPTIONS":
            return {
                "status": 200,
                "headers": {
                    "Access-Control-Allow-Origin": ", ".join(allow_origins),
                    "Access-Control-Allow-Methods": ", ".join(allow_methods),
                    "Access-Control-Allow-Headers": ", ".join(allow_headers),
                    "Access-Control-Max-Age": str(max_age),
                    **(
                        {"Access-Control-Allow-Credentials": "true"}
                        if allow_credentials
                        else {}
                    ),
                },
                "body": "",
            }

        # Process normal request
        response = await next()

        # Add CORS headers to response
        if isinstance(response, dict) and "headers" not in response:
            response["headers"] = {}

        if isinstance(response, dict) and "headers" in response:
            response["headers"].update(
                {
                    "Access-Control-Allow-Origin": ", ".join(allow_origins),
                    "Access-Control-Allow-Methods": ", ".join(allow_methods),
                    "Access-Control-Allow-Headers": ", ".join(allow_headers),
                    **(
                        {"Access-Control-Allow-Credentials": "true"}
                        if allow_credentials
                        else {}
                    ),
                }
            )

        return response

    return middleware
