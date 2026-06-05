---
doc_id: ARCH-018
design_status: draft
issue_status: in-progress
issue_url: https://github.com/handsondad/agentic-ai-for-coding/issues/18
pr_url: TBD
owner: @unassigned
last_updated: 20260602
---

# 背景

- 没有在线指标就无法知道流程是否在变好。需要先把关键指标采起来，再做策略优化。
- 当前流程可运行，但缺少统一可观测指标，难以判断改动后是否真的提升了效率和质量。

# 目标与范围

## 目标

- 定义 KPI 字段和计算口径
- 增加执行日志到指标快照的抽取脚本
- 建立每周周报模板（Markdown）
- 在文档中明确指标查看方式

## 不在范围

- 不搭建复杂 BI 平台
- 不引入外部付费监控系统

# 设计与执行建议

- 建议领域: ARCH (architecture)
- 建议模板: 00-template/architecture-design-template.md
- 分类依据: 偏流程治理与架构编排
- 反向来源: .github/issues-backlog/task/20260602/setup-online-metrics-and-weekly-report.md

# 验收映射

- 定义并采集核心 KPI（成功率、一次通过率、Lead Time、返工率、门禁通过率）
- 输出每周指标快照文件
- 提供周报模板，包含趋势与Top阻塞原因
- 指标字段与失败分类结果可关联
