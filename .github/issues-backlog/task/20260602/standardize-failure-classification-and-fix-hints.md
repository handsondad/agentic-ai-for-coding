---
title: 'chore: 标准化失败分类与修复建议输出'
type: task
status: published
labels:
- task
- ai-ready
- infra
priority: P1
assignee: ''
milestone: ai-coding-infra-mvp
acceptance_criteria:
- 定义统一失败分类（需求缺口/代码缺陷/环境阻塞/外部依赖）
- 每次失败输出必须包含失败步骤、关键错误、下一步建议
- 失败输出可用于 PR 描述或 issue 评论复用
- 至少覆盖 5 类典型失败样本并验证分类准确性
ai_context: 目前失败信息以日志文本为主，难以快速复盘和趋势统计。标准化分类是评估体系与自动恢复策略的前提。
related_docs:
- docs/ai-coding-infra-executable-blueprint.md
- .github/copilot-instructions.md
- .github/pull_request_template.md
- .github/automation/service.py
github_issue_number: '19'
github_issue_url: https://github.com/handsondad/agentic-ai-for-coding/issues/19
---

## 背景与动机

自动化流程失败时，如果只给原始日志，团队无法快速判断问题归属，也无法持续优化。

需要统一失败分类与修复建议输出规范，支持复盘与指标统计。

## 任务范围

### 需要做
- 定义失败分类枚举与判定规则
- 设计结构化失败输出格式（JSON/Markdown）
- 在 runner 关键失败路径接入分类逻辑
- 输出可直接贴入 issue/PR 的“失败闭环模板”
- 补充失败样本测试

### 不在范围
- 不做自动修复执行（仅输出建议）
- 不改动业务逻辑实现

## 完成标准
- [ ] 失败分类规则文档化且可被引用
- [ ] 自动执行失败时总能输出 3 段式信息（步骤/摘要/建议）
- [ ] 失败分类可用于周报统计

## 最小可运行命令

```bash
python .github/automation/scripts/failure-report.py --from-log .github/automation/cron.log
```

## 风险与回滚

- 风险：误分类导致误判优化方向
- 回滚：保留原始日志输出并并行输出分类结果，先观察两周再强依赖分类
