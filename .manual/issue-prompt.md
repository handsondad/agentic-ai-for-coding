# AI Agent 工程师工作规范

你是一个专业的 AI 软件工程师，正在处理以下 GitHub Issue：

**Issue**: #23 — 多 Code Agent 接入与 Generic OpenAI-compatible 模型服务替代方案
**优先级**: P2
**链接**: https://github.com/handsondad/agentic-ai-for-coding/issues/23

## 任务描述

## 背景与动机

当前团队主要依赖 GitHub Copilot credits，成本与额度存在上限。需要评估并接入公司 Generic OpenAI-compatible 模型服务，同时建立多 Agent 备选能力。

## 任务范围

### 需要做
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

### 不在范围
- 不重写现有核心业务逻辑。
- 不做所有 Agent 的深度定制插件开发。

## 完成标准
- [ ] 提交多 Agent 对比与选型报告。
- [ ] 提交 Generic OpenAI-compatible 配置与接入说明。
- [ ] 至少 1 条替代链路跑通并有结果记录。
- [ ] 输出推荐默认配置与治理建议（限额、审计、回退）。

## AI 上下文

- 重点关注成本、稳定性、可控性。
- 保持与现有 issue/worktree/quality gate 流程兼容。

## 关联文档

- AGENTS.md
- WORKFLOW.md
- docs/ai-coding-infra-executable-blueprint.md

---

## 任务类型

架构选型 + 平台集成 + 成本治理

## 技术说明（可选）

- 推荐定义统一环境变量契约，避免 agent 切换时修改业务代码。

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

1. **PR 标题格式**：`feat: 多 Code Agent 接入与 Generic OpenAI-compatible 模型服务替代方案 (closes ##23)`

2. **PR 描述使用模板**（`.github/pull_request_template.md`），必须填写：
   - 变更背景和原因
   - 变更内容摘要
   - 测试计划
  - 使用 `gh` 创建/编辑 PR 时必须使用 `--body-file`，不要使用 `--body` 直接传多行内容。
  - 手动模式建议使用 `.github/manual/scripts/create-pr.py|.ps1|.sh` 创建 PR。

3. **自检清单**：
   - [ ] 所有测试通过（`make test`）
  - [ ] 严格质量门禁通过（`python .github/automation/scripts/quality-gate.py --mode full`）
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