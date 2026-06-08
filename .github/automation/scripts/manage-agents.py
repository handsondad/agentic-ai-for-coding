#!/usr/bin/env python3
"""多 Agent 配置管理工具。"""

import argparse
import json
import os
import sys
from pathlib import Path

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from agent_manager import create_default_agent_manager


def cmd_list_agents(args: argparse.Namespace) -> None:
    """列出所有可用的 Agent。"""
    manager = create_default_agent_manager(Path(args.repo_root))
    agents = manager.list_available_agents()

    if not agents:
        print("没有找到任何 Agent 配置")
        return

    print("可用的 Agent:")
    for agent_name in agents:
        config = manager.get_agent_config(agent_name)
        if config:
            print(f"  {agent_name}")
            print(f"    命令模板: {config.command_template}")
            if config.model:
                print(f"    模型: {config.model}")
            if config.base_url:
                print(f"    API 基础 URL: {config.base_url}")
            print(f"    超时: {config.timeout_seconds}s")
            print(f"    重试次数: {config.retry_count}")
            print()


def cmd_validate_agent(args: argparse.Namespace) -> None:
    """验证指定 Agent 的配置。"""
    manager = create_default_agent_manager(Path(args.repo_root))
    errors = manager.validate_agent(args.agent_name)

    if not errors:
        print(f"✅ Agent '{args.agent_name}' 配置有效")
    else:
        print(f"❌ Agent '{args.agent_name}' 配置错误:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


def cmd_validate_all(args: argparse.Namespace) -> None:
    """验证所有 Agent 配置。"""
    manager = create_default_agent_manager(Path(args.repo_root))
    agents = manager.list_available_agents()

    if not agents:
        print("没有找到任何 Agent 配置")
        return

    all_valid = True
    for agent_name in agents:
        errors = manager.validate_agent(agent_name)
        if errors:
            print(f"❌ Agent '{agent_name}' 配置错误:")
            for error in errors:
                print(f"  - {error}")
            all_valid = False
        else:
            print(f"✅ Agent '{agent_name}' 配置有效")

    if not all_valid:
        sys.exit(1)


def cmd_create_template(args: argparse.Namespace) -> None:
    """创建配置文件模板。"""
    manager = create_default_agent_manager(Path(args.repo_root))
    template = manager.create_agent_config_template()

    output_file = Path(args.output)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2, ensure_ascii=False)

    print(f"配置文件模板已创建: {output_file}")
    print()
    print("请编辑配置文件，设置正确的 API 密钥和命令模板。")
    print("环境变量格式: ${VARIABLE_NAME}")


