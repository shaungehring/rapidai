"""Conversation memory system for RapidAI."""

from typing import Dict, List, Optional
from .types import Message, ConversationHistory
from .exceptions import MemoryError


class ConversationMemory:
    """Manages conversation history for a specific user/session."""

    def __init__(
        self,
        user_id: str,
        storage: "MemoryStorage",
        max_history: int = 10,
    ):
        """Initialize conversation memory.

        Args:
            user_id: User identifier
            storage: Backend storage implementation
            max_history: Maximum number of messages to keep
        """
        self.user_id = user_id
        self.storage = storage
        self.max_history = max_history

    def get(self) -> List[Message]:
        """Get conversation history.

        Returns:
            List of messages in the conversation
        """
        history = self.storage.get(self.user_id)
        if history:
            return history.messages
        return []

    def add(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Add a message to the conversation.

        Args:
            role: Message role ("user", "assistant", "system")
            content: Message content
            metadata: Optional metadata
        """
        message = Message(role=role, content=content, metadata=metadata)
        history = self.storage.get(self.user_id) or ConversationHistory(
            messages=[], user_id=self.user_id
        )

        history.messages.append(message)

        # Trim history if too long
        if len(history.messages) > self.max_history:
            history.messages = history.messages[-self.max_history :]

        self.storage.set(self.user_id, history)

    def clear(self) -> None:
        """Clear conversation history."""
        self.storage.delete(self.user_id)

    def to_dict_list(self) -> List[Dict[str, str]]:
        """Convert messages to list of dicts (for LLM APIs).

        Returns:
            List of message dictionaries
        """
        messages = self.get()
        return [{"role": msg.role, "content": msg.content} for msg in messages]


class MemoryStorage:
    """Base class for memory storage backends."""

    def get(self, user_id: str) -> Optional[ConversationHistory]:
        """Get conversation history for a user."""
        raise NotImplementedError

    def set(self, user_id: str, history: ConversationHistory) -> None:
        """Set conversation history for a user."""
        raise NotImplementedError

    def delete(self, user_id: str) -> None:
        """Delete conversation history for a user."""
        raise NotImplementedError


class InMemoryStorage(MemoryStorage):
    """In-memory storage backend."""

    def __init__(self) -> None:
        self._storage: Dict[str, ConversationHistory] = {}

    def get(self, user_id: str) -> Optional[ConversationHistory]:
        return self._storage.get(user_id)

    def set(self, user_id: str, history: ConversationHistory) -> None:
        self._storage[user_id] = history

    def delete(self, user_id: str) -> None:
        if user_id in self._storage:
            del self._storage[user_id]


class RedisStorage(MemoryStorage):
    """Redis storage backend."""

    def __init__(self, url: str = "redis://localhost:6379", prefix: str = "rapidai:memory:"):
        """Initialize Redis storage.

        Args:
            url: Redis connection URL
            prefix: Key prefix for namespacing
        """
        try:
            import redis
            import pickle
        except ImportError:
            raise MemoryError(
                "redis not installed. Install with: pip install redis"
            )

        self.prefix = prefix
        self.client = redis.from_url(url, decode_responses=False)

    def get(self, user_id: str) -> Optional[ConversationHistory]:
        """Get conversation history from Redis."""
        try:
            import pickle
            data = self.client.get(self.prefix + user_id)
            if data:
                return pickle.loads(data)
            return None
        except Exception as e:
            raise MemoryError(f"Redis get error: {str(e)}")

    def set(self, user_id: str, history: ConversationHistory) -> None:
        """Set conversation history in Redis."""
        try:
            import pickle
            serialized = pickle.dumps(history)
            # Store indefinitely (no expiry)
            self.client.set(self.prefix + user_id, serialized)
        except Exception as e:
            raise MemoryError(f"Redis set error: {str(e)}")

    def delete(self, user_id: str) -> None:
        """Delete conversation history from Redis."""
        try:
            self.client.delete(self.prefix + user_id)
        except Exception as e:
            raise MemoryError(f"Redis delete error: {str(e)}")


class PostgresStorage(MemoryStorage):
    """PostgreSQL storage backend."""

    def __init__(self, connection_string: str = None):
        """Initialize PostgreSQL storage.

        Args:
            connection_string: PostgreSQL connection string
                Example: "postgresql://user:password@localhost/dbname"
        """
        try:
            import psycopg2
            import json
        except ImportError:
            raise MemoryError(
                "psycopg2 not installed. Install with: pip install psycopg2-binary"
            )

        if not connection_string:
            raise MemoryError("PostgreSQL connection string required")

        self.conn = psycopg2.connect(connection_string)
        self._create_table()

    def _create_table(self) -> None:
        """Create conversations table if it doesn't exist."""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    user_id VARCHAR(255) PRIMARY KEY,
                    messages JSONB NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.commit()

    def get(self, user_id: str) -> Optional[ConversationHistory]:
        """Get conversation history from PostgreSQL."""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT messages FROM conversations WHERE user_id = %s",
                    (user_id,)
                )
                result = cursor.fetchone()

                if result:
                    import json
                    messages_data = result[0]
                    messages = [
                        Message(**msg) for msg in messages_data
                    ]
                    return ConversationHistory(
                        messages=messages,
                        user_id=user_id
                    )
                return None
        except Exception as e:
            raise MemoryError(f"PostgreSQL get error: {str(e)}")

    def set(self, user_id: str, history: ConversationHistory) -> None:
        """Set conversation history in PostgreSQL."""
        try:
            import json
            messages_data = [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "metadata": msg.metadata
                }
                for msg in history.messages
            ]

            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO conversations (user_id, messages)
                    VALUES (%s, %s)
                    ON CONFLICT (user_id)
                    DO UPDATE SET messages = %s, updated_at = CURRENT_TIMESTAMP
                """, (user_id, json.dumps(messages_data), json.dumps(messages_data)))
                self.conn.commit()
        except Exception as e:
            raise MemoryError(f"PostgreSQL set error: {str(e)}")

    def delete(self, user_id: str) -> None:
        """Delete conversation history from PostgreSQL."""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM conversations WHERE user_id = %s",
                    (user_id,)
                )
                self.conn.commit()
        except Exception as e:
            raise MemoryError(f"PostgreSQL delete error: {str(e)}")


class MemoryManager:
    """Manages conversation memory instances."""

    def __init__(self, backend: str = "memory", max_history: int = 10):
        """Initialize memory manager.

        Args:
            backend: Storage backend ("memory", "redis", "postgres")
            max_history: Maximum messages to keep per conversation
        """
        self.max_history = max_history
        self.storage = self._create_storage(backend)
        self._memories: Dict[str, ConversationMemory] = {}

    def _create_storage(self, backend: str) -> MemoryStorage:
        """Create storage backend instance."""
        if backend == "memory":
            return InMemoryStorage()
        elif backend == "redis":
            from .config import RapidAIConfig
            config = RapidAIConfig.load()
            redis_url = config.memory.redis_url or "redis://localhost:6379"
            return RedisStorage(url=redis_url)
        elif backend == "postgres":
            from .config import RapidAIConfig
            import os
            config = RapidAIConfig.load()
            # Get connection string from config or environment
            conn_str = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")
            if not conn_str:
                raise MemoryError(
                    "PostgreSQL connection string required. "
                    "Set DATABASE_URL or POSTGRES_URL environment variable."
                )
            return PostgresStorage(connection_string=conn_str)
        else:
            raise MemoryError(f"Unknown backend: {backend}")

    def get(self, user_id: str) -> ConversationMemory:
        """Get or create conversation memory for a user.

        Args:
            user_id: User identifier

        Returns:
            ConversationMemory instance
        """
        if user_id not in self._memories:
            self._memories[user_id] = ConversationMemory(
                user_id=user_id,
                storage=self.storage,
                max_history=self.max_history,
            )
        return self._memories[user_id]
