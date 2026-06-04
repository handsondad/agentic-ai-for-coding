# 手动模式说明

本目录用于人工监督的一次一任务流程，不依赖批处理调度。

当你希望人工逐步介入、按任务单独推进时，使用该模式。

## 脚本清单

- `scripts/start-backlog-issue.py|.ps1|.sh`
  - 创建 backlog 前置流程入口。
  - 自动执行：同步基线分支 -> 创建独立 backlog 分支 -> 生成本地 backlog 草稿文件。
  - 默认分支命名：`backlog/<type>-YYYYMMDD-<slug>`。

- `scripts/prepare-single-issue.py|.ps1|.sh`
  - 准备单个 Issue 的工作区，并生成 `.manual/issue-prompt.md`。
  - 不轮询队列，不执行批量编排。

- `scripts/publish-backlog-issue.py|.ps1|.sh`
  - 将本地 backlog Markdown 发布为 GitHub Issue。
  - 自动回填本地 front matter 的 issue 编号与 URL。

- `scripts/run-quality-gate.py|.ps1|.sh`
  - 手动模式下的本地质量门禁入口。
  - 默认执行严格检查（`full`）：Ruff 格式检查、Ruff Lint、mypy、unit test、integration test。

## 推荐流程（手动模式）

1. 先执行 `start-backlog-issue`，基于最新 `main` 创建独立 backlog 分支。
2. 在该分支完善 `.github/issues-backlog/` 草稿并将状态改为 `ready`。
3. 执行 `publish-backlog-issue` 发布到 GitHub，并自动回填本地元数据。
4. 再执行 `prepare-single-issue` 准备实现 worktree 和 prompt。
5. 在 worktree 中完成代码实现。
6. 提交前强制执行质量门禁：
   - Windows: `pwsh .github/manual/scripts/run-quality-gate.ps1 -Mode full`
   - Linux/macOS: `sh .github/manual/scripts/run-quality-gate.sh --mode full`
7. 通过后再执行 commit / push / PR。

## 常用命令

### 1) backlog 分支化创建（推荐）

- Windows:
  - `pwsh .github/manual/scripts/start-backlog-issue.ps1 -Type task -Title "优化 issue 创建流程"`
- Linux/macOS:
  - `sh .github/manual/scripts/start-backlog-issue.sh --type task --title "优化 issue 创建流程"`

### 2) backlog 发布到 GitHub Issue

- Windows:
  - `pwsh .github/manual/scripts/publish-backlog-issue.ps1 .github/issues-backlog/task/20260604/optimize-issue-creation-flow.md`
- Linux/macOS:
  - `sh .github/manual/scripts/publish-backlog-issue.sh .github/issues-backlog/task/20260604/optimize-issue-creation-flow.md`

### 3) 单 issue 准备 + 质量门禁

- Windows:
  - `pwsh .github/manual/scripts/prepare-single-issue.ps1 -IssueNumber 12`
  - `pwsh .github/manual/scripts/run-quality-gate.ps1 -Mode full`
- Linux/macOS:
  - `sh .github/manual/scripts/prepare-single-issue.sh --issue-number 12`
  - `sh .github/manual/scripts/run-quality-gate.sh --mode full`

## 环境变量说明

### 公共变量（automation/manual 都会用到）

- `GITHUB_TOKEN`
  - 必填。访问 GitHub API 所需令牌。
- `GITHUB_REPOSITORY`
  - 必填。格式 `owner/repo`。
- `GITHUB_BASE_BRANCH`
  - 可选。默认 `main`，用于准备 worktree 时的基线分支。

### 手动模式专属变量

- `MANUAL_REPO_ROOT`
  - 可选。手动脚本运行时的仓库根目录覆盖。
- `MANUAL_WORKSPACE_ROOT`
  - 可选。单 issue worktree 的输出目录覆盖。

## 运行产物

- backlog 草稿：`.github/issues-backlog/<type>/YYYYMMDD/<slug>.md`
- 单 issue prompt：`<worktree>/.manual/issue-prompt.md`

## 建议约束

- 发布 backlog 前，建议先提交 backlog 分支，确保提单改动可追溯。
- 若脚本提示工作区不干净，优先提交或暂存后再创建 backlog 分支。
- 若你明确需要在当前未提交改动基础上继续，可显式传入：
  - PowerShell: `pwsh .github/manual/scripts/start-backlog-issue.ps1 -Type task -Title "..." -AllowDirty`
  - Python: `python .github/manual/scripts/start-backlog-issue.py --type task --title "..." --allow-dirty`
- `--dry-run` 可用于预览分支名和文件路径，不会修改 git 状态。

## 无 Issue 阻断策略

为避免“先改代码再补 Issue”的流程违规，手动质量门禁已内置阻断检查：

- 必须在 `ai/issue-*` 分支执行。
- 当前目录必须存在 `.manual/issue-prompt.md`（说明已完成 issue 准备）。
- 不满足时直接中断，并提示先走 `start-backlog-issue -> publish-backlog-issue -> prepare-single-issue`。

仅排障时可临时绕过（不建议常态使用）：

```powershell
$env:MANUAL_ALLOW_NO_ISSUE = "true"
```

## 快速配置示例（PowerShell）

```powershell
[Environment]::SetEnvironmentVariable("GITHUB_TOKEN", "<token>", "User")
[Environment]::SetEnvironmentVariable("GITHUB_REPOSITORY", "owner/repo", "User")
[Environment]::SetEnvironmentVariable("GITHUB_BASE_BRANCH", "main", "User")
[Environment]::SetEnvironmentVariable("MANUAL_WORKSPACE_ROOT", "C:\\Xiuqin\\code\\agentic-ai-for-coding\\.worktrees", "User")
```

## 边界约定

- `.github/automation/` 仅用于 Celery 批处理自动化。
- `.github/manual/` 仅用于人工监督的单任务执行。