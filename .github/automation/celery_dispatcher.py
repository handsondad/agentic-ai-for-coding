"""Celery 调度器：轮询 issue 并分层投递任务。"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import subprocess
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    from celery import group
except ImportError:  # pragma: no cover - runtime dependency
    group = None

try:
    from .github_client import GitHubClient
    from .models import GitHubIssue, RuntimeSettings
except ImportError:
    from github_client import GitHubClient
    from models import GitHubIssue, RuntimeSettings

logger = logging.getLogger(__name__)

_DEPENDS_ON_PATTERN = re.compile(r"depends\s+on:\s*#(\d+)", re.IGNORECASE)
_DISPATCH_STATE_REL_PATH = ".automation/dispatch-state.json"


class CeleryDispatcherError(RuntimeError):
    """Celery 调度阶段失败。"""


class CeleryDispatchService:
    """使用 Celery 进行自动化 issue 调度。"""

    def __init__(self, settings: RuntimeSettings) -> None:
        self._settings = settings
        self._github = GitHubClient(token=settings.github_token, repo=settings.github_repo)
        os.environ["AUTOMATION_CELERY_BROKER_URL"] = settings.celery_broker_url
        os.environ["AUTOMATION_CELERY_RESULT_BACKEND"] = settings.celery_result_backend
        os.environ["AUTOMATION_CELERY_QUEUE"] = settings.celery_queue

    async def run_once(self) -> None:
        """执行单次调度，并按依赖分层投递任务。"""
        _require_celery()

        base_head = await _resolve_base_head(self._settings)
        state_path = self._settings.repo_root / _DISPATCH_STATE_REL_PATH
        dispatch_state = _load_dispatch_state(state_path)

        issues = await self._github.list_candidate_issues(
            active_labels=self._settings.active_labels,
            terminal_labels=self._settings.terminal_labels,
        )
        candidates = [issue for issue in issues if _is_ready(issue)]
        if not candidates:
            logger.info("celery-mode: 未发现 ai-ready issue")
            return

        candidates = [
            issue
            for issue in candidates
            if _should_dispatch_issue(issue, base_head=base_head, state=dispatch_state)
        ]
        if not candidates:
            logger.info("celery-mode: ai-ready issue 未检测到更新，跳过本轮")
            return

        levels = build_dependency_levels(candidates)
        logger.info(
            "celery-mode: 本轮调度 issue=%s levels=%s",
            len(candidates),
            len(levels),
        )

        for index, level in enumerate(levels, start=1):
            signatures = [
                _build_issue_signature(
                    issue_number=issue.number,
                    workflow_path=str(self._settings.workflow_path),
                )
                for issue in level
            ]

            level_numbers = [issue.number for issue in level]
            logger.info("celery-mode: dispatch level=%s issues=%s", index, level_numbers)

            group_result = group(signatures).apply_async(queue=self._settings.celery_queue)
            await asyncio.to_thread(group_result.get, None, False)

            failed = [item.id for item in group_result.results if not item.successful()]
            if failed:
                raise CeleryDispatcherError(
                    f"level={index} 执行失败，已停止后续依赖层调度 failed={failed}"
                )

            _record_dispatched_issues(
                state=dispatch_state,
                issues=level,
                base_head=base_head,
            )
            _save_dispatch_state(state_path, dispatch_state)

    async def run_forever(self) -> None:
        """循环执行调度。"""
        while True:
            try:
                await self.run_once()
            except Exception as exc:  # noqa: BLE001
                logger.exception("celery-mode: 调度循环失败 err=%s", exc)

            await asyncio.sleep(self._settings.poll_interval_ms / 1000)


def build_dependency_levels(issues: list[GitHubIssue]) -> list[list[GitHubIssue]]:
    """根据 issue 依赖关系构造分层调度结果。"""
    issue_map = {issue.number: issue for issue in issues}

    dependencies: dict[int, set[int]] = {}
    for issue in issues:
        parent_ids = _parse_dependencies(issue.body)
        dependencies[issue.number] = {item for item in parent_ids if item in issue_map}

    reverse: dict[int, set[int]] = defaultdict(set)
    indegree: dict[int, int] = {}

    for issue_number, parent_ids in dependencies.items():
        indegree[issue_number] = len(parent_ids)
        for parent_id in parent_ids:
            reverse[parent_id].add(issue_number)

    ready = sorted(
        [item for item, degree in indegree.items() if degree == 0],
        key=lambda item: _sort_key(issue_map[item]),
    )
    levels: list[list[GitHubIssue]] = []
    processed = 0

    while ready:
        level_ids = ready
        levels.append([issue_map[item] for item in level_ids])
        processed += len(level_ids)

        next_ready: list[int] = []
        for parent_id in level_ids:
            for child_id in reverse.get(parent_id, set()):
                indegree[child_id] -= 1
                if indegree[child_id] == 0:
                    next_ready.append(child_id)

        ready = sorted(next_ready, key=lambda item: _sort_key(issue_map[item]))

    if processed != len(issues):
        raise CeleryDispatcherError("检测到循环依赖，请检查 Issue body 中的 Depends on 声明")

    return levels


def _build_issue_signature(issue_number: int, workflow_path: str):
    try:
        from .celery_tasks import run_issue_task
    except ImportError:
        from celery_tasks import run_issue_task

    return run_issue_task.s(issue_number=issue_number, workflow_path=workflow_path)


def _parse_dependencies(body: str) -> set[int]:
    return {int(item) for item in _DEPENDS_ON_PATTERN.findall(body or "")}


def _is_ready(issue: GitHubIssue) -> bool:
    labels = {label.lower() for label in issue.labels}
    return "ai-ready" in labels


def _sort_key(issue: GitHubIssue) -> tuple[datetime, int]:
    created_at = issue.created_at or datetime.max
    return (created_at, issue.number)


def _require_celery() -> None:
    if group is None:
        raise CeleryDispatcherError(
            "未安装 celery，请先安装: pip install celery[redis]"
        )


def _resolve_base_head(settings: RuntimeSettings) -> Any:
    async def _runner() -> str | None:
        skip_fetch = os.getenv("AUTOMATION_SKIP_GIT_FETCH", "").strip().lower() in {
            "1",
            "true",
            "yes",
        }
        if not skip_fetch:
            fetch_result = await asyncio.to_thread(
                _run_process,
                ["git", "fetch", "origin", settings.base_branch],
                settings.repo_root,
            )
            if fetch_result.returncode != 0:
                logger.warning(
                    "celery-mode: 获取远端分支失败 branch=%s output=%s",
                    settings.base_branch,
                    fetch_result.output.strip(),
                )

        rev_parse_result = await asyncio.to_thread(
            _run_process,
            ["git", "rev-parse", f"origin/{settings.base_branch}"],
            settings.repo_root,
        )
        if rev_parse_result.returncode != 0:
            logger.warning(
                "celery-mode: 读取分支头失败 branch=%s output=%s",
                settings.base_branch,
                rev_parse_result.output.strip(),
            )
            return None
        value = rev_parse_result.output.strip()
        return value or None

    return _runner()


class _ProcessResult:
    def __init__(self, returncode: int, output: str) -> None:
        self.returncode = returncode
        self.output = output


def _run_process(args: list[str], cwd: Path) -> _ProcessResult:
    process = subprocess.run(  # noqa: S603
        args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
        encoding="utf-8",
        errors="replace",
    )
    output = (process.stdout or "") + (process.stderr or "")
    return _ProcessResult(returncode=process.returncode, output=output)


def _load_dispatch_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"issues": {}}

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"issues": {}}

    if not isinstance(payload, dict):
        return {"issues": {}}
    issues = payload.get("issues")
    if not isinstance(issues, dict):
        payload["issues"] = {}
    return payload


def _save_dispatch_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _should_dispatch_issue(issue: GitHubIssue, base_head: str | None, state: dict[str, Any]) -> bool:
    issues_state = state.get("issues")
    if not isinstance(issues_state, dict):
        return True

    entry = issues_state.get(str(issue.number))
    if not isinstance(entry, dict):
        return True

    current_issue_updated = issue.updated_at.isoformat() if issue.updated_at else ""
    recorded_issue_updated = str(entry.get("issue_updated_at", "")).strip()
    if current_issue_updated and current_issue_updated != recorded_issue_updated:
        return True

    if base_head:
        recorded_base_head = str(entry.get("base_head", "")).strip()
        if recorded_base_head != base_head:
            return True

    return False


def _record_dispatched_issues(
    state: dict[str, Any],
    issues: list[GitHubIssue],
    base_head: str | None,
) -> None:
    issues_state = state.get("issues")
    if not isinstance(issues_state, dict):
        issues_state = {}
        state["issues"] = issues_state

    now = datetime.now(tz=UTC).isoformat()
    for issue in issues:
        issues_state[str(issue.number)] = {
            "issue_updated_at": issue.updated_at.isoformat() if issue.updated_at else "",
            "base_head": base_head or "",
            "last_dispatched_at": now,
        }
