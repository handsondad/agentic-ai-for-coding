"""轮询调度服务。"""

from __future__ import annotations

import asyncio
import logging

try:
    from .executor import IssuePipeline, PipelineError
    from .github_client import GitHubClient
    from .models import GitHubIssue, RuntimeSettings
except ImportError:
    from executor import IssuePipeline, PipelineError
    from github_client import GitHubClient
    from models import GitHubIssue, RuntimeSettings

logger = logging.getLogger(__name__)


class AutomationService:
    """本地 issue 自动调度器。"""

    def __init__(self, settings: RuntimeSettings) -> None:
        self._settings = settings
        self._github = GitHubClient(token=settings.github_token, repo=settings.github_repo)
        self._pipeline = IssuePipeline(settings=settings, github=self._github)
        self._claimed: set[int] = set()

    async def run_once(self) -> None:
        """执行单次轮询调度。"""
        issues = await self._github.list_candidate_issues(
            active_labels=self._settings.active_labels,
            terminal_labels=self._settings.terminal_labels,
        )

        candidates = [issue for issue in issues if issue.number not in self._claimed]
        if not candidates:
            logger.info("未发现待处理 issue")
            return

        semaphore = asyncio.Semaphore(self._settings.max_concurrent_agents)
        tasks = [self._run_with_guard(issue, semaphore) for issue in candidates]
        await asyncio.gather(*tasks)

    async def run_forever(self) -> None:
        """循环执行轮询调度。"""
        while True:
            await self.run_once()
            await asyncio.sleep(self._settings.poll_interval_ms / 1000)

    async def _run_with_guard(self, issue: GitHubIssue, semaphore: asyncio.Semaphore) -> None:
        async with semaphore:
            self._claimed.add(issue.number)
            await self._mark_in_progress(issue)
            try:
                result = await self._pipeline.run(issue)
            except PipelineError as exc:
                logger.error("issue=%s 执行失败: %s", issue.number, exc)
                await self._github.comment_issue(
                    issue.number,
                    f"自动执行失败: {exc}\n\n请修复后重新打上 ai-ready 标签。",
                )
                await self._github.add_labels(issue.number, ["ai-failed"])
                return
            finally:
                self._claimed.discard(issue.number)

            if result.changed and result.pr_url:
                await self._github.comment_issue(
                    issue.number,
                    f"自动处理完成，已创建 PR: {result.pr_url}",
                )
                await self._github.add_labels(issue.number, ["human-review"])
            else:
                await self._github.comment_issue(
                    issue.number,
                    "自动执行完成，但未检测到代码变更。",
                )

            await self._github.remove_label(issue.number, "ai-ready")
            await self._github.remove_label(issue.number, "in-progress")

    async def _mark_in_progress(self, issue: GitHubIssue) -> None:
        await self._github.add_labels(issue.number, ["in-progress"])
        await self._github.remove_label(issue.number, "ai-ready")


def filter_new_candidates(issues: list[GitHubIssue], claimed: set[int]) -> list[GitHubIssue]:
    """返回未被占用的候选 Issue。"""
    return [issue for issue in issues if issue.number not in claimed]
