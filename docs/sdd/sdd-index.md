# SDD 索引矩阵

状态: active
负责人: engineering
最后更新: 20260605

## 目标

该矩阵用于追踪每个 SDD 文档与 issue/PR 生命周期。

## 状态枚举

- `design_status`: `draft | reviewed | approved | deprecated`
- `issue_status`: `not-created | created | in-progress | merged | blocked`

## 矩阵

| doc_id | domain | title | path | design_status | issue_status | issue_url | pr_url | owner | last_updated |
|---|---|---|---|---|---|---|---|---|---|
| ARCH-009 | architecture | 新增 issue 同步工作流（本地与 GitHub 双向同步） | docs/sdd/10-detailed-design/01-architecture/20260602/ARCH-009-feat-新增-issue-同步工作流-本地与-github-双向同步.md | draft | in-progress | https://github.com/handsondad/agentic-ai-for-coding/issues/9 | TBD | @unassigned | 20260602 |
| ARCH-024 | architecture | 初始化与模板变更（PR #1~#5） | docs/sdd/10-detailed-design/01-architecture/20260528/ARCH-024-初始化与模板变更-pr-1-5.md | draft | in-progress | https://github.com/handsondad/agentic-ai-for-coding/issues/24 | TBD | @unassigned | 20260528 |
| ARCH-011 | architecture | 新增 AGENTS.md 统一 AI for Coding 规范入口 | docs/sdd/10-detailed-design/01-architecture/20260602/ARCH-011-docs-新增-agents-md-统一-ai-for-coding-规范入口.md | draft | in-progress | https://github.com/handsondad/agentic-ai-for-coding/issues/11 | TBD | @unassigned | 20260602 |
| ARCH-014 | architecture | 新增 PR 模板完整性校验器 | docs/sdd/10-detailed-design/01-architecture/20260602/ARCH-014-chore-新增-pr-模板完整性校验器.md | draft | in-progress | https://github.com/handsondad/agentic-ai-for-coding/issues/14 | TBD | @unassigned | 20260602 |
| ARCH-025 | architecture | 自动化基础与流程强化（含 direct commits） | docs/sdd/10-detailed-design/01-architecture/20260602/ARCH-025-自动化基础与流程强化-含-direct-commits.md | draft | in-progress | https://github.com/handsondad/agentic-ai-for-coding/issues/25 | TBD | @unassigned | 20260602 |
| ARCH-015 | architecture | 建设离线评估集与回放脚本 | docs/sdd/10-detailed-design/01-architecture/20260602/ARCH-015-chore-建设离线评估集与回放脚本.md | draft | in-progress | https://github.com/handsondad/agentic-ai-for-coding/issues/15 | TBD | @unassigned | 20260602 |
| ARCH-016 | architecture | 构建 Starter Kit 接入清单与模板化配置 | docs/sdd/10-detailed-design/01-architecture/20260602/ARCH-016-chore-构建-starter-kit-接入清单与模板化配置.md | draft | in-progress | https://github.com/handsondad/agentic-ai-for-coding/issues/16 | TBD | @unassigned | 20260602 |
| ARCH-017 | architecture | 新增统一质量门禁执行器 | docs/sdd/10-detailed-design/01-architecture/20260602/ARCH-017-chore-新增统一质量门禁执行器-lint-type-test-checklist.md | draft | in-progress | https://github.com/handsondad/agentic-ai-for-coding/issues/17 | TBD | @unassigned | 20260602 |
| ARCH-018 | architecture | 建立在线指标采集与周报模板 | docs/sdd/10-detailed-design/01-architecture/20260602/ARCH-018-chore-建立在线指标采集与周报模板.md | draft | in-progress | https://github.com/handsondad/agentic-ai-for-coding/issues/18 | TBD | @unassigned | 20260602 |
| BL-019 | business-logic | 标准化失败分类与修复建议输出 | docs/sdd/10-detailed-design/03-business-logic/20260602/BL-019-chore-标准化失败分类与修复建议输出.md | draft | in-progress | https://github.com/handsondad/agentic-ai-for-coding/issues/19 | TBD | @unassigned | 20260602 |
| ARCH-007 | architecture | 验证 automation runner 可端到端处理 GitHub issue | docs/sdd/10-detailed-design/01-architecture/20260602/ARCH-007-chore-验证-automation-runner-可端到端处理-github-issue.md | draft | in-progress | https://github.com/handsondad/agentic-ai-for-coding/issues/7 | TBD | @unassigned | 20260602 |
| ARCH-026 | architecture | Celery 重构与手动模式治理 | docs/sdd/10-detailed-design/01-architecture/20260603/ARCH-026-celery-重构与手动模式治理.md | draft | in-progress | https://github.com/handsondad/agentic-ai-for-coding/issues/26 | TBD | @unassigned | 20260603 |
| ARCH-020 | architecture | 前端页面 AI 生成与自动化测试流程设计 | docs/sdd/10-detailed-design/01-architecture/20260604/ARCH-020-前端页面-ai-生成与自动化测试流程设计-issue-构建规范-skill-mcp-增强.md | draft | in-progress | https://github.com/handsondad/agentic-ai-for-coding/issues/20 | TBD | @unassigned | 20260604 |
| OPS-022 | ops-deployment | 基于 GitHub Actions 的 Docker 部署方案 | docs/sdd/10-detailed-design/04-ops-deployment/20260604/OPS-022-基于-github-actions-驱动自有-docker-环境部署的可行性与落地方案.md | draft | in-progress | https://github.com/handsondad/agentic-ai-for-coding/issues/22 | TBD | @unassigned | 20260604 |
| ARCH-023 | architecture | 多 code agent 接入与 generic openai compatible 方案 | docs/sdd/10-detailed-design/01-architecture/20260604/ARCH-023-多-code-agent-接入与-generic-openai-compatible-模型服务替代方案.md | draft | in-progress | https://github.com/handsondad/agentic-ai-for-coding/issues/23 | TBD | @unassigned | 20260604 |
| ARCH-021 | architecture | 脚手架引入 MCP Skill 与云端 agent 可用性验证 | docs/sdd/10-detailed-design/01-architecture/20260604/ARCH-021-脚手架引入-mcp-skill-的标准方案与-copilot-云端-agent-可用性验证.md | draft | in-progress | https://github.com/handsondad/agentic-ai-for-coding/issues/21 | TBD | @unassigned | 20260604 |
| ARCH-028 | architecture | 建立 SDD 文档规范与工作流 | docs/sdd/10-detailed-design/01-architecture/20260605/ARCH-028-建立-sdd-详细设计驱动开发-文档规范与工作流.md | draft | in-progress | https://github.com/handsondad/agentic-ai-for-coding/issues/28 | TBD | @unassigned | 20260605 |
| UI-001 | ui-frontend | 统一管理 automate 与 manual 运行日志页面 | docs/sdd/10-detailed-design/02-ui-frontend/20260605/UI-001-unified-automation-manual-log-management.md | draft | created | https://github.com/handsondad/agentic-ai-for-coding/issues/30 | TBD | @unassigned | 20260605 |

## 同步检查清单

- 设计文档元信息变化时，必须在同一提交中更新本文件。
- 保持 `doc_id`、`design_status`、`issue_status` 与链接和文档 front matter 一致。
- 文档删除或重命名后，不得保留过期记录。
