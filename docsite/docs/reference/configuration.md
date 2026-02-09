# Configuration API Reference

Complete API reference for RapidAI's configuration system.

## Configuration Classes

### RapidAIConfig

```python
class RapidAIConfig(BaseSettings):
    app: AppConfig
    llm: LLMConfig
    cache: CacheConfig
    memory: MemoryConfig
    rag: RAGConfig
    prompts: PromptsConfig
```

Root configuration object that contains all subsystem configurations.

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `app` | `AppConfig` | Application configuration |
| `llm` | `LLMConfig` | LLM provider configuration |
| `cache` | `CacheConfig` | Caching configuration |
| `memory` | `MemoryConfig` | Memory storage configuration |
| `rag` | `RAGConfig` | RAG system configuration |
| `prompts` | `PromptsConfig` | Prompt management configuration |

**Example:**

```python
from rapidai.config import get_config

config = get_config()
print(config.app.title)
print(config.llm.provider)
```

### AppConfig

```python
class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RAPIDAI_APP_", extra="ignore")

    title: str = "RapidAI Application"
    version: str = "0.1.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
```

Application-level configuration.

**Environment Variables:**

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `RAPIDAI_APP_TITLE` | `str` | `"RapidAI Application"` | Application title |
| `RAPIDAI_APP_VERSION` | `str` | `"0.1.0"` | Application version |
| `RAPIDAI_APP_DEBUG` | `bool` | `False` | Enable debug mode |
| `RAPIDAI_APP_HOST` | `str` | `"0.0.0.0"` | Server host |
| `RAPIDAI_APP_PORT` | `int` | `8000` | Server port |

**Example:**

```bash
export RAPIDAI_APP_TITLE="My AI App"
export RAPIDAI_APP_DEBUG=true
export RAPIDAI_APP_PORT=3000
```

### LLMConfig

```python
class LLMConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RAPIDAI_LLM_", extra="ignore")

    provider: str = "anthropic"
    model: str = "claude-3-haiku-20240307"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1024
```

LLM provider configuration.

**Environment Variables:**

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `RAPIDAI_LLM_PROVIDER` | `str` | `"anthropic"` | LLM provider (anthropic/openai) |
| `RAPIDAI_LLM_MODEL` | `str` | `"claude-3-haiku-20240307"` | Model name |
| `RAPIDAI_LLM_API_KEY` | `str` | `None` | API key |
| `RAPIDAI_LLM_TEMPERATURE` | `float` | `0.7` | Sampling temperature |
| `RAPIDAI_LLM_MAX_TOKENS` | `int` | `1024` | Maximum tokens |

**Example:**

```bash
export RAPIDAI_LLM_PROVIDER=openai
export RAPIDAI_LLM_MODEL=gpt-4o-mini
export RAPIDAI_LLM_API_KEY=sk-...
export RAPIDAI_LLM_TEMPERATURE=0.5
```

### CacheConfig

```python
class CacheConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RAPIDAI_CACHE_", extra="ignore")

    backend: str = "memory"
    ttl: int = 3600
    redis_url: Optional[str] = None
```

Caching configuration.

**Environment Variables:**

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `RAPIDAI_CACHE_BACKEND` | `str` | `"memory"` | Cache backend (memory/redis) |
| `RAPIDAI_CACHE_TTL` | `int` | `3600` | Default TTL in seconds |
| `RAPIDAI_CACHE_REDIS_URL` | `str` | `None` | Redis connection URL |

**Example:**

```bash
export RAPIDAI_CACHE_BACKEND=redis
export RAPIDAI_CACHE_TTL=7200
export RAPIDAI_CACHE_REDIS_URL=redis://localhost:6379
```

### MemoryConfig

```python
class MemoryConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RAPIDAI_MEMORY_", extra="ignore")

    backend: str = "memory"
    max_messages: int = 100
    redis_url: Optional[str] = None
```

Memory storage configuration.

**Environment Variables:**

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `RAPIDAI_MEMORY_BACKEND` | `str` | `"memory"` | Memory backend (memory/redis) |
| `RAPIDAI_MEMORY_MAX_MESSAGES` | `int` | `100` | Max messages per conversation |
| `RAPIDAI_MEMORY_REDIS_URL` | `str` | `None` | Redis connection URL |

**Example:**

```bash
export RAPIDAI_MEMORY_BACKEND=redis
export RAPIDAI_MEMORY_MAX_MESSAGES=500
export RAPIDAI_MEMORY_REDIS_URL=redis://localhost:6379
```

### RAGConfig

```python
class RAGConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RAPIDAI_RAG_", extra="ignore")

    embedding: EmbeddingConfig
    chunking: ChunkingConfig
    vectordb: VectorDBConfig
    top_k: int = 5
```

RAG system configuration.

**Environment Variables:**

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `RAPIDAI_RAG_TOP_K` | `int` | `5` | Default number of results |

#### EmbeddingConfig

```python
class EmbeddingConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RAPIDAI_EMBEDDING_", extra="ignore")

    provider: str = "sentence-transformers"
    model: str = "all-MiniLM-L6-v2"
    batch_size: int = 32
    api_key: Optional[str] = None
```

