"""Online execution metrics collection and weekly snapshot helpers."""

from __future__ import annotations

import json
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from .failure_reporting import classify_failure
except ImportError:
    from failure_reporting import classify_failure


@dataclass(slots=True)
class ExecutionMetricEvent:
    """Single issue execution event captured by the automation service."""

    issue_number: int
    issue_title: str
    issue_identifier: str
    issue_created_at: str | None
    started_at: str
    completed_at: str
    duration_ms: int
    success: bool
    pr_created: bool
    pr_url: str | None
    quality_gate_passed: bool
    quality_gate_failures: int
    failure_step: str | None = None
    failure_message: str | None = None
    failure_category: str | None = None
    failure_reason: str | None = None
    retryable: bool | None = None
    labels: list[str] = field(default_factory=list)
    branch_name: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the event to a JSON-serializable dictionary."""
        return asdict(self)


def append_event(event_file: Path, event: ExecutionMetricEvent) -> None:
    """Append one execution event to the JSONL event stream."""
    event_file.parent.mkdir(parents=True, exist_ok=True)
    with event_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event.to_dict(), ensure_ascii=False))
        handle.write("\n")


def load_events(event_file: Path) -> list[dict[str, Any]]:
    """Load execution events from a JSONL file."""
    if not event_file.exists():
        return []

    events: list[dict[str, Any]] = []
    for raw_line in event_file.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip().lstrip("\ufeff")
        if not line:
            continue
        payload = json.loads(line)
        if isinstance(payload, dict):
            events.append(payload)
    return events


def build_weekly_snapshot(events: list[dict[str, Any]], period: str = "weekly") -> dict[str, Any]:
    """Aggregate issue execution events into a weekly snapshot."""
    grouped = _group_events_by_issue(events)
    issue_summaries = [
        _summarize_issue(issue_number, attempts)
        for issue_number, attempts in grouped.items()
    ]

    total_issues = len(issue_summaries)
    success_count = sum(1 for item in issue_summaries if item["success"])
    first_pass_count = sum(1 for item in issue_summaries if item["first_pass"])
    rework_count = sum(1 for item in issue_summaries if item["attempt_count"] > 1)
    gate_pass_count = sum(1 for item in issue_summaries if item["quality_gate_passed"])

    lead_times = [
        item["lead_time_ms"]
        for item in issue_summaries
        if item["lead_time_ms"] is not None
    ]
    failure_counter = Counter(
        item["failure_category"]
        for item in issue_summaries
        if not item["success"] and item["failure_category"]
    )

    snapshot: dict[str, Any] = {
        "period": period,
        "generated_at": _now_iso(),
        "summary": {
            "total_issues": total_issues,
            "success_count": success_count,
            "success_rate": _rate(success_count, total_issues),
            "first_pass_count": first_pass_count,
            "first_pass_rate": _rate(first_pass_count, total_issues),
            "rework_count": rework_count,
            "rework_rate": _rate(rework_count, total_issues),
            "gate_pass_count": gate_pass_count,
            "gate_pass_rate": _rate(gate_pass_count, total_issues),
            "avg_lead_time_ms": _average(lead_times),
        },
        "top_blockers": _top_blockers(failure_counter),
        "issues": issue_summaries,
    }
    return snapshot


def compare_snapshots(current: dict[str, Any], previous: dict[str, Any]) -> dict[str, float]:
    """Compare two weekly snapshots and return KPI deltas."""
    current_summary = current.get("summary", {}) if isinstance(current, dict) else {}
    previous_summary = previous.get("summary", {}) if isinstance(previous, dict) else {}

    return {
        "success_rate_delta_pp": _delta(current_summary, previous_summary, "success_rate"),
        "first_pass_rate_delta_pp": _delta(current_summary, previous_summary, "first_pass_rate"),
        "rework_rate_delta_pp": _delta(current_summary, previous_summary, "rework_rate"),
        "gate_pass_rate_delta_pp": _delta(current_summary, previous_summary, "gate_pass_rate"),
        "avg_lead_time_ms_delta": _delta(current_summary, previous_summary, "avg_lead_time_ms"),
    }


def render_weekly_report(
    snapshot: dict[str, Any],
    comparison: dict[str, float] | None = None,
) -> str:
    """Render a markdown weekly report from a snapshot."""
    summary = snapshot.get("summary", {}) if isinstance(snapshot, dict) else {}
    comparison = comparison or {}
    blockers = snapshot.get("top_blockers", []) if isinstance(snapshot, dict) else []

    lines = [
        "# Weekly AI Coding Metrics",
        "",
        f"- period: `{snapshot.get('period', 'weekly')}`",
        f"- generated_at: `{snapshot.get('generated_at', '')}`",
        "",
        "## KPI Snapshot",
        "",
        "| KPI | Value |",
        "| --- | ---: |",
        f"| Total issues | {summary.get('total_issues', 0)} |",
        f"| Success rate | {summary.get('success_rate', 0)}% |",
        f"| First-pass rate | {summary.get('first_pass_rate', 0)}% |",
        f"| Rework rate | {summary.get('rework_rate', 0)}% |",
        f"| Gate pass rate | {summary.get('gate_pass_rate', 0)}% |",
        f"| Avg lead time (ms) | {summary.get('avg_lead_time_ms', 0)} |",
        "",
        "## Trend",
    ]

    if comparison:
        lines.extend(
            [
                f"- success_rate_delta_pp: `{comparison.get('success_rate_delta_pp', 0)}`",
                f"- first_pass_rate_delta_pp: `{comparison.get('first_pass_rate_delta_pp', 0)}`",
                f"- rework_rate_delta_pp: `{comparison.get('rework_rate_delta_pp', 0)}`",
                f"- gate_pass_rate_delta_pp: `{comparison.get('gate_pass_rate_delta_pp', 0)}`",
                f"- avg_lead_time_ms_delta: `{comparison.get('avg_lead_time_ms_delta', 0)}`",
            ]
        )
    else:
        lines.append("- no comparison snapshot provided")

    lines.extend(["", "## Top 3 Blockers"])
    if blockers:
        for item in blockers[:3]:
            lines.append(
                f"- {item['category']}: {item['count']} ({item['share']}%)"
            )
    else:
        lines.append("- no blockers recorded")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Data source: `.automation/execution-metrics.jsonl`",
            (
                "- Lead time is measured from GitHub issue creation to automation completion "
                "when timestamps are available."
            ),
        ]
    )
    return "\n".join(lines) + "\n"


def write_json_snapshot(snapshot: dict[str, Any], output_file: Path) -> None:
    """Write a snapshot JSON file."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")


