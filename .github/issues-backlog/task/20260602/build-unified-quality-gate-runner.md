---
title: 'chore: 新增统一质量门禁执行器（lint/type/test/checklist）'
type: task
status: published
labels:
- task
- ai-ready
- quality-gate
priority: P1
assignee: ''
milestone: ''
acceptance_criteria:
- 仓库中存在统一门禁执行入口（脚本或命令）
- 门禁执行顺序固定且可配置
- 失败输出包含失败步骤与命令摘要
- 在 README 或 dev-guide 中补充使用方式
ai_context: 该任务用于把分散的质量检查命令收敛成单一入口，提升 agent 执行稳定性与可审计性。
related_docs:
- docs/ai-coding-infra-executable-blueprint.md
- WORKFLOW.md
- README.md
github_issue_number: '17'
github_issue_url: https://github.com/handsondad/agentic-ai-for-coding/issues/17
---

## 背景与动机

当前 lint、type、test、PR 描述检查分散在不同命令与脚本中。agent 在不同任务中容易出现执行顺序不一致、遗漏某一步或失败信息不完整的问题。

需要新增统一门禁执行器，作为开发与自动化流程的标准入口。

## 任务范围

### 需要做
- 提供统一门禁入口（例如 `make gate` 或 `.github/automation/scripts/run-quality-gates.*`）
- 固化默认顺序：format-check -> lint -> type-check -> unit-test -> template-check
- 支持最小配置（跳过某阶段、仅运行某阶段）
- 失败时输出标准化摘要（步骤、退出码、关键日志）
- 更新 README/dev-guide 的门禁使用说明

### 不在范围
- 不改造业务代码逻辑
- 不在本任务内引入复杂分布式执行

## 完成标准
- [ ] 本地与 CI 可复用同一门禁入口
- [ ] 统一入口在失败时能输出标准化摘要
- [ ] 至少提供 3 个测试场景：全通过、lint 失败、test 失败
- [ ] 文档已更新且可按文档复现

## 最小可运行命令（建议）

```bash
make gate
```

或：

```bash
python .github/automation/scripts/run-quality-gates.py
```

## 风险与回滚

- 风险：门禁顺序变更导致历史习惯命令失效
- 回滚：保留旧命令入口并通过文档标记为兼容模式
