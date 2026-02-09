"""RAG decorator for routes."""

import asyncio
from functools import wraps
from pathlib import Path
from typing import Any, Callable, List, Optional, Union

from .config import RAGConfig
from .retriever import RAG


def rag(
    sources: Optional[List[Union[str, Path]]] = None,
    top_k: int = 5,
    collection_name: Optional[str] = None,
    auto_initialize: bool = True,
) -> Callable:
    """Decorator to add RAG capabilities to a route.

    Args:
        sources: Documents to load (loaded once at startup)
        top_k: Number of chunks to retrieve
        collection_name: Vector DB collection name
        auto_initialize: Auto-initialize RAG system

    Returns:
        Decorator function

    Example:
        ```python
        from rapidai import App, LLM
        from rapidai.rag import rag

        app = App()
        llm = LLM("claude-3-haiku-20240307")

        @app.route("/ask", methods=["POST"])
        @rag(sources=["docs/manual.pdf"], top_k=5)
        async def ask(query: str, rag_context):
            # rag_context is automatically injected
            prompt = f"Context: {rag_context.text}\\n\\nQuestion: {query}"
            response = await llm.complete(prompt)
            return {
                "answer": response,
                "sources": [s.metadata for s in rag_context.sources]
            }
        ```
    """
    # Initialize RAG system
    rag_config = RAGConfig()
    if collection_name:
        rag_config.vectordb.collection_name = collection_name

    rag_system = RAG(config=rag_config)

    # Load sources at decoration time if provided
    if sources and auto_initialize:
        # Schedule loading for later (when event loop is running)
        _scheduled_loading = False

        async def _load_sources_async():
            nonlocal _scheduled_loading
            if not _scheduled_loading:
                _scheduled_loading = True
                await rag_system.initialize()
                await rag_system.add_documents(sources)

        # Try to schedule immediately if event loop is running
        try:
            loop = asyncio.get_running_loop()
            asyncio.create_task(_load_sources_async())
        except RuntimeError:
            # No event loop running yet, will be loaded on first call
            pass

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Load sources on first call if not already loaded
            if sources and not rag_system._collection_initialized:
                await rag_system.initialize()
                await rag_system.add_documents(sources)

            # Extract query from kwargs
            query = (
                kwargs.get("query")
                or kwargs.get("question")
                or kwargs.get("message")
            )

            if not query:
                # No query parameter, just call function
                return await func(*args, **kwargs)

            # Retrieve context
            retrieval = await rag_system.retrieve(query, top_k=top_k)

            # Inject rag_context into kwargs
            kwargs["rag_context"] = retrieval

            # Call original function
            return await func(*args, **kwargs)

        return wrapper

    return decorator
