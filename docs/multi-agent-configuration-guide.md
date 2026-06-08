# 多 Coding Agent 配置说明文档

## 概述

本文档详细说明如何配置和使用多 Coding Agent 系统。该系统支持多种 coding agent CLI 工具的统一接入，包括 GitHub Copilot、Claude Code、Cline、OpenCode、DeepSeek 等，并提供自动降级和成本优化功能。

## 快速开始

### 1. 环境变量配置

最简单的配置方式是通过环境变量：

```bash
# 设置主要和备选 Agent
export AUTOMATION_PRIMARY_AGENT="copilot"
export AUTOMATION_FALLBACK_AGENTS="claude-code,deepseek"

# 配置 GitHub Copilot
export AGENT_COPILOT_COMMAND="gh copilot suggest --workspace {workspace} --prompt-file {prompt}"
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 配置 Claude Code
export AGENT_CLAUDE_CODE_COMMAND="claude-code --workspace {workspace} --prompt-file {prompt}"
export ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 配置 DeepSeek
export AGENT_DEEPSEEK_COMMAND="deepseek-tui --workspace {workspace} --prompt {prompt}"
export DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### 2. 配置文件方式

创建 `.github/automation/agent-configs.json`：

```json
{
  "agents": {
    "copilot": {
      "command_template": "gh copilot suggest --workspace {workspace} --prompt-file {prompt}",
      "model": "gpt-4",
      "timeout_seconds": 3600,
      "retry_count": 2
    },
    "claude-code": {
      "command_template": "claude-code --workspace {workspace} --prompt-file {prompt}",
      "model": "claude-3-5-sonnet-20241022",
      "api_key": "${ANTHROPIC_API_KEY}",
      "timeout_seconds": 3600,
      "retry_count": 2
    },
    "deepseek": {
      "command_template": "deepseek-tui --workspace {workspace} --prompt {prompt}",
      "model": "deepseek-coder",
      "base_url": "https://api.deepseek.com/v1",
      "api_key": "${DEEPSEEK_API_KEY}",
      "timeout_seconds": 1800,
      "retry_count": 1
    }
  }
}
```

## 详细配置指南

### Agent 配置参数

每个 Agent 支持以下配置参数：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | Agent 名称，用于标识和日志 |
| `command_template` | string | ✅ | 命令模板，支持占位符替换 |
| `model` | string | ❌ | 使用的模型名称 |
| `base_url` | string | ❌ | API 基础 URL（OpenAI-compatible） |
| `api_key` | string | ❌ | API 密钥 |
| `timeout_seconds` | number | ❌ | 超时时间（默认 3600s） |
| `retry_count` | number | ❌ | 重试次数（默认 1） |
| `extra_env` | object | ❌ | 额外的环境变量 |

### 命令模板占位符

命令模板支持以下占位符：

| 占位符 | 说明 | 示例值 |
|--------|------|--------|
| `{workspace}` | 工作目录路径 | `/path/to/workspace` |
| `{prompt}` | Prompt 文件路径 | `/path/to/prompt.md` |
| `{issue_number}` | Issue 编号 | `123` |
| `{issue_title}` | Issue 标题 | `Fix login bug` |
| `{issue_url}` | Issue URL | `https://github.com/...` |
| `{workflow}` | Workflow 文件路径 | `/path/to/WORKFLOW.md` |
| `{base_branch}` | 基础分支 | `main` |
| `{model}` | 模型名称 | `gpt-4` |
| `{base_url}` | API 基础 URL | `https://api.openai.com/v1` |
| `{api_key}` | API 密钥 | `sk-xxx...` |

## 各 Agent 的具体配置

### GitHub Copilot

```bash
# 环境变量配置
export AGENT_COPILOT_COMMAND="gh copilot suggest --workspace {workspace} --prompt-file {prompt}"
export AGENT_COPILOT_MODEL="gpt-4"
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 或者使用 GitHub CLI 的其他命令
export AGENT_COPILOT_COMMAND="gh copilot explain --workspace {workspace} --file {prompt}"
```

