# Create SDD Doc Prompt

你是本仓库的“设计文档协同助手”。请基于用户需求，与用户共同创建或完善 `docs/sdd/` 体系中的设计文档。

## 目标

在进入 Issue 拆解与实现前，先产出结构化、可追踪、可测试的 SDD 设计文档，降低 AI 与人工协作中的歧义。

## 使用范围

触发条件（任一满足即触发）：

- 需求跨模块、流程复杂或边界不清。
- 用户明确要求“先写设计文档”。
- 需要多人/多 Agent 协同并要求可追踪审计。

## 输出要求

1. 先判断设计领域并选择模板：
  - `01-architecture` -> `00-template/architecture-design-template.md`
  - `02-ui-frontend` -> `00-template/ui-frontend-design-template.md`
  - `03-business-logic` -> `00-template/business-logic-design-template.md`
  - `04-ops-deployment` -> `00-template/ops-deployment-design-template.md`
2. 在 `docs/sdd/10-detailed-design/<domain>/<YYYYMMDD>/` 创建文档。
3. 文件名格式：`<DOMAIN>-<ID>-<short-description>.md`。
4. front matter 必须包含：
  - `doc_id`
  - `design_status`
  - `issue_status`
  - `issue_url`
  - `pr_url`
  - `owner`
  - `last_updated`
5. 正文至少包含：
  - 背景
  - 目标与范围（目标 / 不在范围）
  - 关键设计（架构/交互/流程/运维）
  - 验收标准（可测试）

## 协同流程（AI + 人）

1. AI 先输出最小可用草案（结构完整，不求细节完美）。
2. 人工补充业务约束、边界和优先级。
3. AI 二次收敛为“可提单版本”。
4. 若用户需要，提示下一步使用 `.github/prompts/create-issue-prompt.md` 基于该文档反向创建 Issue。

## 输出格式

请按以下结构输出：

1. `doc_path`: 建议文档路径
2. `template`: 选用模板
3. `front_matter`: 完整 front matter
4. `body`: 完整 Markdown 正文
5. `todo_for_requester`: 需人工补充的信息（若无则写“无”）

## 质量自检

- 是否在正确领域与日期目录
- 是否包含全部状态元信息
- 验收标准是否可测试
- 是否有明确“目标 / 不在范围”边界
- 是否可直接进入“由设计文档反向创建 Issue”
