---
title: 脚手架引入 MCP/Skill 的标准方案与 Copilot 云端 Agent 可用性验证
type: task
status: published
labels:
- task
- ai-ready
priority: P2
assignee: ''
milestone: ''
acceptance_criteria:
- 明确 MCP 与 Skill 的引入路径、目录规范和版本策略。
- 完成 Copilot 云端 Agent 可用性验证清单与结论。
- 输出脚手架层面的最小集成示例与运维建议。
ai_context: 目标是把“工具扩展能力”标准化，而不是每次靠人工临时拼装。
related_docs:
- SPEC.md
- WORKFLOW.md
- .github/copilot-instructions.md
- AGENTS.md
github_issue_number: '21'
github_issue_url: https://github.com/handsondad/agentic-ai-for-coding/issues/21
---

## 背景与动机

当前项目已具备基础自动化流程，但 MCP/Skill 的接入方式、边界和云端兼容性缺少统一规范，影响可复制性和团队扩展。

## 任务范围

### 需要做
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

### 不在范围
- 不实现与业务系统深度耦合的专用 MCP。
- 不替代现有 manual/automation 主流程。

## 完成标准
- [ ] 输出 MCP/Skill 接入规范文档（包含示例目录结构）。
- [ ] 输出 Copilot 云端 Agent 兼容性测试报告。
- [ ] 给出“可用/受限/不可用”能力分级表。
- [ ] 给出脚手架默认推荐配置（含回退策略）。

## AI 上下文

- 该任务以“平台能力标准化”为核心。
- 强调从单人可用走向团队可复用。

## 关联文档

- SPEC.md
- AGENTS.md
- .github/manual/README.md
- .github/automation/README.md

---

## 任务类型

架构规范 + 能力验证 + 集成策略

## 技术说明（可选）

- 推荐以“本地 Agent / 云端 Agent”双场景对照验证。
- 每项验证需记录输入、执行路径、输出与失败原因。
