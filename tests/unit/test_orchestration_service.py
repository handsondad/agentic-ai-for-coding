"""Celery 调度器依赖分层测试。"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

AUTOMATION_DIR = Path(__file__).resolve().parents[2] / ".github" / "automation"
if str(AUTOMATION_DIR) not in sys.path:
    sys.path.insert(0, str(AUTOMATION_DIR))

models_module = importlib.import_module("models")
dispatcher_module = importlib.import_module("celery_dispatcher")

GitHubIssue = models_module.GitHubIssue
build_dependency_levels = dispatcher_module.build_dependency_levels


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
