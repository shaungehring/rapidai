"""Configuration management for RapidAI."""

from typing import Any, Dict, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from pathlib import Path
import yaml
from dotenv import load_dotenv

# Load .env file at module import time
load_dotenv()

# Import RAGConfig
from .rag.config import RAGConfig


class LLMConfig(BaseSettings):
    """LLM configuration."""

    model_config = SettingsConfigDict(env_prefix="RAPIDAI_LLM_", extra="ignore")

    provider: str = "anthropic"
    model: str = "claude-3-5-sonnet-20241022"
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout: int = 30


class CacheConfig(BaseSettings):
    """Cache configuration."""

    model_config = SettingsConfigDict(env_prefix="RAPIDAI_CACHE_", extra="ignore")

    backend: str = "memory"
    ttl: int = 3600
    redis_url: Optional[str] = None


class MemoryConfig(BaseSettings):
    """Memory configuration."""

    model_config = SettingsConfigDict(env_prefix="RAPIDAI_MEMORY_", extra="ignore")

    backend: str = "memory"
    max_history: int = 10
    redis_url: Optional[str] = None


class ServerConfig(BaseSettings):
    """Server configuration."""

    model_config = SettingsConfigDict(env_prefix="RAPIDAI_", extra="ignore")

    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    debug: bool = True


class MonitoringConfig(BaseSettings):
    """Monitoring configuration."""

    model_config = SettingsConfigDict(env_prefix="RAPIDAI_", extra="ignore")

    track_costs: bool = True
    log_conversations: bool = False


class RapidAIConfig(BaseSettings):
    """Main configuration class for RapidAI."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    llm: LLMConfig = Field(default_factory=LLMConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    rag: RAGConfig = Field(default_factory=RAGConfig)

    @classmethod
    def from_yaml(cls, path: str) -> "RapidAIConfig":
        """Load configuration from YAML file."""
        yaml_path = Path(path)
        if not yaml_path.exists():
            return cls()

        with open(yaml_path) as f:
            data = yaml.safe_load(f)

        return cls(**data)

    @classmethod
    def load(cls, yaml_path: Optional[str] = None) -> "RapidAIConfig":
        """Load configuration from environment and optionally from YAML."""
        if yaml_path and os.path.exists(yaml_path):
            return cls.from_yaml(yaml_path)
        return cls()
