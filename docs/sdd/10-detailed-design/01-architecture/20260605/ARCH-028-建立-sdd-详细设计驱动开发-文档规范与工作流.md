---
doc_id: ARCH-028
design_status: draft
issue_status: in-progress
issue_url: https://github.com/handsondad/agentic-ai-for-coding/issues/28
pr_url: TBD
owner: @unassigned
last_updated: 20260605
---

# 背景

- 基于 SDD（详细设计驱动开发）建立统一入口规范，解决文档分散、状态不可追踪、Issue/PR 关联弱的问题。
- 当前详细设计文档缺少统一的目录结构、模板选型规则和状态追踪字段，导致团队协作中出现“文档位置不一致、命名不统一、Issue/PR 难追溯”的问题。 需要建立 SDD 工作区总规范，统一从模板到设计文档再到 Issue/PR 回填的闭环。

# 目标与范围

## 目标

- 建立 SDD 工作区总规范入口，明确以下目录结构：
- `sdd-index.md`：文档到 Issue 的索引与状态矩阵。
- `00-template/`：模板库（仅模板）。
- `10-detailed-design/`：具体详细设计（按领域 + 日期）。
- 统一模板清单与选型规则：
- 架构类：`architecture-design-template.md`
- UI/前端类：`ui-frontend-design-template.md`
- 业务逻辑类：`business-logic-design-template.md`
- 部署运维类：`ops-deployment-design-template.md`
- 约束模板最少状态字段：
- `design_status`
- `issue_status`
- `issue_url`
- `pr_url`
- `owner`
- `last_updated`
- 明确全局规则：
- 文件名与目录名使用英文，文档内容默认中文。
- 全局规范仅写在总规范与模板目录，不散落在详细设计文档。
- 具体设计内容仅写在 `10-detailed-design/`。
- 新设计文档必须在日期子目录（`YYYY-MM-DD`）下。
- 每个设计文档必须包含状态元信息与 Issue/PR 链接字段。
- 明确日期目录规范：
- `10-detailed-design/01-architecture/YYYY-MM-DD/`
- `10-detailed-design/02-ui-frontend/YYYY-MM-DD/`
- `10-detailed-design/03-business-logic/YYYY-MM-DD/`
- `10-detailed-design/04-ops-deployment/YYYY-MM-DD/`
- 明确状态元信息规范：
- `doc_id`
- `design_status: draft | reviewed | approved | deprecated`
- `issue_status: not-created | created | in-progress | merged | blocked`
- `issue_url`
- `pr_url`
- `owner`
- `last_updated`
- 明确 SDD 工作流：
- 明确命名规范：
- 目录名：英文小写 + 短横线。
- 文件名：`<DOMAIN>-<ID>-<short-description>.md`。
- 示例：`ARCH-001-system-architecture-and-state-machine.md`。
- 输出设计文档完成标准（DoD）：
- 使用正确领域目录与日期目录。
- 元信息字段填写完整。
- Scope 与验收标准明确。
- 文档与索引都能追踪到 issue/pr 链接。

## 不在范围

- 不在本 issue 中完成所有历史设计文档迁移。
- 不引入新的文档平台或外部知识库系统。
- 不替代业务实现类技术方案评审流程。

# 设计与执行建议

- 建议领域: ARCH (architecture)
- 建议模板: 00-template/architecture-design-template.md
- 分类依据: 偏流程治理与架构编排
- 反向来源: .github/issues-backlog/task/20260605/sdd-workspace-spec-and-workflow.md

# 验收映射

- SDD 目录结构、模板选型、命名与状态字段规范形成统一文档并可执行。
- 详细设计文档按领域与日期目录管理，且能追踪 issue/pr 链接。
- 提供 DoD 与 sdd-index 同步规则，支持团队审计和持续维护。
