"""记忆存储模块。

提供 Agent 对话历史和状态的持久化管理。
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any

logger = logging.getLogger(__name__)


class MemoryStore:
    """内存存储，管理 Agent 的会话数据。

    当前实现为内存存储（进程内），生产环境可替换为 Redis 或数据库实现。

    设计为无状态接口，便于替换为分布式存储。
    """

    def __init__(self) -> None:
        # key: session_id, value: dict of stored data
        self._store: dict[str, dict[str, Any]] = defaultdict(dict)
        logger.debug("MemoryStore 初始化（内存模式）")

    def set(self, session_id: str, key: str, value: Any) -> None:
        """存储会话相关数据。

        Args:
            session_id: 会话 ID
            key: 数据键
            value: 数据值（必须可 JSON 序列化）
        """
        self._store[session_id][key] = value
        logger.debug("存储数据", extra={"session_id": session_id, "key": key})

    def get(self, session_id: str, key: str, default: Any = None) -> Any:
        """获取会话相关数据。

        Args:
            session_id: 会话 ID
            key: 数据键
            default: 键不存在时的默认值

        Returns:
            存储的值，如果不存在则返回 default
        """
        return self._store.get(session_id, {}).get(key, default)

    def delete(self, session_id: str, key: str | None = None) -> None:
        """删除会话数据。

        Args:
            session_id: 会话 ID
            key: 如果提供，只删除该键；如果为 None，删除整个会话数据
        """
        if key is None:
            self._store.pop(session_id, None)
            logger.debug("删除会话数据", extra={"session_id": session_id})
        elif session_id in self._store:
            self._store[session_id].pop(key, None)
            logger.debug(
                "删除数据键",
                extra={"session_id": session_id, "key": key},
            )

    def get_all(self, session_id: str) -> dict[str, Any]:
        """获取会话的所有存储数据。

        Args:
            session_id: 会话 ID

        Returns:
            会话数据的副本字典
        """
        return dict(self._store.get(session_id, {}))
