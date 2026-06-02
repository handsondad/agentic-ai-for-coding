---
title: 'feat: 新增 issue 同步工作流（本地与 GitHub 双向同步）'
type: feature
status: published
labels:
- feature
- ai-ready
priority: P1
assignee: ''
milestone: ''
acceptance_criteria:
- 支持从本地 backlog 文件创建或更新 GitHub Issue
- 支持从 GitHub Issue 状态回写本地文件状态字段
- 提供可重复执行的同步命令，幂等且不会重复创建同标题 issue
- 发生冲突时有明确策略（例如以本地为准/以远端为准）和可追踪日志
- README 补充同步流程、前置条件与常见故障排查
ai_context: 目标是把 issue 生命周期管理标准化，减少手工在本地文档与 GitHub 之间搬运信息的成本。优先实现可落地的同步闭环和幂等保障，再逐步扩展批量能力。
related_docs:
- README.md
- .github/issues-backlog/README.md
- WORKFLOW.md
github_issue_number: '9'
github_issue_url: https://github.com/handsondad/agentic-ai-for-coding/issues/9
---

## 背景与动机

当前团队会在本地 backlog 维护任务草稿，再手工发布到 GitHub。手工流程容易出现重复创建、状态不一致和链接缺失，影响自动化执行与团队协作。

## 任务范围

### 需要做
- 设计并实现 issue 同步工作流（本地 -> GitHub、GitHub -> 本地）
- 明确同步触发方式（手动命令、定时任务或事件驱动）
- 定义状态映射规则（draft/ready/published 与 GitHub open/closed）
- 提供去重机制，避免重复创建同一任务
- 输出最小可用的同步操作文档和示例

### 不在范围
- 不要求在本任务中接入复杂权限系统
- 不要求一次性覆盖所有历史 backlog 文件的数据修复
- 不要求实现跨仓库同步

## 完成标准
- [ ] 新增并验证 issue 同步工作流
- [ ] 可以从本地创建并回填 GitHub issue 编号与 URL
- [ ] 可以从 GitHub 回写至少一个状态字段到本地
- [ ] 同标题重复发布不再产生重复 issue
- [ ] 文档包含完整使用步骤与故障排查

## AI 上下文

优先保证同步逻辑的幂等性和可观测性。任何自动更新都应可追溯，并且在失败时保留可重试入口。

## 关联文档
- README.md
- .github/issues-backlog/README.md
- WORKFLOW.md

---

## 类型化正文（按 type 选择并完善）

### feature 结构（对齐 `.github/ISSUE_TEMPLATE/feature.yml`）

#### 用户故事
作为自动化框架维护者，我希望建立本地 issue 与 GitHub issue 的同步工作流，以便降低手工维护成本并保证任务状态一致。

#### 验收标准
- [ ] 满足 frontmatter 的 acceptance_criteria

#### 技术规格（可选）
- 复用现有 publish 脚本能力，新增反向同步命令
- 增加幂等去重与冲突策略配置

#### 背景与上下文
通过统一同步流程，确保本地 issue 文档与 GitHub issue 信息一致，降低人工维护成本和误差。