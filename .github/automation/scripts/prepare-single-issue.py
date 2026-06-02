"""Prepare a single issue workspace for manual/agent-driven development."""

from __future__ import annotations

import argparse
import asyncio
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
AUTOMATION_DIR = SCRIPT_DIR.parent

if str(AUTOMATION_DIR) not in sys.path:
    sys.path.insert(0, str(AUTOMATION_DIR))

from executor import IssuePipeline  # noqa: E402
from github_client import GitHubClient  # noqa: E402
from models import GitHubIssue, RuntimeSettings, slugify  # noqa: E402
from workflow import load_runtime_settings  # noqa: E402

_FRONT_MATTER_PATTERN = re.compile(r"^\ufeff?---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)


class PrepareIssueError(RuntimeError):
    """Raised when single-issue preparation cannot continue."""


@dataclass(slots=True)
class PreparedIssueContext:
    """Prepared local context for an issue."""

    issue: GitHubIssue
    branch_name: str
    worktree_path: Path
    prompt_path: Path
    source: str


class _NoopGitHubClient:
    async def create_pull_request(
        self,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str,
    ) -> str:
        raise PrepareIssueError(
            "Single issue prepare mode does not create pull requests automatically"
        )


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

    _load_windows_user_env_fallback(
        "GITHUB_TOKEN",
        "GITHUB_REPOSITORY",
        "AUTOMATION_CA_BUNDLE",
        "AUTOMATION_TLS_NO_VERIFY",
    )

    workflow_path = Path(args.workflow).resolve()
    settings = load_runtime_settings(workflow_path)

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


async def _prepare_remote_issue(
    settings: RuntimeSettings,
    issue_number: int,
) -> PreparedIssueContext:
    client = GitHubClient(token=settings.github_token, repo=settings.github_repo)
    issue = await client.get_issue(issue_number)
    if issue is None:
        raise PrepareIssueError(f"Issue not found: #{issue_number}")
    return await _prepare_issue_context(settings, issue, source=f"github:{issue.identifier}")


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
    issue_key = str(issue.number) if issue.number > 0 else f"local-{slugify(issue.title, 16)}"
    branch_name = f"ai/issue-{issue_key}-{slugify(issue.title, 36)}"
    worktree_path = settings.workspace_root / f"issue-{issue_key}"

    pipeline = IssuePipeline(settings=settings, github=_NoopGitHubClient())
    settings.workspace_root.mkdir(parents=True, exist_ok=True)
    await pipeline._prepare_worktree(worktree_path, branch_name)

    prompt_dir = worktree_path / ".automation"
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
