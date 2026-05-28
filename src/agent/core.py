"""Agent 核心模块。

提供 Agent 的主循环和消息处理逻辑。
"""

from __future__ import annotations

import logging
import os
from collections.abc import AsyncIterator

from src.agent.session import AgentSession, SessionStatus
from src.memory.store import MemoryStore
from src.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class AgentCore:
    """Agent 核心，负责协调 LLM 调用、工具执行和记忆管理。

    Example:
        agent = AgentCore()
        async for chunk in agent.chat(session_id="123", message="你好"):
            print(chunk, end="", flush=True)
    """

    def __init__(
        self,
        tool_registry: ToolRegistry | None = None,
        memory_store: MemoryStore | None = None,
        model: str | None = None,
    ) -> None:
        """初始化 AgentCore。

        Args:
            tool_registry: 工具注册中心，为 None 时使用全局注册中心
            memory_store: 记忆存储，为 None 时使用内存存储
            model: LLM 模型名称，为 None 时从环境变量读取
        """
        self._tool_registry = tool_registry or ToolRegistry.get_global()
        self._memory = memory_store or MemoryStore()
        self._model = model or os.getenv("OPENAI_MODEL", "gpt-4o")
        self._sessions: dict[str, AgentSession] = {}

        logger.info("AgentCore 初始化完成", extra={"model": self._model})

    def get_or_create_session(self, session_id: str) -> AgentSession:
        """获取或创建会话。

        Args:
            session_id: 会话唯一标识符

        Returns:
            会话对象
        """
        if session_id not in self._sessions:
            self._sessions[session_id] = AgentSession(session_id=session_id)
            logger.info("创建新会话", extra={"session_id": session_id})
        return self._sessions[session_id]

    async def chat(
        self,
        session_id: str,
        message: str,
    ) -> AsyncIterator[str]:
        """处理用户消息并流式返回 Agent 响应。

        Args:
            session_id: 会话 ID
            message: 用户输入的消息

        Yields:
            Agent 响应的文本片段（流式）

        Raises:
            RuntimeError: 如果会话处于非法状态
        """
        session = self.get_or_create_session(session_id)

        if session.status == SessionStatus.PROCESSING:
            raise RuntimeError(f"会话 {session_id} 正在处理中，请等待完成后再发送消息")

        session.add_user_message(message)
        session.status = SessionStatus.PROCESSING

        logger.info(
            "开始处理消息",
            extra={"session_id": session_id, "message_length": len(message)},
        )

        try:
            # TODO: 实现真正的 LLM 调用（以下为示例占位）
            # 生产环境中替换为实际的 OpenAI API 调用
            response_text = f"[占位响应] 收到消息：{message}"
            session.add_assistant_message(response_text)

            yield response_text

        except Exception as e:
            logger.error(
                "消息处理失败",
                extra={"session_id": session_id, "error": str(e)},
            )
            session.status = SessionStatus.ERROR
            raise
        else:
            session.status = SessionStatus.IDLE

    def terminate_session(self, session_id: str) -> bool:
        """终止并清理会话。

        Args:
            session_id: 要终止的会话 ID

        Returns:
            True 如果会话存在并被终止，False 如果会话不存在
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info("会话已终止", extra={"session_id": session_id})
            return True
        return False

    @property
    def active_session_count(self) -> int:
        """当前活跃会话数量。"""
        return len(self._sessions)
