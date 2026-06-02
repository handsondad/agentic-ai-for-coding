---
title: 'chore: 验证 automation runner 可端到端处理 GitHub Issue'
type: task
status: published
labels:
- task
- ai-ready
priority: P1
assignee: ''
milestone: ''
acceptance_criteria:
- 可以从 GitHub Issues 轮询到带有 ai-ready 标签的任务
- 可以为目标任务创建独立 worktree 并渲染 issue prompt
- 可以执行 agent command、质量门禁和 commit/push 流程
- 可以在成功路径上创建 PR 或输出明确的阻塞信息
- 整个试跑过程有可追踪日志，便于团队复盘
ai_context: 该任务用于验证本仓库 .github/automation 下的本地自动化框架是否具备真实可用性。优先验证单条 issue 的端到端链路，不要求一次性覆盖多并发、复杂重试或全部异常场景。
related_docs:
- WORKFLOW.md
- README.md
- .github/automation/skills/README.md
github_issue_number: '7'
github_issue_url: https://github.com/handsondad/agentic-ai-for-coding/issues/7
---

## 背景与动机

当前仓库已经具备本地自动化执行框架，包括：Issue 轮询、worktree 创建、prompt 渲染、skills、质量门禁、提交与 PR 流程。

在团队正式使用前，需要先通过一条真实 GitHub Issue 验证这条链路能否跑通，并明确最小可用配置、已知阻塞点和后续补强项。

## 任务范围

### 需要做
- 使用一条真实的 GitHub Issue 触发本地自动化流程
- 验证 `ai-ready` 标签任务是否能被正确发现
- 验证 `.github/automation/` 下脚本和配置能否驱动完整执行链路
- 验证 worktree、prompt、skills、quality gate、commit/push、PR 创建等关键步骤
- 记录试跑结果、日志、阻塞点与改进建议

### 不在范围
- 不要求一次性验证所有失败恢复分支
- 不要求覆盖多任务并发场景
- 不要求在本任务中重构自动化框架核心设计

## 完成标准
- [ ] 创建一条真实 GitHub Issue 用于试跑
- [ ] 本地自动化执行器可以识别并开始处理该 Issue
- [ ] 至少完成到以下两种结果之一：
  - [ ] 成功创建 PR
  - [ ] 在明确步骤上失败，并能给出可执行的修复建议
- [ ] 输出一份试跑记录，包含运行命令、日志摘要、结果判断与下一步建议

## AI 上下文

请优先把该任务当作“自动化框架验收任务”而不是普通业务需求处理：
- 目标不是交付某个业务功能，而是验证自动化框架本身是否可用
- 如果运行失败，优先定位最小阻塞点
- 需要给出可复现步骤，便于团队后续重复演练

## 关联文档
- WORKFLOW.md
- README.md
- .github/automation/skills/README.md

---

## 类型化正文（按 type 选择并完善）

### task 结构（对齐 `.github/ISSUE_TEMPLATE/task.yml`）

#### 任务类型
🏗️ 基础设施 - 自动化执行链路验收

#### 背景与动机
当前已经完成本地 automation runner 的框架搭建，但尚未通过真实 GitHub Issue 验证整条执行链路。团队在正式依赖该能力前，需要完成一次端到端试跑，确认最小可用能力和现阶段阻塞点。

#### 任务范围
**需要做**：
- 创建并发布一条用于测试的 GitHub Issue
- 使用本地 automation runner 对该 Issue 进行一次真实处理
- 验证 worktree、agent 执行、quality gate、commit/push、PR 创建各步骤
- 汇总试跑结果与改进建议

**不在本任务范围**：
- 不做并发调度压测
- 不覆盖全部异常分支
- 不在本任务内完成大规模架构重构

#### 完成标准
- [ ] 存在一条可供框架处理的真实 GitHub Issue
- [ ] 可以触发本地 automation runner 对其执行
- [ ] 有成功或失败的可复盘结论
- [ ] 产出可供团队复用的试跑记录

#### 技术说明（可选）
- 建议优先使用 `.github/automation/scripts/run-once.ps1` 或 `.github/automation/scripts/run-once.sh`
- 若创建 Issue 需要认证，请优先补齐 `GITHUB_TOKEN` 或 `gh auth`
- 若运行失败，请记录失败步骤、命令、退出码和日志摘要