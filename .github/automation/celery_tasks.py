"""Celery worker tasks for issue automation."""

from __future__ import annotations

import asyncio
import logging
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    from celery import Celery
except ImportError:  # pragma: no cover - runtime dependency
    Celery = None  # type: ignore[assignment]

try:
    from .executor import IssuePipeline, PipelineError
    from .failure_reporting import classify_failure, render_failure_markdown
    from .github_client import GitHubClient
    from .metrics import ExecutionMetricEvent, append_event
    from .models import GitHubIssue, RuntimeSettings, slugify
    from .workflow import load_runtime_settings
except ImportError:
    from executor import IssuePipeline, PipelineError
    from failure_reporting import classify_failure, render_failure_markdown
    from github_client import GitHubClient
    from metrics import ExecutionMetricEvent, append_event
    from models import GitHubIssue, RuntimeSettings, slugify
    from workflow import load_runtime_settings

logger = logging.getLogger(__name__)


def _build_celery_app() -> Any:
    if Celery is None:
        raise RuntimeError("celery is required. Install with: pip install celery[redis]")

    app = Celery(
        "automation_runner",
        broker=os.getenv("AUTOMATION_CELERY_BROKER_URL", "redis://localhost:6379/0"),
        backend=os.getenv("AUTOMATION_CELERY_RESULT_BACKEND", "redis://localhost:6379/1"),
    )
    app.conf.update(
        task_default_queue=os.getenv("AUTOMATION_CELERY_QUEUE", "automation_issues"),
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        task_track_started=True,
    )
    return app


celery_app = _build_celery_app()


@celery_app.task(name="automation.run_issue")
def run_issue_task(issue_number: int, workflow_path: str = "WORKFLOW.md") -> dict[str, Any]:
    """Execute one issue pipeline in a Celery worker process."""
    return asyncio.run(_run_issue_async(issue_number=issue_number, workflow_path=workflow_path))


async def _run_issue_async(issue_number: int, workflow_path: str) -> dict[str, Any]:
    resolved_workflow = Path(workflow_path).resolve()
    settings = load_runtime_settings(resolved_workflow)
    github = GitHubClient(
        token=settings.github_token,
        repo=settings.github_repo,
        backend=settings.github_backend,
    )

    issue = await github.get_issue(issue_number)
    if issue is None:
        raise PipelineError(f"Issue not found: #{issue_number}")

    pipeline = IssuePipeline(settings=settings, github=github)
    started_at = datetime.now(tz=UTC)
    started_perf = time.perf_counter()

    await _safe_add_labels(github, issue.number, ["in-progress"])
    await _safe_remove_label(github, issue.number, "ai-ready")

    try:
        result = await pipeline.run(issue)
    except PipelineError as exc:
        await _safe_comment(
            github,
            issue.number,
            render_failure_markdown(step="pipeline", raw_error=str(exc)),
        )
        await _safe_add_labels(github, issue.number, ["ai-failed"])
        await _safe_remove_label(github, issue.number, "in-progress")
        await _record_metrics_event(
            settings=settings,
            issue=issue,
            started_at=started_at,
            started_perf=started_perf,
            success=False,
            pr_url=None,
            quality_results=[],
            failure_step="pipeline",
            failure_message=str(exc),
        )
        raise
    except Exception as exc:
        await _safe_comment(
            github,
            issue.number,
            render_failure_markdown(step="unexpected", raw_error=str(exc)),
        )
        await _safe_add_labels(github, issue.number, ["ai-failed"])
        await _safe_remove_label(github, issue.number, "in-progress")
        await _record_metrics_event(
            settings=settings,
            issue=issue,
            started_at=started_at,
            started_perf=started_perf,
            success=False,
            pr_url=None,
            quality_results=[],
            failure_step="unexpected",
            failure_message=str(exc),
        )
        raise

    if result.changed and result.pr_url:
        await _safe_comment(github, issue.number, f"自动处理完成，已创建 PR: {result.pr_url}")
        await _safe_add_labels(github, issue.number, ["human-review"])
    else:
        await _safe_comment(github, issue.number, "自动执行完成，但未检测到代码变更。")

    await _safe_remove_label(github, issue.number, "in-progress")
    await _safe_remove_label(github, issue.number, "ai-ready")
    await _record_metrics_event(
        settings=settings,
        issue=issue,
        started_at=started_at,
        started_perf=started_perf,
        success=True,
        pr_url=result.pr_url,
        quality_results=result.quality_results,
        failure_step=None,
        failure_message=None,
    )

    return {
        "issue_number": issue.number,
        "changed": result.changed,
        "pr_url": result.pr_url,
        "branch_name": result.branch_name,
    }


async def _safe_add_labels(github: GitHubClient, issue_number: int, labels: list[str]) -> None:
    try:
        await github.add_labels(issue_number, labels)
    except Exception as exc:
        logger.warning("issue=%s add_labels failed labels=%s err=%s", issue_number, labels, exc)


async def _safe_remove_label(github: GitHubClient, issue_number: int, label: str) -> None:
    try:
        await github.remove_label(issue_number, label)
    except Exception as exc:
        logger.warning("issue=%s remove_label failed label=%s err=%s", issue_number, label, exc)


async def _safe_comment(github: GitHubClient, issue_number: int, body: str) -> None:
    try:
        await github.comment_issue(issue_number, body)
    except Exception as exc:
        logger.warning("issue=%s comment failed err=%s", issue_number, exc)


async def _record_metrics_event(
    settings: RuntimeSettings,
    issue: GitHubIssue,
    started_at: datetime,
    started_perf: float,
    success: bool,
    pr_url: str | None,
    quality_results: list[object],
    failure_step: str | None,
    failure_message: str | None,
) -> None:
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

    event = ExecutionMetricEvent(
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

    try:
        await asyncio.to_thread(append_event, settings.metrics_file, event)
    except Exception as exc:
        logger.warning("issue=%s metrics write failed err=%s", issue.number, exc)
