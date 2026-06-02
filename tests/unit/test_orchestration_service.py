"""调度服务测试。"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

AUTOMATION_DIR = Path(__file__).resolve().parents[2] / ".github" / "automation"
if str(AUTOMATION_DIR) not in sys.path:
    sys.path.insert(0, str(AUTOMATION_DIR))

models_module = importlib.import_module("models")
service_module = importlib.import_module("service")

GitHubIssue = models_module.GitHubIssue
filter_new_candidates = service_module.filter_new_candidates


def test_filter_new_candidates_excludes_claimed() -> None:
    """已占用 issue 不应重复调度。"""
    issues = [
        GitHubIssue(
            number=1,
            title="One",
            body="",
            state="open",
            html_url="https://example.com/1",
            labels=["ai-ready"],
        ),
        GitHubIssue(
            number=2,
            title="Two",
            body="",
            state="open",
            html_url="https://example.com/2",
            labels=["ai-ready"],
        ),
    ]

    filtered = filter_new_candidates(issues, claimed={2})

    assert [item.number for item in filtered] == [1]
