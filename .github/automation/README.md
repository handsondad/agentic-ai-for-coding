# 自动化模式说明

本目录用于无人值守或低干预的批处理执行，核心为 Celery Dispatcher + Worker。

目标是把「Issue 发现 -> 分层调度 -> 代码实现 -> 本地质量把关 -> 提交与 PR」串成一条可重复、可追溯的流水线。

## 设计目标

- 降低人工轮询与分派成本，持续消费 `ai-ready` 任务。
- 通过依赖分层避免并发任务的顺序冲突。
- 在本地先完成严格质量门禁，减少 PR 后被 CI 打回。
- 对执行结果进行结构化留痕，便于复盘与周报。

## 架构与职责

- `celery_dispatcher.py`
  - 拉取候选 Issue。
  - 基于 `Depends on: #123` 构建依赖层。
  - 只调度“有更新”的任务（见“更新识别机制”）。
  - 将任务投递到 Celery 队列。

- `celery_tasks.py`
  - Worker 进程中的单 Issue 任务入口。
  - 调用执行器完成代码、门禁、提交、PR。
  - 回写 Issue 标签/评论与执行指标。

- `executor.py`
  - 处理 worktree 准备、prompt 渲染、Agent 命令执行。
  - 执行质量门禁并在失败时中断。
  - 负责 commit/push/PR 创建。

- `workflow.py`
  - 从 `WORKFLOW.md` 与环境变量加载运行时配置。
  - 默认质量门禁为严格模式。

- `scripts/`
  - 提供启动/运维脚本（run-once、run-forever、worker/dispatch 启动、质量门禁等）。

## 执行流程

1. Dispatcher 轮询 GitHub Issue，筛选 `ai-ready`。
2. Dispatcher 做更新检测，只投递“有变化”的 Issue。
3. Worker 取任务后准备独立 worktree，并拉取基线分支最新提交。
4. Worker 执行 Agent 与严格质量门禁。
5. 通过后提交并推送分支，创建或复用 PR。
6. 回写标签、评论、失败分类和指标事件。

## 启动方式

### Dispatcher

- 单次调度（适配 Cron/任务计划）：
  - Windows: `pwsh .github/automation/scripts/run-once.ps1`
  - Linux/macOS: `sh .github/automation/scripts/run-once.sh`
- 常驻调度：
  - Windows: `pwsh .github/automation/scripts/run-forever.ps1`
  - Linux/macOS: `sh .github/automation/scripts/run-forever.sh`

### Worker

- Windows: `pwsh .github/automation/scripts/run-celery-worker.ps1`
- Linux/macOS: `sh .github/automation/scripts/run-celery-worker.sh`

### 仅调度进程（不含 worker）

- Windows: `pwsh .github/automation/scripts/run-celery-dispatch.ps1`
- Linux/macOS: `sh .github/automation/scripts/run-celery-dispatch.sh`

## 更新识别机制

- 调度器状态文件：`.automation/dispatch-state.json`。
- 判定“需要重跑”的条件：
  - Issue 的 `updated_at` 发生变化。
  - `origin/<base_branch>` 头提交发生变化。
- 若两者都无变化，则跳过该 Issue，减少重复执行。

## Git 基线同步策略

- 新任务启动时会先 `fetch origin/<base_branch>` 再准备 worktree。
- 默认始终使用远端最新基线创建/重置 issue 分支。
- 若设置 `AUTOMATION_SKIP_GIT_FETCH=true`，会跳过 fetch（仅排障建议）。

## 质量门禁策略

- 默认严格门禁命令：
  - `python .github/automation/scripts/quality-gate.py --mode full`
- `full` 模式包含：
  - Ruff format check
  - Ruff lint
  - mypy
  - unit tests
  - integration tests
- 任一步失败即中断，不进入 commit/push/PR。

## 环境变量说明

### 公共变量（automation/manual 都会用到）

- `GITHUB_TOKEN`
  - 选填。用于 `gh` 非交互认证；若本机已 `gh auth login` 可不设置。
- `GITHUB_REPOSITORY`
  - 必填。格式 `owner/repo`。
- `GITHUB_BASE_BRANCH`
  - 可选。默认 `main`。

### 自动化模式专属变量

- `AUTOMATION_AGENT_COMMAND`
  - 必填。Agent 执行命令模板。
- `AUTOMATION_ADAPTER_BACKEND_COMMAND`
  - 推荐配置。适配器实际调用的后端命令。
- `AUTOMATION_QUALITY_COMMANDS`
  - 可选。覆盖默认质量门禁，多个命令用 `;;` 分隔。
- `AUTOMATION_WORKSPACE_ROOT`
  - 可选。worktree 根目录。
- `AUTOMATION_REPO_ROOT`
  - 可选。仓库根目录覆盖。
- `AUTOMATION_METRICS_FILE`
  - 可选。执行指标文件路径。
- `AUTOMATION_DRY_RUN`
  - 可选。开启后只演练不落地。
- `AUTOMATION_SKIP_GIT_FETCH`
  - 可选。跳过 fetch（仅排障时使用）。
- `AUTOMATION_SKIP_GIT_PUSH`
  - 可选。跳过 push（仅排障时使用）。
- `AUTOMATION_HOOKS_STRICT`
  - 可选。hook 失败时是否强制中断。
- `AUTOMATION_WINDOWS_SHELL`
  - 可选。Windows 下强制 shell 类型（如 powershell/bash）。
- `AUTOMATION_BASH_EXE`
  - 可选。Windows 下自定义 bash 可执行路径。
- `AUTOMATION_CELERY_BROKER_URL`
  - 可选。Celery broker 地址。
- `AUTOMATION_CELERY_RESULT_BACKEND`
  - 可选。Celery result backend 地址。
- `AUTOMATION_CELERY_QUEUE`
  - 可选。Celery 队列名。

## 运行产物

- 调度状态：`.automation/dispatch-state.json`
- 执行指标事件流：`.automation/execution-metrics.jsonl`
- 质量门禁报告：`.automation/quality-gate-report.json`
- 质量门禁摘要：`.automation/quality-gate-summary.md`

## 失败处理与回写

- 流程失败时会回写 Issue 评论，并打上 `ai-failed` 标签。
- 成功且有代码变更时会回写 PR 链接，并打上 `human-review` 标签。
- 无代码变更时会回写“未检测到代码变更”，并跳过 PR 创建。

## 运维建议

- 首次部署建议先跑一次单次调度（run-once）验证配置。
- Worker 与 Dispatcher 建议分开终端/服务进程运行。
- 若出现重复调度，优先检查 `dispatch-state.json` 与基线分支更新记录。
- 若企业网络下遇到 GitHub 访问问题，优先确认 `gh auth status` 和代理配置。

## 快速配置示例（PowerShell）

```powershell
[Environment]::SetEnvironmentVariable("GITHUB_TOKEN", "<token>", "User")
[Environment]::SetEnvironmentVariable("GITHUB_REPOSITORY", "owner/repo", "User")
[Environment]::SetEnvironmentVariable("GITHUB_BASE_BRANCH", "main", "User")
[Environment]::SetEnvironmentVariable("AUTOMATION_QUALITY_COMMANDS", "python .github/automation/scripts/quality-gate.py --mode full", "User")
```

## 使用边界

- 本目录只放自动化脚本与运行时组件。
- 人工单任务脚本统一放在 `.github/manual/scripts/`。
- 不在 automation 目录中保留手工模式辅助脚本。