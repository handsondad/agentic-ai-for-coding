---
doc_id: UI-001
design_status: draft
issue_status: created
issue_url: https://github.com/handsondad/agentic-ai-for-coding/issues/30
pr_url: TBD
owner: @unassigned
last_updated: 20260605
---

# 背景

当前 automate 与 manual 运行日志分散在不同路径与执行入口，排查问题时需要频繁切换上下文，效率低且难以形成统一审计视图。

# 目标与范围

## 目标

- 提供一个统一页面，聚合 automate 与 manual 两类运行日志。
- 支持按时间、模式、状态、issue 编号、分支、执行器进行过滤与检索。
- 支持单条运行详情查看、跨模式对比和失败定位。
- 支持从页面直接跳转到关联日志文件、issue、PR、worktree 路径。

## 不在范围

- 不在本设计中实现日志采集 Agent 重构。
- 不在本设计中实现跨仓库日志汇总。
- 不在本设计中实现权限系统与多租户隔离。

# 交互与状态设计

## 页面结构

- 顶部统计区：今日运行数、成功率、失败率、平均耗时、重试率。
- 左侧筛选区：
- 运行模式（automate/manual）
- 时间范围
- 状态（success/failed/running/cancelled）
- issue 编号
- 分支名
- 关键词全文检索
- 中间列表区：运行记录表格（支持排序和分页）。
- 右侧详情区：选中运行的完整上下文与时间线。

## 交互流程

- 用户进入页面后默认展示最近 24 小时全部运行记录。
- 用户可通过筛选器收敛范围，列表实时更新。
- 点击任一运行记录后，右侧展示：
- 基本信息（mode、issue、branch、trigger、开始结束时间）
- 阶段时间线（prepare、implement、test、gate、pr）
- 错误摘要与修复建议（若失败）
- 关联链接（日志文件、issue、PR、worktree）
- 用户可勾选两条记录执行 diff 对比（常见于 automate vs manual）。

## 前端状态

- 加载态：骨架屏 + 最近更新时间提示。
- 空态：展示无结果说明及推荐筛选项。
- 错误态：展示请求失败原因与重试按钮。
- 增量刷新态：每 10-30 秒轮询或手动刷新，避免页面闪烁。

# 数据模型建议

- run_id
- mode: automate | manual
- issue_number
- branch
- status
- started_at
- finished_at
- duration_ms
- summary
- error_type
- error_message
- log_path
- issue_url
- pr_url
- worktree_path

# 验收标准

- [ ] 页面能同时展示 automate 与 manual 两类日志。
- [ ] 支持多维筛选、排序、分页和关键词检索。
- [ ] 支持查看单条运行详情与失败定位信息。
- [ ] 支持至少一组跨模式运行记录对比。
- [ ] 页面中的 issue/pr/log/worktree 链接可直接跳转。
