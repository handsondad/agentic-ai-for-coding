"""Orchestration 数据模型。"""

from __future__ import annotations

from dataclasses import dataclass
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
    dry_run: bool
    use_skills: bool
    skills_file: Path | None
    skill_commands: dict[str, str]


@dataclass(slots=True)
class GitHubIssue:
    """归一化后的 GitHub Issue 模型。"""

    number: int
    title: str
    body: str
    state: str
    html_url: str
    labels: list[str]

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
    """生成可用于分支名的 slug。"""
    normalized = "".join(ch.lower() if ch.isalnum() else "-" for ch in text)
    while "--" in normalized:
        normalized = normalized.replace("--", "-")
    normalized = normalized.strip("-") or "issue"
    return normalized[:max_length].strip("-") or "issue"
