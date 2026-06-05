---
doc_id: ARCH-014
design_status: draft
issue_status: in-progress
issue_url: https://github.com/handsondad/agentic-ai-for-coding/issues/14
pr_url: TBD
owner: @unassigned
last_updated: 20260602
---

# 背景

- 该任务用于保证 PR 描述质量稳定，避免空白或占位文本进入审查流程。
- 已有 PR 模板，但仍可能出现章节缺失或仅保留占位文本的情况，影响审查效率与可追溯性。

# 目标与范围

## 目标

- 实现 PR 描述完整性检查器（脚本或 action）
- 校验至少包含：背景、变更摘要、变更详情、测试计划、审查重点
- 校验“测试计划”必须包含已执行或未执行说明
- 集成到 CI 并提供本地运行命令

## 不在范围

- 不校验业务内容正确性
- 不替代人工代码审查

# 设计与执行建议

- 建议领域: ARCH (architecture)
- 建议模板: 00-template/architecture-design-template.md
- 分类依据: 偏流程治理与架构编排
- 反向来源: .github/issues-backlog/task/20260602/add-pr-template-completeness-checker.md

# 验收映射

- PR 描述可自动检查模板完整性
- 未填写章节可在 CI 中失败提示
- 检查规则可配置且文档化
- 本地可先行执行同样检查
