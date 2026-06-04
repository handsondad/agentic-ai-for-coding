# 自动化模式说明

本目录用于无人值守或低干预的批处理执行，核心为 Celery dispatcher + worker。

## 职责

- 持续轮询并筛选可执行 Issue（例如 ai-ready）。
- 按依赖关系分层调度任务并下发到队列。
- 在隔离 worktree 中执行流水线（Agent、质量门禁、提交、PR）。
- 记录执行指标与失败分类，便于回溯与周报汇总。
- 在批量调度前识别更新：仅当 issue 内容更新或基线分支有新提交时才重新投递。
- 在提交前执行严格质量门禁（Ruff format/lint、mypy、pytest），失败即中断流程。

## 关键目录

- `scripts/`
  - 自动化运行入口与运维脚本。
- `celery_dispatcher.py`
  - 调度器，负责拉取任务并投递到队列。
- `celery_tasks.py`
  - Worker 任务实现，负责单 Issue 执行。

## 使用边界

- 本目录只放自动化脚本与运行时组件。
- 人工单任务脚本统一放在 `.github/manual/scripts/`。
- 不在 automation 目录中保留手工模式辅助脚本。

## 更新识别

- 调度器会将最近一次投递状态写入 `.automation/dispatch-state.json`。
- 若目标 issue 的 `updated_at` 变化，或 `origin/<base_branch>` 头提交变化，则判定为有更新并重新执行。
- 若无更新，则本轮跳过该 issue，避免重复消耗。
