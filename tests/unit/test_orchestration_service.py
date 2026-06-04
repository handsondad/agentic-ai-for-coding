"""Celery 调度器依赖分层测试。"""

from __future__ import annotations

import importlib
import sys
from datetime import UTC, datetime
from pathlib import Path

AUTOMATION_DIR = Path(__file__).resolve().parents[2] / ".github" / "automation"
if str(AUTOMATION_DIR) not in sys.path:
    sys.path.insert(0, str(AUTOMATION_DIR))

models_module = importlib.import_module("models")
dispatcher_module = importlib.import_module("celery_dispatcher")

GitHubIssue = models_module.GitHubIssue
build_dependency_levels = dispatcher_module.build_dependency_levels
should_dispatch_issue = dispatcher_module._should_dispatch_issue
record_dispatched_issues = dispatcher_module._record_dispatched_issues


def test_build_dependency_levels_orders_by_depends_on() -> None:
    """应按 Depends on 关系进行分层调度。"""
    issues = [
        GitHubIssue(
            number=10,
            title="Base",
            body="",
            state="open",
            html_url="https://example.com/10",
            labels=["ai-ready"],
        ),
        GitHubIssue(
            number=11,
            title="Child-A",
            body="Depends on: #10",
            state="open",
            html_url="https://example.com/11",
            labels=["ai-ready"],
        ),
        GitHubIssue(
            number=12,
            title="Child-B",
            body="Depends on: #10",
            state="open",
            html_url="https://example.com/12",
            labels=["ai-ready"],
        ),
    ]

    levels = build_dependency_levels(issues)

    assert [item.number for item in levels[0]] == [10]
    assert sorted(item.number for item in levels[1]) == [11, 12]


def test_should_dispatch_issue_when_no_previous_state() -> None:
    issue = GitHubIssue(
        number=20,
        title="New",
        body="",
        state="open",
        html_url="https://example.com/20",
        labels=["ai-ready"],
        updated_at=datetime(2026, 6, 4, 8, 0, tzinfo=UTC),
    )

    assert should_dispatch_issue(issue, base_head="abc123", state={"issues": {}}) is True


def test_should_dispatch_issue_when_issue_or_base_updated() -> None:
    issue = GitHubIssue(
        number=21,
        title="Updated",
        body="",
        state="open",
        html_url="https://example.com/21",
        labels=["ai-ready"],
        updated_at=datetime(2026, 6, 4, 9, 0, tzinfo=UTC),
    )

    state = {
        "issues": {
            "21": {
                "issue_updated_at": "2026-06-04T08:00:00+00:00",
                "base_head": "oldbase",
            }
        }
    }

    assert should_dispatch_issue(issue, base_head="newbase", state=state) is True


def test_should_dispatch_issue_skips_when_no_changes() -> None:
    updated_at = datetime(2026, 6, 4, 10, 0, tzinfo=UTC)
    issue = GitHubIssue(
        number=22,
        title="Stable",
        body="",
        state="open",
        html_url="https://example.com/22",
        labels=["ai-ready"],
        updated_at=updated_at,
    )

    state = {
        "issues": {
            "22": {
                "issue_updated_at": updated_at.isoformat(),
                "base_head": "samebase",
            }
        }
    }

    assert should_dispatch_issue(issue, base_head="samebase", state=state) is False


def test_record_dispatched_issues_updates_state() -> None:
    updated_at = datetime(2026, 6, 4, 11, 0, tzinfo=UTC)
    issue = GitHubIssue(
        number=23,
        title="Record",
        body="",
        state="open",
        html_url="https://example.com/23",
        labels=["ai-ready"],
        updated_at=updated_at,
    )
    state: dict[str, object] = {"issues": {}}

    record_dispatched_issues(state=state, issues=[issue], base_head="head123")

    entry = state["issues"]["23"]
    assert entry["issue_updated_at"] == updated_at.isoformat()
    assert entry["base_head"] == "head123"
    assert "last_dispatched_at" in entry