**前置要求：**
- 安装 GitHub CLI (`gh`)
- 配置 GitHub 认证 (`gh auth login`)
- 启用 Copilot 服务

### Claude Code

```bash
# 环境变量配置
export AGENT_CLAUDE_CODE_COMMAND="claude-code --workspace {workspace} --prompt-file {prompt}"
export AGENT_CLAUDE_CODE_MODEL="claude-3-5-sonnet-20241022"
export ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 高级配置
export AGENT_CLAUDE_CODE_TIMEOUT="1800"
export AGENT_CLAUDE_CODE_RETRY="2"
```

**前置要求：**
- 安装 Claude Code CLI
- 获取 Anthropic API Key
- 配置 API 访问权限

### Cline (VS Code Extension)

```bash
# 环境变量配置
export AGENT_CLINE_COMMAND="cline --workspace {workspace} --prompt-file {prompt}"
export AGENT_CLINE_MODEL="gpt-4"
export OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 如果使用其他模型
export AGENT_CLINE_MODEL="claude-3-5-sonnet"
export ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

**前置要求：**
- 安装 VS Code 和 Cline 扩展
- 配置 Cline 的 API 访问
- 确保 VS Code 可以在命令行调用

### OpenCode

```bash
# 环境变量配置
export AGENT_OPENCODE_COMMAND="opencode --workspace {workspace} --prompt {prompt}"
export AGENT_OPENCODE_MODEL="gpt-4"
export AGENT_OPENCODE_BASE_URL="https://api.openai.com/v1"
export OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 自定义 API 端点
export AGENT_OPENCODE_BASE_URL="https://your-custom-api.com/v1"
```

**前置要求：**
- 安装 OpenCode CLI
- 配置 OpenAI-compatible API 访问
- 设置正确的 API 端点

### DeepSeek

```bash
# 环境变量配置
export AGENT_DEEPSEEK_COMMAND="deepseek-tui --workspace {workspace} --prompt {prompt}"
export AGENT_DEEPSEEK_MODEL="deepseek-coder"
export AGENT_DEEPSEEK_BASE_URL="https://api.deepseek.com/v1"
export DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 性能优化配置
export AGENT_DEEPSEEK_TIMEOUT="900"  # 15分钟，DeepSeek 速度较快
export AGENT_DEEPSEEK_RETRY="1"      # 减少重试次数
```

**前置要求：**
- 注册 DeepSeek 账号
- 获取 API Key
- 安装 DeepSeek CLI 工具

### 通用 OpenAI-Compatible 配置

```bash
# 通用配置模板
export AGENT_GENERIC_COMMAND="your-agent-cli --workspace {workspace} --prompt-file {prompt} --model {model}"
export AGENT_GENERIC_MODEL="your-model-name"
export AGENT_GENERIC_BASE_URL="https://your-api-provider.com/v1"
export AGENT_GENERIC_API_KEY="your-api-key"

# 额外环境变量
export AGENT_GENERIC_EXTRA_ENV='{"CUSTOM_VAR": "value", "ANOTHER_VAR": "value2"}'
```

## 管理工具使用

### 列出可用的 Agent

```bash
python .github/automation/scripts/manage-agents.py list
```

### 验证 Agent 配置

```bash
# 验证单个 Agent
python .github/automation/scripts/manage-agents.py validate copilot

# 验证所有 Agent
python .github/automation/scripts/manage-agents.py validate-all
```

### 创建配置模板

```bash
python .github/automation/scripts/manage-agents.py create-template --output agent-configs.json
```

### 显示环境变量模板

```bash
python .github/automation/scripts/manage-agents.py show-env-template
```

### 查看推荐的降级链

```bash
python .github/automation/scripts/manage-agents.py show-fallback-chain
```

## 运行 PoC 演示

```bash
# 运行多 Agent 切换演示
python .github/automation/scripts/poc-multi-agent-demo.py
```

这个演示会：
1. 展示所有可用的 Agent
2. 逐个执行每个 Agent
3. 演示降级策略
4. 显示配置验证结果

## 高级配置

### 自定义适配器

如果需要支持新的 Agent，可以创建自定义适配器：

```python
from .agent_adapter import AgentAdapter, AgentConfig, AgentExecutionContext, AgentExecutionResult

