# 手动模式说明

本目录用于人工监督的一次一任务流程，不依赖批处理调度。

当你希望人工逐步介入、按任务单独推进时，使用该模式。

## 脚本清单

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

1. 先执行 `prepare-single-issue` 准备工作区和 prompt。
2. 在 worktree 中完成代码实现。
3. 提交前强制执行质量门禁：
   - Windows: `pwsh .github/manual/scripts/run-quality-gate.ps1 -Mode full`
   - Linux/macOS: `sh .github/manual/scripts/run-quality-gate.sh --mode full`
4. 通过后再执行 commit / push / PR。

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
