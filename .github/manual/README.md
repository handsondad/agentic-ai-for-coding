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

## 边界约定

- `.github/automation/` 仅用于 Celery 批处理自动化。
- `.github/manual/` 仅用于人工监督的单任务执行。
