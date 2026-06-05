"""Prepare a single issue workspace for manual/agent-driven development."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

_FRONT_MATTER_PATTERN = re.compile(r"^\ufeff?---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)


class PrepareIssueError(RuntimeError):
    """Raised when single-issue preparation cannot continue."""


@dataclass(slots=True)
class GitHubIssue:
    """Normalized issue model used by manual preparation mode."""

    number: int
    title: str
    body: str
    state: str
    html_url: str
    labels: list[str]

    @property
    def identifier(self) -> str:
        return f"#{self.number}"


@dataclass(slots=True)
class RuntimeSettings:
    """Runtime settings required for single issue preparation."""

    github_token: str
    github_repo: str
    repo_root: Path
    workspace_root: Path
    workflow_path: Path
    prompt_template: str
    base_branch: str


@dataclass(slots=True)
class PreparedIssueContext:
    """Prepared local context for an issue."""

    issue: GitHubIssue
    branch_name: str
    worktree_path: Path
    prompt_path: Path
    source: str


def _load_windows_user_env_fallback(*names: str) -> None:
    if os.name != "nt":
        return

    try:
        import winreg
    except ImportError:
        return

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            for name in names:
                if os.getenv(name):
                    continue
                try:
                    value, _ = winreg.QueryValueEx(key, name)
                except OSError:
                    continue
                if isinstance(value, str) and value.strip():
                    os.environ[name] = value.strip()
    except OSError:
        return


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Prepare a single issue workspace")
    parser.add_argument("--workflow", default="WORKFLOW.md", help="Path to WORKFLOW.md")
    parser.add_argument("--issue-number", type=int, default=0, help="GitHub issue number")
    parser.add_argument("--issue-file", default="", help="Local issue/backlog markdown path")

    args = parser.parse_args()

    if bool(args.issue_number) == bool(args.issue_file.strip()):
        raise SystemExit("Specify exactly one of --issue-number or --issue-file")

    _load_windows_user_env_fallback("GITHUB_TOKEN", "GITHUB_REPOSITORY")

    workflow_path = Path(args.workflow).resolve()
    settings = _load_runtime_settings(workflow_path)

    if args.issue_number:
        prepared = asyncio.run(_prepare_remote_issue(settings, args.issue_number))
    else:
        prepared = asyncio.run(_prepare_local_issue(settings, Path(args.issue_file).resolve()))

    print(f"Prepared source: {prepared.source}")
    print(f"Issue title: {prepared.issue.title}")
    print(f"Branch: {prepared.branch_name}")
    print(f"Worktree: {prepared.worktree_path}")
    print(f"Prompt: {prepared.prompt_path}")
    print("Next step: open the worktree with your code agent and execute the prompt file.")


def _load_runtime_settings(workflow_path: Path) -> RuntimeSettings:
    text = workflow_path.read_text(encoding="utf-8")
    match = _FRONT_MATTER_PATTERN.match(text)
    if match is None:
        raise PrepareIssueError("WORKFLOW.md 缺少 YAML front matter")

    front_matter_raw, prompt_template = match.groups()
    try:
        front_matter = yaml.safe_load(front_matter_raw)
    except yaml.YAMLError as exc:
        raise PrepareIssueError(f"WORKFLOW front matter YAML 解析失败: {exc}") from exc

    if not isinstance(front_matter, dict):
        raise PrepareIssueError("WORKFLOW front matter 必须是对象")

    tracker = front_matter.get("tracker")
    if not isinstance(tracker, dict):
        raise PrepareIssueError("缺少配置段: tracker")

    repo_root = Path(os.getenv("MANUAL_REPO_ROOT", os.getcwd())).resolve()
    workspace_root = _resolve_workspace_root(front_matter, repo_root)

    token = _resolve_optional_env_like(tracker.get("api_key"))
    repo = _resolve_env_like(_required_str(tracker, "repo", "tracker.repo"))
    base_branch = os.getenv("GITHUB_BASE_BRANCH", "main").strip() or "main"

    return RuntimeSettings(
        github_token=token,
        github_repo=repo,
        repo_root=repo_root,
        workspace_root=workspace_root,
        workflow_path=workflow_path,
        prompt_template=prompt_template.strip(),
        base_branch=base_branch,
    )


def _resolve_workspace_root(front_matter: dict[str, Any], repo_root: Path) -> Path:
    workspace = front_matter.get("workspace")
    if not isinstance(workspace, dict):
        return (repo_root / ".worktrees").resolve()

    root_raw = str(workspace.get("root", "$MANUAL_WORKSPACE_ROOT"))
    if root_raw.startswith("$"):
        env_name = root_raw[1:]
        env_value = os.getenv(env_name)
        if env_value is None:
            return (repo_root / ".worktrees").resolve()
        return Path(env_value).resolve()
    return Path(root_raw).resolve()


def _required_str(source: dict[str, Any], key: str, name: str) -> str:
    value = source.get(key)
    if not isinstance(value, str) or not value.strip():
        raise PrepareIssueError(f"缺少配置: {name}")
    return value.strip()


def _resolve_env_like(value: str) -> str:
    if not value.startswith("$"):
        return value
    env_name = value[1:]
    env_value = os.getenv(env_name)
    if env_value is None:
        raise PrepareIssueError(f"环境变量未设置: {env_name}")
    return env_value


def _resolve_optional_env_like(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        return ""
    raw = value.strip()
    if not raw.startswith("$"):
        return raw
    env_name = raw[1:]
    return (os.getenv(env_name) or "").strip()


async def _prepare_remote_issue(
    settings: RuntimeSettings,
    issue_number: int,
) -> PreparedIssueContext:
    issue = await _fetch_issue(settings.github_repo, issue_number)
    if issue is None:
        raise PrepareIssueError(f"Issue not found: #{issue_number}")
    return await _prepare_issue_context(settings, issue, source=f"github:{issue.identifier}")


async def _fetch_issue(repo: str, issue_number: int) -> GitHubIssue | None:
    if "/" not in repo:
        raise PrepareIssueError("tracker.repo 必须是 owner/repo 格式")

    gh_path = shutil.which("gh")
    if gh_path is None:
        raise PrepareIssueError("gh CLI not found in PATH")

    result = await asyncio.to_thread(
        _exec_process,
        [
            gh_path,
            "issue",
            "view",
            str(issue_number),
            "--repo",
            repo,
            "--json",
            "number,title,body,state,url,labels",
        ],
        Path.cwd(),
    )

    if result.returncode != 0:
        output = (result.stdout or "") + (result.stderr or "")
        lowered = output.casefold()
        if "could not resolve to an issue" in lowered or "not found" in lowered:
            return None
        raise PrepareIssueError(f"gh issue view failed: {output}")

    try:
        payload = json.loads(result.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise PrepareIssueError(f"无法解析 gh issue view 输出: {exc}") from exc

    if not isinstance(payload, dict):
        return None

    labels_raw = payload.get("labels", [])
    labels: list[str] = []
    if isinstance(labels_raw, list):
        for label in labels_raw:
            if isinstance(label, dict) and isinstance(label.get("name"), str):
                labels.append(label["name"].strip().lower())

    number = payload.get("number")
    title = payload.get("title")
    html_url = payload.get("url")
    body = payload.get("body")
    state = payload.get("state")

    if not isinstance(number, int):
        return None
    if not isinstance(title, str) or not title.strip():
        return None
    if not isinstance(html_url, str) or not html_url.strip():
        return None

    return GitHubIssue(
        number=number,
        title=title.strip(),
        body=body.strip() if isinstance(body, str) else "",
        state=state.strip() if isinstance(state, str) else "open",
        html_url=html_url.strip(),
        labels=labels,
    )


async def _prepare_local_issue(
    settings: RuntimeSettings,
    issue_file: Path,
) -> PreparedIssueContext:
    issue = _load_local_issue(issue_file)
    return await _prepare_issue_context(settings, issue, source=f"file:{issue_file}")


async def _prepare_issue_context(
    settings: RuntimeSettings,
    issue: GitHubIssue,
    source: str,
) -> PreparedIssueContext:
    issue_key = str(issue.number) if issue.number > 0 else f"local-{_slugify(issue.title, 16)}"
    branch_name = f"ai/issue-{issue_key}-{_slugify(issue.title, 36)}"
    worktree_path = settings.workspace_root / f"issue-{issue_key}"

    settings.workspace_root.mkdir(parents=True, exist_ok=True)
    await _prepare_worktree(settings, worktree_path, branch_name)

    prompt_dir = worktree_path / ".manual"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = prompt_dir / "issue-prompt.md"
    prompt_text = _render_issue_prompt(settings.prompt_template, issue)
    prompt_path.write_text(prompt_text, encoding="utf-8")

    return PreparedIssueContext(
        issue=issue,
        branch_name=branch_name,
        worktree_path=worktree_path,
        prompt_path=prompt_path,
        source=source,
    )


async def _prepare_worktree(settings: RuntimeSettings, path: Path, branch_name: str) -> None:
    await _run_git(
        ["git", "fetch", "origin", settings.base_branch],
        cwd=settings.repo_root,
    )

    if not path.exists():
        await _run_git(
            [
                "git",
                "worktree",
                "add",
                "-B",
                branch_name,
                str(path),
                f"origin/{settings.base_branch}",
            ],
            cwd=settings.repo_root,
        )
        return

    status = await _run_git(
        ["git", "status", "--porcelain"],
        cwd=path,
        check=False,
    )
    if status.stdout.strip():
        raise PrepareIssueError(f"工作目录存在未提交改动，请先清理: {path}")

    await _run_git(
        ["git", "checkout", "-B", branch_name, f"origin/{settings.base_branch}"],
        cwd=path,
    )


@dataclass(slots=True)
class _CommandResult:
    exit_code: int
    stdout: str


async def _run_git(args: list[str], cwd: Path, check: bool = True) -> _CommandResult:
    result = await asyncio.to_thread(_exec_command, args, cwd)
    if check and result.exit_code != 0:
        rendered = " ".join(args)
        raise PrepareIssueError(
            f"命令执行失败: {rendered}\n退出码: {result.exit_code}\n输出:\n{result.stdout}"
        )
    return result


def _exec_command(args: list[str], cwd: Path) -> _CommandResult:
    process = subprocess.run(  # noqa: S603
        args,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        encoding="utf-8",
        errors="replace",
    )
    output = (process.stdout or "") + (process.stderr or "")
    return _CommandResult(exit_code=process.returncode, stdout=output)


def _exec_process(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        args,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        encoding="utf-8",
        errors="replace",
    )


def _slugify(text: str, max_length: int = 48) -> str:
    normalized = "".join(ch.lower() if ch.isalnum() else "-" for ch in text)
    while "--" in normalized:
        normalized = normalized.replace("--", "-")
    normalized = normalized.strip("-") or "issue"
    return normalized[:max_length].strip("-") or "issue"


def _load_local_issue(path: Path) -> GitHubIssue:
    if not path.exists():
        raise PrepareIssueError(f"Issue file not found: {path}")

    text = path.read_text(encoding="utf-8")
    match = _FRONT_MATTER_PATTERN.match(text)
    if match is not None:
        raw_meta, body = match.groups()
        try:
            meta = yaml.safe_load(raw_meta) or {}
        except yaml.YAMLError as exc:
            raise PrepareIssueError(f"Invalid YAML front matter: {exc}") from exc
    else:
        meta = {}
        body = text

    if not isinstance(meta, dict):
        raise PrepareIssueError("Local issue front matter must be an object when present")

    title = str(meta.get("title", "")).strip() or _extract_title_from_body(body, path)
    labels = _normalize_labels(meta.get("labels"))
    html_url = str(meta.get("github_issue_url", "")).strip() or str(path)

    issue_number_raw = str(meta.get("github_issue_number", "")).strip()
    issue_number = int(issue_number_raw) if issue_number_raw.isdigit() else 0

    return GitHubIssue(
        number=issue_number,
        title=title,
        body=body.strip(),
        state="open",
        html_url=html_url,
        labels=labels,
    )


def _extract_title_from_body(body: str, path: Path) -> str:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return path.stem


def _normalize_labels(raw: Any) -> list[str]:
    if not isinstance(raw, list):
        return []
    return [str(item).strip().lower() for item in raw if str(item).strip()]


def _render_issue_prompt(template: str, issue: GitHubIssue) -> str:
    issue_identifier = issue.identifier if issue.number > 0 else "LOCAL"
    prompt = template
    prompt = prompt.replace("{{ issue.identifier }}", issue_identifier)
    prompt = prompt.replace("{{ issue.title }}", issue.title)
    prompt = prompt.replace("{{ issue.description }}", issue.body)
    prompt = prompt.replace("{{ issue.url }}", issue.html_url)
    prompt = prompt.replace("{{ issue.priority }}", "P2")
    return prompt


if __name__ == "__main__":
    main()
