---
doc_id: ARCH-023
design_status: draft
issue_status: in-progress
issue_url: https://github.com/handsondad/agentic-ai-for-coding/issues/23
pr_url: TBD
owner: @unassigned
last_updated: 20260604
---

# 背景

- 目标是降低对单一商业 credits 的依赖，形成可持续的多 Agent + 自有模型服务策略。
- 当前团队主要依赖 GitHub Copilot credits，成本与额度存在上限。需要评估并接入公司 Generic OpenAI-compatible 模型服务，同时建立多 Agent 备选能力。

# 目标与范围

## 目标

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

## 不在范围

- 不重写现有核心业务逻辑。
- 不做所有 Agent 的深度定制插件开发。

# 设计与执行建议

- 建议领域: ARCH (architecture)
- 建议模板: 00-template/architecture-design-template.md
- 分类依据: 偏流程治理与架构编排
- 反向来源: .github/issues-backlog/task/20260604/multi-agent-openai-compatible-integration.md

# 验收映射

- 输出多 Agent 接入对比矩阵（能力、成本、接入复杂度、限制）。
- 明确 Generic OpenAI-compatible 接口接入方案与配置模板。
- 完成至少一个替代链路的可执行 PoC。
