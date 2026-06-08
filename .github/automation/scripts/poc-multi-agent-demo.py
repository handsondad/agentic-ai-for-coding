#!/usr/bin/env python3
"""多 Agent 切换 PoC 演示脚本。

演示如何在同一任务上切换不同的 coding agent 或模型端点。
"""

import asyncio
import json
import sys
import tempfile
import time
from pathlib import Path

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from agent_adapter import AgentConfig, AgentExecutionContext
from agent_manager import AgentManager


class MockAgentConfig:
    """模拟的 Agent 配置，用于演示。"""

    @staticmethod
    def create_mock_configs() -> dict[str, AgentConfig]:
        """创建模拟的 Agent 配置。"""
        return {
            "mock-copilot": AgentConfig(
                name="mock-copilot",
                command_template="echo '[MOCK COPILOT] Processing {prompt} in {workspace}' && sleep 2 && echo 'Copilot completed successfully'",
                model="gpt-4",
                timeout_seconds=10,
            ),
            "mock-claude": AgentConfig(
                name="mock-claude",
                command_template="echo '[MOCK CLAUDE] Processing {prompt} in {workspace}' && sleep 3 && echo 'Claude completed successfully'",
                model="claude-3-5-sonnet",
                timeout_seconds=10,
            ),
            "mock-opencode": AgentConfig(
                name="mock-opencode",
                command_template="echo '[MOCK OPENCODE] Processing {prompt} in {workspace}' && sleep 1 && echo 'OpenCode completed successfully'",
                model="gpt-4",
                base_url="https://api.example.com/v1",
                timeout_seconds=10,
            ),
            "mock-deepseek": AgentConfig(
                name="mock-deepseek",
                command_template="echo '[MOCK DEEPSEEK] Processing {prompt} in {workspace}' && sleep 2 && echo 'DeepSeek completed successfully'",
                model="deepseek-coder",
                base_url="https://api.deepseek.com/v1",
                timeout_seconds=10,
            ),
            "mock-failing": AgentConfig(
                name="mock-failing",
                command_template="echo '[MOCK FAILING] This agent will fail' && exit 1",
                model="failing-model",
                timeout_seconds=10,
            ),
        }


def create_test_prompt(workspace: Path) -> Path:
    """创建测试用的 prompt 文件。"""
    prompt_content = """# 测试任务

你是一个专业的 AI 软件工程师，正在处理以下任务：

**任务**: 创建一个简单的 Hello World 程序

## 要求
- 使用 Python 语言
- 输出 "Hello, World from {agent_name}!"
- 确保代码格式正确

## 文件位置
请在当前工作目录创建 `hello.py` 文件。
"""

    prompt_file = workspace / "test-prompt.md"
    prompt_file.write_text(prompt_content, encoding="utf-8")
    return prompt_file


