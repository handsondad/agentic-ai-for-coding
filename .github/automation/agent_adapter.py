"""多 Coding Agent 统一适配器接口和实现。

支持多种 coding agent CLI 工具的统一接入，包括：
- GitHub Copilot CLI
- Claude Code CLI
- Cline CLI
- OpenCode CLI
- DeepSeek TUI CLI
- Qoder CLI
- Trae CLI
- CodeBuddy CLI

每个 Agent 都可以配置不同的模型、认证方式和执行参数。
"""

from __future__ import annotations

import abc
import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AgentConfig:
    """Agent 配置信息。"""

    name: str  # Agent 名称，如 "copilot", "claude-code", "cline" 等
    command_template: str  # 命令模板，支持占位符替换
    model: str | None = None  # 使用的模型，如 "gpt-4", "claude-3-5-sonnet" 等
    base_url: str | None = None  # API 基础 URL（用于 OpenAI-compatible 服务）
    api_key: str | None = None  # API 密钥
    extra_env: dict[str, str] = field(default_factory=dict)  # 额外的环境变量
    timeout_seconds: int = 3600  # 超时时间（秒）
    retry_count: int = 1  # 重试次数

    def to_env_vars(self) -> dict[str, str]:
        """转换为环境变量字典。"""
        env = self.extra_env.copy()

        if self.model:
            env["AGENT_MODEL"] = self.model
        if self.base_url:
            env["AGENT_BASE_URL"] = self.base_url
        if self.api_key:
            env["AGENT_API_KEY"] = self.api_key

        return env


@dataclass(slots=True)
class AgentExecutionContext:
    """Agent 执行上下文。"""

    workspace: Path
    prompt_file: Path
    issue_number: str
    issue_title: str
    issue_url: str
    workflow_file: Path
    base_branch: str = "main"


@dataclass(slots=True)
class AgentExecutionResult:
    """Agent 执行结果。"""

    success: bool
    exit_code: int
    stdout: str
    stderr: str
    execution_time_seconds: float
    agent_name: str


class AgentAdapter(abc.ABC):
    """Agent 适配器抽象基类。"""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config

    @abc.abstractmethod
    async def execute(self, context: AgentExecutionContext) -> AgentExecutionResult:
        """执行 Agent 任务。

        Args:
            context: 执行上下文

        Returns:
            执行结果
        """

    @abc.abstractmethod
    def validate_config(self) -> list[str]:
        """验证配置是否有效。

        Returns:
            配置错误列表，空列表表示配置有效
        """

    def render_command(self, template: str, context: AgentExecutionContext) -> str:
        """渲染命令模板。"""
        placeholders = {
            "workspace": str(context.workspace),
            "prompt": str(context.prompt_file),
            "issue_number": context.issue_number,
            "issue_title": context.issue_title,
            "issue_url": context.issue_url,
            "workflow": str(context.workflow_file),
            "base_branch": context.base_branch,
            "model": self.config.model or "",
            "base_url": self.config.base_url or "",
            "api_key": self.config.api_key or "",
        }

        rendered = template
        for key, value in placeholders.items():
            rendered = rendered.replace(f"{{{key}}}", value)

        return rendered


class GenericAgentAdapter(AgentAdapter):
    """通用 Agent 适配器，支持任意 CLI 工具。"""

    async def execute(self, context: AgentExecutionContext) -> AgentExecutionResult:
        """执行通用 Agent 命令。"""
        import asyncio
        import time

        command = self.render_command(self.config.command_template, context)
        env = os.environ.copy()
        env.update(self.config.to_env_vars())

        logger.info(f"执行 {self.config.name} Agent: {command}")
        logger.info(f"工作目录: {context.workspace}")

        start_time = time.time()

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=context.workspace,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=self.config.timeout_seconds
            )

            execution_time = time.time() - start_time

            return AgentExecutionResult(
                success=process.returncode == 0,
                exit_code=process.returncode or 0,
                stdout=stdout.decode("utf-8", errors="replace"),
                stderr=stderr.decode("utf-8", errors="replace"),
                execution_time_seconds=execution_time,
                agent_name=self.config.name,
            )

        except TimeoutError:
            execution_time = time.time() - start_time
            logger.error(f"{self.config.name} Agent 执行超时 ({self.config.timeout_seconds}s)")

            return AgentExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"执行超时 ({self.config.timeout_seconds}s)",
                execution_time_seconds=execution_time,
                agent_name=self.config.name,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{self.config.name} Agent 执行失败: {e}")

            return AgentExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                execution_time_seconds=execution_time,
                agent_name=self.config.name,
            )

    def validate_config(self) -> list[str]:
        """验证通用配置。"""
        errors = []

        if not self.config.command_template.strip():
            errors.append("command_template 不能为空")

        # 检查必需的占位符
        required_placeholders = ["{workspace}", "{prompt}"]
        for placeholder in required_placeholders:
            if placeholder not in self.config.command_template:
                errors.append(f"command_template 必须包含 {placeholder} 占位符")

        return errors


