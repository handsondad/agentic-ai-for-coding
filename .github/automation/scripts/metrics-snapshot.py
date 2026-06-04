"""Generate weekly online metrics snapshot and markdown report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
AUTOMATION_DIR = SCRIPT_DIR.parent

if str(AUTOMATION_DIR) not in sys.path:
    sys.path.insert(0, str(AUTOMATION_DIR))

from metrics import (  # noqa: E402
    build_weekly_snapshot,
    compare_snapshots,
    load_events,
    render_weekly_report,
    write_json_snapshot,
    write_markdown_report,
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate weekly metrics snapshot")
    parser.add_argument(
        "--period", default="weekly", choices=["weekly"], help="Snapshot period"
    )
    parser.add_argument(
        "--events-file",
        default=".automation/execution-metrics.jsonl",
        help="Execution event JSONL file",
    )
    parser.add_argument(
        "--snapshot-file",
        default=".automation/weekly-metrics-snapshot.json",
        help="Output snapshot JSON file",
    )
    parser.add_argument(
        "--report-file",
        default=".automation/weekly-metrics-report.md",
        help="Output markdown report file",
    )
    parser.add_argument(
        "--compare-to",
        default="",
        help="Optional previous snapshot JSON for trend comparison",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root used to resolve relative paths",
    )
    return parser.parse_args()


def _resolve_path(path_text: str, repo_root: Path) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return (repo_root / path).resolve()


def main() -> None:
    """CLI entrypoint."""
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()

    events_file = _resolve_path(args.events_file, repo_root)
    snapshot_file = _resolve_path(args.snapshot_file, repo_root)
    report_file = _resolve_path(args.report_file, repo_root)

    events = load_events(events_file)
    snapshot = build_weekly_snapshot(events, period=args.period)

    comparison: dict[str, float] | None = None
    if args.compare_to.strip():
        compare_path = _resolve_path(args.compare_to, repo_root)
        if compare_path.exists():
            previous = json.loads(compare_path.read_text(encoding="utf-8"))
            comparison = compare_snapshots(snapshot, previous)

    write_json_snapshot(snapshot, snapshot_file)
    write_markdown_report(render_weekly_report(snapshot, comparison), report_file)

    print("Weekly metrics snapshot generated")
    print(f"Events: {events_file}")
    print(f"Snapshot: {snapshot_file}")
    print(f"Report: {report_file}")
    print(f"Success rate: {snapshot['summary']['success_rate']}%")
    print(f"First-pass rate: {snapshot['summary']['first_pass_rate']}%")
    print(f"Rework rate: {snapshot['summary']['rework_rate']}%")
    print(f"Gate pass rate: {snapshot['summary']['gate_pass_rate']}%")


if __name__ == "__main__":
    main()
