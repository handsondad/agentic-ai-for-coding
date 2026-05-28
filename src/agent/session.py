"""Agent 会话管理模块。"""

from __future__ import annotations

import enum
from datetime import UTC, datetime
from typing import Any


class SessionStatus(enum.Enum):
    """会话状态枚举。"""

    IDLE = "idle"  # 空闲，等待用户输入
    PROCESSING = "processing"  # 正在处理用户消息
    WAITING_TOOL = "waiting_tool"  # 等待工具调用结果
    ERROR = "error"  # 发生错误
    DONE = "done"  # 会话已完成


class Message:
    """对话消息。"""

    def __init__(self, role: str, content: str) -> None:
        self.role = role
        self.content = content
        self.created_at = datetime.now(tz=UTC)

    def to_dict(self) -> dict[str, Any]:
        """转换为 OpenAI API 格式的字典。"""
        return {"role": self.role, "content": self.content}


class AgentSession:
    """Agent 会话，管理单个用户会话的完整生命周期。

    包括对话历史、会话状态和元数据管理。
    """

    # 对话历史最大长度（超出时截断旧消息）
    MAX_HISTORY_LENGTH = 50

    def __init__(self, session_id: str) -> None:
        """初始化会话。

        Args:
            session_id: 会话唯一标识符
        """
        self.session_id = session_id
        self.status = SessionStatus.IDLE
        self.created_at = datetime.now(tz=UTC)
        self.updated_at = datetime.now(tz=UTC)
        self._messages: list[Message] = []

    def add_user_message(self, content: str) -> None:
        """添加用户消息到对话历史。

        Args:
            content: 用户消息内容
        """
        self._messages.append(Message(role="user", content=content))
        self._truncate_history()
        self.updated_at = datetime.now(tz=UTC)

    def add_assistant_message(self, content: str) -> None:
        """添加 Assistant 消息到对话历史。

        Args:
            content: Assistant 响应内容
        """
        self._messages.append(Message(role="assistant", content=content))
        self._truncate_history()
        self.updated_at = datetime.now(tz=UTC)

    def get_messages_for_api(self) -> list[dict[str, Any]]:
        """获取适合传给 LLM API 的消息列表格式。

        Returns:
            符合 OpenAI API 格式的消息列表
        """
        return [msg.to_dict() for msg in self._messages]

    def clear_history(self) -> None:
        """清空对话历史（保留会话，只清消息）。"""
        self._messages.clear()
        self.updated_at = datetime.now(tz=UTC)

    @property
    def message_count(self) -> int:
        """当前对话历史中的消息数量。"""
        return len(self._messages)

    def _truncate_history(self) -> None:
        """当对话历史超过限制时，截断旧消息（保留最新的消息）。"""
        if len(self._messages) > self.MAX_HISTORY_LENGTH:
            # 保留最新的 MAX_HISTORY_LENGTH 条消息
            self._messages = self._messages[-self.MAX_HISTORY_LENGTH :]
