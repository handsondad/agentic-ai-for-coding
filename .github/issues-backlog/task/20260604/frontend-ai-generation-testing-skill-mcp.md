---
title: 前端页面 AI 生成与自动化测试流程设计（Issue 构建规范 + Skill/MCP 增强）
type: task
status: published
labels:
- task
- ai-ready
priority: P2
assignee: ''
milestone: ''
acceptance_criteria:
- 输出一套前端任务 issue 模板，覆盖页面生成、测试、验收、回滚。
- 在仓库内提供最小可执行示例，能被 agent 按模板落地。
- 明确 Skill 与 MCP 的触发规则、职责边界和失败兜底策略。
ai_context: 该任务聚焦“如何让 AI 更稳定地产生可上线前端页面并完成自动化测试”，优先形成标准 issue 模板与执行约定。
related_docs:
- SPEC.md
- WORKFLOW.md
- .github/copilot-instructions.md
- .github/manual/README.md
github_issue_number: '20'
github_issue_url: https://github.com/handsondad/agentic-ai-for-coding/issues/20
---

## 背景与动机

当前前端需求在交给 AI 时，常出现“描述模糊 -> 产物风格不一致 -> 测试覆盖不足 -> 回归风险高”的问题。
需要把前端任务转成结构化 issue，让 agent 可按固定契约执行，并引入 Skill/MCP 提升稳定性。

## 任务范围

### 需要做
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

### 不在范围
- 不实现完整设计系统重构。
- 不绑定某一具体 UI 框架版本升级。

## 完成标准
- [ ] 新增并评审通过前端 issue 模板文档。
- [ ] 新增一份“前端 AI 协作约定”文档，包含示例输入与反例。
- [ ] 在示例任务中跑通测试命令并记录结果。
- [ ] 输出 Skill/MCP 接入建议矩阵（场景-能力-风险-兜底）。

## AI 上下文

- 前端设计任务应强调“视觉目标 + 交互验收 + 测试门禁”三段式输入。
- 任务默认要求可在桌面与移动端正常加载。
- 对 UI 质量要求高于通用脚手架默认样式。

## 关联文档

- SPEC.md
- WORKFLOW.md
- .github/copilot-instructions.md
- docs/dev-guide.md

---

## 任务类型

流程规范 + 模板建设 + 示例验证

## 技术说明（可选）

- 建议对接 Playwright 测试流水线。
- 若引用设计系统或组件库，需在 issue 中注明版本与约束。
