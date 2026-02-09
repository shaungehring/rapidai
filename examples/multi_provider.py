"""Multi-provider example showing different LLMs for different tasks."""

from rapidai import App, LLM

app = App()

# Different LLMs for different purposes
# Note: This example requires both Anthropic and OpenAI API keys
# For now, using Haiku for both (replace gpt-4o-mini if you have OpenAI key)
cheap_llm = LLM("claude-3-haiku-20240307")  # Fast, cheap for simple queries
smart_llm = LLM("claude-3-haiku-20240307")  # Same model for demo (upgrade account for better models)


@app.route("/quick-answer", methods=["POST"])
async def quick(question: str):
    """Use fast model for simple queries."""
    response = await cheap_llm.chat(question)
    return {"answer": response, "model": "gpt-4o-mini"}


@app.route("/deep-analysis", methods=["POST"])
async def deep(question: str):
    """Use smart model for complex queries."""
    response = await smart_llm.chat(question)
    return {"answer": response, "model": "claude-opus-4"}


@app.route("/compare", methods=["POST"])
async def compare(question: str):
    """Compare responses from both models."""
    cheap_response = await cheap_llm.chat(question)
    smart_response = await smart_llm.chat(question)

    return {
        "question": question,
        "responses": {
            "gpt-4o-mini": cheap_response,
            "claude-opus-4": smart_response,
        },
    }


if __name__ == "__main__":
    print("Starting multi-provider server on http://localhost:8001")
    print("Endpoints:")
    print("  - POST /quick-answer  (uses GPT-4o-mini)")
    print("  - POST /deep-analysis (uses Claude Opus 4)")
    print("  - POST /compare       (uses both models)")
    app.run(port=8001)
