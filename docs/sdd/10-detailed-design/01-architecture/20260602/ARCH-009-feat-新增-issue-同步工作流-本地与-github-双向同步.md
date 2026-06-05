---
doc_id: ARCH-009
design_status: draft
issue_status: in-progress
issue_url: https://github.com/handsondad/agentic-ai-for-coding/issues/9
pr_url: TBD
owner: @unassigned
last_updated: 20260602
---

# 背景

- 目标是把 issue 生命周期管理标准化，减少手工在本地文档与 GitHub 之间搬运信息的成本。优先实现可落地的同步闭环和幂等保障，再逐步扩展批量能力。
- 当前团队会在本地 backlog 维护任务草稿，再手工发布到 GitHub。手工流程容易出现重复创建、状态不一致和链接缺失，影响自动化执行与团队协作。

# 目标与范围

## 目标

- 设计并实现 issue 同步工作流（本地 -> GitHub、GitHub -> 本地）
- 明确同步触发方式（手动命令、定时任务或事件驱动）
- 定义状态映射规则（draft/ready/published 与 GitHub open/closed）
- 提供去重机制，避免重复创建同一任务
- 输出最小可用的同步操作文档和示例

## 不在范围

- 不要求在本任务中接入复杂权限系统
- 不要求一次性覆盖所有历史 backlog 文件的数据修复
- 不要求实现跨仓库同步

# 设计与执行建议

- 建议领域: ARCH (architecture)
- 建议模板: 00-template/architecture-design-template.md
- 分类依据: 偏流程治理与架构编排
- 反向来源: .github/issues-backlog/feature/20260602/add-issue-sync-workflow.md

# 验收映射

- 支持从本地 backlog 文件创建或更新 GitHub Issue
- 支持从 GitHub Issue 状态回写本地文件状态字段
- 提供可重复执行的同步命令，幂等且不会重复创建同标题 issue
- 发生冲突时有明确策略（例如以本地为准/以远端为准）和可追踪日志
- README 补充同步流程、前置条件与常见故障排查
