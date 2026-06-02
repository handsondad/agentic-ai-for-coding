# Automation Runner E2E 试跑记录

## 背景

本次试跑用于验证 issue `#6` 对应的自动化框架验收链路，目标是确认：

- 单 issue 准备入口是否可直接使用
- worktree 和 prompt 是否能正确生成
- Windows 企业环境下最小可用前置条件是什么
- 当前明确阻塞点和后续补强项分别是什么

## 试跑环境

- 日期：2026-06-02
- 操作系统：Windows
- Shell：Windows PowerShell 5.1
- Python：3.12.12
- 仓库：`handsondad/agentic-ai-for-coding`

## 本次改动

为降低单 issue 工作流的启动门槛，本次补充了以下兼容行为：

1. `.github/automation/scripts/prepare-single-issue.py`
   - 在 Windows 上自动回退读取 User 级别环境变量：
     - `GITHUB_TOKEN`
     - `GITHUB_REPOSITORY`
     - `AUTOMATION_CA_BUNDLE`
     - `AUTOMATION_TLS_NO_VERIFY`
2. `.github/automation/scripts/prepare-single-issue.ps1`
   - 同样增加 User 级别环境变量回退
   - 修复 PowerShell 5.1 动态读取环境变量时的语法兼容问题
3. `.github/automation/scripts/workspace-hooks.py`
   - 新增跨平台 workspace hook helper，统一处理：
     - `after-create`
     - `before-run`
     - `after-run`
4. `.github/automation/workflow.py` + `WORKFLOW.md`
   - 默认 hooks 改为调用 Python helper
   - hook 命令支持渲染 `{{ repo_root }}` 和 `{{ base_branch }}`，避免依赖新 worktree 内部的相对脚本路径
5. `tests/unit/test_prepare_single_issue.py`
   - 增加 Windows User 环境变量回退单测
6. `tests/unit/test_workspace_hooks.py` / `tests/unit/test_workflow_loader.py`
   - 增加 hook helper 行为测试和 hook 模板渲染测试

## 执行命令

### 1. 单测和 lint

```powershell
python -m pytest C:\Xiuqin\code\agentic-ai-for-coding\tests\unit\test_prepare_single_issue.py -v
python -m ruff check C:\Xiuqin\code\agentic-ai-for-coding\.github\automation\scripts\prepare-single-issue.py C:\Xiuqin\code\agentic-ai-for-coding\tests\unit\test_prepare_single_issue.py
```

结果：通过。

### 2. 不手工注入环境变量，直接运行单 issue 准备脚本

```powershell
$env:GITHUB_TOKEN=$null
$env:GITHUB_REPOSITORY=$null
$env:AUTOMATION_CA_BUNDLE=$null
$env:AUTOMATION_TLS_NO_VERIFY=$null

powershell -NoProfile -ExecutionPolicy Bypass -File \
  C:\Xiuqin\code\agentic-ai-for-coding\.github\automation\scripts\prepare-single-issue.ps1 \
  -Workflow C:\Xiuqin\code\agentic-ai-for-coding\WORKFLOW.md \
  -IssueFile C:\Xiuqin\code\agentic-ai-for-coding\.github\issues-backlog\task\20260602\validate-automation-runner-e2e.md
```

结果：脚本成功从 Windows User 环境读取必需变量，成功创建 worktree 和 prompt。

### 3. 验证跨平台 hooks 在 Windows 下可用

本次验证使用临时本地 issue 文件触发新的 worktree 准备流程，验证点如下：

- `prepare-single-issue.ps1` 能正常调用默认 hooks
- hooks 能从主仓库绝对路径调用 `workspace-hooks.py`
- Windows 下不再因为 POSIX shell 语法报错

结果：通过。成功输出新的 worktree 和 prompt 路径，且不再出现 PowerShell 解析 `if [ -f ... ]` 的错误。

## 关键输出摘要

成功输出了以下结果：

- `Prepared source: file:...validate-automation-runner-e2e.md`
- `Issue title: chore: 验证 automation runner 可端到端处理 GitHub Issue`
- `Branch: ai/issue-7-chore-验证-automation-runner-可端到端处理-gi`
- `Worktree: C:\Xiuqin\code\agentic-ai-for-coding\.worktrees\issue-7`
- `Prompt: C:\Xiuqin\code\agentic-ai-for-coding\.worktrees\issue-7\.automation\issue-prompt.md`

说明：本次命令使用的是本地 backlog 文件，因此生成的分支和 worktree 对应本地文件 frontmatter 中的 `github_issue_number: '7'`。

## 结果判断

### 已验证成功

1. 单 issue 入口可以在 Windows PowerShell 5.1 下直接使用
2. `prepare-single-issue` 不再依赖调用方手工注入 `GITHUB_TOKEN` 和 `GITHUB_REPOSITORY`
3. worktree 创建和 prompt 渲染链路可正常完成
4. 默认 hooks 已改为跨平台 Python helper，Windows 下不再依赖 Git Bash

## 建议的下一步

### 团队使用建议

1. 个人单 issue 场景：优先使用 `prepare-single-issue.ps1/.sh`
2. 批量调度场景：继续使用 `run-once.ps1/.sh` 或 `run-forever.ps1/.sh`
3. 如需自定义 hooks，优先继续使用 Python helper 或保持 shell 语法跨平台一致，避免重新引入平台差异

## 当前结论

本次试跑已经满足“可以触发本地 automation runner 对其执行，并产出可复盘结论”的验收目标：

- 单 issue 准备链路已验证可用
- Windows User 环境变量回退已验证可用
- 默认 hooks 的跨平台兼容问题已修复，并完成真实验证