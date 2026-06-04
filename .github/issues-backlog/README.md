# Issues Backlog 管理约定

该目录用于存放“尚未发布到 GitHub 的 Issue 草稿”，作为 AI/人工协作的统一输入池。

## 1) 目录结构

```text
.github/issues-backlog/
├── README.md
├── TEMPLATE.md
├── feature/
│   └── YYYYMMDD/
├── bug/
│   └── YYYYMMDD/
└── task/
  └── YYYYMMDD/
```

- `feature/`：功能需求类 backlog
- `bug/`：缺陷修复类 backlog
- `task/`：工程任务类 backlog

## 2) 命名规则

- 使用“按天子目录”组织：`.github/issues-backlog/<type>/YYYYMMDD/<short-title>.md`
- 文件名不再重复日期前缀，仅保留语义化短标题
- 示例：`.github/issues-backlog/feature/20260602/add-streaming-chat.md`

## 3) 元数据（文件头）

每个 backlog 文件必须包含 YAML Front Matter，最少包含：

- `title`（标题）
- `type`（feature/bug/task）
- `status`（draft/ready/published）
- `labels`（标签数组）
- `priority`（优先级）
- `assignee`（负责人，可为空）
- `acceptance_criteria`（验收标准数组）
- `ai_context`（AI 上下文）
- `related_docs`（关联文档数组）

发布后补充：

- `github_issue_number`
- `github_issue_url`

## 4) 状态流转

- `draft`：AI/人工初稿，可继续补充
- `ready`：信息完整，可发布到 GitHub
- `published`：已发布到 GitHub，且已回写编号与链接

只允许：`draft -> ready -> published`。

## 5) 发布流程（单条）

在发布前，建议先走“分支化创建”流程，确保 backlog 的本地改动可追溯：

1. 同步 `main` 并创建独立 backlog 分支
2. 在分支中创建/编辑 backlog 草稿
3. 草稿达到 `ready` 后再发布到 GitHub

推荐分支命名：

- `backlog/<type>-YYYYMMDD-<slug>`
- 示例：`backlog/task-20260604-optimize-issue-creation-flow`

推荐命令（Windows PowerShell）：

```powershell
pwsh .github/manual/scripts/start-backlog-issue.ps1 -Type task -Title "优化 issue 创建流程"
```

推荐命令（Linux/macOS）：

```bash
sh .github/manual/scripts/start-backlog-issue.sh --type task --title "优化 issue 创建流程"
```

然后再执行发布：

1. 从 backlog 中选择 `status: ready` 的文件
2. 使用自动发布脚本创建 GitHub Issue 并自动回填本地元数据

推荐命令（Windows PowerShell）：

```powershell
pwsh .github/manual/scripts/publish-backlog-issue.ps1 \
  .github/issues-backlog/task/20260602/validate-automation-runner-e2e.md
```

推荐命令（Linux/macOS）：

```bash
sh .github/manual/scripts/publish-backlog-issue.sh \
  .github/issues-backlog/task/20260602/validate-automation-runner-e2e.md
```

发布成功后会自动回填：

- `status: published`
- `github_issue_number`
- `github_issue_url`

## 6) 批量发布约定

一次批量发布仅允许同一组任务：

- 同一优先级，或
- 同一里程碑

避免一次性创建大量低质量 Issue。

## 7) 质量门禁（进入 ready 前必须满足）

必须完整填写以下信息：

- 背景
- 范围
- 完成标准
- 优先级
- 标签

任一缺失，保持 `draft`。

## 8) 维护机制

- 每周清理过期 `draft`
- 每个迭代结束时核对 `published` 与 GitHub Issue 实际状态
- 发现不一致时立即回写修正

