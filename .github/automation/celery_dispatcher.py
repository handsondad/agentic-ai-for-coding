"""Celery 调度器：轮询 issue 并分层投递任务。"""

from __future__ import annotations

import asyncio
import logging
import os
import re
from collections import defaultdict
from datetime import datetime

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

        issues = await self._github.list_candidate_issues(
            active_labels=self._settings.active_labels,
            terminal_labels=self._settings.terminal_labels,
        )
        candidates = [issue for issue in issues if _is_ready(issue)]
        if not candidates:
            logger.info("celery-mode: 未发现 ai-ready issue")
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
