---
title: 多 Code Agent 接入与 Generic OpenAI-compatible 模型服务替代方案
type: task
status: published
labels:
- task
- ai-ready
priority: P2
assignee: ''
milestone: ''
acceptance_criteria:
- 输出多 Agent 接入对比矩阵（能力、成本、接入复杂度、限制）。
- 明确 Generic OpenAI-compatible 接口接入方案与配置模板。
- 完成至少一个替代链路的可执行 PoC。
ai_context: 目标是降低对单一商业 credits 的依赖，形成可持续的多 Agent + 自有模型服务策略。
related_docs:
- SPEC.md
- AGENTS.md
- docs/architecture.md
github_issue_number: '23'
github_issue_url: https://github.com/handsondad/agentic-ai-for-coding/issues/23
---

## 背景与动机

当前团队主要依赖 GitHub Copilot credits，成本与额度存在上限。需要评估并接入公司 Generic OpenAI-compatible 模型服务，同时建立多 Agent 备选能力。

## 任务范围

### 需要做
- 评估多 Agent 方案：
	- Copilot
	- Cline
	- Claude Code
	- OpenCode
	- DeepSeek TUI
	- Qoder
	- Trae
	- CodeBuddy
- 设计统一接入抽象：
	- 模型配置（base_url、api_key、model）
	- prompt/工具协议
	- 失败重试与降级
- 形成“默认主链路 + 备选链路”策略。
- 提供 PoC：在同一任务上可切换两个以上 agent 或模型端点。

### 不在范围
- 不重写现有核心业务逻辑。
- 不做所有 Agent 的深度定制插件开发。

## 完成标准
- [ ] 提交多 Agent 对比与选型报告。
- [ ] 提交 Generic OpenAI-compatible 配置与接入说明。
- [ ] 至少 1 条替代链路跑通并有结果记录。
- [ ] 输出推荐默认配置与治理建议（限额、审计、回退）。

## AI 上下文

- 重点关注成本、稳定性、可控性。
- 保持与现有 issue/worktree/quality gate 流程兼容。

## 关联文档

- AGENTS.md
- WORKFLOW.md
- docs/ai-coding-infra-executable-blueprint.md

---

## 任务类型

架构选型 + 平台集成 + 成本治理

## 技术说明（可选）

- 推荐定义统一环境变量契约，避免 agent 切换时修改业务代码。
