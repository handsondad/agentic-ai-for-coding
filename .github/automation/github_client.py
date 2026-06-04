"""GitHub REST API 客户端。"""

from __future__ import annotations

import logging
import os
import ssl
from datetime import datetime
from typing import Any

import httpx

try:
    from .models import GitHubIssue, GitHubRepo
except ImportError:
    from models import GitHubIssue, GitHubRepo

logger = logging.getLogger(__name__)


class GitHubClient:
    """用于 Issue 轮询与 PR 创建的最小 GitHub 客户端。"""

    def __init__(self, token: str, repo: GitHubRepo) -> None:
        self._token = token
        self._repo = repo
        self._base_url = f"https://api.github.com/repos/{repo.full_name}"
        self._tls_verify: bool | str | ssl.SSLContext = _resolve_tls_verify()
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _new_client(self) -> httpx.AsyncClient:
        """Create AsyncClient with configurable TLS verification behavior."""
        return httpx.AsyncClient(timeout=30, verify=self._tls_verify)

    async def list_candidate_issues(
        self,
        active_labels: list[str],
        terminal_labels: list[str],
    ) -> list[GitHubIssue]:
        """获取待处理 Issue 列表。"""
        async with self._new_client() as client:
            response = await client.get(
                f"{self._base_url}/issues",
                headers=self._headers,
                params={
                    "state": "open",
                    "per_page": 100,
                    "sort": "created",
                    "direction": "asc",
                },
            )
            response.raise_for_status()

        payload = response.json()
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
        async with self._new_client() as client:
            response = await client.get(
                f"{self._base_url}/issues/{issue_number}",
                headers=self._headers,
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()

        return _normalize_issue(response.json())

    async def add_labels(self, issue_number: int, labels: list[str]) -> None:
        """为 issue 添加标签。"""
        async with self._new_client() as client:
            response = await client.post(
                f"{self._base_url}/issues/{issue_number}/labels",
                headers=self._headers,
                json={"labels": labels},
            )
            response.raise_for_status()

    async def remove_label(self, issue_number: int, label: str) -> None:
        """移除 issue 标签，标签不存在时忽略。"""
        encoded = label.replace(" ", "%20")
        async with self._new_client() as client:
            response = await client.delete(
                f"{self._base_url}/issues/{issue_number}/labels/{encoded}",
                headers=self._headers,
            )
            if response.status_code not in {200, 204, 404}:
                response.raise_for_status()

    async def comment_issue(self, issue_number: int, body: str) -> None:
        """向 issue 添加评论。"""
        async with self._new_client() as client:
            response = await client.post(
                f"{self._base_url}/issues/{issue_number}/comments",
                headers=self._headers,
                json={"body": body},
            )
            response.raise_for_status()

    async def find_open_pr(self, branch_name: str) -> str | None:
        """查找指定分支的开放 PR。"""
        async with self._new_client() as client:
            response = await client.get(
                f"{self._base_url}/pulls",
                headers=self._headers,
                params={
                    "state": "open",
                    "head": f"{self._repo.owner}:{branch_name}",
                },
            )
            response.raise_for_status()

        payload = response.json()
        if not isinstance(payload, list) or not payload:
            return None

        first = payload[0]
        if not isinstance(first, dict):
            return None
        html_url = first.get("html_url")
        return str(html_url) if html_url else None

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

        async with self._new_client() as client:
            response = await client.post(
                f"{self._base_url}/pulls",
                headers=self._headers,
                json={
                    "title": title,
                    "body": body,
                    "head": head_branch,
                    "base": base_branch,
                },
            )
            response.raise_for_status()

        payload = response.json()
        html_url = payload.get("html_url")
        if not isinstance(html_url, str) or not html_url:
            raise RuntimeError("GitHub 返回的 PR URL 无效")
        return html_url


def _normalize_issue(payload: Any) -> GitHubIssue | None:
    if not isinstance(payload, dict):
        return None
    if "pull_request" in payload:
        return None

    labels_raw = payload.get("labels", [])
    labels: list[str] = []

    if isinstance(labels_raw, list):
        for label in labels_raw:
            if isinstance(label, dict) and isinstance(label.get("name"), str):
                labels.append(label["name"].strip().lower())

    number = payload.get("number")
    title = payload.get("title")
    html_url = payload.get("html_url")
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
        created_at=_parse_github_datetime(payload.get("created_at")),
        updated_at=_parse_github_datetime(payload.get("updated_at")),
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


def _resolve_tls_verify() -> bool | str | ssl.SSLContext:
    """Resolve TLS verification strategy for enterprise network environments.

    Env vars:
    - AUTOMATION_TLS_NO_VERIFY=true/1/yes: disable TLS verification (not recommended)
    - AUTOMATION_CA_BUNDLE=/path/to/ca.pem: custom CA bundle path
    """
    disable_verify = os.getenv("AUTOMATION_TLS_NO_VERIFY", "").strip().lower()
    if disable_verify in {"1", "true", "yes"}:
        logger.warning(
            "AUTOMATION_TLS_NO_VERIFY is enabled; TLS verification is disabled."
        )
        return False

    ca_bundle = os.getenv("AUTOMATION_CA_BUNDLE", "").strip()
    if ca_bundle:
        return ca_bundle

    # Default to system trust store.
    # This matches tools like GitHub CLI on enterprise networks.
    return ssl.create_default_context()
