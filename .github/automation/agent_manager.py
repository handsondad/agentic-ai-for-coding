"""多 Agent 管理器，支持 Agent 选择、切换和降级策略。"""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path
from typing import Any

try:
    from .agent_adapter import (
        AgentConfig,
        AgentExecutionContext,
        AgentExecutionResult,
        get_agent_registry,
        load_agent_config_from_env,
        load_agent_configs_from_file,
    )
except ImportError:
    from agent_adapter import (
        AgentConfig,
        AgentExecutionContext,
        AgentExecutionResult,
        get_agent_registry,
        load_agent_config_from_env,
        load_agent_configs_from_file,
    )

logger = logging.getLogger(__name__)


class AgentManager:
    """多 Agent 管理器，负责 Agent 选择、执行和降级。"""

    def __init__(self, config_file: Path | None = None) -> None:
        self.registry = get_agent_registry()
        self.config_file = config_file
        self._agent_configs: dict[str, AgentConfig] = {}
        self._load_configs()

    def _load_configs(self) -> None:
        """加载 Agent 配置。"""
        # 1. 从配置文件加载
        if self.config_file and self.config_file.exists():
            file_configs = load_agent_configs_from_file(self.config_file)
            self._agent_configs.update(file_configs)
            logger.info(f"从配置文件加载了 {len(file_configs)} 个 Agent 配置")

        # 2. 从环境变量加载（优先级更高）
        env_agent_names = self._discover_agent_names_from_env()
        for name in env_agent_names:
            config = load_agent_config_from_env(name)
            if config.command_template:
                self._agent_configs[name] = config
                logger.info(f"从环境变量加载 Agent 配置: {name}")

        # 3. 添加默认配置（如果没有任何配置）
        if not self._agent_configs:
            self._add_default_configs()

    def _discover_agent_names_from_env(self) -> list[str]:
        """从环境变量中发现 Agent 名称。"""
        agent_names = set()

        for key in os.environ:
            if key.startswith("AGENT_") and key.endswith("_COMMAND"):
                # 提取 Agent 名称：AGENT_COPILOT_COMMAND -> copilot
                name_part = key[6:-8]  # 去掉 "AGENT_" 和 "_COMMAND"
                agent_name = name_part.lower().replace("_", "-")
                agent_names.add(agent_name)

        return list(agent_names)

    def _add_default_configs(self) -> None:
        """添加默认 Agent 配置。"""
        # 如果设置了通用的 AUTOMATION_AGENT_COMMAND，创建一个默认配置
        default_command = os.getenv("AUTOMATION_AGENT_COMMAND", "")
        if default_command:
            self._agent_configs["default"] = AgentConfig(
                name="default",
                command_template=default_command,
            )
            logger.info("创建了默认 Agent 配置")

    def list_available_agents(self) -> list[str]:
        """列出所有可用的 Agent。"""
        return list(self._agent_configs.keys())

    def get_agent_config(self, agent_name: str) -> AgentConfig | None:
        """获取指定 Agent 的配置。"""
        return self._agent_configs.get(agent_name)

    def validate_agent(self, agent_name: str) -> list[str]:
        """验证指定 Agent 的配置。

        Returns:
            配置错误列表，空列表表示配置有效
        """
        config = self.get_agent_config(agent_name)
        if not config:
            return [f"未找到 Agent 配置: {agent_name}"]

        adapter = self.registry.create_adapter(config)
        return adapter.validate_config()

    async def execute_with_agent(
        self,
        agent_name: str,
        context: AgentExecutionContext,
    ) -> AgentExecutionResult:
        """使用指定 Agent 执行任务。"""
        config = self.get_agent_config(agent_name)
        if not config:
            return AgentExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"未找到 Agent 配置: {agent_name}",
                execution_time_seconds=0.0,
                agent_name=agent_name,
            )

        # 验证配置
        validation_errors = self.validate_agent(agent_name)
        if validation_errors:
            error_msg = f"Agent 配置验证失败: {'; '.join(validation_errors)}"
            return AgentExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=error_msg,
                execution_time_seconds=0.0,
                agent_name=agent_name,
            )

        # 创建适配器并执行
        adapter = self.registry.create_adapter(config)

        # 支持重试
        last_result = None
        for attempt in range(config.retry_count):
            if attempt > 0:
                logger.info(f"重试 {agent_name} Agent (第 {attempt + 1}/{config.retry_count} 次)")
                await asyncio.sleep(2**attempt)  # 指数退避

            result = await adapter.execute(context)
            last_result = result

            if result.success:
                return result

            logger.warning(
                f"{agent_name} Agent 执行失败 (尝试 {attempt + 1}/{config.retry_count}): {result.stderr}"
            )

        return last_result or AgentExecutionResult(
            success=False,
            exit_code=-1,
            stdout="",
            stderr="所有重试都失败了",
            execution_time_seconds=0.0,
            agent_name=agent_name,
        )

    async def execute_with_fallback(
        self,
        primary_agent: str,
        fallback_agents: list[str],
        context: AgentExecutionContext,
    ) -> AgentExecutionResult:
        """使用主 Agent 执行，失败时自动降级到备选 Agent。

        Args:
            primary_agent: 主要使用的 Agent
            fallback_agents: 备选 Agent 列表，按优先级排序
            context: 执行上下文

        Returns:
            执行结果
        """
        # 先尝试主 Agent
        logger.info(f"使用主 Agent: {primary_agent}")
        result = await self.execute_with_agent(primary_agent, context)

        if result.success:
            logger.info(f"主 Agent {primary_agent} 执行成功")
            return result

        logger.warning(f"主 Agent {primary_agent} 执行失败，开始尝试备选 Agent")

        # 依次尝试备选 Agent
        for fallback_agent in fallback_agents:
            logger.info(f"尝试备选 Agent: {fallback_agent}")
            result = await self.execute_with_agent(fallback_agent, context)

            if result.success:
                logger.info(f"备选 Agent {fallback_agent} 执行成功")
                return result

            logger.warning(f"备选 Agent {fallback_agent} 也执行失败")

        # 所有 Agent 都失败了
        logger.error("所有 Agent 都执行失败")
        return result  # 返回最后一个 Agent 的结果

    def get_recommended_fallback_chain(self) -> list[str]:
        """获取推荐的 Agent 降级链。

        根据成本、稳定性、可控性等因素排序。
        """
        available_agents = self.list_available_agents()

        # 定义推荐的优先级顺序
        priority_order = [
            "copilot",  # GitHub Copilot - 官方支持，稳定性好
            "claude-code",  # Claude Code - 功能强大，理解能力好
            "cline",  # Cline - VS Code 插件，集成度好
            "opencode",  # OpenCode - 开源方案
            "deepseek",  # DeepSeek - 国产方案，成本低
            "qoder",  # Qoder - 备选方案
            "trae",  # Trae - 备选方案
            "codebuddy",  # CodeBuddy - 备选方案
            "default",  # 默认配置
            "generic",  # 通用配置
        ]

        # 按优先级过滤可用的 Agent
        recommended = []
        for agent_name in priority_order:
            if agent_name in available_agents:
                recommended.append(agent_name)

        # 添加其他可用的 Agent
        for agent_name in available_agents:
            if agent_name not in recommended:
                recommended.append(agent_name)

        return recommended

    def create_agent_config_template(self) -> dict[str, Any]:
        """创建 Agent 配置模板，用于生成示例配置文件。"""
        return {
            "agents": {
                "copilot": {
                    "command_template": "gh copilot suggest --workspace {workspace} --prompt-file {prompt}",
                    "model": "gpt-4",
                    "timeout_seconds": 3600,
                    "retry_count": 2,
                },
                "claude-code": {
                    "command_template": "claude-code --workspace {workspace} --prompt-file {prompt}",
                    "model": "claude-3-5-sonnet-20241022",
                    "api_key": "${ANTHROPIC_API_KEY}",
                    "timeout_seconds": 3600,
                    "retry_count": 2,
                },
                "cline": {
                    "command_template": "cline --workspace {workspace} --prompt-file {prompt}",
                    "model": "gpt-4",
                    "api_key": "${OPENAI_API_KEY}",
                    "timeout_seconds": 3600,
                    "retry_count": 1,
                },
                "opencode": {
                    "command_template": "opencode --workspace {workspace} --prompt {prompt}",
                    "model": "gpt-4",
                    "base_url": "${OPENAI_BASE_URL}",
                    "api_key": "${OPENAI_API_KEY}",
                    "timeout_seconds": 3600,
                    "retry_count": 1,
                },
                "deepseek": {
                    "command_template": "deepseek-tui --workspace {workspace} --prompt {prompt}",
                    "model": "deepseek-coder",
                    "base_url": "https://api.deepseek.com/v1",
                    "api_key": "${DEEPSEEK_API_KEY}",
                    "timeout_seconds": 3600,
                    "retry_count": 1,
                },
                "qoder": {
                    "command_template": "qoder --workspace {workspace} --prompt {prompt}",
                    "model": "qwen-coder",
                    "base_url": "${QODER_BASE_URL}",
                    "api_key": "${QODER_API_KEY}",
                    "timeout_seconds": 3600,
                    "retry_count": 1,
                },
                "generic-openai": {
                    "command_template": "your-agent-cli --workspace {workspace} --prompt-file {prompt} --model {model}",
                    "model": "${AGENT_MODEL}",
                    "base_url": "${OPENAI_BASE_URL}",
                    "api_key": "${OPENAI_API_KEY}",
                    "timeout_seconds": 3600,
                    "retry_count": 1,
                    "extra_env": {
                        "OPENAI_MODEL": "${AGENT_MODEL}",
                        "OPENAI_BASE_URL": "${OPENAI_BASE_URL}",
                        "OPENAI_API_KEY": "${OPENAI_API_KEY}",
                    },
                },
            }
        }


def create_default_agent_manager(repo_root: Path) -> AgentManager:
    """创建默认的 Agent 管理器。"""
    config_file = repo_root / ".github" / "automation" / "agent-configs.json"
    return AgentManager(config_file)
