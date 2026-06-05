---
doc_id: ARCH-015
design_status: draft
issue_status: in-progress
issue_url: https://github.com/handsondad/agentic-ai-for-coding/issues/15
pr_url: TBD
owner: @unassigned
last_updated: 20260602
---

# 背景

- 该任务用于让 agent 策略优化可量化、可回归，避免依赖主观感受调整流程。
- 当前优化更多依赖线上试错，缺少稳定的离线回放基线。需要建立评估集与回放机制，支持策略迭代前后量化对比。

# 目标与范围

## 目标

- 定义评估样本结构（issue 内容、预期输出、风险等级）
- 构建首批 20 条样本（feature/bug/task 覆盖）
- 实现回放脚本并输出标准报告
- 报告至少包含：成功率、平均时长、门禁通过率、失败分类分布

## 不在范围

- 不要求覆盖全部历史 issue
- 不做复杂可视化平台

# 设计与执行建议

- 建议领域: ARCH (architecture)
- 建议模板: 00-template/architecture-design-template.md
- 分类依据: 偏流程治理与架构编排
- 反向来源: .github/issues-backlog/task/20260602/build-offline-eval-dataset-and-replay.md

# 验收映射

- 建立不少于 20 条样本的离线评估集
- 提供一键回放脚本
- 输出评估报告（成功率、门禁通过率、失败分类）
- 支持策略变更前后对比