def write_markdown_report(report: str, output_file: Path) -> None:
    """Write a markdown report file."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(report, encoding="utf-8")


def _group_events_by_issue(events: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    grouped: dict[int, list[dict[str, Any]]] = {}
    for event in events:
        issue_number = event.get("issue_number")
        if not isinstance(issue_number, int):
            continue
        grouped.setdefault(issue_number, []).append(event)

    for attempts in grouped.values():
        attempts.sort(key=_event_sort_key)
    return grouped


def _summarize_issue(issue_number: int, attempts: list[dict[str, Any]]) -> dict[str, Any]:
    final_event = attempts[-1]
    created_at = _parse_datetime(final_event.get("issue_created_at"))
    completed_at = _parse_datetime(final_event.get("completed_at"))

    lead_time_ms: int | None = None
    if created_at is not None and completed_at is not None:
        lead_time_ms = int((completed_at - created_at).total_seconds() * 1000)

    failure_category = final_event.get("failure_category")
    if not isinstance(failure_category, str) or not failure_category.strip():
        failure_message = str(final_event.get("failure_message", "")).strip()
        if failure_message:
            failure_category = classify_failure(failure_message).category
        else:
            failure_category = None

    success = bool(final_event.get("success", False))
    pr_created = bool(final_event.get("pr_created", False))
    quality_gate_passed = bool(final_event.get("quality_gate_passed", False))

    return {
        "issue_number": issue_number,
        "issue_title": str(final_event.get("issue_title", "")),
        "attempt_count": len(attempts),
        "success": success,
        "first_pass": success and pr_created and quality_gate_passed and len(attempts) == 1,
        "reworked": len(attempts) > 1,
        "pr_created": pr_created,
        "quality_gate_passed": quality_gate_passed,
        "lead_time_ms": lead_time_ms,
        "failure_category": failure_category,
    }


def _top_blockers(counter: Counter[str]) -> list[dict[str, Any]]:
    total = sum(counter.values())
    if total <= 0:
        return []

    blockers: list[dict[str, Any]] = []
    for category, count in counter.most_common(3):
        blockers.append(
            {
                "category": category,
                "count": count,
                "share": round((count / total) * 100, 2),
            }
        )
    return blockers


def _rate(count: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round((count / total) * 100, 2)


def _average(values: list[int]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 2)


def _delta(current_summary: dict[str, Any], previous_summary: dict[str, Any], key: str) -> float:
    current_value = float(current_summary.get(key, 0.0))
    previous_value = float(previous_summary.get(key, 0.0))
    if key.endswith("_ms"):
        return round(current_value - previous_value, 2)
    return round(current_value - previous_value, 2)


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None

    normalized = value.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def _event_sort_key(event: dict[str, Any]) -> tuple[str, int]:
    completed_at = str(event.get("completed_at", ""))
    duration_raw = event.get("duration_ms", 0)
    duration_ms = int(duration_raw) if isinstance(duration_raw, int) else 0
    return completed_at, duration_ms


def _now_iso() -> str:
    return datetime.now(tz=UTC).isoformat()
