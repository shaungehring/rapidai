"""Stateful chatbot with conversation memory."""

from rapidai import App, LLM, stream

app = App()
llm = LLM("claude-3-haiku-20240307")


@app.route("/chat", methods=["POST"])
@stream
async def chat(user_id: str, message: str):
    """Stateful conversation with memory."""
    memory = app.memory(user_id)

    # Get conversation history
    history = memory.to_dict_list()

    # Generate response with context
    response = await llm.chat(message, history=history, stream=True)
    async for chunk in response:
        yield chunk

    # Save conversation (user message and assistant response)
    memory.add(role="user", content=message)
    # Note: In production, you'd accumulate the full response before saving
    memory.add(role="assistant", content="[Response would be accumulated here]")


@app.route("/clear", methods=["POST"])
async def clear_history(user_id: str):
    """Clear conversation history for a user."""
    memory = app.memory(user_id)
    memory.clear()
    return {"status": "cleared"}


if __name__ == "__main__":
    print("Starting stateful chatbot server on http://localhost:8001")
    print("Try: curl -X POST http://localhost:8001/chat -H 'Content-Type: application/json' -d '{\"user_id\": \"user123\", \"message\": \"Hello!\"}'")
    app.run(port=8001)
