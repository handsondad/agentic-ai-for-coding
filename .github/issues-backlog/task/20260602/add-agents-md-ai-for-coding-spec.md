---
title: 'docs: 新增 AGENTS.md 统一 AI for Coding 规范入口'
type: task
status: published
labels:
- task
- ai-ready
priority: P1
assignee: ''
milestone: ''
acceptance_criteria:
- 仓库根目录存在 AGENTS.md
- 文档可在 3-5 分钟内帮助新 agent 建立执行上下文
- 明确默认自动推进到 PR、用户仅最终审核
- 与现有规范不冲突（WORKFLOW.md、.github/copilot-instructions.md、.github/pull_request_template.md）
- PR 中说明该文档如何降低 agent 启动成本
ai_context: 该任务用于建立仓库级 AI for Coding 统一入口文档，降低任意 code agent 的冷启动成本，确保“读规范即可开干”。
related_docs:
- WORKFLOW.md
- .github/copilot-instructions.md
- .github/pull_request_template.md
- .github/automation/scripts/README.md
github_issue_number: '11'
github_issue_url: https://github.com/handsondad/agentic-ai-for-coding/issues/11
---

## 任务类型
🏗️ 基础设施 - AI for Coding 规范沉淀

## 背景与动机

当前仓库已有多处与 AI for Coding 相关的规范与流程（如 `WORKFLOW.md`、`.github/copilot-instructions.md`、`.github/pull_request_template.md`、自动化脚本与 issue 工作流约定），但分散在多个文件中。

为了让任意 code agent 进入仓库后能够在最短时间理解我们的协作方式，需要新增一个仓库根目录的 `AGENTS.md` 作为统一入口文档，覆盖：目标、默认执行流程、角色边界、质量门禁、PR 规范、阻塞处理、常用命令与关键文件索引。

## 目标

新增 `AGENTS.md`，让任何 code agent 打开仓库后可快速完成“读规范 -> 理解流程 -> 开始执行”。

## 任务范围

### 需要做
- 在仓库根目录新增 `AGENTS.md`
- 以“可执行规范”为导向组织内容，而非泛泛介绍
- 明确单 issue 模式与批量模式边界
- 明确默认自主流程（实现 -> 验证 -> commit -> push -> PR）与例外中断条件
- 明确 PR 描述必须完整填写模板
- 给出最小启动步骤与常用命令
- 提供关键文件导航（WORKFLOW、copilot-instructions、PR 模板、automation 脚本）
- 在 `README.md` 中增加到 `AGENTS.md` 的显式入口链接（如适用）

### 不在范围
- 不要求重构现有 automation 框架实现
- 不要求一次性改造所有历史文档结构

## 建议文档结构（AGENTS.md）
1. 我们在做什么（AI for Coding 的目标）
2. 角色与边界（用户/Agent 各自职责）
3. 默认执行流程（端到端）
4. 阻塞与升级机制（何时必须回到用户）
5. 代码与测试质量门禁
6. PR 规范（模板必填、测试说明要求）
7. 快速开始（5 分钟上手）
8. 关键文件索引

## 完成标准
- [ ] 仓库根目录存在 `AGENTS.md`
- [ ] 文档可在 3-5 分钟内帮助新 agent 建立执行上下文
- [ ] 明确“默认自动推进到 PR，用户仅最终审核”
- [ ] 与现有规范不冲突（`WORKFLOW.md`、`.github/copilot-instructions.md`、`.github/pull_request_template.md`）
- [ ] PR 中说明该文档如何降低 agent 启动成本

## 交付物
- `AGENTS.md`（主交付）
- 必要时的 README 链接更新

## 关联
- `WORKFLOW.md`
- `.github/copilot-instructions.md`
- `.github/pull_request_template.md`
- `.github/automation/scripts/*`
