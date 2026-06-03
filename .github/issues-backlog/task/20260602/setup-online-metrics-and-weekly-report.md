---
title: 'chore: 建立在线指标采集与周报模板'
type: task
status: published
labels:
- task
- ai-ready
- observability
priority: P1
assignee: ''
milestone: ai-coding-infra-phase2
acceptance_criteria:
- 定义并采集核心 KPI（成功率、一次通过率、Lead Time、返工率、门禁通过率）
- 输出每周指标快照文件
- 提供周报模板，包含趋势与Top阻塞原因
- 指标字段与失败分类结果可关联
ai_context: 没有在线指标就无法知道流程是否在变好。需要先把关键指标采起来，再做策略优化。
related_docs:
- docs/ai-coding-infra-executable-blueprint.md
- .github/automation/service.py
- docs/dev-guide.md
github_issue_number: '18'
github_issue_url: https://github.com/handsondad/agentic-ai-for-coding/issues/18
---

## 背景与动机

当前流程可运行，但缺少统一可观测指标，难以判断改动后是否真的提升了效率和质量。

## 任务范围

### 需要做
- 定义 KPI 字段和计算口径
- 增加执行日志到指标快照的抽取脚本
- 建立每周周报模板（Markdown）
- 在文档中明确指标查看方式

### 不在范围
- 不搭建复杂 BI 平台
- 不引入外部付费监控系统

## 完成标准
- [ ] 每周能自动生成一份指标快照
- [ ] 周报包含环比变化和 Top3 阻塞原因
- [ ] 指标计算逻辑文档化

## 最小可运行命令

```bash
python .github/automation/scripts/metrics-snapshot.py --period weekly
```

## 风险与回滚

- 风险：日志字段不稳定导致指标缺失
- 回滚：先从最小字段集开始（issue_id、status、duration、exit_code），逐步扩展