async def demonstrate_agent_switching() -> None:
    """演示 Agent 切换功能。"""
    print("🚀 多 Agent 切换 PoC 演示")
    print("=" * 50)

    # 创建临时工作目录
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace = Path(temp_dir)
        prompt_file = create_test_prompt(workspace)
        workflow_file = workspace / "WORKFLOW.md"
        workflow_file.write_text("# Mock Workflow", encoding="utf-8")

        # 创建执行上下文
        context = AgentExecutionContext(
            workspace=workspace,
            prompt_file=prompt_file,
            issue_number="123",
            issue_title="测试多 Agent 切换",
            issue_url="https://github.com/example/repo/issues/123",
            workflow_file=workflow_file,
            base_branch="main",
        )

        # 创建 Agent 管理器并添加模拟配置
        manager = AgentManager()
        mock_configs = MockAgentConfig.create_mock_configs()
        manager._agent_configs = mock_configs

        print(f"📁 工作目录: {workspace}")
        print(f"📝 Prompt 文件: {prompt_file}")
        print()

        # 演示 1: 列出可用的 Agent
        print("📋 可用的 Agent:")
        for i, agent_name in enumerate(manager.list_available_agents(), 1):
            config = manager.get_agent_config(agent_name)
            print(f"  {i}. {agent_name} (模型: {config.model})")
        print()

        # 演示 2: 单独执行每个 Agent
        print("🔄 单独执行每个 Agent:")
        print("-" * 30)

        for agent_name in ["mock-copilot", "mock-claude", "mock-opencode", "mock-deepseek"]:
            print(f"\n🤖 执行 Agent: {agent_name}")
            start_time = time.time()

            result = await manager.execute_with_agent(agent_name, context)

            execution_time = time.time() - start_time
            status = "✅ 成功" if result.success else "❌ 失败"

            print(f"   状态: {status}")
            print(f"   执行时间: {execution_time:.1f}s")
            print(f"   输出: {result.stdout.strip()}")

            if not result.success:
                print(f"   错误: {result.stderr.strip()}")

        # 演示 3: 降级策略
        print("\n" + "=" * 50)
        print("🔄 演示降级策略 (主 Agent 失败时自动切换)")
        print("-" * 30)

        print("\n场景 1: 主 Agent 失败，自动切换到备选 Agent")
        primary_agent = "mock-failing"  # 这个 Agent 会失败
        fallback_agents = ["mock-copilot", "mock-claude"]

        print(f"主 Agent: {primary_agent}")
        print(f"备选 Agent: {', '.join(fallback_agents)}")

        start_time = time.time()
        result = await manager.execute_with_fallback(primary_agent, fallback_agents, context)
        execution_time = time.time() - start_time

        status = "✅ 成功" if result.success else "❌ 失败"
        print(f"\n最终状态: {status}")
        print(f"执行的 Agent: {result.agent_name}")
        print(f"总执行时间: {execution_time:.1f}s")
        print(f"输出: {result.stdout.strip()}")

        # 演示 4: 推荐的降级链
        print("\n" + "=" * 50)
        print("📊 推荐的 Agent 降级链")
        print("-" * 30)

        chain = manager.get_recommended_fallback_chain()
        print("推荐顺序 (按优先级):")
        for i, agent_name in enumerate(chain, 1):
            config = manager.get_agent_config(agent_name)
            print(f"  {i}. {agent_name} (模型: {config.model})")

        # 演示 5: 配置验证
        print("\n" + "=" * 50)
        print("🔍 配置验证")
        print("-" * 30)

        for agent_name in manager.list_available_agents():
            errors = manager.validate_agent(agent_name)
            status = "✅ 有效" if not errors else "❌ 无效"
            print(f"  {agent_name}: {status}")
            if errors:
                for error in errors:
                    print(f"    - {error}")

        # 演示 6: 配置模板
        print("\n" + "=" * 50)
        print("📋 配置模板示例")
        print("-" * 30)

        template = manager.create_agent_config_template()
        print("JSON 配置模板:")
        print(json.dumps(template, indent=2, ensure_ascii=False)[:500] + "...")

    print("\n🎉 演示完成！")


async def demonstrate_real_world_scenario() -> None:
    """演示真实场景的配置。"""
    print("\n" + "=" * 50)
    print("🌍 真实场景配置示例")
    print("-" * 30)

    print("1. 环境变量配置:")
    print("   export AUTOMATION_PRIMARY_AGENT=copilot")
    print("   export AUTOMATION_FALLBACK_AGENTS=claude-code,cline,opencode")
    print("   export GITHUB_TOKEN=<YOUR_GITHUB_TOKEN>")
    print("   export ANTHROPIC_API_KEY=<YOUR_ANTHROPIC_API_KEY>")
    print()

    print("2. Agent 特定配置:")
    print(
        "   export AGENT_COPILOT_COMMAND='gh copilot suggest --workspace {workspace} --prompt-file {prompt}'"
    )
    print(
        "   export AGENT_CLAUDE_CODE_COMMAND='claude-code --workspace {workspace} --prompt-file {prompt}'"
    )
    print("   export AGENT_CLINE_COMMAND='cline --workspace {workspace} --prompt-file {prompt}'")
    print()

    print("3. 模型和 API 配置:")
    print("   export AGENT_COPILOT_MODEL=gpt-4")
    print("   export AGENT_CLAUDE_CODE_MODEL=claude-3-5-sonnet-20241022")
    print("   export AGENT_OPENCODE_BASE_URL=https://api.openai.com/v1")
    print("   export AGENT_DEEPSEEK_BASE_URL=https://api.deepseek.com/v1")
    print()

    print("4. 使用配置文件 (.github/automation/agent-configs.json):")
    example_config = {
        "agents": {
            "copilot": {
                "command_template": "gh copilot suggest --workspace {workspace} --prompt-file {prompt}",
                "model": "gpt-4",
                "timeout_seconds": 3600,
            },
            "claude-code": {
                "command_template": "claude-code --workspace {workspace} --prompt-file {prompt}",
                "model": "claude-3-5-sonnet-20241022",
                "api_key": "${ANTHROPIC_API_KEY}",
                "timeout_seconds": 3600,
            },
        }
    }
    print(json.dumps(example_config, indent=2, ensure_ascii=False))


def main() -> None:
    """主函数。"""
    print("多 Agent 切换 PoC 演示")
    print("这个演示展示了如何在同一任务上切换不同的 coding agent")
    print()

    try:
        # 运行主要演示
        asyncio.run(demonstrate_agent_switching())

        # 显示真实场景配置
        asyncio.run(demonstrate_real_world_scenario())

    except KeyboardInterrupt:
        print("\n\n演示被用户中断")
    except Exception as e:
        print(f"\n\n演示过程中发生错误: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
