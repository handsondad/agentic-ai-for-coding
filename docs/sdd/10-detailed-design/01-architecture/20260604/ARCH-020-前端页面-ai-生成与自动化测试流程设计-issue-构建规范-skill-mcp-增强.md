---
doc_id: ARCH-020
design_status: draft
issue_status: in-progress
issue_url: https://github.com/handsondad/agentic-ai-for-coding/issues/20
pr_url: TBD
owner: @unassigned
last_updated: 20260604
---

# 背景

- 该任务聚焦“如何让 AI 更稳定地产生可上线前端页面并完成自动化测试”，优先形成标准 issue 模板与执行约定。
- 当前前端需求在交给 AI 时，常出现“描述模糊 -> 产物风格不一致 -> 测试覆盖不足 -> 回归风险高”的问题。 需要把前端任务转成结构化 issue，让 agent 可按固定契约执行，并引入 Skill/MCP 提升稳定性。

# 目标与范围

## 目标

- 设计前端类 issue 模板（页面型、组件型、重构型），至少包含：
- 页面目标与视觉方向
- 信息架构与交互要求
- 响应式与可访问性约束
- 测试策略（单测/组件测试/E2E）
- 性能与发布验收门槛
- 产出“前端 AI 任务描述指南”，明确怎么写 prompt 才能减少返工。
- 给出 Skill/MCP 增强建议：
- Skill 负责风格和流程约束
- MCP 负责外部系统能力（设计稿、测试平台、部署环境）
- 给出一个最小示例：从 issue 到页面生成、测试通过、可 PR 的完整链路。

## 不在范围

- 不实现完整设计系统重构。
- 不绑定某一具体 UI 框架版本升级。

# 设计与执行建议

- 建议领域: ARCH (architecture)
- 建议模板: 00-template/architecture-design-template.md
- 分类依据: 偏流程治理与架构编排
- 反向来源: .github/issues-backlog/task/20260604/frontend-ai-generation-testing-skill-mcp.md

# 验收映射

- 输出一套前端任务 issue 模板，覆盖页面生成、测试、验收、回滚。
- 在仓库内提供最小可执行示例，能被 agent 按模板落地。
- 明确 Skill 与 MCP 的触发规则、职责边界和失败兜底策略。
