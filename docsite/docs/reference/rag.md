# RAG API Reference

Complete API reference for RapidAI's RAG system.

## Classes

### RAG

Main orchestrator for retrieval-augmented generation.

```python
class RAG:
    def __init__(
        self,
        embedding: Optional[BaseEmbedding] = None,
        vectordb: Optional[BaseVectorDB] = None,
        chunker: Optional[BaseChunker] = None,
        config: Optional[RAGConfig] = None,
    )
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `embedding` | `BaseEmbedding` | Auto-created | Embedding provider |
| `vectordb` | `BaseVectorDB` | Auto-created | Vector database |
| `chunker` | `BaseChunker` | Auto-created | Text chunker |
| `config` | `RAGConfig` | `None` | Configuration (loads from env if None) |

**Methods:**

#### `async initialize()`

Initialize vector database collection.

```python
await rag.initialize()
```

#### `async add_document(source)`

Add a document to the RAG system.

```python
chunks = await rag.add_document("path/to/doc.pdf")
```

**Parameters:**

- `source` (`str | Path | Document`) - File path or Document object

**Returns:** `List[DocumentChunk]` - Created chunks

#### `async add_documents(sources)`

Add multiple documents.

```python
all_chunks = await rag.add_documents(["doc1.pdf", "doc2.md"])
```

**Parameters:**

- `sources` (`List[str | Path | Document]`) - List of file paths or Document objects

**Returns:** `List[List[DocumentChunk]]` - List of chunk lists

#### `async retrieve(query, top_k, filter_metadata)`

Retrieve relevant chunks for a query.

```python
result = await rag.retrieve("query", top_k=5)
```

**Parameters:**

- `query` (`str`) - Search query
- `top_k` (`Optional[int]`) - Number of results (default from config)
- `filter_metadata` (`Optional[Dict[str, Any]]`) - Metadata filters

**Returns:** `RetrievalResult` - Result with text and sources

#### `async query(query, llm, system_prompt, top_k)`

Full RAG query: retrieve + generate.

```python
answer = await rag.query("question", llm=llm)
```

**Parameters:**

- `query` (`str`) - User query
- `llm` (`BaseLLM`) - LLM instance for generation
- `system_prompt` (`Optional[str]`) - System prompt
- `top_k` (`Optional[int]`) - Number of chunks to retrieve

**Returns:** `str` - Generated response

---

### Embedding

Factory function for creating embedding providers.

```python
def Embedding(
    provider: str = "sentence-transformers",
    **kwargs
) -> BaseEmbedding
```

**Parameters:**

- `provider` (`str`) - Provider name ("sentence-transformers", "openai", "mock")
- `**kwargs` - Additional parameters for provider

**Returns:** `BaseEmbedding` - Embedding instance

**Example:**

```python
# Sentence transformers
embedding = Embedding()

# OpenAI
embedding = Embedding(provider="openai", model="text-embedding-3-large")
```

---

### DocumentLoader

Factory function for creating document loaders.

```python
def DocumentLoader(source: Union[str, Path]) -> BaseDocumentLoader
```

Auto-detects file type from extension and returns appropriate loader.

**Supported extensions:** `.pdf`, `.docx`, `.txt`, `.md`, `.markdown`, `.html`, `.htm`

**Example:**

```python
loader = DocumentLoader("document.pdf")
doc = await loader.load("document.pdf")
```

---

### Chunker

Factory function for creating chunkers.

```python
def Chunker(
    strategy: str = "recursive",
    **kwargs
) -> BaseChunker
```

**Parameters:**

- `strategy` (`str`) - Chunking strategy ("recursive", "sentence")
- `**kwargs` - Additional parameters for chunker

**Strategies:**

- `recursive` - Hierarchical splitting with multiple separators
- `sentence` - Sentence-based splitting

**Example:**

```python
# Recursive
chunker = Chunker()

