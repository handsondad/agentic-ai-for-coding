"""多 Agent 适配器和管理器的测试用例。"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / ".github" / "automation"))

# 导入被测试的模块
from agent_adapter import (
    AgentConfig,
    AgentExecutionContext,
    AgentExecutionResult,
    ClaudeCodeAdapter,
    CopilotAdapter,
    GenericAgentAdapter,
    OpenAICompatibleAdapter,
    get_agent_registry,
    load_agent_config_from_env,
)
from agent_manager import AgentManager


class TestAgentConfig:
    """测试 AgentConfig 类。"""

    def test_to_env_vars(self):
        """测试环境变量转换。"""
        config = AgentConfig(
            name="test-agent",
            command_template="test {workspace}",
            model="gpt-4",
            base_url="https://api.example.com",
            api_key="test-key",
            extra_env={"CUSTOM_VAR": "custom_value"},
        )

        env_vars = config.to_env_vars()

        assert env_vars["AGENT_MODEL"] == "gpt-4"
        assert env_vars["AGENT_BASE_URL"] == "https://api.example.com"
        assert env_vars["AGENT_API_KEY"] == "test-key"
        assert env_vars["CUSTOM_VAR"] == "custom_value"

    def test_to_env_vars_with_none_values(self):
        """测试包含 None 值的环境变量转换。"""
        config = AgentConfig(
            name="test-agent",
            command_template="test {workspace}",
            model=None,
            base_url=None,
            api_key=None,
        )

        env_vars = config.to_env_vars()

        assert "AGENT_MODEL" not in env_vars
        assert "AGENT_BASE_URL" not in env_vars
        assert "AGENT_API_KEY" not in env_vars


class TestGenericAgentAdapter:
    """测试通用 Agent 适配器。"""

    def test_validate_config_success(self):
        """测试有效配置的验证。"""
        config = AgentConfig(
            name="test-agent",
            command_template="echo 'Processing {workspace} with {prompt}'",
        )
        adapter = GenericAgentAdapter(config)

        errors = adapter.validate_config()
        assert errors == []

    def test_validate_config_missing_template(self):
        """测试缺少命令模板的验证。"""
        config = AgentConfig(name="test-agent", command_template="")
        adapter = GenericAgentAdapter(config)

        errors = adapter.validate_config()
        assert "command_template 不能为空" in errors

    def test_validate_config_missing_placeholders(self):
        """测试缺少必需占位符的验证。"""
        config = AgentConfig(
            name="test-agent",
            command_template="echo 'test'",  # 缺少 {workspace} 和 {prompt}
        )
        adapter = GenericAgentAdapter(config)

        errors = adapter.validate_config()
        assert any("{workspace}" in error for error in errors)
        assert any("{prompt}" in error for error in errors)

    def test_render_command(self):
        """测试命令模板渲染。"""
        config = AgentConfig(
            name="test-agent",
            command_template="process --workspace {workspace} --prompt {prompt} --model {model}",
            model="gpt-4",
        )
        adapter = GenericAgentAdapter(config)

        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            prompt_file = workspace / "prompt.md"
            prompt_file.write_text("test prompt")

            context = AgentExecutionContext(
                workspace=workspace,
                prompt_file=prompt_file,
                issue_number="123",
                issue_title="Test Issue",
                issue_url="https://example.com/issue/123",
                workflow_file=workspace / "workflow.md",
            )

            rendered = adapter.render_command(config.command_template, context)
            expected = f"process --workspace {workspace} --prompt {prompt_file} --model gpt-4"
            assert rendered == expected

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """测试成功执行。"""
        config = AgentConfig(
            name="test-agent",
            command_template="echo 'Success from {workspace}'",
            timeout_seconds=10,
        )
        adapter = GenericAgentAdapter(config)

        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            prompt_file = workspace / "prompt.md"
            prompt_file.write_text("test prompt")

            context = AgentExecutionContext(
                workspace=workspace,
                prompt_file=prompt_file,
                issue_number="123",
                issue_title="Test Issue",
                issue_url="https://example.com/issue/123",
                workflow_file=workspace / "workflow.md",
            )

            result = await adapter.execute(context)

            assert result.success is True
            assert result.exit_code == 0
            assert "Success from" in result.stdout
            assert result.agent_name == "test-agent"
            assert result.execution_time_seconds > 0

    @pytest.mark.asyncio
    async def test_execute_failure(self):
        """测试执行失败。"""
        config = AgentConfig(
            name="test-agent",
            command_template="exit 1",  # 会导致失败
            timeout_seconds=10,
        )
        adapter = GenericAgentAdapter(config)

        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            prompt_file = workspace / "prompt.md"
            prompt_file.write_text("test prompt")

            context = AgentExecutionContext(
                workspace=workspace,
                prompt_file=prompt_file,
                issue_number="123",
                issue_title="Test Issue",
                issue_url="https://example.com/issue/123",
                workflow_file=workspace / "workflow.md",
            )

            result = await adapter.execute(context)

            assert result.success is False
            assert result.exit_code == 1
            assert result.agent_name == "test-agent"


class TestSpecializedAdapters:
    """测试专门的适配器。"""

    def test_copilot_adapter_validation(self):
        """测试 Copilot 适配器验证。"""
        config = AgentConfig(
            name="copilot",
            command_template="gh copilot suggest --workspace {workspace} --prompt {prompt}",
        )
        adapter = CopilotAdapter(config)

        # 没有 GitHub token 时应该有错误
        with patch.dict(os.environ, {}, clear=True):
            errors = adapter.validate_config()
            assert any("GITHUB_TOKEN" in error for error in errors)

        # 有 API key 时应该通过
        config.api_key = "test-token"
        errors = adapter.validate_config()
        assert not any("GITHUB_TOKEN" in error for error in errors)

    def test_claude_code_adapter_validation(self):
        """测试 Claude Code 适配器验证。"""
        config = AgentConfig(
            name="claude-code",
            command_template="claude-code --workspace {workspace} --prompt {prompt}",
        )
        adapter = ClaudeCodeAdapter(config)

        # 没有 Anthropic API key 时应该有错误
        with patch.dict(os.environ, {}, clear=True):
            errors = adapter.validate_config()
            assert any("ANTHROPIC_API_KEY" in error for error in errors)

        # 有 API key 时应该通过
        config.api_key = "test-key"
        errors = adapter.validate_config()
        assert not any("ANTHROPIC_API_KEY" in error for error in errors)

    def test_openai_compatible_adapter_validation(self):
        """测试 OpenAI-compatible 适配器验证。"""
        config = AgentConfig(
            name="openai-compatible",
            command_template="openai-cli --workspace {workspace} --prompt {prompt}",
        )
        adapter = OpenAICompatibleAdapter(config)

        # 没有 API key 和 base URL 时应该有错误
        with patch.dict(os.environ, {}, clear=True):
            errors = adapter.validate_config()
            assert any("api_key" in error for error in errors)
            assert any("base_url" in error for error in errors)

        # 有配置时应该通过
        config.api_key = "test-key"
        config.base_url = "https://api.example.com"
        errors = adapter.validate_config()
        assert not any("api_key" in error for error in errors)
        assert not any("base_url" in error for error in errors)


class TestAgentRegistry:
    """测试 Agent 注册中心。"""

    def test_register_and_create_adapter(self):
        """测试注册和创建适配器。"""
        registry = get_agent_registry()

        # 测试内置适配器
        config = AgentConfig(name="copilot", command_template="test {workspace} {prompt}")
        adapter = registry.create_adapter(config)
        assert isinstance(adapter, CopilotAdapter)

        config = AgentConfig(name="claude-code", command_template="test {workspace} {prompt}")
        adapter = registry.create_adapter(config)
        assert isinstance(adapter, ClaudeCodeAdapter)

        config = AgentConfig(name="opencode", command_template="test {workspace} {prompt}")
        adapter = registry.create_adapter(config)
        assert isinstance(adapter, OpenAICompatibleAdapter)

        config = AgentConfig(name="unknown", command_template="test {workspace} {prompt}")
        adapter = registry.create_adapter(config)
        assert isinstance(adapter, GenericAgentAdapter)

    def test_list_adapters(self):
        """测试列出适配器。"""
        registry = get_agent_registry()
        adapters = registry.list_adapters()

        assert "copilot" in adapters
        assert "claude-code" in adapters
        assert "openai-compatible" in adapters
        assert "generic" in adapters


class TestAgentManager:
    """测试 Agent 管理器。"""

    def test_load_configs_from_env(self):
        """测试从环境变量加载配置。"""
        with patch.dict(
            os.environ,
            {
                "AGENT_TEST_COMMAND": "test --workspace {workspace} --prompt {prompt}",
                "AGENT_TEST_MODEL": "gpt-4",
                "AGENT_TEST_TIMEOUT": "1800",
            },
        ):
            manager = AgentManager()
            config = manager.get_agent_config("test")

            assert config is not None
            assert config.name == "test"
            assert config.command_template == "test --workspace {workspace} --prompt {prompt}"
            assert config.model == "gpt-4"
            assert config.timeout_seconds == 1800

    def test_validate_agent(self):
        """测试验证 Agent 配置。"""
        manager = AgentManager()

        # 添加测试配置
        manager._agent_configs["test-valid"] = AgentConfig(
            name="test-valid",
            command_template="test --workspace {workspace} --prompt {prompt}",
        )
        manager._agent_configs["test-invalid"] = AgentConfig(
            name="test-invalid",
            command_template="",  # 无效的命令模板
        )

        # 验证有效配置
        errors = manager.validate_agent("test-valid")
        assert errors == []

        # 验证无效配置
        errors = manager.validate_agent("test-invalid")
        assert len(errors) > 0

        # 验证不存在的 Agent
        errors = manager.validate_agent("non-existent")
        assert "未找到 Agent 配置" in errors[0]

    @pytest.mark.asyncio
    async def test_execute_with_agent_success(self):
        """测试成功执行 Agent。"""
        manager = AgentManager()

        # 添加测试配置（包含必需的占位符）
        manager._agent_configs["test-agent"] = AgentConfig(
            name="test-agent",
            command_template="echo 'Success from {workspace}' && echo 'Prompt: {prompt}'",
            timeout_seconds=10,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            prompt_file = workspace / "prompt.md"
            prompt_file.write_text("test prompt")

            context = AgentExecutionContext(
                workspace=workspace,
                prompt_file=prompt_file,
                issue_number="123",
                issue_title="Test Issue",
                issue_url="https://example.com/issue/123",
                workflow_file=workspace / "workflow.md",
            )

            result = await manager.execute_with_agent("test-agent", context)

            assert result.success is True
            assert "Success" in result.stdout

    @pytest.mark.asyncio
    async def test_execute_with_fallback(self):
        """测试降级执行。"""
        manager = AgentManager()

        # 添加测试配置（包含必需的占位符）
        manager._agent_configs["failing-agent"] = AgentConfig(
            name="failing-agent",
            command_template="echo 'Failing from {workspace}' && echo 'Prompt: {prompt}' && exit 1",  # 会失败
            timeout_seconds=10,
            retry_count=1,
        )
        manager._agent_configs["backup-agent"] = AgentConfig(
            name="backup-agent",
            command_template="echo 'Backup Success from {workspace}' && echo 'Prompt: {prompt}'",
            timeout_seconds=10,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            prompt_file = workspace / "prompt.md"
            prompt_file.write_text("test prompt")

            context = AgentExecutionContext(
                workspace=workspace,
                prompt_file=prompt_file,
                issue_number="123",
                issue_title="Test Issue",
                issue_url="https://example.com/issue/123",
                workflow_file=workspace / "workflow.md",
            )

            result = await manager.execute_with_fallback(
                "failing-agent", ["backup-agent"], context
            )

            assert result.success is True
            assert result.agent_name == "backup-agent"
            assert "Backup Success" in result.stdout

    def test_get_recommended_fallback_chain(self):
        """测试推荐的降级链。"""
        manager = AgentManager()

        # 添加一些测试配置
        manager._agent_configs["copilot"] = AgentConfig(
            name="copilot", command_template="test {workspace} {prompt}"
        )
        manager._agent_configs["claude-code"] = AgentConfig(
            name="claude-code", command_template="test {workspace} {prompt}"
        )
        manager._agent_configs["custom"] = AgentConfig(
            name="custom", command_template="test {workspace} {prompt}"
        )

        chain = manager.get_recommended_fallback_chain()

        # copilot 应该在前面（如果存在）
        assert "copilot" in chain
        assert "claude-code" in chain
        assert "custom" in chain

        # copilot 应该在 claude-code 前面
        copilot_index = chain.index("copilot")
        claude_index = chain.index("claude-code")
        assert copilot_index < claude_index

    def test_create_agent_config_template(self):
        """测试创建配置模板。"""
        manager = AgentManager()
        template = manager.create_agent_config_template()

        assert "agents" in template
        assert "copilot" in template["agents"]
        assert "claude-code" in template["agents"]
        assert "command_template" in template["agents"]["copilot"]


class TestLoadAgentConfigFromEnv:
    """测试从环境变量加载 Agent 配置。"""

    def test_load_basic_config(self):
        """测试加载基本配置。"""
        with patch.dict(
            os.environ,
            {
                "AGENT_TEST_COMMAND": "test-cli --workspace {workspace}",
                "AGENT_TEST_MODEL": "test-model",
                "AGENT_TEST_BASE_URL": "https://test.api.com",
                "AGENT_TEST_API_KEY": "test-key",
                "AGENT_TEST_TIMEOUT": "1800",
                "AGENT_TEST_RETRY": "3",
            },
        ):
            config = load_agent_config_from_env("test")

            assert config.name == "test"
            assert config.command_template == "test-cli --workspace {workspace}"
            assert config.model == "test-model"
            assert config.base_url == "https://test.api.com"
            assert config.api_key == "test-key"
            assert config.timeout_seconds == 1800
            assert config.retry_count == 3

    def test_load_with_fallback(self):
        """测试使用回退配置。"""
        with patch.dict(
            os.environ,
            {
                "AUTOMATION_AGENT_COMMAND": "fallback-command {workspace} {prompt}",
            },
            clear=True,
        ):
            config = load_agent_config_from_env("test")

            assert config.name == "test"
            assert config.command_template == "fallback-command {workspace} {prompt}"
            assert config.model is None
            assert config.timeout_seconds == 3600  # 默认值