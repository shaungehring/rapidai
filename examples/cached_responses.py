"""Example showing caching to reduce LLM costs."""

from rapidai import App, LLM, cache

app = App()
llm = LLM("claude-3-haiku-20240307")


@app.route("/summarize", methods=["POST"])
@cache(ttl=3600)  # Cache for 1 hour
async def summarize(text: str):
    """Summarize text with exact caching."""
    response = await llm.complete(f"Summarize this text concisely:\n\n{text}")
    return {"summary": response, "cached": False}  # Note: In production, track cache hits


@app.route("/analyze", methods=["POST"])
@cache(ttl=1800)  # Cache for 30 minutes
async def analyze(text: str):
    """Analyze text sentiment with caching."""
    response = await llm.complete(
        f"Analyze the sentiment of this text (positive/negative/neutral):\n\n{text}"
    )
    return {"sentiment": response}


if __name__ == "__main__":
    print("Starting cached responses server on http://localhost:8001")
    print("Try the same request twice to see caching in action:")
    print("  curl -X POST http://localhost:8001/summarize -H 'Content-Type: application/json' -d '{\"text\": \"Your text here\"}'")
    app.run(port=8001)
