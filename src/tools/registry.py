"""工具注册中心模块。

提供工具注册、发现和调用的统一接口。
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Coroutine
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)

ToolHandler = Callable[..., Coroutine[Any, Any, Any]]


class ToolDefinition:
    """工具定义，包含元数据和处理函数。"""

    def __init__(
        self,
        name: str,
        description: str,
        parameters_schema: type[BaseModel],
        handler: ToolHandler,
    ) -> None:
        self.name = name
        self.description = description
        self.parameters_schema = parameters_schema
        self.handler = handler

    def to_openai_spec(self) -> dict[str, Any]:
        """转换为 OpenAI Function Calling 格式的工具规格。"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema.model_json_schema(),
            },
        }


class ToolRegistry:
    """工具注册中心，管理所有可用工具的注册和调用。

    支持作为全局单例使用，也支持创建独立实例（用于测试隔离）。

    Example:
        registry = ToolRegistry()

        @registry.register(
            name="search",
            description="搜索网络",
            parameters=SearchParams
        )
        async def search(params: SearchParams) -> dict:
            ...
    """

    _global_instance: ToolRegistry | None = None

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    @classmethod
    def get_global(cls) -> ToolRegistry:
        """获取全局单例注册中心。"""
        if cls._global_instance is None:
            cls._global_instance = cls()
        return cls._global_instance

    def register(
        self,
        name: str,
        description: str,
        parameters: type[BaseModel],
    ) -> Callable[[ToolHandler], ToolHandler]:
        """注册工具的装饰器。

        Args:
            name: 工具唯一名称（供 LLM 调用时使用）
            description: 工具功能描述（供 LLM 理解用途）
            parameters: 参数的 Pydantic 模型类

        Returns:
            装饰器函数

        Raises:
            ValueError: 如果工具名称已存在

        Example:
            @registry.register(name="my_tool", description="...", parameters=MyParams)
            async def my_tool(params: MyParams) -> dict:
                ...
        """

        def decorator(handler: ToolHandler) -> ToolHandler:
            if name in self._tools:
                raise ValueError(f"工具 '{name}' 已注册，请使用不同的名称")

            self._tools[name] = ToolDefinition(
                name=name,
                description=description,
                parameters_schema=parameters,
                handler=handler,
            )
            logger.debug("工具已注册", extra={"tool_name": name})
            return handler

        return decorator

    async def call(self, name: str, arguments: dict[str, Any]) -> Any:
        """调用指定工具。

        Args:
            name: 工具名称
            arguments: 工具参数字典

        Returns:
            工具执行结果

        Raises:
            KeyError: 如果工具不存在
            ValidationError: 如果参数不符合工具的参数模型
        """
        if name not in self._tools:
            raise KeyError(f"工具 '{name}' 不存在")

        tool = self._tools[name]
        params = tool.parameters_schema.model_validate(arguments)

        logger.info("执行工具", extra={"tool_name": name})
        return await tool.handler(params)

    def get_all_specs(self) -> list[dict[str, Any]]:
        """获取所有工具的 OpenAI Function Calling 格式规格。

        Returns:
            工具规格列表，用于传递给 LLM API
        """
        return [tool.to_openai_spec() for tool in self._tools.values()]

    @property
    def tool_names(self) -> list[str]:
        """已注册的工具名称列表。"""
        return list(self._tools.keys())
