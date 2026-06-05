# SDD 工作区总规范

状态: active
负责人: engineering
最后更新: 2026-06-05

## 1. 目标与定位

本文档是本仓库 SDD（详细设计驱动开发）的唯一入口规范。

核心目标:
- 统一详细设计的目录与命名规范。
- 统一模板选型与元信息字段。
- 确保每个设计文档都能追踪 issue 与 PR 生命周期。
- 以 `sdd-index.md` 作为状态追踪唯一真相源。

## 2. 工作区结构

所有 SDD 产物都放在 `docs/sdd/` 下:

```text
docs/sdd/
  README.md
  sdd-index.md
  00-template/
    architecture-design-template.md
    ui-frontend-design-template.md
    business-logic-design-template.md
    ops-deployment-design-template.md
  10-detailed-design/
    01-architecture/
      YYYY-MM-DD/
    02-ui-frontend/
      YYYY-MM-DD/
    03-business-logic/
      YYYY-MM-DD/
    04-ops-deployment/
      YYYY-MM-DD/
```

## 3. 全局规则

- 目录名与文件名必须使用英文。
- 文档内容默认中文，除非任务明确要求英文。
- 全局规范仅允许维护在本文件和 `00-template/` 中。
- 具体设计内容仅允许写在 `10-detailed-design/` 中。
- 新建设计文档必须落在 `YYYY-MM-DD` 的日期子目录。

## 4. 模板清单与选型规则

- 通用元信息模板: `00-template/common-design-metadata-template.md`
- 架构类: `00-template/architecture-design-template.md`
- UI/前端类: `00-template/ui-frontend-design-template.md`
- 业务逻辑类: `00-template/business-logic-design-template.md`
- 部署运维类: `00-template/ops-deployment-design-template.md`

选型建议:
- 需求涉及模块边界、领域模型、跨服务链路时，选架构模板。
- 需求涉及页面交互、状态呈现、前端行为时，选 UI/前端模板。
- 需求主要是领域规则、流程编排、状态机逻辑时，选业务逻辑模板。
- 需求涉及部署发布、运行维护、监控告警时，选部署运维模板。

## 5. 必填状态元信息

每个设计文档 front matter 必须包含以下字段:

- `doc_id`
- `design_status`: `draft | reviewed | approved | deprecated`
- `issue_status`: `not-created | created | in-progress | merged | blocked`
- `issue_url`
- `pr_url`
- `owner`
- `last_updated`

## 6. 命名规范

- 目录名: 英文小写 + 短横线。
- 文件名: `<DOMAIN>-<ID>-<short-description>.md`。
- 示例: `ARCH-001-system-architecture-and-state-machine.md`。

领域前缀:
- `ARCH`: 架构类
- `UI`: UI/前端类
- `BL`: 业务逻辑类
- `OPS`: 部署运维类

## 7. SDD 工作流

1. 从 `sdd-index.md` 选择设计单元。
2. 在 `00-template/` 选择合适模板。
3. 在正确领域与日期目录下创建或更新设计文档。
4. 创建 issue 后回填 `issue_status` 与 `issue_url`。
5. 合并 PR 后回填 `pr_url` 与相关状态字段。
6. 同步更新 `sdd-index.md` 对应行。

## 8. `sdd-index.md` 同步规则

`sdd-index.md` 是团队审计矩阵，以下场景必须更新:
- 新建设计文档；
- `design_status` 变化；
- `issue_status` 变化；
- issue/PR 链接新增或变化。

一致性要求:
- 矩阵行的 `doc_id` 必须与文档 front matter 完全一致。
- 矩阵中的 `path` 必须指向 `docs/sdd/10-detailed-design/` 下真实文件路径。
- 矩阵中的 `issue_status` 必须与文档 front matter 保持一致。
- 文档有更新时，`last_updated` 应在同一提交中同步更新。

## 9. 设计文档 DoD

仅当以下条件全部满足时，设计文档才算完成:

- 位于 `docs/sdd/10-detailed-design/` 下正确的领域目录与日期目录。
- 必填状态元信息完整且合法。
- Scope 与验收标准明确且可验证。
- `issue_url` 与 `pr_url` 可追踪（若暂缺需标注 `TBD` 并说明原因）。
- `sdd-index.md` 中存在与文档匹配且状态同步的记录。

## 10. 不在范围

- 本规范不在单个任务中迁移全部历史设计文档。
- 本规范不引入外部文档平台或知识库系统。
- 本规范不替代实现级技术方案评审流程。
