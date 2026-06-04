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

## 边界约定

- `.github/automation/` 仅用于 Celery 批处理自动化。
- `.github/manual/` 仅用于人工监督的单任务执行。
