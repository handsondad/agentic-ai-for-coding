# Backlog 反向生成的 SDD 设计总结

- 生成日期: 20260605
- 数据来源: `.github/issues-backlog`
- 反向总结条目数: 17

## 全局统计

- 类型分布: feature=1, task=16
- 状态分布: published=17
- 优先级分布: P1=7, P2=10

## Backlog -> SDD 映射矩阵

| backlog 文件 | Issue | 建议 SDD 领域 | 建议模板 | 关键设计焦点 | 关键验收线索 |
|---|---|---|---|---|---|
| `.github/issues-backlog/feature/20260602/add-issue-sync-workflow.md` | [#9](https://github.com/handsondad/agentic-ai-for-coding/issues/9) | ARCH (architecture) | `architecture-design-template.md` | 设计并实现 issue 同步工作流（本地 -> GitHub、GitHub -> 本地）；明确同步触发方式（手动命令、定时任务或事件驱动） | 支持从本地 backlog 文件创建或更新 GitHub Issue；支持从 GitHub Issue 状态回写本地文件状态字段 |
| `.github/issues-backlog/task/20260528/bootstrap-pr1-pr5.md` | [#24](https://github.com/handsondad/agentic-ai-for-coding/issues/24) | ARCH (architecture) | `architecture-design-template.md` | 记录该时间窗口内的关键 commit 与 PR 映射。；标注每条变更是否已有 issue 覆盖。 | 梳理 2026-05-28~2026-05-29 历史提交与 PR 对应关系。；为缺少 issue 的历史提交建立追溯档案。 |
| `.github/issues-backlog/task/20260602/add-agents-md-ai-for-coding-spec.md` | [#11](https://github.com/handsondad/agentic-ai-for-coding/issues/11) | ARCH (architecture) | `architecture-design-template.md` | 在仓库根目录新增 `AGENTS.md`；以“可执行规范”为导向组织内容，而非泛泛介绍 | 仓库根目录存在 AGENTS.md；文档可在 3-5 分钟内帮助新 agent 建立执行上下文 |
| `.github/issues-backlog/task/20260602/add-pr-template-completeness-checker.md` | [#14](https://github.com/handsondad/agentic-ai-for-coding/issues/14) | ARCH (architecture) | `architecture-design-template.md` | 实现 PR 描述完整性检查器（脚本或 action）；校验至少包含：背景、变更摘要、变更详情、测试计划、审查重点 | PR 描述可自动检查模板完整性；未填写章节可在 CI 中失败提示 |
| `.github/issues-backlog/task/20260602/automation-foundation.md` | [#25](https://github.com/handsondad/agentic-ai-for-coding/issues/25) | ARCH (architecture) | `architecture-design-template.md` | 梳理当日全部关键提交。；标注每条提交的 issue/PR 对应关系。 | 梳理 2026-06-02 当日提交与 issue/PR 对应关系。；对 direct commit 补齐追溯说明，避免治理盲区。 |
| `.github/issues-backlog/task/20260602/build-offline-eval-dataset-and-replay.md` | [#15](https://github.com/handsondad/agentic-ai-for-coding/issues/15) | ARCH (architecture) | `architecture-design-template.md` | 定义评估样本结构（issue 内容、预期输出、风险等级）；构建首批 20 条样本（feature/bug/task 覆盖） | 建立不少于 20 条样本的离线评估集；提供一键回放脚本 |
| `.github/issues-backlog/task/20260602/build-starter-kit-onboarding-pack.md` | [#16](https://github.com/handsondad/agentic-ai-for-coding/issues/16) | ARCH (architecture) | `architecture-design-template.md` | 梳理接入前置条件和环境初始化步骤；提供可复制模板文件集合 | 提供新项目 30 分钟接入清单；抽象关键配置模板（WORKFLOW、PR 模板、issue backlog 约定） |
| `.github/issues-backlog/task/20260602/build-unified-quality-gate-runner.md` | [#17](https://github.com/handsondad/agentic-ai-for-coding/issues/17) | ARCH (architecture) | `architecture-design-template.md` | 提供统一门禁入口（例如 `make gate` 或 `.github/automation/scripts/run-quality-gates.*`）；固化默认顺序：format-check -> lint -> type-check -> unit-test -> template-check | 仓库中存在统一门禁执行入口（脚本或命令）；门禁执行顺序固定且可配置 |
| `.github/issues-backlog/task/20260602/setup-online-metrics-and-weekly-report.md` | [#18](https://github.com/handsondad/agentic-ai-for-coding/issues/18) | ARCH (architecture) | `architecture-design-template.md` | 定义 KPI 字段和计算口径；增加执行日志到指标快照的抽取脚本 | 定义并采集核心 KPI（成功率、一次通过率、Lead Time、返工率、门禁通过率）；输出每周指标快照文件 |
| `.github/issues-backlog/task/20260602/standardize-failure-classification-and-fix-hints.md` | [#19](https://github.com/handsondad/agentic-ai-for-coding/issues/19) | BL (business-logic) | `business-logic-design-template.md` | 定义失败分类枚举与判定规则；设计结构化失败输出格式（JSON/Markdown） | 定义统一失败分类（需求缺口/代码缺陷/环境阻塞/外部依赖）；每次失败输出必须包含失败步骤、关键错误、下一步建议 |
| `.github/issues-backlog/task/20260602/validate-automation-runner-e2e.md` | [#7](https://github.com/handsondad/agentic-ai-for-coding/issues/7) | ARCH (architecture) | `architecture-design-template.md` | 使用一条真实的 GitHub Issue 触发本地自动化流程；验证 `ai-ready` 标签任务是否能被正确发现 | 可以从 GitHub Issues 轮询到带有 ai-ready 标签的任务；可以为目标任务创建独立 worktree 并渲染 issue prompt |
| `.github/issues-backlog/task/20260603/celery-manual-policy.md` | [#26](https://github.com/handsondad/agentic-ai-for-coding/issues/26) | ARCH (architecture) | `architecture-design-template.md` | 建立该阶段 commit 清单与对应关系。；标注是否与近期规划 issue（#20-#23）相关。 | 梳理 2026-06-03~2026-06-04 提交并建立追溯链路。；标注与现有 issue（#20-#23）和 direct commit 的关系。 |
| `.github/issues-backlog/task/20260604/frontend-ai-generation-testing-skill-mcp.md` | [#20](https://github.com/handsondad/agentic-ai-for-coding/issues/20) | ARCH (architecture) | `architecture-design-template.md` | 设计前端类 issue 模板（页面型、组件型、重构型），至少包含：；页面目标与视觉方向 | 输出一套前端任务 issue 模板，覆盖页面生成、测试、验收、回滚。；在仓库内提供最小可执行示例，能被 agent 按模板落地。 |
| `.github/issues-backlog/task/20260604/github-actions-docker-deploy.md` | [#22](https://github.com/handsondad/agentic-ai-for-coding/issues/22) | OPS (ops-deployment) | `ops-deployment-design-template.md` | 设计部署链路：代码触发 -> 镜像构建 -> 镜像推送 -> 远端部署 -> 健康检查。；明确目标环境连接方式（SSH/Runner 自托管/远端 API）及风险。 | 明确 GitHub Actions 驱动 Docker 部署的目标架构与安全边界。；产出可运行的 workflow 草案（构建、推送、部署、回滚）。 |
| `.github/issues-backlog/task/20260604/multi-agent-openai-compatible-integration.md` | [#23](https://github.com/handsondad/agentic-ai-for-coding/issues/23) | ARCH (architecture) | `architecture-design-template.md` | 评估多 Agent 方案：；Copilot | 输出多 Agent 接入对比矩阵（能力、成本、接入复杂度、限制）。；明确 Generic OpenAI-compatible 接口接入方案与配置模板。 |
| `.github/issues-backlog/task/20260604/scaffold-tooling-mcp-skill-copilot-cloud.md` | [#21](https://github.com/handsondad/agentic-ai-for-coding/issues/21) | ARCH (architecture) | `architecture-design-template.md` | 梳理脚手架内 MCP 与 Skill 的接入点：；配置位置 | 明确 MCP 与 Skill 的引入路径、目录规范和版本策略。；完成 Copilot 云端 Agent 可用性验证清单与结论。 |
| `.github/issues-backlog/task/20260605/sdd-workspace-spec-and-workflow.md` | [#28](https://github.com/handsondad/agentic-ai-for-coding/issues/28) | ARCH (architecture) | `architecture-design-template.md` | 建立 SDD 工作区总规范入口，明确以下目录结构：；`sdd-index.md`：文档到 Issue 的索引与状态矩阵。 | SDD 目录结构、模板选型、命名与状态字段规范形成统一文档并可执行。；详细设计文档按领域与日期目录管理，且能追踪 issue/pr 链接。 |

## 逐项设计摘要

### #9 feat: 新增 issue 同步工作流（本地与 GitHub 双向同步）

- backlog 路径: `.github/issues-backlog/feature/20260602/add-issue-sync-workflow.md`
- issue 类型: `feature`
- 建议 SDD 归档: `docs/sdd/10-detailed-design/01-architecture/20260602/`
- 建议模板: `00-template/architecture-design-template.md`
- 分类依据: 偏流程治理与架构编排
- issue 链接: https://github.com/handsondad/agentic-ai-for-coding/issues/9

设计目标:
- 目标是把 issue 生命周期管理标准化，减少手工在本地文档与 GitHub 之间搬运信息的成本。优先实现可落地的同步闭环和幂等保障，再逐步扩展批量能力。
- 当前团队会在本地 backlog 维护任务草稿，再手工发布到 GitHub。手工流程容易出现重复创建、状态不一致和链接缺失，影响自动化执行与团队协作。

范围(需要做):
- 设计并实现 issue 同步工作流（本地 -> GitHub、GitHub -> 本地）
- 明确同步触发方式（手动命令、定时任务或事件驱动）
- 定义状态映射规则（draft/ready/published 与 GitHub open/closed）
- 提供去重机制，避免重复创建同一任务
- 输出最小可用的同步操作文档和示例

范围(不在范围):
- 不要求在本任务中接入复杂权限系统
- 不要求一次性覆盖所有历史 backlog 文件的数据修复
- 不要求实现跨仓库同步

验收映射:
- 支持从本地 backlog 文件创建或更新 GitHub Issue
- 支持从 GitHub Issue 状态回写本地文件状态字段
- 提供可重复执行的同步命令，幂等且不会重复创建同标题 issue
- 发生冲突时有明确策略（例如以本地为准/以远端为准）和可追踪日志
- README 补充同步流程、前置条件与常见故障排查

### #24 初始化与模板变更（PR #1~#5）

- backlog 路径: `.github/issues-backlog/task/20260528/bootstrap-pr1-pr5.md`
- issue 类型: `task`
- 建议 SDD 归档: `docs/sdd/10-detailed-design/01-architecture/20260528/`
- 建议模板: `00-template/architecture-design-template.md`
- 分类依据: 偏流程治理与架构编排
- issue 链接: https://github.com/handsondad/agentic-ai-for-coding/issues/24

设计目标:
- 历史阶段存在直接提交和回滚操作，需要补齐 issue 轨迹并形成可追溯记录。
- 仓库初始化阶段（2026-05-28~2026-05-29）包含模板建立、README 重写、回滚与流程目录建设。 该阶段存在“先提交后补流程”的情况，需补建历史追溯 issue 以完善治理闭环。

范围(需要做):
- 记录该时间窗口内的关键 commit 与 PR 映射。
- 标注每条变更是否已有 issue 覆盖。
- 形成后续审计可直接引用的追溯基线。

范围(不在范围):
- 不重写当时的代码实现。
- 不对已关闭 PR 进行历史改写。

验收映射:
- 梳理 2026-05-28~2026-05-29 历史提交与 PR 对应关系。
- 为缺少 issue 的历史提交建立追溯档案。
- 在 issue 中给出 commit/PR 一一映射表，便于后续审计。

### #11 docs: 新增 AGENTS.md 统一 AI for Coding 规范入口

- backlog 路径: `.github/issues-backlog/task/20260602/add-agents-md-ai-for-coding-spec.md`
- issue 类型: `task`
- 建议 SDD 归档: `docs/sdd/10-detailed-design/01-architecture/20260602/`
- 建议模板: `00-template/architecture-design-template.md`
- 分类依据: 偏流程治理与架构编排
- issue 链接: https://github.com/handsondad/agentic-ai-for-coding/issues/11

设计目标:
- 该任务用于建立仓库级 AI for Coding 统一入口文档，降低任意 code agent 的冷启动成本，确保“读规范即可开干”。
- 当前仓库已有多处与 AI for Coding 相关的规范与流程（如 `WORKFLOW.md`、`.github/copilot-instructions.md`、`.github/pull_request_template.md`、自动化脚本与 issue 工作流约定），但分散在多个文件中。 为了让任意 code agent 进入仓库后能够在最短时间理解我们的协作方式，需要新增一个仓库根目录的 `AGENTS.md` 作为统一入口文档，覆盖：目标、默认执行流程、角色边界、质量门禁、PR 规范、阻塞处理、常用命令与关键文件索引。

范围(需要做):
- 在仓库根目录新增 `AGENTS.md`
- 以“可执行规范”为导向组织内容，而非泛泛介绍
- 明确单 issue 模式与批量模式边界
- 明确默认自主流程（实现 -> 验证 -> commit -> push -> PR）与例外中断条件
- 明确 PR 描述必须完整填写模板
- 给出最小启动步骤与常用命令
- 提供关键文件导航（WORKFLOW、copilot-instructions、PR 模板、automation 脚本）
- 在 `README.md` 中增加到 `AGENTS.md` 的显式入口链接（如适用）

范围(不在范围):
- 不要求重构现有 automation 框架实现
- 不要求一次性改造所有历史文档结构

验收映射:
- 仓库根目录存在 AGENTS.md
- 文档可在 3-5 分钟内帮助新 agent 建立执行上下文
- 明确默认自动推进到 PR、用户仅最终审核
- 与现有规范不冲突（WORKFLOW.md、.github/copilot-instructions.md、.github/pull_request_template.md）
- PR 中说明该文档如何降低 agent 启动成本

### #14 chore: 新增 PR 模板完整性校验器

- backlog 路径: `.github/issues-backlog/task/20260602/add-pr-template-completeness-checker.md`
- issue 类型: `task`
- 建议 SDD 归档: `docs/sdd/10-detailed-design/01-architecture/20260602/`
- 建议模板: `00-template/architecture-design-template.md`
- 分类依据: 偏流程治理与架构编排
- issue 链接: https://github.com/handsondad/agentic-ai-for-coding/issues/14

设计目标:
- 该任务用于保证 PR 描述质量稳定，避免空白或占位文本进入审查流程。
- 已有 PR 模板，但仍可能出现章节缺失或仅保留占位文本的情况，影响审查效率与可追溯性。

范围(需要做):
- 实现 PR 描述完整性检查器（脚本或 action）
- 校验至少包含：背景、变更摘要、变更详情、测试计划、审查重点
- 校验“测试计划”必须包含已执行或未执行说明
- 集成到 CI 并提供本地运行命令

范围(不在范围):
- 不校验业务内容正确性
- 不替代人工代码审查

验收映射:
- PR 描述可自动检查模板完整性
- 未填写章节可在 CI 中失败提示
- 检查规则可配置且文档化
- 本地可先行执行同样检查

### #25 自动化基础与流程强化（含 direct commits）

- backlog 路径: `.github/issues-backlog/task/20260602/automation-foundation.md`
- issue 类型: `task`
- 建议 SDD 归档: `docs/sdd/10-detailed-design/01-architecture/20260602/`
- 建议模板: `00-template/architecture-design-template.md`
- 分类依据: 偏流程治理与架构编排
- issue 链接: https://github.com/handsondad/agentic-ai-for-coding/issues/25

设计目标:
- 该日期提交密度高，既有已关联 issue 的提交，也有未显式挂接 issue 的直接提交。
- 2026-06-02 是自动化基础设施快速迭代日，提交数量集中，部分变更已挂 issue（#6/#9/#11/#13-#19），部分仍是 direct commit，需要统一追溯口径。

范围(需要做):
- 梳理当日全部关键提交。
- 标注每条提交的 issue/PR 对应关系。
- 明确“已覆盖”和“待补规范”的治理结论。

范围(不在范围):
- 不改动既有功能实现。
- 不重开已合并 PR。

验收映射:
- 梳理 2026-06-02 当日提交与 issue/PR 对应关系。
- 对 direct commit 补齐追溯说明，避免治理盲区。
- 输出后续防回归约束。

### #15 chore: 建设离线评估集与回放脚本

- backlog 路径: `.github/issues-backlog/task/20260602/build-offline-eval-dataset-and-replay.md`
- issue 类型: `task`
- 建议 SDD 归档: `docs/sdd/10-detailed-design/01-architecture/20260602/`
- 建议模板: `00-template/architecture-design-template.md`
- 分类依据: 偏流程治理与架构编排
- issue 链接: https://github.com/handsondad/agentic-ai-for-coding/issues/15

设计目标:
- 该任务用于让 agent 策略优化可量化、可回归，避免依赖主观感受调整流程。
- 当前优化更多依赖线上试错，缺少稳定的离线回放基线。需要建立评估集与回放机制，支持策略迭代前后量化对比。

范围(需要做):
- 定义评估样本结构（issue 内容、预期输出、风险等级）
- 构建首批 20 条样本（feature/bug/task 覆盖）
- 实现回放脚本并输出标准报告
- 报告至少包含：成功率、平均时长、门禁通过率、失败分类分布

范围(不在范围):
- 不要求覆盖全部历史 issue
- 不做复杂可视化平台

验收映射:
- 建立不少于 20 条样本的离线评估集
- 提供一键回放脚本
- 输出评估报告（成功率、门禁通过率、失败分类）
- 支持策略变更前后对比

### #16 chore: 构建 Starter Kit 接入清单与模板化配置

- backlog 路径: `.github/issues-backlog/task/20260602/build-starter-kit-onboarding-pack.md`
- issue 类型: `task`
- 建议 SDD 归档: `docs/sdd/10-detailed-design/01-architecture/20260602/`
- 建议模板: `00-template/architecture-design-template.md`
- 分类依据: 偏流程治理与架构编排
- issue 链接: https://github.com/handsondad/agentic-ai-for-coding/issues/16

设计目标:
- 要把当前仓库沉淀为可复制的平台能力，需要把接入步骤、模板和验收路径产品化，而不是靠口口相传。
- 当前能力主要服务于本仓库，缺少面向“新项目快速接入”的标准包和接入手册。

范围(需要做):
- 梳理接入前置条件和环境初始化步骤
- 提供可复制模板文件集合
- 输出“30 分钟接入”操作指南
- 提供接入后的最小验收脚本

范围(不在范围):
- 不做跨组织权限治理平台
- 不做多云部署方案

验收映射:
- 提供新项目 30 分钟接入清单
- 抽象关键配置模板（WORKFLOW、PR 模板、issue backlog 约定）
- 提供最小接入验证步骤
- 文档说明多项目复用边界与可选项

### #17 chore: 新增统一质量门禁执行器（lint/type/test/checklist）

- backlog 路径: `.github/issues-backlog/task/20260602/build-unified-quality-gate-runner.md`
- issue 类型: `task`
- 建议 SDD 归档: `docs/sdd/10-detailed-design/01-architecture/20260602/`
- 建议模板: `00-template/architecture-design-template.md`
- 分类依据: 偏流程治理与架构编排
- issue 链接: https://github.com/handsondad/agentic-ai-for-coding/issues/17

设计目标:
- 该任务用于把分散的质量检查命令收敛成单一入口，提升 agent 执行稳定性与可审计性。
- 当前 lint、type、test、PR 描述检查分散在不同命令与脚本中。agent 在不同任务中容易出现执行顺序不一致、遗漏某一步或失败信息不完整的问题。 需要新增统一门禁执行器，作为开发与自动化流程的标准入口。

范围(需要做):
- 提供统一门禁入口（例如 `make gate` 或 `.github/automation/scripts/run-quality-gates.*`）
- 固化默认顺序：format-check -> lint -> type-check -> unit-test -> template-check
- 支持最小配置（跳过某阶段、仅运行某阶段）
- 失败时输出标准化摘要（步骤、退出码、关键日志）
- 更新 README/dev-guide 的门禁使用说明

范围(不在范围):
- 不改造业务代码逻辑
- 不在本任务内引入复杂分布式执行

验收映射:
- 仓库中存在统一门禁执行入口（脚本或命令）
- 门禁执行顺序固定且可配置
- 失败输出包含失败步骤与命令摘要
- 在 README 或 dev-guide 中补充使用方式

### #18 chore: 建立在线指标采集与周报模板

- backlog 路径: `.github/issues-backlog/task/20260602/setup-online-metrics-and-weekly-report.md`
- issue 类型: `task`
- 建议 SDD 归档: `docs/sdd/10-detailed-design/01-architecture/20260602/`
- 建议模板: `00-template/architecture-design-template.md`
- 分类依据: 偏流程治理与架构编排
- issue 链接: https://github.com/handsondad/agentic-ai-for-coding/issues/18

设计目标:
- 没有在线指标就无法知道流程是否在变好。需要先把关键指标采起来，再做策略优化。
- 当前流程可运行，但缺少统一可观测指标，难以判断改动后是否真的提升了效率和质量。

范围(需要做):
- 定义 KPI 字段和计算口径
- 增加执行日志到指标快照的抽取脚本
- 建立每周周报模板（Markdown）
- 在文档中明确指标查看方式

范围(不在范围):
- 不搭建复杂 BI 平台
- 不引入外部付费监控系统

验收映射:
- 定义并采集核心 KPI（成功率、一次通过率、Lead Time、返工率、门禁通过率）
- 输出每周指标快照文件
- 提供周报模板，包含趋势与Top阻塞原因
- 指标字段与失败分类结果可关联

### #19 chore: 标准化失败分类与修复建议输出

- backlog 路径: `.github/issues-backlog/task/20260602/standardize-failure-classification-and-fix-hints.md`
- issue 类型: `task`
- 建议 SDD 归档: `docs/sdd/10-detailed-design/03-business-logic/20260602/`
- 建议模板: `00-template/business-logic-design-template.md`
- 分类依据: 默认归类为业务逻辑域
- issue 链接: https://github.com/handsondad/agentic-ai-for-coding/issues/19

设计目标:
- 目前失败信息以日志文本为主，难以快速复盘和趋势统计。标准化分类是评估体系与自动恢复策略的前提。
- 自动化流程失败时，如果只给原始日志，团队无法快速判断问题归属，也无法持续优化。 需要统一失败分类与修复建议输出规范，支持复盘与指标统计。

范围(需要做):
- 定义失败分类枚举与判定规则
- 设计结构化失败输出格式（JSON/Markdown）
- 在 runner 关键失败路径接入分类逻辑
- 输出可直接贴入 issue/PR 的“失败闭环模板”
- 补充失败样本测试

范围(不在范围):
- 不做自动修复执行（仅输出建议）
- 不改动业务逻辑实现

验收映射:
- 定义统一失败分类（需求缺口/代码缺陷/环境阻塞/外部依赖）
- 每次失败输出必须包含失败步骤、关键错误、下一步建议
- 失败输出可用于 PR 描述或 issue 评论复用
- 至少覆盖 5 类典型失败样本并验证分类准确性

### #7 chore: 验证 automation runner 可端到端处理 GitHub Issue

- backlog 路径: `.github/issues-backlog/task/20260602/validate-automation-runner-e2e.md`
- issue 类型: `task`
- 建议 SDD 归档: `docs/sdd/10-detailed-design/01-architecture/20260602/`
- 建议模板: `00-template/architecture-design-template.md`
- 分类依据: 偏流程治理与架构编排
- issue 链接: https://github.com/handsondad/agentic-ai-for-coding/issues/7

设计目标:
- 该任务用于验证本仓库 .github/automation 下的本地自动化框架是否具备真实可用性。优先验证单条 issue 的端到端链路，不要求一次性覆盖多并发、复杂重试或全部异常场景。
- 当前仓库已经具备本地自动化执行框架，包括：Issue 轮询、worktree 创建、prompt 渲染、质量门禁、提交与 PR 流程。 在团队正式使用前，需要先通过一条真实 GitHub Issue 验证这条链路能否跑通，并明确最小可用配置、已知阻塞点和后续补强项。

范围(需要做):
- 使用一条真实的 GitHub Issue 触发本地自动化流程
- 验证 `ai-ready` 标签任务是否能被正确发现
- 验证 `.github/automation/` 下脚本和配置能否驱动完整执行链路
- 验证 worktree、prompt、quality gate、commit/push、PR 创建等关键步骤
- 记录试跑结果、日志、阻塞点与改进建议

范围(不在范围):
- 不要求一次性验证所有失败恢复分支
- 不要求覆盖多任务并发场景
- 不要求在本任务中重构自动化框架核心设计

验收映射:
- 可以从 GitHub Issues 轮询到带有 ai-ready 标签的任务
- 可以为目标任务创建独立 worktree 并渲染 issue prompt
- 可以执行 agent command、质量门禁和 commit/push 流程
- 可以在成功路径上创建 PR 或输出明确的阻塞信息
- 整个试跑过程有可追踪日志，便于团队复盘

### #26 Celery 重构与手动模式治理

- backlog 路径: `.github/issues-backlog/task/20260603/celery-manual-policy.md`
- issue 类型: `task`
- 建议 SDD 归档: `docs/sdd/10-detailed-design/01-architecture/20260603/`
- 建议模板: `00-template/architecture-design-template.md`
- 分类依据: 偏流程治理与架构编排
- issue 链接: https://github.com/handsondad/agentic-ai-for-coding/issues/26

设计目标:
- 该阶段以 Celery 重构、manual 阻断策略和文档治理为主，存在多次直接提交。
- 2026-06-03~2026-06-04 完成了自动化架构重构与手动流程治理增强，但提交路径以 direct commit 为主，需要补齐历史 issue 追溯。

范围(需要做):
- 建立该阶段 commit 清单与对应关系。
- 标注是否与近期规划 issue（#20-#23）相关。
- 输出后续“issue -> branch -> PR”强约束建议。

范围(不在范围):
- 不回滚既有重构结果。
- 不为历史 direct commit 强行补建虚拟 PR。

验收映射:
- 梳理 2026-06-03~2026-06-04 提交并建立追溯链路。
- 标注与现有 issue（#20-#23）和 direct commit 的关系。
- 给出 PR 一一对应治理建议。

### #20 前端页面 AI 生成与自动化测试流程设计（Issue 构建规范 + Skill/MCP 增强）

- backlog 路径: `.github/issues-backlog/task/20260604/frontend-ai-generation-testing-skill-mcp.md`
- issue 类型: `task`
- 建议 SDD 归档: `docs/sdd/10-detailed-design/01-architecture/20260604/`
- 建议模板: `00-template/architecture-design-template.md`
- 分类依据: 偏流程治理与架构编排
- issue 链接: https://github.com/handsondad/agentic-ai-for-coding/issues/20

设计目标:
- 该任务聚焦“如何让 AI 更稳定地产生可上线前端页面并完成自动化测试”，优先形成标准 issue 模板与执行约定。
- 当前前端需求在交给 AI 时，常出现“描述模糊 -> 产物风格不一致 -> 测试覆盖不足 -> 回归风险高”的问题。 需要把前端任务转成结构化 issue，让 agent 可按固定契约执行，并引入 Skill/MCP 提升稳定性。

范围(需要做):
- 设计前端类 issue 模板（页面型、组件型、重构型），至少包含：
- 页面目标与视觉方向
- 信息架构与交互要求
- 响应式与可访问性约束
- 测试策略（单测/组件测试/E2E）
- 性能与发布验收门槛
- 产出“前端 AI 任务描述指南”，明确怎么写 prompt 才能减少返工。
- 给出 Skill/MCP 增强建议：
- Skill 负责风格和流程约束
- MCP 负责外部系统能力（设计稿、测试平台、部署环境）
- 给出一个最小示例：从 issue 到页面生成、测试通过、可 PR 的完整链路。

范围(不在范围):
- 不实现完整设计系统重构。
- 不绑定某一具体 UI 框架版本升级。

验收映射:
- 输出一套前端任务 issue 模板，覆盖页面生成、测试、验收、回滚。
- 在仓库内提供最小可执行示例，能被 agent 按模板落地。
- 明确 Skill 与 MCP 的触发规则、职责边界和失败兜底策略。

### #22 基于 GitHub Actions 驱动自有 Docker 环境部署的可行性与落地方案

- backlog 路径: `.github/issues-backlog/task/20260604/github-actions-docker-deploy.md`
- issue 类型: `task`
- 建议 SDD 归档: `docs/sdd/10-detailed-design/04-ops-deployment/20260604/`
- 建议模板: `00-template/ops-deployment-design-template.md`
- 分类依据: 包含部署/运维/监控关键词
- issue 链接: https://github.com/handsondad/agentic-ai-for-coding/issues/22

设计目标:
- 目标是验证并落地“由 GitHub Actions 驱动自有 Docker 环境部署”的标准路径。
- 当前发布流程仍有人工步骤，部署一致性与可追踪性不足。希望通过 GitHub Actions 驱动私有 Docker 环境，实现标准化构建与部署。

范围(需要做):
- 设计部署链路：代码触发 -> 镜像构建 -> 镜像推送 -> 远端部署 -> 健康检查。
- 明确目标环境连接方式（SSH/Runner 自托管/远端 API）及风险。
- 输出 GitHub Actions workflow 样例：
- `build-and-push`
- `deploy`
- `rollback`
- 明确 secrets 策略：最小权限、轮换、审计。
- 形成部署验收清单（成功标准、超时策略、失败告警）。

范围(不在范围):
- 不做云厂商多环境编排（如 K8s 全量方案）。
- 不替换现有业务应用逻辑。

验收映射:
- 明确 GitHub Actions 驱动 Docker 部署的目标架构与安全边界。
- 产出可运行的 workflow 草案（构建、推送、部署、回滚）。
- 给出凭据管理、审计和失败恢复方案。

### #23 多 Code Agent 接入与 Generic OpenAI-compatible 模型服务替代方案

- backlog 路径: `.github/issues-backlog/task/20260604/multi-agent-openai-compatible-integration.md`
- issue 类型: `task`
- 建议 SDD 归档: `docs/sdd/10-detailed-design/01-architecture/20260604/`
- 建议模板: `00-template/architecture-design-template.md`
- 分类依据: 偏流程治理与架构编排
- issue 链接: https://github.com/handsondad/agentic-ai-for-coding/issues/23

设计目标:
- 目标是降低对单一商业 credits 的依赖，形成可持续的多 Agent + 自有模型服务策略。
- 当前团队主要依赖 GitHub Copilot credits，成本与额度存在上限。需要评估并接入公司 Generic OpenAI-compatible 模型服务，同时建立多 Agent 备选能力。

范围(需要做):
- 评估多 Agent 方案：
- Copilot
- Cline
- Claude Code
- OpenCode
- DeepSeek TUI
- Qoder
- Trae
- CodeBuddy
- 设计统一接入抽象：
- 模型配置（base_url、api_key、model）
- prompt/工具协议
- 失败重试与降级
- 形成“默认主链路 + 备选链路”策略。
- 提供 PoC：在同一任务上可切换两个以上 agent 或模型端点。

范围(不在范围):
- 不重写现有核心业务逻辑。
- 不做所有 Agent 的深度定制插件开发。

验收映射:
- 输出多 Agent 接入对比矩阵（能力、成本、接入复杂度、限制）。
- 明确 Generic OpenAI-compatible 接口接入方案与配置模板。
- 完成至少一个替代链路的可执行 PoC。

### #21 脚手架引入 MCP/Skill 的标准方案与 Copilot 云端 Agent 可用性验证

- backlog 路径: `.github/issues-backlog/task/20260604/scaffold-tooling-mcp-skill-copilot-cloud.md`
- issue 类型: `task`
- 建议 SDD 归档: `docs/sdd/10-detailed-design/01-architecture/20260604/`
- 建议模板: `00-template/architecture-design-template.md`
- 分类依据: 偏流程治理与架构编排
- issue 链接: https://github.com/handsondad/agentic-ai-for-coding/issues/21

设计目标:
- 目标是把“工具扩展能力”标准化，而不是每次靠人工临时拼装。
- 当前项目已具备基础自动化流程，但 MCP/Skill 的接入方式、边界和云端兼容性缺少统一规范，影响可复制性和团队扩展。

范围(需要做):
- 梳理脚手架内 MCP 与 Skill 的接入点：
- 配置位置
- 启用方式
- 权限边界
- 失败降级策略
- 建立“工具接入规范”：命名、版本、目录、文档要求、变更评审要求。
- 验证 GitHub Copilot 云端 Agent 下的可用性：
- 是否可加载本地/仓库级指令
- Skill 触发稳定性
- MCP 能力是否受限
- 远端运行的依赖前置条件
- 提供一个可复用的示例配置与验证步骤。

范围(不在范围):
- 不实现与业务系统深度耦合的专用 MCP。
- 不替代现有 manual/automation 主流程。

验收映射:
- 明确 MCP 与 Skill 的引入路径、目录规范和版本策略。
- 完成 Copilot 云端 Agent 可用性验证清单与结论。
- 输出脚手架层面的最小集成示例与运维建议。

### #28 建立 SDD（详细设计驱动开发）文档规范与工作流

- backlog 路径: `.github/issues-backlog/task/20260605/sdd-workspace-spec-and-workflow.md`
- issue 类型: `task`
- 建议 SDD 归档: `docs/sdd/10-detailed-design/01-architecture/20260605/`
- 建议模板: `00-template/architecture-design-template.md`
- 分类依据: 偏流程治理与架构编排
- issue 链接: https://github.com/handsondad/agentic-ai-for-coding/issues/28

设计目标:
- 基于 SDD（详细设计驱动开发）建立统一入口规范，解决文档分散、状态不可追踪、Issue/PR 关联弱的问题。
- 当前详细设计文档缺少统一的目录结构、模板选型规则和状态追踪字段，导致团队协作中出现“文档位置不一致、命名不统一、Issue/PR 难追溯”的问题。 需要建立 SDD 工作区总规范，统一从模板到设计文档再到 Issue/PR 回填的闭环。

范围(需要做):
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

范围(不在范围):
- 不在本 issue 中完成所有历史设计文档迁移。
- 不引入新的文档平台或外部知识库系统。
- 不替代业务实现类技术方案评审流程。

验收映射:
- SDD 目录结构、模板选型、命名与状态字段规范形成统一文档并可执行。
- 详细设计文档按领域与日期目录管理，且能追踪 issue/pr 链接。
- 提供 DoD 与 sdd-index 同步规则，支持团队审计和持续维护。