# Sentence-based
chunker = Chunker(strategy="sentence", chunk_size=512, chunk_overlap=2)
```

---

### VectorDB

Factory function for creating vector databases.

```python
def VectorDB(
    backend: str = "chromadb",
    **kwargs
) -> BaseVectorDB
```

**Parameters:**

- `backend` (`str`) - Backend name ("chromadb", "mock")
- `**kwargs` - Additional parameters for backend

**Example:**

```python
vectordb = VectorDB(backend="chromadb", persist_directory="./my_data")
```

---

## Decorators

### @rag()

Decorator for adding RAG to routes.

```python
def rag(
    sources: Optional[List[Union[str, Path]]] = None,
    top_k: int = 5,
    collection_name: Optional[str] = None,
    auto_initialize: bool = True,
) -> Callable
```

**Parameters:**

- `sources` - Documents to load at startup
- `top_k` - Number of chunks to retrieve
- `collection_name` - Vector DB collection name
- `auto_initialize` - Auto-initialize RAG system

**Example:**

```python
@app.route("/ask", methods=["POST"])
@rag(sources=["docs/manual.pdf"], top_k=5)
async def ask(query: str, rag_context):
    # rag_context is automatically injected
    pass
```

---

## Configuration

### RAGConfig

```python
class RAGConfig(BaseSettings):
    embedding: EmbeddingConfig
    chunking: ChunkingConfig
    vectordb: VectorDBConfig
    top_k: int = 5
    enable_caching: bool = True
    cache_ttl: int = 3600
```

**Environment Variables:**

- `RAPIDAI_RAG_TOP_K` - Default top_k value

### EmbeddingConfig

```python
class EmbeddingConfig(BaseSettings):
    provider: str = "sentence-transformers"
    model: str = "all-MiniLM-L6-v2"
    batch_size: int = 32
    api_key: Optional[str] = None
```

**Environment Variables:**

- `RAPIDAI_EMBEDDING_PROVIDER` - Embedding provider
- `RAPIDAI_EMBEDDING_MODEL` - Model name
- `RAPIDAI_EMBEDDING_BATCH_SIZE` - Batch size
- `RAPIDAI_EMBEDDING_API_KEY` - API key (for OpenAI)

### ChunkingConfig

```python
class ChunkingConfig(BaseSettings):
    strategy: str = "recursive"
    chunk_size: int = 512
    chunk_overlap: int = 50
    separator: str = "\n\n"
```

**Environment Variables:**

- `RAPIDAI_CHUNKING_STRATEGY` - Chunking strategy
- `RAPIDAI_CHUNKING_CHUNK_SIZE` - Chunk size
- `RAPIDAI_CHUNKING_CHUNK_OVERLAP` - Chunk overlap
- `RAPIDAI_CHUNKING_SEPARATOR` - Separator

### VectorDBConfig

```python
class VectorDBConfig(BaseSettings):
    backend: str = "chromadb"
    persist_directory: str = "./chroma_data"
    collection_name: str = "rapidai_docs"
```

**Environment Variables:**

- `RAPIDAI_VECTORDB_BACKEND` - Vector DB backend
- `RAPIDAI_VECTORDB_PERSIST_DIRECTORY` - Persist directory
- `RAPIDAI_VECTORDB_COLLECTION_NAME` - Collection name

---

## Types

All RAG-related types are defined in `rapidai.types`:

### Document

```python
@dataclass
class Document:
    content: str
    metadata: Dict[str, Any]
    chunks: Optional[List[DocumentChunk]] = None
```

### DocumentChunk

```python
@dataclass
class DocumentChunk:
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
```

### RetrievalResult

```python
@dataclass
class RetrievalResult:
    text: str
    sources: List[DocumentChunk]
    score: Optional[float] = None
```

---

## Base Classes

For implementing custom components:

### BaseEmbedding

```python
class BaseEmbedding(ABC):
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        pass
```

### BaseDocumentLoader

```python
class BaseDocumentLoader(ABC):
    @abstractmethod
    async def load(self, source: Union[str, Path]) -> Document:
        pass

    async def load_batch(self, sources: List[Union[str, Path]]) -> List[Document]:
        pass
```

### BaseChunker

```python
class BaseChunker(ABC):
    @abstractmethod
    def chunk(self, document: Document) -> List[DocumentChunk]:
        pass
```

### BaseVectorDB

```python
class BaseVectorDB(ABC):
    @abstractmethod
    async def create_collection(self, name: str, dimension: int, **kwargs) -> None:
        pass

    @abstractmethod
    async def add_chunks(self, collection: str, chunks: List[DocumentChunk]) -> None:
        pass

    @abstractmethod
    async def search(
        self,
        collection: str,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[DocumentChunk]:
        pass

    @abstractmethod
    async def delete_collection(self, name: str) -> None:
        pass
```

---

## See Also

- [RAG Guide](../advanced/rag.md)
- [App Reference](app.md)
- [LLM Reference](llm.md)
