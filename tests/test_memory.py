"""Tests for memory system."""

import pytest
from rapidai.memory import ConversationMemory, InMemoryStorage, MemoryManager
from rapidai.types import Message


def test_in_memory_storage():
    """Test in-memory storage backend."""
    storage = InMemoryStorage()

    # Test set and get
    from rapidai.types import ConversationHistory

    history = ConversationHistory(
        messages=[Message(role="user", content="Hello")],
        user_id="user1",
    )
    storage.set("user1", history)

    retrieved = storage.get("user1")
    assert retrieved is not None
    assert len(retrieved.messages) == 1
    assert retrieved.messages[0].content == "Hello"

    # Test delete
    storage.delete("user1")
    assert storage.get("user1") is None


def test_conversation_memory():
    """Test conversation memory."""
    storage = InMemoryStorage()
    memory = ConversationMemory("user1", storage, max_history=5)

    # Add messages
    memory.add("user", "Hello")
    memory.add("assistant", "Hi there!")

    # Get history
    messages = memory.get()
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[1].role == "assistant"


def test_conversation_memory_max_history():
    """Test max history limit."""
    storage = InMemoryStorage()
    memory = ConversationMemory("user1", storage, max_history=3)

    # Add more messages than max
    for i in range(5):
        memory.add("user", f"Message {i}")

    # Should only keep last 3
    messages = memory.get()
    assert len(messages) == 3
    assert messages[0].content == "Message 2"
    assert messages[2].content == "Message 4"


def test_conversation_memory_clear():
    """Test clearing conversation history."""
    storage = InMemoryStorage()
    memory = ConversationMemory("user1", storage)

    memory.add("user", "Hello")
    memory.add("assistant", "Hi!")

    assert len(memory.get()) == 2

    memory.clear()
    assert len(memory.get()) == 0


def test_conversation_memory_to_dict_list():
    """Test converting messages to dict list."""
    storage = InMemoryStorage()
    memory = ConversationMemory("user1", storage)

    memory.add("user", "Hello")
    memory.add("assistant", "Hi there!")

    dict_list = memory.to_dict_list()
    assert len(dict_list) == 2
    assert dict_list[0] == {"role": "user", "content": "Hello"}
    assert dict_list[1] == {"role": "assistant", "content": "Hi there!"}


def test_memory_manager():
    """Test memory manager."""
    manager = MemoryManager(backend="memory", max_history=10)

    # Get memory for different users
    memory1 = manager.get("user1")
    memory2 = manager.get("user2")

    assert memory1.user_id == "user1"
    assert memory2.user_id == "user2"

    # Same user should get same memory instance
    memory1_again = manager.get("user1")
    assert memory1 is memory1_again
