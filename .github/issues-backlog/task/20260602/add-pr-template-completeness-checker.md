---
title: 'chore: 新增 PR 模板完整性校验器'
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
- PR 描述可自动检查模板完整性
- 未填写章节可在 CI 中失败提示
- 检查规则可配置且文档化
- 本地可先行执行同样检查
ai_context: 该任务用于保证 PR 描述质量稳定，避免空白或占位文本进入审查流程。
related_docs:
- .github/pull_request_template.md
- .github/workflows/ci.yml
- docs/ai-coding-infra-executable-blueprint.md
github_issue_number: '14'
github_issue_url: https://github.com/handsondad/agentic-ai-for-coding/issues/14
---

## 背景与动机

已有 PR 模板，但仍可能出现章节缺失或仅保留占位文本的情况，影响审查效率与可追溯性。

## 任务范围

### 需要做
- 实现 PR 描述完整性检查器（脚本或 action）
- 校验至少包含：背景、变更摘要、变更详情、测试计划、审查重点
- 校验“测试计划”必须包含已执行或未执行说明
- 集成到 CI 并提供本地运行命令

### 不在范围
- 不校验业务内容正确性
- 不替代人工代码审查

## 完成标准
- [ ] 缺失章节时 CI 明确失败并给出提示
- [ ] 占位注释未替换时 CI 明确失败
- [ ] 本地命令可复现 CI 检查结果
- [ ] 文档包含“如何修复失败”指引

## 最小可运行命令（建议）

```bash
python .github/automation/scripts/check-pr-template.py --body-file pr.md
```

## 风险与回滚

- 风险：规则过严导致正常 PR 被误拦截
- 回滚：提供 warning 模式并逐步切换到 fail 模式
