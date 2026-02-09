"""Basic RAG example with manual document upload."""

from rapidai import App, LLM
from rapidai.rag import RAG

app = App(title="RAG Basic Example")
llm = LLM("claude-3-haiku-20240307")

# Initialize RAG system
rag = RAG()


@app.route("/upload", methods=["POST"])
async def upload_document(filepath: str):
    """Upload a document to the RAG system.

    Args:
        filepath: Path to the document to upload

    Returns:
        Upload confirmation with chunk count

    Example:
        curl -X POST http://localhost:8001/upload \\
            -H "Content-Type: application/json" \\
            -d '{"filepath": "test.txt"}'
    """
    try:
        chunks = await rag.add_document(filepath)
        return {
            "message": "Document uploaded successfully",
            "filepath": filepath,
            "chunks": len(chunks),
        }
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/ask", methods=["POST"])
async def ask(question: str):
    """Ask a question using RAG.

    Args:
        question: Question to ask

    Returns:
        Answer based on uploaded documents

    Example:
        curl -X POST http://localhost:8001/ask \\
            -H "Content-Type: application/json" \\
            -d '{"question": "What is this document about?"}'
    """
    try:
        answer = await rag.query(question, llm=llm, top_k=5)
        return {"answer": answer}
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/search", methods=["POST"])
async def search(query: str, top_k: int = 5):
    """Search for relevant document chunks.

    Args:
        query: Search query
        top_k: Number of results to return

    Returns:
        Relevant document chunks

    Example:
        curl -X POST http://localhost:8001/search \\
            -H "Content-Type: application/json" \\
            -d '{"query": "installation", "top_k": 3}'
    """
    try:
        result = await rag.retrieve(query, top_k=top_k)
        return {
            "results": [
                {
                    "content": chunk.content[:200],  # First 200 chars
                    "source": chunk.metadata.get("filename"),
                    "type": chunk.metadata.get("type"),
                }
                for chunk in result.sources
            ]
        }
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/health", methods=["GET"])
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    print("Starting RAG Basic Example...")
    print("Upload documents: POST /upload")
    print("Ask questions: POST /ask")
    print("Search: POST /search")
    app.run(port=8001)
