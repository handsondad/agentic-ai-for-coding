"""Tests for online metrics snapshot generation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module() -> object:
    script_path = (
        Path(__file__).resolve().parents[2]
        / ".github"
        / "automation"
        / "metrics.py"
    )
    spec = importlib.util.spec_from_file_location("automation_metrics", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _event(
    issue_number: int,
    *,
    success: bool,
    pr_created: bool,
    quality_gate_passed: bool,
    failure_category: str | None = None,
    issue_created_at: str = "2026-06-01T00:00:00+00:00",
    started_at: str = "2026-06-01T00:00:00+00:00",
    completed_at: str = "2026-06-01T00:30:00+00:00",
) -> dict[str, object]:
    return {
        "issue_number": issue_number,
        "issue_title": f"issue-{issue_number}",
        "issue_identifier": f"#{issue_number}",
        "issue_created_at": issue_created_at,
        "started_at": started_at,
        "completed_at": completed_at,
        "duration_ms": 1800,
        "success": success,
        "pr_created": pr_created,
        "pr_url": "https://example.com/pr" if pr_created else None,
        "quality_gate_passed": quality_gate_passed,
        "quality_gate_failures": 0 if quality_gate_passed else 1,
        "failure_step": None if success else "pipeline",
        "failure_message": None if success else "timeout while running quality gate",
        "failure_category": failure_category,
        "failure_reason": None,
        "retryable": None,
        "labels": ["ai-ready"],
        "branch_name": f"ai/issue-{issue_number}",
    }


def test_build_weekly_snapshot_aggregates_kpis() -> None:
    module = _load_module()
    events = [
        _event(
            1,
            success=False,
            pr_created=False,
            quality_gate_passed=False,
            failure_category="environment_blocker",
        ),
        _event(1, success=True, pr_created=True, quality_gate_passed=True),
        _event(2, success=True, pr_created=True, quality_gate_passed=True),
        _event(
            3,
            success=False,
            pr_created=False,
            quality_gate_passed=False,
            failure_category="code_defect",
        ),
    ]

    snapshot = module.build_weekly_snapshot(events)

    assert snapshot["summary"]["total_issues"] == 3
    assert snapshot["summary"]["success_count"] == 2
    assert snapshot["summary"]["first_pass_count"] == 1
    assert snapshot["summary"]["rework_count"] == 1
    assert snapshot["summary"]["gate_pass_count"] == 2
    assert snapshot["top_blockers"][0]["category"] == "code_defect"
    assert snapshot["top_blockers"][0]["count"] == 1


def test_compare_snapshots_returns_deltas() -> None:
    module = _load_module()
    current = {
        "summary": {
            "success_rate": 90.0,
            "first_pass_rate": 80.0,
            "rework_rate": 10.0,
            "gate_pass_rate": 85.0,
            "avg_lead_time_ms": 1800.0,
        }
    }
    previous = {
        "summary": {
            "success_rate": 80.0,
            "first_pass_rate": 75.0,
            "rework_rate": 15.0,
            "gate_pass_rate": 82.0,
            "avg_lead_time_ms": 2000.0,
        }
    }

    comparison = module.compare_snapshots(current, previous)

    assert comparison == {
        "success_rate_delta_pp": 10.0,
        "first_pass_rate_delta_pp": 5.0,
        "rework_rate_delta_pp": -5.0,
        "gate_pass_rate_delta_pp": 3.0,
        "avg_lead_time_ms_delta": -200.0,
    }


def test_render_weekly_report_contains_trends_and_blockers() -> None:
    module = _load_module()
    snapshot = {
        "period": "weekly",
        "generated_at": "2026-06-02T00:00:00+00:00",
        "summary": {
            "total_issues": 3,
            "success_rate": 66.67,
            "first_pass_rate": 33.33,
            "rework_rate": 33.33,
            "gate_pass_rate": 66.67,
            "avg_lead_time_ms": 1800.0,
        },
        "top_blockers": [{"category": "code_defect", "count": 2, "share": 66.67}],
    }

    report = module.render_weekly_report(
        snapshot,
        {
            "success_rate_delta_pp": 4.0,
            "first_pass_rate_delta_pp": 2.0,
            "rework_rate_delta_pp": -2.0,
            "gate_pass_rate_delta_pp": 1.0,
            "avg_lead_time_ms_delta": -100.0,
        },
    )

    assert "Weekly AI Coding Metrics" in report
    assert "success_rate_delta_pp" in report
    assert "Top 3 Blockers" in report
    assert "code_defect" in report


def test_append_and_load_events_roundtrip(tmp_path: Path) -> None:
    module = _load_module()
    event_file = tmp_path / "metrics.jsonl"
    event = module.ExecutionMetricEvent(
        issue_number=1,
        issue_title="issue-1",
        issue_identifier="#1",
        issue_created_at="2026-06-01T00:00:00+00:00",
        started_at="2026-06-01T00:00:00+00:00",
        completed_at="2026-06-01T00:10:00+00:00",
        duration_ms=600000,
        success=True,
        pr_created=True,
        pr_url="https://example.com/pr",
        quality_gate_passed=True,
        quality_gate_failures=0,
        labels=["ai-ready"],
        branch_name="ai/issue-1",
    )

    module.append_event(event_file, event)
    loaded = module.load_events(event_file)

    assert len(loaded) == 1
    assert loaded[0]["issue_number"] == 1
    assert loaded[0]["success"] is True
