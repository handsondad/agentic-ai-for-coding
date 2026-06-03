---
title: 'chore: 构建 Starter Kit 接入清单与模板化配置'
type: task
status: published
labels:
- task
- ai-ready
- platform
priority: P2
assignee: ''
milestone: ai-coding-infra-phase3
acceptance_criteria:
- 提供新项目 30 分钟接入清单
- 抽象关键配置模板（WORKFLOW、PR 模板、issue backlog 约定）
- 提供最小接入验证步骤
- 文档说明多项目复用边界与可选项
ai_context: 要把当前仓库沉淀为可复制的平台能力，需要把接入步骤、模板和验收路径产品化，而不是靠口口相传。
related_docs:
- docs/ai-coding-infra-executable-blueprint.md
- README.md
- WORKFLOW.md
- .github/copilot-instructions.md
github_issue_number: '16'
github_issue_url: https://github.com/handsondad/agentic-ai-for-coding/issues/16
---

## 背景与动机

当前能力主要服务于本仓库，缺少面向“新项目快速接入”的标准包和接入手册。

## 任务范围

### 需要做
- 梳理接入前置条件和环境初始化步骤
- 提供可复制模板文件集合
- 输出“30 分钟接入”操作指南
- 提供接入后的最小验收脚本

### 不在范围
- 不做跨组织权限治理平台
- 不做多云部署方案

## 完成标准
- [ ] 新项目可按清单完成初始化
- [ ] 接入后可跑通单 issue 自动链路
- [ ] 文档包含常见失败排查

## 最小可运行命令

```bash
# 新仓库初始化后验证
python .github/manual/scripts/prepare-single-issue.py --issue-file .github/issues-backlog/task/YYYYMMDD/sample-task.md
```

## 风险与回滚

- 风险：模板过多导致接入复杂
- 回滚：拆分为“必选模板 + 可选增强模板”，先交付必选最小集合

