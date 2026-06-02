"""轮询调度服务。"""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import UTC, datetime

try:
    from .executor import IssuePipeline, PipelineError
    from .failure_reporting import classify_failure, render_failure_markdown
    from .metrics import ExecutionMetricEvent, append_event
    from .github_client import GitHubClient
    from .models import GitHubIssue, RuntimeSettings, slugify
except ImportError:
    from executor import IssuePipeline, PipelineError
    from failure_reporting import classify_failure, render_failure_markdown
    from metrics import ExecutionMetricEvent, append_event
    from github_client import GitHubClient
    from models import GitHubIssue, RuntimeSettings, slugify

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
            started_at = datetime.now(tz=UTC)
            started_perf = time.perf_counter()
            try:
                await self._mark_in_progress(issue)
                result = await self._pipeline.run(issue)
            except PipelineError as exc:
                await self._record_metrics_event(
                    self._build_metric_event(
                        issue=issue,
                        started_at=started_at,
                        started_perf=started_perf,
                        success=False,
                        pr_url=None,
                        quality_results=[],
                        failure_step="pipeline",
                        failure_message=str(exc),
                    )
                )
                logger.error("issue=%s 执行失败: %s", issue.number, exc)
                await self._safe_comment(
                    issue.number,
                    render_failure_markdown(step="pipeline", raw_error=str(exc)),
                )
                await self._safe_add_labels(issue.number, ["ai-failed"])
                return
            except Exception as exc:
                await self._record_metrics_event(
                    self._build_metric_event(
                        issue=issue,
                        started_at=started_at,
                        started_perf=started_perf,
                        success=False,
                        pr_url=None,
                        quality_results=[],
                        failure_step="unexpected",
                        failure_message=str(exc),
                    )
                )
                logger.exception("issue=%s 执行出现未预期异常: %s", issue.number, exc)
                await self._safe_comment(
                    issue.number,
                    render_failure_markdown(step="unexpected", raw_error=str(exc)),
                )
                await self._safe_add_labels(issue.number, ["ai-failed"])
                return
            finally:
                self._claimed.discard(issue.number)

            if result.changed and result.pr_url:
                await self._safe_comment(
                    issue.number,
                    f"自动处理完成，已创建 PR: {result.pr_url}",
                )
                await self._safe_add_labels(issue.number, ["human-review"])
            else:
                await self._safe_comment(
                    issue.number,
                    "自动执行完成，但未检测到代码变更。",
                )

            await self._safe_remove_label(issue.number, "ai-ready")
            await self._safe_remove_label(issue.number, "in-progress")
            await self._record_metrics_event(
                self._build_metric_event(
                    issue=issue,
                    started_at=started_at,
                    started_perf=started_perf,
                    success=True,
                    pr_url=result.pr_url,
                    quality_results=result.quality_results,
                    failure_step=None,
                    failure_message=None,
                )
            )

    async def _mark_in_progress(self, issue: GitHubIssue) -> None:
        await self._safe_add_labels(issue.number, ["in-progress"])
        await self._safe_remove_label(issue.number, "ai-ready")

    async def _safe_add_labels(self, issue_number: int, labels: list[str]) -> None:
        try:
            await self._github.add_labels(issue_number, labels)
        except Exception as exc:
            self._log_github_write_failure(
                op="add_labels",
                issue_number=issue_number,
                detail=f"labels={labels}",
                exc=exc,
            )

    async def _safe_remove_label(self, issue_number: int, label: str) -> None:
        try:
            await self._github.remove_label(issue_number, label)
        except Exception as exc:
            self._log_github_write_failure(
                op="remove_label",
                issue_number=issue_number,
                detail=f"label={label}",
                exc=exc,
            )

    async def _safe_comment(self, issue_number: int, body: str) -> None:
        try:
            await self._github.comment_issue(issue_number, body)
        except Exception as exc:
            self._log_github_write_failure(
                op="comment_issue",
                issue_number=issue_number,
                detail="comment_body=<omitted>",
                exc=exc,
            )

    def _log_github_write_failure(
        self,
        op: str,
        issue_number: int,
        detail: str,
        exc: Exception,
    ) -> None:
        response = getattr(exc, "response", None)
        status_code = getattr(response, "status_code", None)
        logger.warning(
            "issue=%s GitHub写操作失败 op=%s %s err=%s",
            issue_number,
            op,
            detail,
            exc,
        )
        if status_code == 403:
            logger.error(
                "issue=%s 检测到 403 Forbidden。请检查 Token 权限："
                "Issues(读写) + Pull requests(读写) + Contents(读写)。",
                issue_number,
            )

    def _build_metric_event(
        self,
        issue: GitHubIssue,
        started_at: datetime,
        started_perf: float,
        success: bool,
        pr_url: str | None,
        quality_results: list[object],
        failure_step: str | None,
        failure_message: str | None,
    ) -> ExecutionMetricEvent:
        completed_at = datetime.now(tz=UTC)
        duration_ms = int((time.perf_counter() - started_perf) * 1000)
        quality_gate_failures = sum(1 for item in quality_results if getattr(item, "exit_code", 0) != 0)
        gate_passed = quality_gate_failures == 0 and success

        failure_category = None
        failure_reason = None
        retryable = None
        if failure_message:
            classification = classify_failure(failure_message)
            failure_category = classification.category
            failure_reason = classification.reason
            retryable = classification.retryable

        return ExecutionMetricEvent(
            issue_number=issue.number,
            issue_title=issue.title,
            issue_identifier=issue.identifier,
            issue_created_at=issue.created_at.isoformat() if issue.created_at else None,
            started_at=started_at.isoformat(),
            completed_at=completed_at.isoformat(),
            duration_ms=duration_ms,
            success=success,
            pr_created=bool(pr_url),
            pr_url=pr_url,
            quality_gate_passed=gate_passed,
            quality_gate_failures=quality_gate_failures,
            failure_step=failure_step,
            failure_message=failure_message,
            failure_category=failure_category,
            failure_reason=failure_reason,
            retryable=retryable,
            labels=issue.labels,
            branch_name=f"ai/issue-{issue.number}-{slugify(issue.title, 36)}",
        )

    async def _record_metrics_event(self, event: ExecutionMetricEvent) -> None:
        try:
            await asyncio.to_thread(append_event, self._settings.metrics_file, event)
        except Exception as exc:
            logger.warning("issue=%s 指标写入失败: %s", event.issue_number, exc)


def filter_new_candidates(issues: list[GitHubIssue], claimed: set[int]) -> list[GitHubIssue]:
    """返回未被占用的候选 Issue。"""
    return [issue for issue in issues if issue.number not in claimed]
