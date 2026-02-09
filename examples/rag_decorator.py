"""RAG example using the @rag decorator."""

from rapidai import App, LLM
from rapidai.rag import rag

app = App(title="RAG Decorator Example")
llm = LLM("claude-3-haiku-20240307")


@app.route("/ask", methods=["POST"])
@rag(sources=["README.md"], top_k=5)
async def ask_docs(query: str, rag_context):
    """Ask questions about the README documentation.

    The @rag decorator automatically:
    1. Loads the README.md file at startup
    2. Chunks and embeds the content
    3. Retrieves relevant chunks for each query
    4. Injects rag_context into the function

    Args:
        query: Question to ask
        rag_context: Automatically injected retrieval result

    Returns:
        Answer with sources

    Example:
        curl -X POST http://localhost:8002/ask \\
            -H "Content-Type: application/json" \\
            -d '{"query": "What is RapidAI?"}'
    """
    # Build prompt with context
    prompt = f"""Based on the following context, answer the question.

Context:
{rag_context.text}

Question: {query}

Answer:"""

    # Generate response
    response = await llm.complete(prompt)

    return {
        "answer": response,
        "sources": [
            {
                "filename": chunk.metadata.get("filename"),
                "excerpt": chunk.content[:100] + "...",
            }
            for chunk in rag_context.sources
        ],
    }


@app.route("/health", methods=["GET"])
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    print("Starting RAG Decorator Example...")
    print("This example automatically loads README.md at startup")
    print("Ask questions: POST /ask")
    print("")
    print("Note: Make sure README.md exists in the current directory")
    app.run(port=8002)