class CopilotAdapter(AgentAdapter):
    """GitHub Copilot CLI 适配器。"""

    async def execute(self, context: AgentExecutionContext) -> AgentExecutionResult:
        """执行 Copilot CLI 命令。"""
        # 使用通用适配器执行，但添加 Copilot 特定的逻辑
        generic = GenericAgentAdapter(self.config)
        result = await generic.execute(context)

        # 可以在这里添加 Copilot 特定的后处理逻辑
        return result

    def validate_config(self) -> list[str]:
        """验证 Copilot 配置。"""
        errors = []

        # Copilot 通常需要 GitHub 认证
        if not os.getenv("GITHUB_TOKEN") and not self.config.api_key:
            errors.append("Copilot 需要 GITHUB_TOKEN 或在配置中设置 api_key")

        return errors


class ClaudeCodeAdapter(AgentAdapter):
    """Claude Code CLI 适配器。"""

    async def execute(self, context: AgentExecutionContext) -> AgentExecutionResult:
        """执行 Claude Code CLI 命令。"""
        # 设置 Claude Code 特定的环境变量
        if self.config.api_key:
            self.config.extra_env["ANTHROPIC_API_KEY"] = self.config.api_key

        generic = GenericAgentAdapter(self.config)
        return await generic.execute(context)

    def validate_config(self) -> list[str]:
        """验证 Claude Code 配置。"""
        errors = []

        # Claude Code 需要 Anthropic API Key
        if not os.getenv("ANTHROPIC_API_KEY") and not self.config.api_key:
            errors.append("Claude Code 需要 ANTHROPIC_API_KEY 或在配置中设置 api_key")

        return errors


class OpenAICompatibleAdapter(AgentAdapter):
    """OpenAI-compatible API 适配器（用于 OpenCode、DeepSeek 等）。"""

    async def execute(self, context: AgentExecutionContext) -> AgentExecutionResult:
        """执行 OpenAI-compatible CLI 命令。"""
        # 设置 OpenAI-compatible 环境变量
        env_updates = {}

        if self.config.api_key:
            env_updates["OPENAI_API_KEY"] = self.config.api_key
        if self.config.base_url:
            env_updates["OPENAI_BASE_URL"] = self.config.base_url
        if self.config.model:
            env_updates["OPENAI_MODEL"] = self.config.model

        self.config.extra_env.update(env_updates)

        generic = GenericAgentAdapter(self.config)
        return await generic.execute(context)

    def validate_config(self) -> list[str]:
        """验证 OpenAI-compatible 配置。"""
        errors = []

        if not self.config.api_key and not os.getenv("OPENAI_API_KEY"):
            errors.append("OpenAI-compatible Agent 需要 api_key 或 OPENAI_API_KEY 环境变量")

        if not self.config.base_url and not os.getenv("OPENAI_BASE_URL"):
            errors.append("OpenAI-compatible Agent 需要 base_url 或 OPENAI_BASE_URL 环境变量")

        return errors


