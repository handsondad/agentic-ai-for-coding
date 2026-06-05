---
doc_id: BL-019
design_status: draft
issue_status: in-progress
issue_url: https://github.com/handsondad/agentic-ai-for-coding/issues/19
pr_url: TBD
owner: @unassigned
last_updated: 20260602
---

# 背景

- 目前失败信息以日志文本为主，难以快速复盘和趋势统计。标准化分类是评估体系与自动恢复策略的前提。
- 自动化流程失败时，如果只给原始日志，团队无法快速判断问题归属，也无法持续优化。 需要统一失败分类与修复建议输出规范，支持复盘与指标统计。

# 目标与范围

## 目标

- 定义失败分类枚举与判定规则
- 设计结构化失败输出格式（JSON/Markdown）
- 在 runner 关键失败路径接入分类逻辑
- 输出可直接贴入 issue/PR 的“失败闭环模板”
- 补充失败样本测试

## 不在范围

- 不做自动修复执行（仅输出建议）
- 不改动业务逻辑实现

# 设计与执行建议

- 建议领域: BL (business-logic)
- 建议模板: 00-template/business-logic-design-template.md
- 分类依据: 默认归类为业务逻辑域
- 反向来源: .github/issues-backlog/task/20260602/standardize-failure-classification-and-fix-hints.md

# 验收映射

- 定义统一失败分类（需求缺口/代码缺陷/环境阻塞/外部依赖）
- 每次失败输出必须包含失败步骤、关键错误、下一步建议
- 失败输出可用于 PR 描述或 issue 评论复用
- 至少覆盖 5 类典型失败样本并验证分类准确性
