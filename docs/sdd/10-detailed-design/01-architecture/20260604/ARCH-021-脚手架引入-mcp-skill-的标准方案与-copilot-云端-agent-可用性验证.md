---
doc_id: ARCH-021
design_status: draft
issue_status: in-progress
issue_url: https://github.com/handsondad/agentic-ai-for-coding/issues/21
pr_url: TBD
owner: @unassigned
last_updated: 20260604
---

# 背景

- 目标是把“工具扩展能力”标准化，而不是每次靠人工临时拼装。
- 当前项目已具备基础自动化流程，但 MCP/Skill 的接入方式、边界和云端兼容性缺少统一规范，影响可复制性和团队扩展。

# 目标与范围

## 目标

- 梳理脚手架内 MCP 与 Skill 的接入点：
- 配置位置
- 启用方式
- 权限边界
- 失败降级策略
- 建立“工具接入规范”：命名、版本、目录、文档要求、变更评审要求。
- 验证 GitHub Copilot 云端 Agent 下的可用性：
- 是否可加载本地/仓库级指令
- Skill 触发稳定性
- MCP 能力是否受限
- 远端运行的依赖前置条件
- 提供一个可复用的示例配置与验证步骤。

## 不在范围

- 不实现与业务系统深度耦合的专用 MCP。
- 不替代现有 manual/automation 主流程。

# 设计与执行建议

- 建议领域: ARCH (architecture)
- 建议模板: 00-template/architecture-design-template.md
- 分类依据: 偏流程治理与架构编排
- 反向来源: .github/issues-backlog/task/20260604/scaffold-tooling-mcp-skill-copilot-cloud.md

# 验收映射

- 明确 MCP 与 Skill 的引入路径、目录规范和版本策略。
- 完成 Copilot 云端 Agent 可用性验证清单与结论。
- 输出脚手架层面的最小集成示例与运维建议。
