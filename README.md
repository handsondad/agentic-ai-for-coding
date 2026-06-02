# AI Agent 项目开发流程模板

> 基于本仓库自动化调度方案构建的 AI Agent 项目开发流程模板，深度集成 GitHub 生态工具，以 **AI for Coding** 为核心驱动力，适合 10 人以内的小团队打造生产级 AI Agent 产品。

---

## 目录

- [核心理念](#核心理念)
- [整体架构](#整体架构)
- [开发流程设计](#开发流程设计)
- [GitHub 工具链](#github-工具链)
- [快速开始](#快速开始)
- [目录结构](#目录结构)
- [工作流详解](#工作流详解)
- [自动化集成](#自动化-集成)
- [分支与发布策略](#分支与发布策略)
- [团队协作规范](#团队协作规范)
- [常见问题](#常见问题)

---

## 核心理念

### 为什么是 AI for Coding 驱动？

传统开发流程中，工程师需要亲自监督每一行代码的编写。而 **AI for Coding 驱动**的开发模式让工程师从代码实施者转变为**工作管理者**——你负责定义清晰的需求和验收标准，AI Agent 负责自主实现，工程师专注于架构决策、代码审查和产品方向。

这种模式带来的核心优势：

| 传统模式 | AI 驱动模式 |
|---------|------------|
| 工程师编写每行代码 | 工程师定义需求，AI 实现 |
| 手动监督代码质量 | CI/CD + 自动化测试保障质量 |
| 线性开发速度 | 并发执行多个任务 |
| 经验依赖性强 | 知识沉淀在 Prompt 和规范中 |

### 核心原则

1. **需求即代码**：每个 GitHub Issue 都是一个完整的工作单元，包含足够的上下文让 AI 自主完成实现
2. **规范驱动**：通过 `WORKFLOW.md` 和 `.github/copilot-instructions.md` 定义 AI 的行为边界
3. **测试优先**：所有 AI 生成的代码必须通过 CI 验证才能合并
4. **可观测性**：每个 AI 执行会话都有完整的日志和工作证明
5. **人工把关**：AI 实现，人工审查，确保产品质量

---

## 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        产品开发循环                               │
│                                                                   │
│  需求定义  →  Issue创建  →  AI实现  →  代码审查  →  合并上线        │
│   (PM/TL)    (规范模板)   (Copilot)   (工程师)    (自动发布)       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      GitHub 生态工具栈                             │
│                                                                   │
│  GitHub Issues    →  任务追踪与需求管理                            │
│  GitHub Projects  →  项目看板与进度管理                            │
│  GitHub Copilot   →  AI 辅助编码（个人开发）                       │
│  Copilot Agent    →  AI 自主实现（任务执行）                        │
│  GitHub Actions   →  CI/CD 与工作流编排                            │
│  GitHub Code Rev  →  代码审查与质量保障                             │
│  Automation Runner → AI Agent 任务调度编排                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 开发流程设计

### 标准开发流程

```
1. 需求拆解
   PM/TL → 创建 GitHub Issue（使用标准模板）
   └─ 填写：用户故事、验收标准、技术要点、测试要求

2. 任务分配
   TL → 给 Issue 打上 `copilot` 标签
   └─ GitHub Actions 自动触发 Copilot Coding Agent

3. AI 自主实现
   Copilot Agent → 读取 Issue + WORKFLOW.md + copilot-instructions.md
   └─ 创建分支 → 实现功能 → 编写测试 → 提交 PR

4. 自动化验证
   GitHub Actions CI → 运行测试 + 代码分析 + 安全扫描
   └─ 所有检查通过后，PR 标记为可审查

5. 人工代码审查
   工程师 → 审查 PR（关注：逻辑正确性、安全性、架构合理性）
   └─ 提供反馈 → Copilot Agent 根据反馈修改

6. 合并与发布
   审查通过 → 合并到 main
   └─ 自动触发发布流水线
```

### Automation 编排模式（高级）

对于需要并发处理多个任务的场景，使用本地 Automation Runner 进行 AI Agent 任务调度：

```
Automation Runner 服务
├── 持续监听 GitHub Issues（标记为 ai-ready 状态）
├── 为每个 Issue 创建隔离工作空间
├── 启动 Codex/Copilot Agent 会话
├── 收集工作证明（CI状态、PR链接、测试结果）
└── 汇报进度给项目看板
```

---

## GitHub 工具链

### 1. GitHub Issues — 任务中枢

所有工作从 Issue 开始。本模板提供三种 Issue 模板：

- **功能需求** (`feature.yml`)：新功能开发，包含用户故事和验收标准
- **Bug 报告** (`bug.yml`)：问题修复，包含复现步骤和期望行为
- **开发任务** (`task.yml`)：技术任务，包含技术规格和完成标准

**关键实践**：
- Issue 描述必须足够详细，让 AI 无需额外沟通即可理解需求
- 可复用 Prompt 统一放在 `.github/prompts/`，例如 `create-issue-prompt.md` 用于按 Issue Template 生成规范化提单内容
- 使用标签体系管理任务状态：`ai-ready`、`in-progress`、`human-review`
- 通过 GitHub Projects 管理任务优先级和进度

### 2. GitHub Copilot Coding Agent — AI 实现引擎

Copilot Coding Agent 是本流程的核心执行引擎：

```yaml
# 触发方式
- 给 Issue 添加 'copilot' 标签 → 自动触发
- 在 Issue 评论 '@copilot implement this' → 手动触发
- GitHub Actions 计划任务 → 批量处理
```

**Agent 工作模式**：
1. 读取 Issue 内容和 `WORKFLOW.md` 中的工作规范
2. 分析现有代码库，理解架构上下文
3. 创建功能分支并实现代码
4. 编写对应的单元测试和集成测试
5. 提交 PR 并附上实现说明

### 3. GitHub Actions — 自动化流水线

三条核心流水线：

```
ci.yml          → 每次 PR/Push 触发
                   ├── 代码格式检查
                   ├── 单元测试
                   ├── 集成测试
                   └── 安全扫描

copilot-agent.yml → Issue 打标签触发
                   ├── 启动 Copilot Agent
                   ├── 监控执行状态
                   └── 更新 Issue 状态

release.yml     → 合并到 main 触发
                   ├── 版本打标
                   ├── 构建 Docker 镜像
                   └── 部署到目标环境
```

### 4. GitHub Code Review — 质量把关

代码审查是唯一的人工质量关卡：

- **CODEOWNERS** 文件定义核心模块的必须审查人
- **Branch Protection Rules** 强制要求 CI 通过 + 至少 1 人审查
- PR 模板引导填写完整的变更说明和测试计划
- AI 生成的代码需要更关注逻辑正确性和安全边界

---

## 快速开始

### 前置条件

- GitHub 仓库（已启用 GitHub Copilot 和 Copilot Coding Agent）
- Python 3.11+（或你的目标语言运行时）
- [mise](https://mise.jdx.dev/) — 工具版本管理
- Docker（可选，用于本地集成测试）

### 1. 使用本模板

```bash
# 方式一：使用 GitHub Template 功能
# 点击仓库页面的 "Use this template" 按钮

# 方式二：克隆并重新初始化
git clone https://github.com/handsondad/agentic-ai-for-coding.git my-ai-agent-project
cd my-ai-agent-project
rm -rf .git && git init
```

### 2. 初始化开发环境

```bash
# 安装依赖工具
make setup

# 复制环境变量模板
cp .env.example .env
# 编辑 .env 填入你的 API Keys
```

### 3. 配置 WORKFLOW.md

编辑根目录的 `WORKFLOW.md`，配置：
- 你的项目特定的编码规范
- AI Agent 的工作边界和约束
- 任务验收标准的定义方式

### 4. 配置 GitHub 仓库设置

```bash
# 在 GitHub 仓库设置中启用：
# Settings → General → Features → Issues ✓
# Settings → Code and automation → Actions → Allow all actions ✓
# Settings → Code and automation → Branches → Add branch protection rule for 'main'
#   ├── Require a pull request before merging ✓
#   ├── Require status checks to pass ✓ (选择 ci/test)
#   └── Require conversation resolution ✓
```

### 5. 创建你的第一个 AI 实现的功能

```bash
# 1. 创建 Issue（使用功能需求模板）
# 2. 给 Issue 打上 'copilot' 标签
# 3. 等待 Copilot Agent 自动创建 PR
# 4. 审查并合并 PR
```

---

## 目录结构

```
.
├── README.md                          # 本文档
├── WORKFLOW.md                        # Automation/Copilot Agent 工作规范
├── Makefile                           # 开发命令集合
├── .env.example                       # 环境变量模板
├── .gitignore
│
├── .github/
│   ├── copilot-instructions.md        # GitHub Copilot 全局编码规范
│   ├── ISSUE_TEMPLATE/
│   │   ├── config.yml                 # Issue 模板配置
│   │   ├── feature.yml                # 功能需求模板
│   │   ├── bug.yml                    # Bug 报告模板
│   │   └── task.yml                   # 开发任务模板
│   ├── prompts/
│   │   └── create-issue-prompt.md     # 按 Issue Template 生成提单内容的 Prompt
│   ├── pull_request_template.md       # PR 描述模板
│   └── workflows/
│       ├── ci.yml                     # 持续集成流水线
│       ├── copilot-agent.yml          # Copilot Agent 自动触发
│       └── release.yml                # 版本发布流程
│
├── docs/
│   ├── architecture.md                # 系统架构文档
│   ├── dev-guide.md                   # 开发者指南
│   └── adr/                           # 架构决策记录
│       └── 0001-record-architecture-decisions.md
│
├── src/
│   ├── agent/                         # Agent 核心逻辑
│   │   ├── __init__.py
│   │   ├── core.py                    # Agent 主循环
│   │   └── session.py                 # 会话管理
│   ├── tools/                         # 工具/函数定义
│   │   ├── __init__.py
│   │   └── registry.py                # 工具注册中心
│   ├── memory/                        # 记忆与状态管理
│   │   ├── __init__.py
│   │   └── store.py                   # 记忆存储
│   └── api/                           # API 层
│       ├── __init__.py
│       └── routes.py                  # API 路由
│
└── tests/
    ├── unit/                          # 单元测试
    ├── integration/                   # 集成测试
    └── conftest.py                    # 测试配置
```

---

## 工作流详解

### Issue 生命周期

```
创建 Issue
    │
    ▼
[backlog] → 待优先级排序
    │
    ▼
[ai-ready] → 需求已完善，可以交给 AI 实现
    │ (打 'copilot' 标签触发 Agent)
    ▼
[in-progress] → Copilot Agent 正在实现
    │
    ▼
[human-review] → PR 已创建，等待人工审查
    │
    ▼
[done] → 合并完成，自动关闭 Issue
```

### PR 审查重点

作为代码审查者，面对 AI 生成的代码时，重点关注：

| 审查维度 | 检查要点 |
|---------|---------|
| **逻辑正确性** | 是否正确理解需求？边界条件处理是否完整？ |
| **安全性** | 输入验证、权限控制、敏感信息处理 |
| **架构合理性** | 是否符合项目架构规范？模块边界是否清晰？ |
| **测试覆盖** | 关键路径是否有测试？测试用例是否有意义？ |
| **可维护性** | 代码是否易于理解？文档是否充分？ |

---

## 自动化集成

本仓库内置本地 Automation Runner，用于自动监听 GitHub Issues 并并发执行多个 Agent 会话。

### 工作原理

```
Automation Runner 服务（长驻进程）
    │
    ├── 每 30 秒轮询 GitHub Issues（active_states 中的 Issue）
    │
    ├── 为每个 Issue 创建隔离工作目录
    │
    ├── 加载 WORKFLOW.md（工作规范 + Agent Prompt 模板）
    │
    ├── 启动 Codex App Server 会话
    │   └── 传入 Issue 上下文 + 项目规范
    │
    ├── 监控执行进度（CI状态、PR创建、测试结果）
    │
    └── 工作完成 → Issue 转为 Human Review 状态
```

### 配置 Automation Runner

本仓库的 `WORKFLOW.md` 已预配置为与 GitHub Issues 协同工作。你可以直接使用 `.github/automation/` 下的运行脚本启动。

### WORKFLOW.md 关键配置

`WORKFLOW.md` 是 Automation Runner 的配置文件和 Agent Prompt 模板，分为两部分：

**前置配置（YAML front matter）**：
```yaml
---
tracker:
  kind: github          # 使用 GitHub Issues 作为任务追踪
  api_key: $GITHUB_TOKEN
  repo: owner/repo
  active_states:        # 触发 AI 处理的 Issue 状态标签
    - "ai-ready"
  terminal_states:
    - "done"
    - "cancelled"

agent:
  max_concurrent_agents: 3   # 最多同时运行 3 个 Agent
  max_turns: 30

polling:
  interval_ms: 30000         # 每 30 秒检查一次
---
```

**Prompt 模板（Markdown 正文）**：
```markdown
你是一个专业的 AI 软件工程师，负责实现以下 GitHub Issue：

Issue: {{ issue.title }}
描述: {{ issue.description }}

请按照项目的编码规范（见 .github/copilot-instructions.md）实现此功能...
```

---

## 分支与发布策略

## 本地自动执行器（Python 版）

仓库已内置一个本地自动调度器（`.github/automation/`），实现核心流程：

1. 轮询 GitHub Issues（按 `WORKFLOW.md` 的 `active_states` 标签筛选）
2. 为每个任务创建本地 Git Worktree
3. 加载 `WORKFLOW.md` 指令模板并渲染为 issue prompt
4. 执行你配置的本地 AI 命令（如 Copilot/Codex/自定义脚本）
5. 自动执行质量门禁（默认 `make lint` + `make test`）
6. 自动提交分支并创建 PR

### 运行方式（脚本优先）

```bash
# 1) 配置环境变量
export GITHUB_TOKEN=ghp_xxx
export GITHUB_REPOSITORY=owner/repo

# 可选：指定 AI 执行命令模板
# 可用占位符：{workspace} {workflow} {prompt} {issue_number} {issue_title} {issue_url}
export AUTOMATION_AGENT_COMMAND='your-agent-cli --workspace "{workspace}" --prompt-file "{prompt}"'

# 可选：覆盖质量门禁，多个命令用 ;; 分隔
export AUTOMATION_QUALITY_COMMANDS='make lint;;make test'

# 可选：启用/禁用团队 skills（默认开启）
export AUTOMATION_USE_SKILLS='true'

# 可选：指定 skills 配置文件（默认 .github/automation/skills/skills.yaml）
export AUTOMATION_SKILLS_FILE='.github/automation/skills/skills.yaml'

# 2) 单次执行（推荐给 Cron/计划任务）
# Windows PowerShell
pwsh .github/automation/scripts/run-once.ps1

# Linux/macOS
sh .github/automation/scripts/run-once.sh

# 3) 常驻轮询执行
# Windows PowerShell
pwsh .github/automation/scripts/run-forever.ps1

# Linux/macOS
sh .github/automation/scripts/run-forever.sh
```

### 与 Cron/计划任务集成

- Linux/macOS（每分钟）：

```bash
* * * * * cd /path/to/repo && /bin/sh .github/automation/scripts/run-once.sh >> .github/automation/cron.log 2>&1
```

- Windows 任务计划程序（每分钟）：
  - 程序: `pwsh`
  - 参数: `-NoProfile -File .github/automation/scripts/run-once.ps1`
  - 起始于: 仓库根目录

你也可以直接用命令行创建任务：

```powershell
schtasks /Create /SC MINUTE /MO 1 /TN "AI-Issue-AutoRunner" /TR "pwsh -NoProfile -File C:\\path\\to\\repo\\.github\\automation\\scripts\\run-once.ps1" /F
```

### 注意事项

- 本地执行器不会直接调用 VS Code UI，而是通过 `AUTOMATION_AGENT_COMMAND` 适配你已有的 AI 执行入口。
- 若命令失败，系统会自动在 Issue 下回写失败评论并打上 `ai-failed` 标签。
- 若没有产生代码变更，会回写“未检测到代码变更”的评论，不会创建空 PR。

### 团队 Skills 配置

团队可在 `.github/automation/skills/skills.yaml` 统一定义执行步骤命令模板，当前支持步骤：

- `run_agent`
- `quality_gate`
- `commit_and_push`

当某个步骤的 `command` 为空时，系统自动回退到内置实现，保证稳定性。

占位符说明见 `.github/automation/skills/README.md`。

默认模板基于 `skill_runner.py` 统一承载步骤执行逻辑，适合团队复用并降低个人脚本差异。

### 分支策略

```
main                   ← 生产环境，受保护分支
  └── develop          ← 开发主线（可选，小团队可省略）
        ├── feat/xxx   ← 功能分支（AI Agent 创建）
        ├── fix/xxx    ← 修复分支
        └── chore/xxx  ← 工程任务分支
```

**分支命名规范**（Copilot Agent 自动遵循）：
- `feat/{issue-number}-{short-description}`
- `fix/{issue-number}-{short-description}`
- `chore/{issue-number}-{short-description}`

### 版本发布

采用 [语义化版本](https://semver.org/lang/zh-CN/)：

```
MAJOR.MINOR.PATCH
  │      │     └── Bug 修复
  │      └──────── 新功能（向后兼容）
  └─────────────── 破坏性变更
```

发布触发方式：
```bash
# 创建版本标签即触发发布流水线
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0
```

---

## 团队协作规范

### 角色分工（10人以内团队）

| 角色 | 职责 | 与 AI 的协作方式 |
|-----|------|----------------|
| **Product Lead** | 产品方向、需求优先级 | 创建高质量 Issue，定义验收标准 |
| **Tech Lead** | 架构决策、技术规范 | 维护 `WORKFLOW.md` 和 `copilot-instructions.md` |
| **工程师（1-5人）** | 代码审查、复杂逻辑 | 审查 AI PR，处理需要深度专业知识的任务 |
| **QA（可选）** | 质量验证 | 完善测试用例，确保覆盖率 |

### 有效的 Issue 写作指南

AI 能否正确实现功能，很大程度上取决于 Issue 的质量：

✅ **好的 Issue**：
```markdown
## 用户故事
作为 API 用户，我希望能够通过 POST /chat/completions 发送多轮对话，
以便进行连续的对话交互。

## 验收标准
- [ ] 支持 messages 数组（包含 role 和 content 字段）
- [ ] 返回标准 OpenAI 兼容格式的响应
- [ ] 支持 stream=true 的流式响应
- [ ] 错误时返回正确的 HTTP 状态码和错误信息

## 技术规格
- 端点：POST /api/v1/chat/completions
- 认证：****** auth middleware）
- 测试：需要单元测试 + 集成测试（使用 httpx 异步测试）
```

❌ **不好的 Issue**：
```markdown
做一个聊天 API
```

### 代码审查清单

PR 审查时使用此清单：

- [ ] 功能逻辑正确，满足 Issue 中的所有验收标准
- [ ] 无明显安全漏洞（SQL 注入、XSS、路径遍历等）
- [ ] 测试覆盖核心逻辑（覆盖率 > 80%）
- [ ] 代码符合项目架构规范
- [ ] PR 描述清晰，包含变更摘要

---

## 常见问题

### Q: AI Agent 生成的代码质量如何保证？

A: 通过三层机制保障：
1. **规范约束**：`WORKFLOW.md` 和 `copilot-instructions.md` 定义了编码标准
2. **自动化测试**：CI 必须通过才能合并
3. **人工审查**：每个 PR 都需要工程师审查

### Q: AI Agent 是否会理解我们的业务逻辑？

A: AI Agent 通过以下方式理解项目上下文：
- 读取现有代码库结构
- 参考 `docs/architecture.md` 中的架构文档
- 遵循 `WORKFLOW.md` 中的项目规范
- 从 Issue 的描述中获取具体需求

因此，**高质量的文档和清晰的需求描述**是成功的关键。

### Q: 多个 AI Agent 并发执行会有冲突吗？

A: Automation Runner 通过隔离工作空间机制避免冲突：
- 每个 Issue 有独立的工作目录
- 每个 Agent 在独立分支上工作
- 合并冲突通过标准 Git 流程解决

### Q: 如何处理 AI 无法解决的复杂任务？

A: 建议策略：
1. 将复杂任务拆解为多个小 Issue
2. 在 Issue 中提供更详细的技术规格
3. 工程师先写接口定义和测试，再让 AI 实现
4. 对于核心算法或业务逻辑，由工程师实现后提交

### Q: 自动化流程是否原生支持 GitHub Issues？

A: 本仓库的 Automation Runner 原生支持 GitHub Issues 轮询与执行。可选方案：
1. 使用本模板的 `copilot-agent.yml` GitHub Actions 工作流直接触发 Copilot Agent
2. 使用本仓库 `.github/automation/` 的本地轮询执行器（Cron/任务计划程序）

---

## 参考资源

- [WORKFLOW.md](WORKFLOW.md) — 自动化流程与 Agent 提示模板
- [.github/automation/skills/README.md](.github/automation/skills/README.md) — 团队 Skills 配置说明
- [GitHub Copilot Coding Agent](https://docs.github.com/en/copilot/using-github-copilot/using-copilot-coding-agent) — 官方文档
- [Harness Engineering](https://openai.com/index/harness-engineering/) — OpenAI 工程实践
- [语义化版本控制](https://semver.org/lang/zh-CN/) — 版本管理规范

---

## 许可证

本模板基于 [Apache License 2.0](LICENSE) 开源。
