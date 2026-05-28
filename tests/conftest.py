"""测试共享配置和 fixtures。"""

from __future__ import annotations

import pytest

from src.agent.core import AgentCore
from src.memory.store import MemoryStore
from src.tools.registry import ToolRegistry


@pytest.fixture
def memory_store() -> MemoryStore:
    """创建独立的内存存储实例（测试隔离）。"""
    return MemoryStore()


@pytest.fixture
def tool_registry() -> ToolRegistry:
    """创建独立的工具注册中心实例（测试隔离）。"""
    return ToolRegistry()


@pytest.fixture
def agent_core(tool_registry: ToolRegistry, memory_store: MemoryStore) -> AgentCore:
    """创建独立的 AgentCore 实例（测试隔离）。"""
    return AgentCore(
        tool_registry=tool_registry,
        memory_store=memory_store,
        model="gpt-4o-mini",  # 测试时使用较小的模型
    )