class AgentRegistry:
    """Agent 注册中心，管理多种 Agent 适配器。"""

    def __init__(self) -> None:
        self._adapters: dict[str, type[AgentAdapter]] = {}
        self._register_builtin_adapters()

    def _register_builtin_adapters(self) -> None:
        """注册内置适配器。"""
        self.register("copilot", CopilotAdapter)
        self.register("claude-code", ClaudeCodeAdapter)
        self.register("openai-compatible", OpenAICompatibleAdapter)
        self.register("generic", GenericAgentAdapter)

    def register(self, name: str, adapter_class: type[AgentAdapter]) -> None:
        """注册 Agent 适配器。"""
        self._adapters[name] = adapter_class
        logger.info(f"注册 Agent 适配器: {name}")

    def create_adapter(self, config: AgentConfig) -> AgentAdapter:
        """根据配置创建 Agent 适配器。"""
        # 根据 Agent 名称选择适配器类型
        adapter_type = self._infer_adapter_type(config.name)
        adapter_class = self._adapters.get(adapter_type, GenericAgentAdapter)

        return adapter_class(config)

    def _infer_adapter_type(self, agent_name: str) -> str:
        """根据 Agent 名称推断适配器类型。"""
        name_lower = agent_name.lower()

        if "copilot" in name_lower:
            return "copilot"
        elif "claude" in name_lower:
            return "claude-code"
        elif any(
            keyword in name_lower
            for keyword in ["opencode", "deepseek", "qoder", "trae", "codebuddy"]
        ):
            return "openai-compatible"
        else:
            return "generic"

    def list_adapters(self) -> list[str]:
        """列出所有注册的适配器。"""
        return list(self._adapters.keys())


# 全局注册中心实例
_global_registry = AgentRegistry()


def get_agent_registry() -> AgentRegistry:
    """获取全局 Agent 注册中心。"""
    return _global_registry


def load_agent_config_from_env(agent_name: str) -> AgentConfig:
    """从环境变量加载 Agent 配置。

    环境变量格式：
    - AGENT_<NAME>_COMMAND: 命令模板
    - AGENT_<NAME>_MODEL: 模型名称
    - AGENT_<NAME>_BASE_URL: API 基础 URL
    - AGENT_<NAME>_API_KEY: API 密钥
    - AGENT_<NAME>_TIMEOUT: 超时时间
    - AGENT_<NAME>_RETRY: 重试次数
    """
    name_upper = agent_name.upper().replace("-", "_")

    command_template = os.getenv(f"AGENT_{name_upper}_COMMAND", "")
    if not command_template:
        # 回退到通用配置
        command_template = os.getenv("AUTOMATION_AGENT_COMMAND", "")

    return AgentConfig(
        name=agent_name,
        command_template=command_template,
        model=os.getenv(f"AGENT_{name_upper}_MODEL"),
        base_url=os.getenv(f"AGENT_{name_upper}_BASE_URL"),
        api_key=os.getenv(f"AGENT_{name_upper}_API_KEY"),
        timeout_seconds=int(os.getenv(f"AGENT_{name_upper}_TIMEOUT", "3600")),
        retry_count=int(os.getenv(f"AGENT_{name_upper}_RETRY", "1")),
    )


def load_agent_configs_from_file(config_file: Path) -> dict[str, AgentConfig]:
    """从配置文件加载多个 Agent 配置。

    配置文件格式（JSON）：
    {
        "agents": {
            "copilot": {
                "command_template": "gh copilot suggest --workspace {workspace} --prompt-file {prompt}",
                "model": "gpt-4",
                "timeout_seconds": 3600
            },
            "claude-code": {
                "command_template": "claude-code --workspace {workspace} --prompt-file {prompt}",
                "model": "claude-3-5-sonnet-20241022",
                "api_key": "${ANTHROPIC_API_KEY}",
                "timeout_seconds": 3600
            }
        }
    }
    """
    if not config_file.exists():
        return {}

    try:
        with open(config_file, encoding="utf-8") as f:
            data = json.load(f)

        configs = {}
        for name, config_data in data.get("agents", {}).items():
            # 处理环境变量替换
            for key, value in config_data.items():
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    env_var = value[2:-1]
                    config_data[key] = os.getenv(env_var, "")

            configs[name] = AgentConfig(
                name=name,
                command_template=config_data.get("command_template", ""),
                model=config_data.get("model"),
                base_url=config_data.get("base_url"),
                api_key=config_data.get("api_key"),
                timeout_seconds=config_data.get("timeout_seconds", 3600),
                retry_count=config_data.get("retry_count", 1),
                extra_env=config_data.get("extra_env", {}),
            )

        return configs

    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"解析 Agent 配置文件失败: {e}")
        return {}
