"""RAG example with multiple document sources and filtering."""

from rapidai import App, LLM
from rapidai.rag import RAG

app = App(title="RAG Multi-Source Example")
llm = LLM("claude-3-haiku-20240307")
rag = RAG()


@app.route("/init", methods=["POST"])
async def initialize(documents: list):
    """Load multiple documents into the RAG system.

    Args:
        documents: List of file paths to load

    Returns:
        Loading summary

    Example:
        curl -X POST http://localhost:8003/init \\
            -H "Content-Type: application/json" \\
            -d '{"documents": ["doc1.pdf", "doc2.md", "doc3.txt"]}'
    """
    try:
        all_chunks = await rag.add_documents(documents)
        total_chunks = sum(len(chunks) for chunks in all_chunks)

        return {
            "message": "Documents loaded successfully",
            "documents_loaded": len(documents),
            "total_chunks": total_chunks,
            "details": [
                {"file": doc, "chunks": len(chunks)}
                for doc, chunks in zip(documents, all_chunks)
            ],
        }
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/search", methods=["POST"])
async def search(query: str, doc_type: str = None, top_k: int = 5):
    """Search with optional document type filtering.

    Args:
        query: Search query
        doc_type: Optional document type filter (pdf, txt, md, etc.)
        top_k: Number of results

    Returns:
        Search results with metadata

    Example:
        # Search all documents
        curl -X POST http://localhost:8003/search \\
            -H "Content-Type: application/json" \\
            -d '{"query": "installation", "top_k": 5}'

        # Search only PDF documents
        curl -X POST http://localhost:8003/search \\
            -H "Content-Type: application/json" \\
            -d '{"query": "installation", "doc_type": "pdf", "top_k": 5}'
    """
    try:
        # Build metadata filter
        filter_meta = {"type": doc_type} if doc_type else None

        result = await rag.retrieve(
            query, top_k=top_k, filter_metadata=filter_meta
        )

        return {
            "query": query,
            "filter": filter_meta,
            "results": [
                {
                    "content": chunk.content[:200],
                    "source": chunk.metadata.get("filename"),
                    "type": chunk.metadata.get("type"),
                    "chunk_index": chunk.metadata.get("chunk_index"),
                }
                for chunk in result.sources
            ],
        }
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/ask", methods=["POST"])
async def ask(question: str, doc_type: str = None):
    """Ask a question with optional document type filtering.

    Args:
        question: Question to ask
        doc_type: Optional document type filter

    Returns:
        Answer with sources

    Example:
        curl -X POST http://localhost:8003/ask \\
            -H "Content-Type: application/json" \\
            -d '{"question": "How do I install?", "doc_type": "pdf"}'
    """
    try:
        # Retrieve with optional filtering
        filter_meta = {"type": doc_type} if doc_type else None
        retrieval = await rag.retrieve(
            question, top_k=5, filter_metadata=filter_meta
        )

        # Build prompt
        prompt = f"""Answer the question based on the provided context.

Context:
{retrieval.text}

Question: {question}

Answer:"""

        # Generate response
        response = await llm.complete(prompt)

        return {
            "answer": response,
            "sources": [
                {
                    "filename": chunk.metadata.get("filename"),
                    "type": chunk.metadata.get("type"),
                }
                for chunk in retrieval.sources
            ],
        }
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/stats", methods=["GET"])
async def stats():
    """Get RAG system statistics.

    Returns:
        System statistics

    Example:
        curl http://localhost:8003/stats
    """
    return {
        "collection_initialized": rag._collection_initialized,
        "embedding_model": rag.embedding.config.model,
        "embedding_provider": rag.embedding.config.provider,
        "chunk_size": rag.chunker.chunk_size,
        "chunk_overlap": rag.chunker.chunk_overlap,
    }


@app.route("/health", methods=["GET"])
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    print("Starting RAG Multi-Source Example...")
    print("Initialize: POST /init")
    print("Search: POST /search")
    print("Ask: POST /ask")
    print("Stats: GET /stats")
    print("")
    print("Features:")
    print("- Load multiple documents")
    print("- Filter by document type")
    print("- View system statistics")
    app.run(port=8003)
