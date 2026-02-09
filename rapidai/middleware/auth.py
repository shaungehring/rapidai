"""Authentication middleware for RapidAI."""

from typing import Any, Callable, Dict, Optional


def auth(verify_fn: Callable[[Dict[str, Any]], bool]) -> Callable:
    """Generic authentication middleware factory.

    Args:
        verify_fn: Function that takes request and returns True if authenticated

    Returns:
        Authentication middleware function

    Example:
        ```python
        from rapidai import App
        from rapidai.middleware import auth

        app = App()

        def verify_user(request):
            token = request.get("headers", {}).get("Authorization")
            return token == "Bearer secret-token"

        app.use(auth(verify_user))
        ```
    """

    async def middleware(request: Dict[str, Any], next: Callable) -> Dict[str, Any]:
        """Authentication middleware function.

        Args:
            request: Request object
            next: Next middleware/handler

        Returns:
            Response or 401 Unauthorized
        """
        if not verify_fn(request):
            return {"status": 401, "body": {"error": "Unauthorized"}}

        return await next()

    return middleware


def bearer_auth(token: str) -> Callable:
    """Bearer token authentication middleware factory.

    Args:
        token: Expected bearer token

    Returns:
        Bearer authentication middleware function

    Example:
        ```python
        from rapidai import App
        from rapidai.middleware import bearer_auth

        app = App()
        app.use(bearer_auth("my-secret-token"))
        ```
    """

    def verify(request: Dict[str, Any]) -> bool:
        """Verify bearer token.

        Args:
            request: Request object

        Returns:
            True if token is valid
        """
        auth_header = request.get("headers", {}).get("authorization", "")
        expected = f"Bearer {token}"
        return auth_header == expected

    return auth(verify)


def api_key_auth(
    api_key: str, header_name: str = "X-API-Key", query_param: Optional[str] = None
) -> Callable:
    """API key authentication middleware factory.

    Args:
        api_key: Expected API key
        header_name: Header name for API key (default: "X-API-Key")
        query_param: Optional query parameter name for API key

    Returns:
        API key authentication middleware function

    Example:
        ```python
        from rapidai import App
        from rapidai.middleware import api_key_auth

        app = App()

        # Check header
        app.use(api_key_auth("my-api-key"))

        # Check header or query param
        app.use(api_key_auth("my-api-key", query_param="api_key"))
        ```
    """

    def verify(request: Dict[str, Any]) -> bool:
        """Verify API key.

        Args:
            request: Request object

        Returns:
            True if API key is valid
        """
        # Check header
        header_key = request.get("headers", {}).get(header_name.lower(), "")
        if header_key == api_key:
            return True

        # Check query param if specified
        if query_param:
            query_key = request.get("query", {}).get(query_param, "")
            if query_key == api_key:
                return True

        return False

    return auth(verify)