**Environment Variables:**

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `RAPIDAI_EMBEDDING_PROVIDER` | `str` | `"sentence-transformers"` | Embedding provider |
| `RAPIDAI_EMBEDDING_MODEL` | `str` | `"all-MiniLM-L6-v2"` | Embedding model |
| `RAPIDAI_EMBEDDING_BATCH_SIZE` | `int` | `32` | Batch size |
| `RAPIDAI_EMBEDDING_API_KEY` | `str` | `None` | API key for OpenAI embeddings |

#### ChunkingConfig

```python
class ChunkingConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RAPIDAI_CHUNKING_", extra="ignore")

    strategy: str = "recursive"
    chunk_size: int = 512
    chunk_overlap: int = 50
```

**Environment Variables:**

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `RAPIDAI_CHUNKING_STRATEGY` | `str` | `"recursive"` | Chunking strategy |
| `RAPIDAI_CHUNKING_CHUNK_SIZE` | `int` | `512` | Chunk size in characters |
| `RAPIDAI_CHUNKING_CHUNK_OVERLAP` | `int` | `50` | Overlap between chunks |

#### VectorDBConfig

```python
class VectorDBConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RAPIDAI_VECTORDB_", extra="ignore")

    backend: str = "chromadb"
    persist_directory: str = "./chroma_data"
    collection_name: str = "rapidai_docs"
```

**Environment Variables:**

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `RAPIDAI_VECTORDB_BACKEND` | `str` | `"chromadb"` | Vector DB backend |
| `RAPIDAI_VECTORDB_PERSIST_DIRECTORY` | `str` | `"./chroma_data"` | Persistence directory |
| `RAPIDAI_VECTORDB_COLLECTION_NAME` | `str` | `"rapidai_docs"` | Collection name |

### PromptsConfig

```python
class PromptsConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RAPIDAI_PROMPTS_", extra="ignore")

    directory: str = "./prompts"
    use_jinja: bool = True
```

Prompt management configuration.

**Environment Variables:**

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `RAPIDAI_PROMPTS_DIRECTORY` | `str` | `"./prompts"` | Prompts directory |
| `RAPIDAI_PROMPTS_USE_JINJA` | `bool` | `True` | Enable Jinja2 templates |

**Example:**

```bash
export RAPIDAI_PROMPTS_DIRECTORY=./templates
export RAPIDAI_PROMPTS_USE_JINJA=true
```

## Functions

### get_config

```python
def get_config() -> RapidAIConfig
```

Get or create global configuration instance.

**Returns:** `RapidAIConfig` - Global configuration singleton

**Example:**

```python
from rapidai.config import get_config

config = get_config()
print(config.app.title)
print(config.llm.model)
```

### load_config

```python
def load_config(path: str) -> RapidAIConfig
```

Load configuration from file.

**Parameters:**

- `path` (`str`) - Path to configuration file (YAML, JSON, or TOML)

**Returns:** `RapidAIConfig` - Loaded configuration

**Example:**

```python
from rapidai.config import load_config

config = load_config("config.yaml")
```

**Supported formats:**

YAML:
```yaml
app:
  title: My AI App
  port: 3000

llm:
  provider: openai
  model: gpt-4o-mini
  api_key: sk-...
```

JSON:
```json
{
  "app": {
    "title": "My AI App",
    "port": 3000
  },
  "llm": {
    "provider": "openai",
    "model": "gpt-4o-mini"
  }
}
```

## Configuration Priority

Configuration values are loaded in the following priority order (highest to lowest):

1. **Environment variables** - `RAPIDAI_*` variables
2. **Configuration file** - Loaded via `load_config()`
3. **Default values** - Built-in defaults

**Example:**

```python
# Default
config.app.port  # 8000

# Override with environment variable
os.environ["RAPIDAI_APP_PORT"] = "3000"
config = get_config()
config.app.port  # 3000

# Override with config file
config = load_config("config.yaml")  # port: 9000
config.app.port  # 9000
```

## Complete Example

**config.yaml:**

```yaml
app:
  title: Production AI App
  debug: false
  port: 8080

llm:
  provider: anthropic
  model: claude-3-haiku-20240307
  temperature: 0.7
  max_tokens: 2048

cache:
  backend: redis
  ttl: 7200
  redis_url: redis://localhost:6379

memory:
  backend: redis
  max_messages: 500
  redis_url: redis://localhost:6379

rag:
  top_k: 10
  embedding:
    provider: openai
    model: text-embedding-3-small
  chunking:
    chunk_size: 1024
    chunk_overlap: 100
  vectordb:
    backend: chromadb
    persist_directory: ./vector_data

prompts:
  directory: ./prompt_templates
  use_jinja: true
```

**app.py:**

```python
from rapidai import App
from rapidai.config import load_config

# Load configuration
config = load_config("config.yaml")

# Create app with config
app = App(
    title=config.app.title,
    debug=config.app.debug
)

@app.route("/config")
async def get_config_info():
    return {
        "app": {
            "title": config.app.title,
            "version": config.app.version,
            "port": config.app.port
        },
        "llm": {
            "provider": config.llm.provider,
            "model": config.llm.model
        },
        "cache": {
            "backend": config.cache.backend,
            "ttl": config.cache.ttl
        }
    }

if __name__ == "__main__":
    app.run(
        host=config.app.host,
        port=config.app.port
    )
```

## See Also

- [CLI Reference](cli.md) - CLI configuration options
- [Deployment Tutorial](../tutorial/deployment.md) - Production configuration
- [RAG Reference](rag.md) - RAG configuration details
