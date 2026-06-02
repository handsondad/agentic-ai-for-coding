# AGENTS.md

本文件是本仓库的统一 AI for Coding 入口。任意 code agent 进入仓库后，优先阅读本文件，再按文末索引跳到更细的规范和工作流文档。

## 1. 我们在做什么

本仓库的目标是把单个 GitHub Issue 变成一条可自动推进的执行链路：理解需求、实现代码、验证质量、提交 commit、推送分支、创建 PR，最后只把审查留给人。

## 2. 角色与边界

用户负责定义问题、验收标准和最终 PR 审核。
Agent 负责把工作连续推进到可审查状态，除非遇到权限、凭据、网络、环境缺失或需求冲突等明确阻塞。

默认原则：不要把常规步骤拆成一连串请求用户确认的动作。先做，再验证，再汇报。

## 3. 默认执行流程

单 issue 默认按以下顺序执行：

1. 阅读 Issue、WORKFLOW.md、.github/copilot-instructions.md 和相关上下文。
2. 创建或切换到对应分支 / worktree。
3. 实现代码与测试，优先覆盖验收标准。
4. 运行格式化、lint、单测和必要的针对性验证。
5. 更新相关文档、运行记录或模板。
6. 提交 commit。
7. 推送分支并创建 PR。
8. 将结果留给用户做最终 PR 审核。

批量模式只在明确需要并发时使用；默认还是单 issue 串行推进。

## 4. 何时必须中断并回到用户

只有在这些情况下才停止自动推进：

- 需要用户提供权限、token、登录态或其他凭据。
- 远端网络、代理或仓库权限阻止继续执行。
- 需求本身冲突，且无法从本地上下文推断正确方向。
- 继续执行会覆盖或破坏用户现有未提交改动。

如果是普通失败，先给出最小可执行修复建议，再继续修复本地问题。

## 5. 质量门禁

默认至少通过这些检查：

- 格式化 / lint
- 单元测试
- 与变更相关的针对性验证
- PR 描述完整性检查

如有集成测试、安全扫描或额外门禁，按 Issue 和 WORKFLOW 的要求补充。

## 6. PR 规范

PR 描述必须完整填写模板内容，尤其是：

- 背景
- 变更摘要
- 变更详情
- 测试计划
- 审查重点

测试计划要明确写出已执行项和未执行项。不要只写一句“已测试通过”。

## 7. 快速开始

新 agent 建议按这个顺序建立上下文：

1. 读本文件。
2. 读 [WORKFLOW.md](WORKFLOW.md)。
3. 读 [.github/copilot-instructions.md](.github/copilot-instructions.md)。
4. 读 [.github/pull_request_template.md](.github/pull_request_template.md)。
5. 需要时查看 [.github/automation/](.github/automation/) 下的脚本与服务。

常用命令：

- `make gate`
- `make gate-full`
- `make pr-check`
- `make eval-replay`
- `make metrics-snapshot`

## 8. 关键文件索引

- [WORKFLOW.md](WORKFLOW.md)：运行时工作规范与 hooks 配置。
- [.github/copilot-instructions.md](.github/copilot-instructions.md)：仓库级编码与自动化执行规范。
- [.github/pull_request_template.md](.github/pull_request_template.md)：PR 描述模板。
- [.github/automation/](.github/automation/)：自动化 runner、质量门禁、评估与指标脚本。
- [docs/dev-guide.md](docs/dev-guide.md)：本地开发和验证入口。
- [docs/ai-coding-infra-executable-blueprint.md](docs/ai-coding-infra-executable-blueprint.md)：基础设施蓝图与任务路线图。
