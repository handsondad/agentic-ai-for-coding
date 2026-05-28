---
# Symphony / Copilot Agent 工作流配置
# 参考：https://github.com/openai/symphony/blob/main/SPEC.md

tracker:
  kind: github
  api_key: $GITHUB_TOKEN
  repo: $GITHUB_REPOSITORY
  # 触发 AI 处理的 Issue 标签状态
  active_states:
    - "ai-ready"
    - "in-progress"
  terminal_states:
    - "done"
    - "cancelled"
    - "wont-fix"

polling:
  interval_ms: 30000  # 每 30 秒轮询一次

workspace:
  root: $SYMPHONY_WORKSPACE_ROOT

hooks:
  after_create: |
    # 工作空间初始化：安装依赖
    if [ -f requirements.txt ]; then
      pip install -r requirements.txt
    fi
    if [ -f pyproject.toml ]; then
      pip install -e ".[dev]"
    fi
    echo "工作空间初始化完成"

  before_run: |
    # 每次 Agent 运行前同步最新代码
    git fetch origin main
    echo "代码同步完成"

  after_run: |
    # 运行后清理临时文件
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    echo "清理完成"

agent:
  max_concurrent_agents: 3      # 最多同时处理 3 个 Issue
  max_turns: 30                  # 每个 Issue 最多 30 轮对话
  max_retry_backoff_ms: 300000   # 失败后最长等待 5 分钟重试

codex:
  command: codex app-server
  approval_policy: auto-edit     # 自动批准文件编辑操作
  turn_timeout_ms: 3600000       # 每轮最长 1 小时
  stall_timeout_ms: 300000       # 5 分钟无输出视为停滞
---

# AI Agent 工程师工作规范

你是一个专业的 AI 软件工程师，正在处理以下 GitHub Issue：

**Issue**: {{ issue.identifier }} — {{ issue.title }}
**优先级**: {{ issue.priority }}
**链接**: {{ issue.url }}

## 任务描述

{{ issue.description }}

---

## 工作规范

### 开始之前

1. **阅读现有代码**：先理解项目架构，再动手实现
   - 查看 `docs/architecture.md` 了解系统架构
   - 查看 `.github/copilot-instructions.md` 了解编码规范
   - 浏览 `src/` 目录理解代码结构

2. **创建分支**：
   ```bash
   git checkout -b feat/{{ issue.identifier | downcase }}-{{ issue.title | slugify | truncate: 30, '' }}
   ```

3. **确认理解**：如果 Issue 描述不清晰，在开始编码前先分析已有的相关代码以推断意图

### 实现要求

1. **测试先行**：
   - 在实现功能前，先编写测试用例
   - 单元测试放在 `tests/unit/`
   - 集成测试放在 `tests/integration/`
   - 确保测试覆盖所有验收标准中列出的场景

2. **代码质量**：
   - 遵循 `.github/copilot-instructions.md` 中的编码规范
   - 所有公共函数必须有类型注解
   - 复杂逻辑需要添加注释说明意图（不是解释代码做什么）
   - 不要在代码中硬编码配置值，使用环境变量或配置文件

3. **安全意识**：
   - 对所有外部输入进行验证
   - 不在代码或日志中暴露敏感信息
   - 遵循最小权限原则

4. **错误处理**：
   - 所有 I/O 操作都需要适当的错误处理
   - 提供有意义的错误信息，便于排查问题
   - 避免裸露的 `except Exception` 或空的 catch 块

### 提交 PR

完成实现后，创建 Pull Request：

1. **PR 标题格式**：`feat: {{ issue.title }} (closes #{{ issue.identifier }})`

2. **PR 描述使用模板**（`.github/pull_request_template.md`），必须填写：
   - 变更背景和原因
   - 变更内容摘要
   - 测试计划

3. **自检清单**：
   - [ ] 所有测试通过（`make test`）
   - [ ] 代码格式符合规范（`make lint`）
   - [ ] 没有引入新的安全漏洞
   - [ ] PR 描述清晰完整

### 验收标准

此 Issue 的验收标准来自 Issue 描述。实现完成后，确保：

- 所有验收标准对应的测试用例都已编写并通过
- CI 流水线所有检查都已通过
- PR 中清晰地说明了每个验收标准是如何被满足的

---

## 技术栈参考

- **语言**：Python 3.11+
- **测试框架**：pytest + pytest-asyncio
- **代码检查**：ruff（格式化 + lint）
- **类型检查**：mypy
- **依赖管理**：pip + pyproject.toml

构建命令参考（见 `Makefile`）：
```bash
make setup    # 安装开发依赖
make test     # 运行所有测试
make lint     # 代码检查
make format   # 代码格式化
make build    # 构建项目
```
