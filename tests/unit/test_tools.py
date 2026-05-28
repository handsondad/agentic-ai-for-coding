"""工具注册中心单元测试。"""

from __future__ import annotations

import pytest
from pydantic import BaseModel

from src.tools.registry import ToolRegistry


class EchoParams(BaseModel):
    message: str


class AddParams(BaseModel):
    a: int
    b: int


@pytest.fixture
def registry_with_tools(tool_registry: ToolRegistry) -> ToolRegistry:
    """创建带有示例工具的注册中心。"""

    @tool_registry.register(
        name="echo",
        description="返回输入的消息",
        parameters=EchoParams,
    )
    async def echo(params: EchoParams) -> dict[str, str]:
        return {"message": params.message}

    @tool_registry.register(
        name="add",
        description="计算两数之和",
        parameters=AddParams,
    )
    async def add(params: AddParams) -> dict[str, int]:
        return {"result": params.a + params.b}

    return tool_registry


class TestToolRegistry:
    """ToolRegistry 单元测试。"""

    def test_register_tool_adds_to_registry(self, registry_with_tools: ToolRegistry) -> None:
        """注册工具后应该可以在列表中找到它。"""
        assert "echo" in registry_with_tools.tool_names
        assert "add" in registry_with_tools.tool_names

    def test_register_duplicate_name_raises(self, tool_registry: ToolRegistry) -> None:
        """重复注册相同名称的工具应该抛出 ValueError。"""

        @tool_registry.register(name="dup", description="first", parameters=EchoParams)
        async def first(params: EchoParams) -> dict:
            return {}

        with pytest.raises(ValueError, match="已注册"):

            @tool_registry.register(name="dup", description="second", parameters=EchoParams)
            async def second(params: EchoParams) -> dict:
                return {}

    @pytest.mark.asyncio
    async def test_call_existing_tool(self, registry_with_tools: ToolRegistry) -> None:
        """调用已注册的工具应该返回正确结果。"""
        result = await registry_with_tools.call("echo", {"message": "hello"})
        assert result == {"message": "hello"}

    @pytest.mark.asyncio
    async def test_call_add_tool(self, registry_with_tools: ToolRegistry) -> None:
        """add 工具应该返回正确的求和结果。"""
        result = await registry_with_tools.call("add", {"a": 3, "b": 5})
        assert result == {"result": 8}

    @pytest.mark.asyncio
    async def test_call_nonexistent_tool_raises(self, tool_registry: ToolRegistry) -> None:
        """调用不存在的工具应该抛出 KeyError。"""
        with pytest.raises(KeyError, match="不存在"):
            await tool_registry.call("nonexistent", {})

    def test_get_all_specs_returns_openai_format(self, registry_with_tools: ToolRegistry) -> None:
        """get_all_specs 应该返回 OpenAI Function Calling 格式的规格。"""
        specs = registry_with_tools.get_all_specs()

        assert len(specs) == 2
        for spec in specs:
            assert spec["type"] == "function"
            assert "function" in spec
            assert "name" in spec["function"]
            assert "description" in spec["function"]
            assert "parameters" in spec["function"]

    def test_empty_registry_has_no_tools(self, tool_registry: ToolRegistry) -> None:
        """新建的注册中心不应该有任何工具。"""
        assert len(tool_registry.tool_names) == 0
        assert len(tool_registry.get_all_specs()) == 0
