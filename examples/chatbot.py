"""Simple chatbot example using RapidAI."""

from rapidai import App, LLM, stream

app = App()
llm = LLM("claude-3-haiku-20240307")


@app.route("/chat", methods=["POST"])
@stream
async def chat(message: str):
    """Stream a chat response."""
    response = await llm.chat(message, stream=True)
    async for chunk in response:
        yield chunk


@app.route("/health", methods=["GET"])
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    print("Starting chatbot server on http://localhost:8001")
    print("Try: curl -X POST http://localhost:8001/chat -H 'Content-Type: application/json' -d '{\"message\": \"Hello!\"}'")
    app.run(port=8001)
