"""Agent 核心模块单元测试。"""

from __future__ import annotations

import pytest

from src.agent.core import AgentCore
from src.agent.session import SessionStatus


class TestAgentCore:
    """AgentCore 单元测试。"""

    def test_init_creates_empty_sessions(self, agent_core: AgentCore) -> None:
        """初始化后应该没有活跃会话。"""
        assert agent_core.active_session_count == 0

    def test_get_or_create_session_creates_new_session(self, agent_core: AgentCore) -> None:
        """get_or_create_session 应该创建新会话。"""
        session = agent_core.get_or_create_session("test-session-1")

        assert session is not None
        assert session.session_id == "test-session-1"
        assert session.status == SessionStatus.IDLE

    def test_get_or_create_session_returns_existing_session(self, agent_core: AgentCore) -> None:
        """相同 session_id 应该返回同一会话对象。"""
        session1 = agent_core.get_or_create_session("test-session-2")
        session2 = agent_core.get_or_create_session("test-session-2")

        assert session1 is session2

    def test_active_session_count_increments_on_create(self, agent_core: AgentCore) -> None:
        """创建会话时，活跃会话数应该增加。"""
        assert agent_core.active_session_count == 0

        agent_core.get_or_create_session("s1")
        assert agent_core.active_session_count == 1

        agent_core.get_or_create_session("s2")
        assert agent_core.active_session_count == 2

    def test_terminate_session_returns_true_for_existing(self, agent_core: AgentCore) -> None:
        """终止存在的会话应该返回 True。"""
        agent_core.get_or_create_session("to-terminate")
        result = agent_core.terminate_session("to-terminate")

        assert result is True
        assert agent_core.active_session_count == 0

    def test_terminate_session_returns_false_for_nonexistent(self, agent_core: AgentCore) -> None:
        """终止不存在的会话应该返回 False。"""
        result = agent_core.terminate_session("nonexistent-session")

        assert result is False

    @pytest.mark.asyncio
    async def test_chat_returns_response(self, agent_core: AgentCore) -> None:
        """chat 应该返回响应文本。"""
        responses = []
        async for chunk in agent_core.chat("chat-session", "你好"):
            responses.append(chunk)

        assert len(responses) > 0
        full_response = "".join(responses)
        assert len(full_response) > 0

    @pytest.mark.asyncio
    async def test_chat_adds_messages_to_session(self, agent_core: AgentCore) -> None:
        """chat 后会话应该有用户消息和助手消息。"""
        async for _ in agent_core.chat("msg-session", "测试消息"):
            pass

        session = agent_core.get_or_create_session("msg-session")
        assert session.message_count >= 2  # 至少有用户消息和助手消息

    @pytest.mark.asyncio
    async def test_chat_raises_when_session_processing(self, agent_core: AgentCore) -> None:
        """当会话正在处理时发送消息应该抛出异常。"""
        session = agent_core.get_or_create_session("busy-session")
        session.status = SessionStatus.PROCESSING

        with pytest.raises(RuntimeError, match="正在处理中"):
            async for _ in agent_core.chat("busy-session", "另一条消息"):
                pass
