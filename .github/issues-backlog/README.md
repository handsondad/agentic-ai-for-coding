# Issues Backlog 管理约定

该目录用于存放“尚未发布到 GitHub 的 Issue 草稿”，作为 AI/人工协作的统一输入池。

## 1) 目录结构

```text
.github/issues-backlog/
├── README.md
├── TEMPLATE.md
├── feature/
├── bug/
└── task/
```

- `feature/`：功能需求类 backlog
- `bug/`：缺陷修复类 backlog
- `task/`：工程任务类 backlog

## 2) 命名规则

- 文件名必须使用：`YYYYMMDD-短标题.md`
- 示例：`20260528-add-streaming-chat.md`

## 3) 元数据（文件头）

每个 backlog 文件必须包含 YAML Front Matter，最少包含：

- `title`（标题）
- `type`（feature/bug/task）
- `status`（draft/ready/published）
- `labels`（标签数组）
- `priority`（优先级）
- `assignee`（负责人，可为空）
- `acceptance_criteria`（验收标准数组）
- `ai_context`（AI 上下文）
- `related_docs`（关联文档数组）

发布后补充：

- `github_issue_number`
- `github_issue_url`

## 4) 状态流转

- `draft`：AI/人工初稿，可继续补充
- `ready`：信息完整，可发布到 GitHub
- `published`：已发布到 GitHub，且已回写编号与链接

只允许：`draft -> ready -> published`。

## 5) 发布流程（单条）

1. 从 backlog 中选择 `status: ready` 的文件
2. 按文件内容在 GitHub 创建 Issue（推荐使用 `gh`）
3. 发布成功后，回写本地文件：
   - `status: published`
   - `github_issue_number`
   - `github_issue_url`

参考命令（示例）：

```bash
# 从文件内容整理标题、正文后创建 Issue
# 注意：labels 使用逗号分隔，需与仓库标签一致
gh issue create \
  --title "feat: 支持流式对话响应" \
  --label "feature,ai-ready" \
  --body-file .github/issues-backlog/feature/20260528-add-streaming-chat.md
```

## 6) 批量发布约定

一次批量发布仅允许同一组任务：

- 同一优先级，或
- 同一里程碑

避免一次性创建大量低质量 Issue。

## 7) 质量门禁（进入 ready 前必须满足）

必须完整填写以下信息：

- 背景
- 范围
- 完成标准
- 优先级
- 标签

任一缺失，保持 `draft`。

## 8) 维护机制

- 每周清理过期 `draft`
- 每个迭代结束时核对 `published` 与 GitHub Issue 实际状态
- 发现不一致时立即回写修正
