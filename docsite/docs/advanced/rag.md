# Retrieval-Augmented Generation (RAG)

RapidAI includes a powerful RAG system that allows you to augment your LLM applications with custom knowledge from documents.

## Quick Start

```python
from rapidai import App, LLM
from rapidai.rag import RAG

app = App()
llm = LLM("claude-3-haiku-20240307")
rag = RAG()

# Add documents
await rag.add_document("docs/manual.pdf")

# Query with context
answer = await rag.query("How do I install?", llm=llm)
```

## Architecture

The RAG system consists of four main components:

1. **Document Loaders** - Load PDF, DOCX, TXT, HTML, Markdown
2. **Chunkers** - Split documents into semantic chunks
3. **Embeddings** - Convert text to vector embeddings
4. **Vector Database** - Store and search embeddings

## Configuration

Configure RAG via environment variables or YAML:

```yaml
rag:
  embedding:
    provider: "sentence-transformers"  # or "openai"
    model: "all-MiniLM-L6-v2"

  chunking:
    strategy: "recursive"  # or "sentence"
    chunk_size: 512
    chunk_overlap: 50

  vectordb:
    backend: "chromadb"
    persist_directory: "./chroma_data"
    collection_name: "my_docs"

  top_k: 5
```

Or via environment variables:

```bash
RAPIDAI_RAG_TOP_K=5
RAPIDAI_EMBEDDING_PROVIDER=openai
RAPIDAI_EMBEDDING_MODEL=text-embedding-3-small
```

## Document Loading

### Supported Formats

- PDF (`.pdf`)
- Word Documents (`.docx`)
- Plain Text (`.txt`)
- Markdown (`.md`)
- HTML (`.html`, `.htm`)

### Loading Documents

```python
from rapidai.rag import RAG

rag = RAG()

# Single document
await rag.add_document("path/to/document.pdf")

# Multiple documents
await rag.add_documents([
    "doc1.pdf",
    "doc2.docx",
    "doc3.md"
])

# From Document object
from rapidai.types import Document

doc = Document(
    content="Custom content",
    metadata={"source": "manual", "version": "1.0"}
)
await rag.add_document(doc)
```

## Embeddings

RapidAI supports multiple embedding providers:

### Sentence Transformers (Default)

```python
from rapidai.rag import Embedding

embedding = Embedding(
    provider="sentence-transformers",
    model="all-MiniLM-L6-v2"
)
```

**Pros:**

- Free and open source
- Runs locally (no API costs)
- Fast for batch processing

**Cons:**

- Requires local compute
- Lower quality than OpenAI

### OpenAI Embeddings

```python
embedding = Embedding(
    provider="openai",
    model="text-embedding-3-small",
    api_key="your-api-key"  # or OPENAI_API_KEY env var
)
```

**Pros:**

- High quality embeddings
- Latest models

**Cons:**

- API costs
- Requires internet connection

### Custom Configuration

```python
from rapidai.rag import RAG, Embedding

embedding = Embedding(provider="openai", model="text-embedding-3-large")
rag = RAG(embedding=embedding)
```

## Retrieval

### Basic Retrieval

```python
# Retrieve relevant chunks
result = await rag.retrieve("your query", top_k=5)

print(result.text)  # Combined text from chunks
print(result.sources)  # List of DocumentChunk objects
```

### With Metadata Filtering

```python
# Only search in specific document types
result = await rag.retrieve(
    "query",
    top_k=5,
    filter_metadata={"type": "pdf"}
)
```

### Full RAG Query

```python
from rapidai import LLM

llm = LLM("claude-3-haiku-20240307")

# Retrieve + Generate in one call
answer = await rag.query(
    "What is the installation process?",
    llm=llm,
    top_k=5
)
```

## RAG Decorator

The `@rag()` decorator automatically injects retrieval context into your routes:

```python
from rapidai import App, LLM
from rapidai.rag import rag

app = App()
llm = LLM("claude-3-haiku-20240307")

@app.route("/ask", methods=["POST"])
@rag(sources=["docs/manual.pdf"], top_k=5)
async def ask(query: str, rag_context):
    """rag_context is automatically injected."""
    prompt = f"Context: {rag_context.text}\n\nQuestion: {query}"
    answer = await llm.complete(prompt)

    return {
        "answer": answer,
        "sources": [s.metadata for s in rag_context.sources]
    }
```

## Chunking Strategies

### Recursive Chunking (Default)

Splits text using multiple separators hierarchically:

```python
from rapidai.rag import Chunker

chunker = Chunker(
    strategy="recursive",
    chunk_size=512,
    chunk_overlap=50
)
```

**Best for:** General purpose, mixed content

### Sentence Chunking

Splits by sentences with semantic boundaries:

```python
chunker = Chunker(
    strategy="sentence",
    chunk_size=512,
    chunk_overlap=2  # Number of sentences to overlap
)
```

**Best for:** Narrative text, articles

## Best Practices

1. **Chunk Size**: Start with 512 tokens, adjust based on your use case
2. **Overlap**: Use 10-20% overlap to maintain context
3. **top_k**: Start with 3-5 chunks, increase if needed
4. **Embeddings**: Use sentence-transformers for speed, OpenAI for quality
5. **Metadata**: Add rich metadata for filtering and provenance

## Complete Example: Customer Support Bot

```python
from rapidai import App, LLM
from rapidai.rag import rag

app = App()
llm = LLM("claude-3-haiku-20240307")

@app.route("/support", methods=["POST"])
@rag(
    sources=[
        "kb/troubleshooting.pdf",
        "kb/faq.md",
        "kb/user_guide.pdf"
    ],
    top_k=5
)
async def support_query(question: str, rag_context):
    """Customer support with RAG."""
    system_prompt = """You are a helpful customer support assistant.
    Answer based on the knowledge base provided. If unsure, say so."""

    prompt = f"""{system_prompt}

Knowledge Base:
{rag_context.text}

Customer Question: {question}

Answer:"""

    response = await llm.complete(prompt)

    return {
        "answer": response,
        "sources": [
            {
                "file": s.metadata.get("filename"),
                "excerpt": s.content[:100]
            }
            for s in rag_context.sources
        ]
    }

if __name__ == "__main__":
    app.run()
```

## See Also

- [RAG API Reference](../reference/rag.html)
- [Configuration Guide](configuration.html)
- [Testing RAG Applications](testing.html)
