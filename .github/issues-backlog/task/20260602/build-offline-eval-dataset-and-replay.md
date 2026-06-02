---
title: 'chore: 建设离线评估集与回放脚本'
type: task
status: ready
labels:
- task
- ai-ready
- evaluation
priority: P2
assignee: ''
milestone: ''
acceptance_criteria:
- 建立不少于 20 条样本的离线评估集
- 提供一键回放脚本
- 输出评估报告（成功率、门禁通过率、失败分类）
- 支持策略变更前后对比
ai_context: 该任务用于让 agent 策略优化可量化、可回归，避免依赖主观感受调整流程。
related_docs:
- docs/ai-coding-infra-executable-blueprint.md
- .github/automation/
- docs/dev-guide.md
---

## 背景与动机

当前优化更多依赖线上试错，缺少稳定的离线回放基线。需要建立评估集与回放机制，支持策略迭代前后量化对比。

## 任务范围

### 需要做
- 定义评估样本结构（issue 内容、预期输出、风险等级）
- 构建首批 20 条样本（feature/bug/task 覆盖）
- 实现回放脚本并输出标准报告
- 报告至少包含：成功率、平均时长、门禁通过率、失败分类分布

### 不在范围
- 不要求覆盖全部历史 issue
- 不做复杂可视化平台

## 完成标准
- [ ] 样本库可版本化管理
- [ ] 回放可在本地独立运行
- [ ] 报告支持与上次结果对比
- [ ] 至少完成一次真实策略对比实验

## 最小可运行命令（建议）

```bash
python .github/automation/scripts/replay-eval.py --dataset .github/automation/evals/dataset.json
```

## 风险与回滚

- 风险：样本分布偏差导致评估失真
- 回滚：先以高频任务构建最小集，再逐周增量扩展
