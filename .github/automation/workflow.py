"""WORKFLOW.md 解析与运行时配置构建。"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml

try:
    from .models import GitHubRepo, RuntimeSettings, WorkflowHooks
except ImportError:
    from models import GitHubRepo, RuntimeSettings, WorkflowHooks

_FRONT_MATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)


class WorkflowParseError(ValueError):
    """WORKFLOW.md 解析失败。"""


def load_runtime_settings(workflow_path: Path) -> RuntimeSettings:
    """加载 WORKFLOW.md 并构建运行时设置。"""
    front_matter, prompt_template = parse_workflow(workflow_path)

    tracker = _get_map(front_matter, "tracker")
    polling = _get_map(front_matter, "polling", required=False)
    agent = _get_map(front_matter, "agent", required=False)
    workspace = _get_map(front_matter, "workspace", required=False)
    hooks_map = _get_map(front_matter, "hooks", required=False)

    token = _resolve_env_like(_required_str(tracker, "api_key", "tracker.api_key"))
    repo_raw = _resolve_env_like(_required_str(tracker, "repo", "tracker.repo"))
    repo = _parse_repo(repo_raw)

    active_labels = _as_label_list(tracker.get("active_states", ["ai-ready"]))
    terminal_labels = _as_label_list(tracker.get("terminal_states", ["done", "cancelled"]))

    poll_interval_ms = int(polling.get("interval_ms", 30000))
    max_concurrent_agents = int(agent.get("max_concurrent_agents", 1))

    repo_root = Path(os.getenv("AUTOMATION_REPO_ROOT", os.getcwd())).resolve()
    workspace_root_raw = workspace.get("root", "$AUTOMATION_WORKSPACE_ROOT")
    workspace_root = Path(_resolve_env_like(str(workspace_root_raw), allow_missing=True)).resolve()

    if str(workspace_root_raw).startswith("$") and workspace_root == Path(".").resolve():
        workspace_root = repo_root / ".worktrees"

    hooks = WorkflowHooks(
        after_create=_opt_str(hooks_map.get("after_create")),
        before_run=_opt_str(hooks_map.get("before_run")),
        after_run=_opt_str(hooks_map.get("after_run")),
    )

    quality_commands = _parse_quality_commands(
        os.getenv("AUTOMATION_QUALITY_COMMANDS", "make lint;;make test")
    )
    agent_command = _opt_str(os.getenv("AUTOMATION_AGENT_COMMAND"))
    base_branch = os.getenv("GITHUB_BASE_BRANCH", "main").strip() or "main"
    dry_run = _parse_bool(os.getenv("AUTOMATION_DRY_RUN", "false"))
    use_skills = _parse_bool(os.getenv("AUTOMATION_USE_SKILLS", "true"))

    skills_file_raw = os.getenv(
        "AUTOMATION_SKILLS_FILE",
        ".github/automation/skills/skills.yaml",
    ).strip()
    skills_file = (repo_root / skills_file_raw).resolve()
    skill_commands = _load_skill_commands(skills_file, enabled=use_skills)

    return RuntimeSettings(
        github_token=token,
        github_repo=repo,
        active_labels=active_labels,
        terminal_labels=terminal_labels,
        poll_interval_ms=poll_interval_ms,
        max_concurrent_agents=max_concurrent_agents,
        repo_root=repo_root,
        workspace_root=workspace_root,
        workflow_path=workflow_path.resolve(),
        prompt_template=prompt_template,
        hooks=hooks,
        agent_command=agent_command,
        quality_commands=quality_commands,
        base_branch=base_branch,
        dry_run=dry_run,
        use_skills=use_skills,
        skills_file=skills_file if use_skills else None,
        skill_commands=skill_commands,
    )


def parse_workflow(workflow_path: Path) -> tuple[dict[str, Any], str]:
    """解析 WORKFLOW.md 的 YAML front matter 与正文模板。"""
    text = workflow_path.read_text(encoding="utf-8")
    match = _FRONT_MATTER_PATTERN.match(text)

    if match is None:
        raise WorkflowParseError("WORKFLOW.md 缺少 YAML front matter")

    front_matter_raw, prompt_template = match.groups()

    try:
        parsed = yaml.safe_load(front_matter_raw)
    except yaml.YAMLError as exc:
        raise WorkflowParseError(f"WORKFLOW front matter YAML 解析失败: {exc}") from exc

    if not isinstance(parsed, dict):
        raise WorkflowParseError("WORKFLOW front matter 必须是对象")

    return parsed, prompt_template.strip()


def _required_str(source: dict[str, Any], key: str, name: str) -> str:
    value = source.get(key)
    if not isinstance(value, str) or not value.strip():
        raise WorkflowParseError(f"缺少配置: {name}")
    return value.strip()


def _get_map(
    source: dict[str, Any],
    key: str,
    required: bool = True,
) -> dict[str, Any]:
    value = source.get(key)
    if value is None:
        if required:
            raise WorkflowParseError(f"缺少配置段: {key}")
        return {}
    if not isinstance(value, dict):
        raise WorkflowParseError(f"配置段必须是对象: {key}")
    return value


def _resolve_env_like(value: str, allow_missing: bool = False) -> str:
    if not value.startswith("$"):
        return value

    env_name = value[1:]
    env_value = os.getenv(env_name)
    if env_value is None:
        if allow_missing:
            return "."
        raise WorkflowParseError(f"环境变量未设置: {env_name}")
    return env_value


def _parse_repo(value: str) -> GitHubRepo:
    parts = value.split("/", maxsplit=1)
    if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
        raise WorkflowParseError("tracker.repo 必须是 owner/repo 格式")
    return GitHubRepo(owner=parts[0].strip(), name=parts[1].strip())


def _as_label_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        raise WorkflowParseError("标签状态配置必须为列表")

    labels = [str(item).strip().lower() for item in value if str(item).strip()]
    if not labels:
        raise WorkflowParseError("标签状态配置不能为空")
    return labels


def _parse_quality_commands(raw: str) -> list[str]:
    commands = [item.strip() for item in raw.split(";;") if item.strip()]
    return commands or ["make lint", "make test"]


def _parse_bool(raw: str) -> bool:
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _opt_str(raw: Any) -> str | None:
    if raw is None:
        return None
    value = str(raw).strip()
    return value or None


def _load_skill_commands(skills_file: Path, enabled: bool) -> dict[str, str]:
    if not enabled:
        return {}
    if not skills_file.exists():
        return {}

    try:
        parsed = yaml.safe_load(skills_file.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise WorkflowParseError(f"skills 文件 YAML 解析失败: {exc}") from exc

    if parsed is None:
        return {}
    if not isinstance(parsed, dict):
        raise WorkflowParseError("skills 文件顶层必须是对象")

    skills_node = parsed.get("skills")
    if skills_node is None:
        return {}
    if not isinstance(skills_node, dict):
        raise WorkflowParseError("skills 字段必须是对象")

    commands: dict[str, str] = {}
    for step_name, config in skills_node.items():
        if not isinstance(step_name, str):
            continue
        if not isinstance(config, dict):
            continue

        command = config.get("command")
        if not isinstance(command, str):
            continue

        stripped = command.strip()
        if stripped:
            commands[step_name.strip().lower()] = stripped

    return commands
