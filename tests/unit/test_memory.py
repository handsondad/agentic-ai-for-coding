"""记忆存储单元测试。"""

from __future__ import annotations

from src.memory.store import MemoryStore


class TestMemoryStore:
    """MemoryStore 单元测试。"""

    def test_set_and_get(self, memory_store: MemoryStore) -> None:
        """set 后应该能通过 get 取回相同的值。"""
        memory_store.set("session-1", "user_name", "Alice")
        assert memory_store.get("session-1", "user_name") == "Alice"

    def test_get_returns_default_for_missing_key(self, memory_store: MemoryStore) -> None:
        """get 一个不存在的 key 应该返回默认值。"""
        result = memory_store.get("session-1", "nonexistent", default="default_value")
        assert result == "default_value"

    def test_get_returns_none_for_missing_key_no_default(self, memory_store: MemoryStore) -> None:
        """get 一个不存在的 key 且无默认值时应该返回 None。"""
        result = memory_store.get("session-1", "nonexistent")
        assert result is None

    def test_sessions_are_isolated(self, memory_store: MemoryStore) -> None:
        """不同会话的数据应该相互隔离。"""
        memory_store.set("session-a", "key", "value-a")
        memory_store.set("session-b", "key", "value-b")

        assert memory_store.get("session-a", "key") == "value-a"
        assert memory_store.get("session-b", "key") == "value-b"

    def test_delete_key_removes_specific_key(self, memory_store: MemoryStore) -> None:
        """delete(session, key) 应该只删除指定的 key。"""
        memory_store.set("session-1", "key1", "v1")
        memory_store.set("session-1", "key2", "v2")

        memory_store.delete("session-1", "key1")

        assert memory_store.get("session-1", "key1") is None
        assert memory_store.get("session-1", "key2") == "v2"

    def test_delete_session_removes_all_data(self, memory_store: MemoryStore) -> None:
        """delete(session) 应该删除该会话的所有数据。"""
        memory_store.set("session-1", "key1", "v1")
        memory_store.set("session-1", "key2", "v2")

        memory_store.delete("session-1")

        assert memory_store.get("session-1", "key1") is None
        assert memory_store.get("session-1", "key2") is None

    def test_get_all_returns_complete_session_data(self, memory_store: MemoryStore) -> None:
        """get_all 应该返回该会话的所有数据。"""
        memory_store.set("session-1", "name", "Alice")
        memory_store.set("session-1", "age", 30)

        all_data = memory_store.get_all("session-1")

        assert all_data == {"name": "Alice", "age": 30}

    def test_get_all_returns_copy_not_reference(self, memory_store: MemoryStore) -> None:
        """get_all 应该返回副本，不是原始数据的引用。"""
        memory_store.set("session-1", "key", "original")
        all_data = memory_store.get_all("session-1")

        # 修改返回的字典不应该影响存储中的数据
        all_data["key"] = "modified"
        assert memory_store.get("session-1", "key") == "original"

    def test_overwrite_existing_key(self, memory_store: MemoryStore) -> None:
        """set 一个已存在的 key 应该覆盖原值。"""
        memory_store.set("session-1", "key", "original")
        memory_store.set("session-1", "key", "updated")

        assert memory_store.get("session-1", "key") == "updated"
