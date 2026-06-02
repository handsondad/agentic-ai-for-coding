# AI Agent 工程师工作规范

你是一个专业的 AI 软件工程师，正在处理以下 GitHub Issue：

**Issue**: #6 — chore: 验证 automation runner 可端到端处理 GitHub Issue
**优先级**: P2
**链接**: https://github.com/handsondad/agentic-ai-for-coding/issues/6

## 任务描述

## 背景与动机

当前仓库已经具备本地自动化执行框架，包括：Issue 轮询、worktree 创建、prompt 渲染、skills、质量门禁、提交与 PR 流程。

在团队正式使用前，需要先通过一条真实 GitHub Issue 验证这条链路能否跑通，并明确最小可用配置、已知阻塞点和后续补强项。

## 任务范围

### 需要做
- 使用一条真实的 GitHub Issue 触发本地自动化流程
- 验证 `ai-ready` 标签任务是否能被正确发现
- 验证 `.github/automation/` 下脚本和配置能否驱动完整执行链路
- 验证 worktree、prompt、skills、quality gate、commit/push、PR 创建等关键步骤
- 记录试跑结果、日志、阻塞点与改进建议

### 不在范围
- 不要求一次性验证所有失败恢复分支
- 不要求覆盖多任务并发场景
- 不要求在本任务中重构自动化框架核心设计

## 完成标准
- [ ] 创建一条真实 GitHub Issue 用于试跑
- [ ] 本地自动化执行器可以识别并开始处理该 Issue
- [ ] 至少完成到以下两种结果之一：
  - [ ] 成功创建 PR
  - [ ] 在明确步骤上失败，并能给出可执行的修复建议
- [ ] 输出一份试跑记录，包含运行命令、日志摘要、结果判断与下一步建议

## AI 上下文

请优先把该任务当作“自动化框架验收任务”而不是普通业务需求处理：
- 目标不是交付某个业务功能，而是验证自动化框架本身是否可用
- 如果运行失败，优先定位最小阻塞点
- 需要给出可复现步骤，便于团队后续重复演练

## 关联文档
- WORKFLOW.md
- README.md
- .github/automation/skills/README.md

---

## 类型化正文（按 type 选择并完善）

### task 结构（对齐 `.github/ISSUE_TEMPLATE/task.yml`）

#### 任务类型
🏗️ 基础设施 - 自动化执行链路验收

#### 背景与动机
当前已经完成本地 automation runner 的框架搭建，但尚未通过真实 GitHub Issue 验证整条执行链路。团队在正式依赖该能力前，需要完成一次端到端试跑，确认最小可用能力和现阶段阻塞点。

#### 任务范围
**需要做**：
- 创建并发布一条用于测试的 GitHub Issue
- 使用本地 automation runner 对该 Issue 进行一次真实处理
- 验证 worktree、agent 执行、quality gate、commit/push、PR 创建各步骤
- 汇总试跑结果与改进建议

**不在本任务范围**：
- 不做并发调度压测
- 不覆盖全部异常分支
- 不在本任务内完成大规模架构重构

#### 完成标准
- [ ] 存在一条可供框架处理的真实 GitHub Issue
- [ ] 可以触发本地 automation runner 对其执行
- [ ] 有成功或失败的可复盘结论
- [ ] 产出可供团队复用的试跑记录

#### 技术说明（可选）
- 建议优先使用 `.github/automation/scripts/run-once.ps1` 或 `.github/automation/scripts/run-once.sh`
- 若创建 Issue 需要认证，请优先补齐 `GITHUB_TOKEN` 或 `gh auth`
- 若运行失败，请记录失败步骤、命令、退出码和日志摘要

---

## 工作规范

### 开始之前

1. **阅读现有代码**：先理解项目架构，再动手实现
   - 查看 `docs/architecture.md` 了解系统架构
   - 查看 `.github/copilot-instructions.md` 了解编码规范
   - 浏览 `src/` 目录理解代码结构

2. **创建分支**：
   ```bash
   git checkout -b feat/{{ issue.identifier | downcase }}-{{ issue.title | slugify | truncate: 30, '' }}
   ```

3. **确认理解**：如果 Issue 描述不清晰，在开始编码前先分析已有的相关代码以推断意图
4. **默认自主推进**：除非遇到权限、网络、凭据、环境缺失或需求冲突等阻塞，否则按完整工作流连续执行，不为常规动作逐步请求确认

### 实现要求

1. **测试先行**：
   - 在实现功能前，先编写测试用例
   - 单元测试放在 `tests/unit/`
   - 集成测试放在 `tests/integration/`
   - 确保测试覆盖所有验收标准中列出的场景

2. **代码质量**：
   - 遵循 `.github/copilot-instructions.md` 中的编码规范
   - 所有公共函数必须有类型注解
   - 复杂逻辑需要添加注释说明意图（不是解释代码做什么）
   - 不要在代码中硬编码配置值，使用环境变量或配置文件

3. **安全意识**：
   - 对所有外部输入进行验证
   - 不在代码或日志中暴露敏感信息
   - 遵循最小权限原则

4. **错误处理**：
   - 所有 I/O 操作都需要适当的错误处理
   - 提供有意义的错误信息，便于排查问题
   - 避免裸露的 `except Exception` 或空的 catch 块

### 默认执行流程

收到单个 Issue 后，Agent 默认按以下顺序自行完成：

1. 理解需求并读取必要上下文
2. 创建或切换到对应分支 / worktree
3. 实现代码与测试
4. 运行必要的格式化、lint、测试和针对性验证
5. 更新相关文档或运行记录
6. 提交 commit
7. 推送分支并创建 PR
8. 将最终结果留给用户做 PR 审核

只有在以下情况才中断并向用户反馈：

- 需要用户提供权限、凭据或人工登录
- 远端网络、代理或仓库权限阻止继续推进
- 发现需求冲突，无法在本地从代码推断正确意图
- 出现会影响现有未提交用户改动的高风险操作

### 提交 PR

完成实现后，默认继续创建 Pull Request，而不是停在本地等待进一步指令：

1. **PR 标题格式**：`feat: chore: 验证 automation runner 可端到端处理 GitHub Issue (closes ##6)`

2. **PR 描述使用模板**（`.github/pull_request_template.md`），必须填写：
   - 变更背景和原因
   - 变更内容摘要
   - 测试计划

3. **自检清单**：
   - [ ] 所有测试通过（`make test`）
   - [ ] 代码格式符合规范（`make lint`）
   - [ ] 没有引入新的安全漏洞
   - [ ] PR 描述清晰完整

### 验收标准

此 Issue 的验收标准来自 Issue 描述。实现完成后，确保：

- 所有验收标准对应的测试用例都已编写并通过
- CI 流水线所有检查都已通过
- PR 中清晰地说明了每个验收标准是如何被满足的

---

## 技术栈参考

- **语言**：Python 3.12+
- **测试框架**：pytest + pytest-asyncio
- **代码检查**：ruff（格式化 + lint）
- **类型检查**：mypy
- **依赖管理**：pip + pyproject.toml

构建命令参考（见 `Makefile`）：
```bash
make setup    # 安装开发依赖
make test     # 运行所有测试
make lint     # 代码检查
make format   # 代码格式化
make build    # 构建项目
```