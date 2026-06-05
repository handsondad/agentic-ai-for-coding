"""GitHub CLI client for automation mode."""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime
from typing import Any

try:
    from .models import GitHubIssue, GitHubRepo
except ImportError:
    from models import GitHubIssue, GitHubRepo


class GitHubClient:
    """Minimal GitHub client implemented via gh CLI."""

    def __init__(self, token: str, repo: GitHubRepo) -> None:
        self._token = token.strip()
        self._repo = repo
        self._verify_gh_runtime()

    def _verify_gh_runtime(self) -> None:
        gh_path = shutil.which("gh")
        if gh_path is None:
            raise RuntimeError(
                "gh CLI not found in PATH; install GitHub CLI before running automation."
            )

        if self._token:
            return

        status = subprocess.run(  # noqa: S603
            [gh_path, "auth", "status"],
            text=True,
            capture_output=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
        if status.returncode != 0:
            output = (status.stdout or "") + (status.stderr or "")
            raise RuntimeError(
                "gh auth status failed; run 'gh auth login' or set GITHUB_TOKEN/GH_TOKEN. "
                f"detail: {output.strip()}"
            )

    async def list_candidate_issues(
        self,
        active_labels: list[str],
        terminal_labels: list[str],
    ) -> list[GitHubIssue]:
        """获取待处理 Issue 列表。"""
        payload = await self._gh_json(
            [
                "issue",
                "list",
                "--repo",
                self._repo.full_name,
                "--state",
                "open",
                "--limit",
                "100",
                "--json",
                "number,title,body,state,url,labels,createdAt,updatedAt",
            ]
        )

        if not isinstance(payload, list):
            return []

        issues: list[GitHubIssue] = []
        for item in payload:
            issue = _normalize_issue(item)
            if issue is None:
                continue

            labels = {label.lower() for label in issue.labels}
            if labels.intersection(terminal_labels):
                continue
            if not labels.intersection(active_labels):
                continue

            issues.append(issue)

        return issues

    async def get_issue(self, issue_number: int) -> GitHubIssue | None:
        """Fetch a single issue by number."""
        result = await self._run_gh(
            [
                "issue",
                "view",
                str(issue_number),
                "--repo",
                self._repo.full_name,
                "--json",
                "number,title,body,state,url,labels,createdAt,updatedAt",
            ]
        )
        if result.returncode != 0:
            output = ((result.stdout or "") + (result.stderr or "")).casefold()
            if "could not resolve to an issue" in output or "not found" in output:
                return None
            raise RuntimeError(
                f"gh issue view failed for #{issue_number}: {(result.stdout or '')}{(result.stderr or '')}"
            )

        return _normalize_issue(_safe_load_json(result.stdout))

    async def add_labels(self, issue_number: int, labels: list[str]) -> None:
        """为 issue 添加标签。"""
        for label in labels:
            result = await self._run_gh(
                [
                    "issue",
                    "edit",
                    str(issue_number),
                    "--repo",
                    self._repo.full_name,
                    "--add-label",
                    label,
                ]
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"gh issue edit --add-label failed: {(result.stdout or '')}{(result.stderr or '')}"
                )

    async def remove_label(self, issue_number: int, label: str) -> None:
        """移除 issue 标签，标签不存在时忽略。"""
        result = await self._run_gh(
            [
                "issue",
                "edit",
                str(issue_number),
                "--repo",
                self._repo.full_name,
                "--remove-label",
                label,
            ]
        )
        if result.returncode != 0:
            output = ((result.stdout or "") + (result.stderr or "")).casefold()
            if "not found" in output or "does not exist" in output:
                return
            raise RuntimeError(
                f"gh issue edit --remove-label failed: {(result.stdout or '')}{(result.stderr or '')}"
            )

    async def comment_issue(self, issue_number: int, body: str) -> None:
        """向 issue 添加评论。"""
        result = await self._run_gh(
            [
                "issue",
                "comment",
                str(issue_number),
                "--repo",
                self._repo.full_name,
                "--body",
                body,
            ]
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"gh issue comment failed: {(result.stdout or '')}{(result.stderr or '')}"
            )

    async def find_open_pr(self, branch_name: str) -> str | None:
        """查找指定分支的开放 PR。"""
        payload = await self._gh_json(
            [
                "pr",
                "list",
                "--repo",
                self._repo.full_name,
                "--state",
                "open",
                "--head",
                branch_name,
                "--limit",
                "1",
                "--json",
                "url",
            ]
        )
        if not isinstance(payload, list) or not payload:
            return None

        first = payload[0]
        if not isinstance(first, dict):
            return None
        pr_url = first.get("url")
        return str(pr_url) if pr_url else None

    async def create_pull_request(
        self,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str,
    ) -> str:
        """创建 PR，已存在时返回已有 URL。"""
        existing = await self.find_open_pr(head_branch)
        if existing is not None:
            return existing

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".md",
            prefix="automation-pr-body-",
            encoding="utf-8",
            delete=False,
        ) as temp:
            temp.write(body)
            body_file = temp.name

        try:
            result = await self._run_gh(
                [
                    "pr",
                    "create",
                    "--repo",
                    self._repo.full_name,
                    "--title",
                    title,
                    "--body-file",
                    body_file,
                    "--head",
                    head_branch,
                    "--base",
                    base_branch,
                ]
            )
        finally:
            try:
                os.remove(body_file)
            except OSError:
                pass

        if result.returncode != 0:
            raise RuntimeError(
                f"gh pr create failed: {(result.stdout or '')}{(result.stderr or '')}"
            )

        pr_url = (result.stdout or "").strip()
        if not pr_url:
            raise RuntimeError("gh pr create 返回为空，无法获取 PR 链接")
        return pr_url

    async def _gh_json(self, args: list[str]) -> Any:
        result = await self._run_gh(args)
        if result.returncode != 0:
            raise RuntimeError(f"gh command failed: {(result.stdout or '')}{(result.stderr or '')}")
        return _safe_load_json(result.stdout)

    async def _run_gh(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        if self._token:
            env.setdefault("GH_TOKEN", self._token)
        result = await asyncio.to_thread(
            subprocess.run,  # noqa: S603
            ["gh", *args],
            text=True,
            capture_output=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        if result.returncode != 0:
            output = ((result.stdout or "") + (result.stderr or "")).casefold()
            if "authentication" in output or "not logged into" in output:
                raise RuntimeError(
                    "gh authentication failed during automation command; "
                    "run 'gh auth login' or set GITHUB_TOKEN/GH_TOKEN."
                )
        return result


def _normalize_issue(payload: Any) -> GitHubIssue | None:
    if not isinstance(payload, dict):
        return None

    labels_raw = payload.get("labels", [])
    labels: list[str] = []

    if isinstance(labels_raw, list):
        for label in labels_raw:
            if isinstance(label, dict) and isinstance(label.get("name"), str):
                labels.append(label["name"].strip().lower())
            elif isinstance(label, str):
                labels.append(label.strip().lower())

    number = payload.get("number")
    title = payload.get("title")
    html_url = payload.get("html_url") or payload.get("url")
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
        created_at=_parse_github_datetime(payload.get("created_at") or payload.get("createdAt")),
        updated_at=_parse_github_datetime(payload.get("updated_at") or payload.get("updatedAt")),
    )


def _parse_github_datetime(value: Any) -> datetime | None:
    """Parse GitHub ISO8601 timestamps."""
    if not isinstance(value, str) or not value.strip():
        return None

    normalized = value.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def _safe_load_json(raw: str) -> Any:
    text = (raw or "").strip()
    if not text:
        return None
    return json.loads(text)
