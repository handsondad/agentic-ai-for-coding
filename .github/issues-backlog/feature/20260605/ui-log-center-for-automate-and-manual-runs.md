---
title: 'feat: 新增统一运行日志管理页面（automate/manual）'
type: feature
status: published
labels:
- feature
- ui
- observability
- ai-ready
priority: P1
assignee: ''
milestone: ''
acceptance_criteria:
- 页面可统一展示 automate 与 manual 两类运行日志。
- 支持按时间、模式、状态、issue 编号、分支和关键词筛选。
- 支持单条运行详情查看，并展示阶段时间线与错误摘要。
- 支持至少一组 automate/manual 运行记录对比。
- 支持跳转到关联 issue、PR、日志文件和 worktree 路径。
ai_context: 该需求来自 SDD 文档 UI-001，目标是先完成日志管理可视化闭环，降低排障与审计成本，再逐步扩展告警和治理能力。
related_docs:
- docs/sdd/README.md
- docs/sdd/sdd-index.md
- docs/sdd/10-detailed-design/02-ui-frontend/20260605/UI-001-unified-automation-manual-log-management.md
github_issue_number: '30'
github_issue_url: https://github.com/handsondad/agentic-ai-for-coding/issues/30
---

## 背景与动机

目前 automate 与 manual 运行日志分散在不同入口和路径，定位问题需要频繁切换上下文，导致排障效率低、状态追踪不连续。

本需求希望通过统一日志管理页面，把运行态信息、失败定位信息和关联链接聚合在同一视图中，提升团队对执行质量的可观测性。

## 任务范围

### 需要做
- 新增统一页面，聚合 automate 与 manual 两类运行日志。
- 提供多维筛选（时间/模式/状态/issue/分支/关键词）。
- 提供运行详情面板（基本信息、阶段时间线、错误摘要、修复建议）。
- 提供运行记录对比能力（至少支持两条记录对比）。
- 提供跳转能力（issue、PR、日志文件、worktree）。

### 不在范围
- 不在本任务中重构日志采集 Agent。
- 不在本任务中实现跨仓库日志汇总。
- 不在本任务中实现权限系统与多租户隔离。

## 完成标准
- [ ] 页面可同时展示 automate/manual 两类运行日志。
- [ ] 多维筛选、排序、分页、关键词检索可用。
- [ ] 单条运行详情可查看阶段时间线与失败摘要。
- [ ] 至少支持一组跨模式运行记录对比。
- [ ] issue/pr/log/worktree 跳转链路可用。

## AI 上下文

优先实现“可视化管理闭环”，先保证查询、详情、对比、跳转四项核心能力。扩展能力（告警、智能归因）放后续 issue。

## 关联文档
- docs/sdd/10-detailed-design/02-ui-frontend/20260605/UI-001-unified-automation-manual-log-management.md
- docs/sdd/sdd-index.md

---

## 类型化正文（feature）

### 用户故事
作为自动化平台维护者，我希望在一个页面统一查看 automate 与 manual 的运行日志，以便快速排障、对比差异并追踪执行质量。

### 验收标准
- [ ] 满足 front matter 中 acceptance_criteria

### 技术规格（可选）
- 日志列表支持分页与服务端筛选。
- 详情面板支持阶段时间线与错误分类展示。
- 记录对比支持字段级差异展示（模式、耗时、状态、错误摘要）。

### 背景与上下文
- SDD Doc: docs/sdd/10-detailed-design/02-ui-frontend/20260605/UI-001-unified-automation-manual-log-management.md
- SDD Doc ID: UI-001