def cmd_show_env_template(args: argparse.Namespace) -> None:
    """显示环境变量配置模板。"""
    print("# 多 Agent 配置环境变量模板")
    print("# 复制以下内容到 .env 文件或设置为系统环境变量")
    print()

    print("# 主要 Agent 和备选 Agent")
    print("AUTOMATION_PRIMARY_AGENT=copilot")
    print("AUTOMATION_FALLBACK_AGENTS=claude-code,cline,opencode")
    print()

    print("# GitHub Copilot")
    print("AGENT_COPILOT_COMMAND=gh copilot suggest --workspace {workspace} --prompt-file {prompt}")
    print("AGENT_COPILOT_MODEL=gpt-4")
    print("GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print()

    print("# Claude Code")
    print("AGENT_CLAUDE_CODE_COMMAND=claude-code --workspace {workspace} --prompt-file {prompt}")
    print("AGENT_CLAUDE_CODE_MODEL=claude-3-5-sonnet-20241022")
    print("ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print()

    print("# Cline (VS Code Extension)")
    print("AGENT_CLINE_COMMAND=cline --workspace {workspace} --prompt-file {prompt}")
    print("AGENT_CLINE_MODEL=gpt-4")
    print("OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print()

    print("# OpenCode")
    print("AGENT_OPENCODE_COMMAND=opencode --workspace {workspace} --prompt {prompt}")
    print("AGENT_OPENCODE_MODEL=gpt-4")
    print("OPENAI_BASE_URL=https://api.openai.com/v1")
    print("OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print()

    print("# DeepSeek")
    print("AGENT_DEEPSEEK_COMMAND=deepseek-tui --workspace {workspace} --prompt {prompt}")
    print("AGENT_DEEPSEEK_MODEL=deepseek-coder")
    print("AGENT_DEEPSEEK_BASE_URL=https://api.deepseek.com/v1")
    print("DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print()

    print("# 通用 OpenAI-compatible 配置")
    print(
        "AGENT_GENERIC_COMMAND=your-agent-cli --workspace {workspace} --prompt-file {prompt} --model {model}"
    )
    print("AGENT_GENERIC_MODEL=gpt-4")
    print("AGENT_GENERIC_BASE_URL=https://your-api-provider.com/v1")
    print("AGENT_GENERIC_API_KEY=your-api-key")
    print()

    print("# 旧版兼容配置（优先级较低）")
    print(
        "AUTOMATION_AGENT_COMMAND=powershell -NoProfile -ExecutionPolicy Bypass -File .github/automation/scripts/run-agent-adapter.ps1 -Workspace {workspace} -PromptFile {prompt}"
    )
    print(
        "AUTOMATION_ADAPTER_BACKEND_COMMAND=your-agent-cli --workspace {workspace} --prompt-file {prompt}"
    )


def cmd_show_fallback_chain(args: argparse.Namespace) -> None:
    """显示推荐的 Agent 降级链。"""
    manager = create_default_agent_manager(Path(args.repo_root))
    chain = manager.get_recommended_fallback_chain()

    if not chain:
        print("没有找到任何可用的 Agent")
        return

    print("推荐的 Agent 降级链 (按优先级排序):")
    for i, agent_name in enumerate(chain, 1):
        config = manager.get_agent_config(agent_name)
        status = "✅" if config and not manager.validate_agent(agent_name) else "❌"
        print(f"  {i}. {status} {agent_name}")

    print()
    print("设置方法:")
    if chain:
        primary = chain[0]
        fallbacks = ",".join(chain[1:])
        print(f"export AUTOMATION_PRIMARY_AGENT={primary}")
        if fallbacks:
            print(f"export AUTOMATION_FALLBACK_AGENTS={fallbacks}")


def main() -> None:
    """主入口函数。"""
    parser = argparse.ArgumentParser(description="多 Agent 配置管理工具")
    parser.add_argument("--repo-root", default=os.getcwd(), help="仓库根目录路径 (默认: 当前目录)")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # list 命令
    subparsers.add_parser("list", help="列出所有可用的 Agent")

    # validate 命令
    validate_parser = subparsers.add_parser("validate", help="验证指定 Agent 配置")
    validate_parser.add_argument("agent_name", help="要验证的 Agent 名称")

    # validate-all 命令
    subparsers.add_parser("validate-all", help="验证所有 Agent 配置")

    # create-template 命令
    template_parser = subparsers.add_parser("create-template", help="创建配置文件模板")
    template_parser.add_argument(
        "--output",
        default=".github/automation/agent-configs.json",
        help="输出文件路径 (默认: .github/automation/agent-configs.json)",
    )

    # show-env-template 命令
    subparsers.add_parser("show-env-template", help="显示环境变量配置模板")

    # show-fallback-chain 命令
    subparsers.add_parser("show-fallback-chain", help="显示推荐的 Agent 降级链")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 执行对应的命令
    command_map = {
        "list": cmd_list_agents,
        "validate": cmd_validate_agent,
        "validate-all": cmd_validate_all,
        "create-template": cmd_create_template,
        "show-env-template": cmd_show_env_template,
        "show-fallback-chain": cmd_show_fallback_chain,
    }

    command_func = command_map.get(args.command)
    if command_func:
        command_func(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