class CustomAgentAdapter(AgentAdapter):
    async def execute(self, context: AgentExecutionContext) -> AgentExecutionResult:
        # 实现自定义的执行逻辑
        pass
    
    def validate_config(self) -> list[str]:
        # 实现配置验证逻辑
        pass

# 注册自定义适配器
from .agent_adapter import get_agent_registry
registry = get_agent_registry()
registry.register("custom-agent", CustomAgentAdapter)
```

### 环境变量优先级

配置的加载优先级（从高到低）：

1. 特定 Agent 的环境变量（`AGENT_<NAME>_*`）
2. 配置文件（`agent-configs.json`）
3. 通用环境变量（`AUTOMATION_AGENT_COMMAND`）
4. 默认值

### 安全配置

```bash
# 敏感信息掩码
export AUTOMATION_MASK_SECRETS="true"

# 禁用不安全的 Agent
export AUTOMATION_DISABLED_AGENTS="untrusted-agent,experimental-agent"

# 启用配置验证
export AUTOMATION_STRICT_VALIDATION="true"
```

### 性能调优

```bash
# 并发控制
export AUTOMATION_MAX_CONCURRENT_AGENTS="3"

# 超时设置
export AUTOMATION_DEFAULT_TIMEOUT="3600"

# 内存限制
export AUTOMATION_MEMORY_LIMIT="2048M"
```

## 故障排除

### 常见问题

**1. Agent 执行失败**
```bash
# 检查配置
python .github/automation/scripts/manage-agents.py validate <agent-name>

# 查看详细日志
export AUTOMATION_VERBOSE_LOGGING="true"
```

**2. API 认证失败**
```bash
# 检查 API Key 是否正确设置
echo $ANTHROPIC_API_KEY | head -c 20
echo $OPENAI_API_KEY | head -c 20

# 测试 API 连接
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

**3. 命令模板错误**
```bash
# 检查占位符是否正确
echo "Command: $AGENT_COPILOT_COMMAND"

# 验证命令是否可执行
which gh
which claude-code
```

### 调试模式

```bash
# 启用调试模式
export AUTOMATION_DEBUG="true"
export AUTOMATION_DRY_RUN="true"  # 只显示命令，不实际执行

# 查看执行日志
tail -f .github/automation/logs/agent-execution.log
```

### 日志分析

```bash
# 查看 Agent 性能统计
python .github/automation/scripts/analyze-agent-performance.py

# 生成成本报告
python .github/automation/scripts/generate-cost-report.py
```

## 最佳实践

### 1. 配置管理
- 使用配置文件而不是硬编码环境变量
- 定期备份配置文件
- 使用版本控制管理配置变更

### 2. 安全措施
- 不要在代码中硬编码 API Key
- 使用环境变量或密钥管理系统
- 定期轮换 API Key

### 3. 成本控制
- 设置合理的超时时间
- 使用成本较低的 Agent 作为主力
- 监控 API 使用量和成本

### 4. 可靠性保障
- 配置多个备选 Agent
- 设置合理的重试策略
- 建立监控和告警机制

### 5. 性能优化
- 根据任务复杂度选择合适的 Agent
- 并行执行独立任务
- 缓存常用的配置和结果

## 支持和反馈

如果遇到问题或有改进建议，请：

1. 查看 [故障排除](#故障排除) 部分
2. 检查 [GitHub Issues](https://github.com/handsondad/agentic-ai-for-coding/issues)
3. 提交新的 Issue 或 Pull Request

## 更新日志

### v1.0.0 (2024-12-XX)
- ✅ 初始版本发布
- ✅ 支持 7 种主流 Coding Agent
- ✅ 实现自动降级策略
- ✅ 提供完整的配置管理工具