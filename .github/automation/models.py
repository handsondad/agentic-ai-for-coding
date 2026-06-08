"""Orchestration 数据模型。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(slots=True)
class GitHubRepo:
    """GitHub 仓库标识。"""

    owner: str
    name: str

    @property
    def full_name(self) -> str:
        """返回 owner/name 格式。"""
        return f"{self.owner}/{self.name}"


@dataclass(slots=True)
class WorkflowHooks:
    """WORKFLOW hooks 配置。"""

    after_create: str | None = None
    before_run: str | None = None
    after_run: str | None = None


@dataclass(slots=True)
class RuntimeSettings:
    """调度运行时设置。"""

    github_token: str
    github_repo: GitHubRepo
    active_labels: list[str]
    terminal_labels: list[str]
    poll_interval_ms: int
    max_concurrent_agents: int
    repo_root: Path
    workspace_root: Path
    workflow_path: Path
    prompt_template: str
    hooks: WorkflowHooks
    agent_command: str | None
    quality_commands: list[str]
    base_branch: str
    metrics_file: Path
    dry_run: bool
    celery_broker_url: str
    celery_result_backend: str
    celery_queue: str


@dataclass(slots=True)
class GitHubIssue:
    """归一化后的 GitHub Issue 模型。"""

    number: int
    title: str
    body: str
    state: str
    html_url: str
    labels: list[str]
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def identifier(self) -> str:
        """返回 issue 标识符。"""
        return f"#{self.number}"


@dataclass(slots=True)
class QualityGateResult:
    """质量门禁结果。"""

    command: str
    exit_code: int
    output: str


@dataclass(slots=True)
class PipelineResult:
    """Issue 执行流水线结果。"""

    issue_number: int
    branch_name: str
    worktree_path: Path
    quality_results: list[QualityGateResult]
    pr_url: str | None = None
    changed: bool = False


def slugify(text: str, max_length: int = 48) -> str:
    """生成可用于分支名的 slug，确保使用英文字符。

    将中文标题转换为英文描述或通用标识符，避免 GitHub 隐藏字符警告。
    """
    # 常见中文到英文的映射
    chinese_to_english = {
        "多": "multi",
        "接入": "integration",
        "支持": "support",
        "优化": "optimization",
        "修复": "fix",
        "更新": "update",
        "添加": "add",
        "实现": "implement",
        "配置": "config",
        "管理": "management",
        "工具": "tool",
        "测试": "test",
        "文档": "docs",
        "API": "api",
        "数据": "data",
        "用户": "user",
        "系统": "system",
        "服务": "service",
        "模型": "model",
        "代码": "code",
        "脚本": "script",
        "自动化": "automation",
        "流程": "workflow",
        "集成": "integration",
    }

    # 先尝试替换常见中文词汇
    result = text
    for chinese, english in chinese_to_english.items():
        result = result.replace(chinese, english)

    # 将非字母数字字符转换为连字符
    normalized = "".join(ch.lower() if ch.isalnum() else "-" for ch in result)

    # 清理多余的连字符
    while "--" in normalized:
        normalized = normalized.replace("--", "-")

    # 移除首尾连字符
    normalized = normalized.strip("-") or "issue"

    # 截断到指定长度
    return normalized[:max_length].strip("-") or "issue"
