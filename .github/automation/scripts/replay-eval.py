"""Offline evaluation dataset replay and strategy comparison runner."""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
AUTOMATION_DIR = SCRIPT_DIR.parent

if str(AUTOMATION_DIR) not in sys.path:
    sys.path.insert(0, str(AUTOMATION_DIR))

from failure_reporting import classify_failure  # noqa: E402


@dataclass(slots=True)
class ReplayAggregate:
    """Aggregate metrics for one replay strategy."""

    strategy: str
    total: int
    success_count: int
    success_rate: float
    gate_pass_count: int
    gate_pass_rate: float
    avg_duration_ms: float
    failure_categories: dict[str, int]


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Replay offline evaluation dataset")
    parser.add_argument(
        "--dataset",
        required=True,
        help="Path to dataset JSON file",
    )
    parser.add_argument(
        "--strategy",
        default="candidate",
        help="Strategy key to evaluate in dataset sample.replays",
    )
    parser.add_argument(
        "--baseline-strategy",
        default="",
        help="Optional baseline strategy key for same-run comparison",
    )
    parser.add_argument(
        "--compare-to",
        default="",
        help="Optional previous report JSON for trend comparison",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root for resolving relative output paths",
    )
    parser.add_argument(
        "--report-file",
        default=".automation/eval-report.json",
        help="JSON report output path",
    )
    parser.add_argument(
        "--summary-file",
        default=".automation/eval-summary.md",
        help="Markdown summary output path",
    )
    return parser.parse_args()


def _load_failure_classifier():
    """Return the repository failure classifier callable."""
    return classify_failure


def load_dataset(path: Path) -> list[dict[str, object]]:
    """Load dataset JSON samples and validate basic constraints."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    samples = payload.get("samples")
    if not isinstance(samples, list):
        raise ValueError("dataset 格式错误：samples 必须是列表")
    if len(samples) < 20:
        raise ValueError("dataset 样本不足：至少需要 20 条")
    return samples


def _get_sample_replay(sample: dict[str, object], strategy: str) -> dict[str, object]:
    replays = sample.get("replays")
    if not isinstance(replays, dict):
        sample_id = sample.get("id", "<unknown>")
        raise ValueError(f"样本 {sample_id} 缺少 replays 字段")

    replay = replays.get(strategy)
    if not isinstance(replay, dict):
        sample_id = sample.get("id", "<unknown>")
        raise ValueError(f"样本 {sample_id} 缺少策略 {strategy} 的回放结果")
    return replay


def aggregate_for_strategy(samples: list[dict[str, object]], strategy: str) -> ReplayAggregate:
    """Aggregate metrics for the selected strategy."""
    classify_failure = _load_failure_classifier()

    success_count = 0
    gate_pass_count = 0
    total_duration = 0
    failure_categories: dict[str, int] = {}

    for sample in samples:
        replay = _get_sample_replay(sample, strategy)
        success = bool(replay.get("success", False))
        gate_passed = bool(replay.get("gate_passed", False))
        duration_ms = int(replay.get("duration_ms", 0))
        failure_message = str(replay.get("failure_message", ""))

        success_count += 1 if success else 0
        gate_pass_count += 1 if gate_passed else 0
        total_duration += duration_ms

        if not success:
            classification = classify_failure(failure_message)
            failure_categories[classification.category] = (
                failure_categories.get(classification.category, 0) + 1
            )

    total = len(samples)
    return ReplayAggregate(
        strategy=strategy,
        total=total,
        success_count=success_count,
        success_rate=round((success_count / total) * 100, 2),
        gate_pass_count=gate_pass_count,
        gate_pass_rate=round((gate_pass_count / total) * 100, 2),
        avg_duration_ms=round(total_duration / total, 2),
        failure_categories=failure_categories,
    )


def compare_aggregates(
    baseline: ReplayAggregate,
    candidate: ReplayAggregate,
) -> dict[str, float]:
    """Compare baseline and candidate metrics."""
    return {
        "success_rate_delta_pp": round(candidate.success_rate - baseline.success_rate, 2),
        "gate_pass_rate_delta_pp": round(candidate.gate_pass_rate - baseline.gate_pass_rate, 2),
        "avg_duration_ms_delta": round(candidate.avg_duration_ms - baseline.avg_duration_ms, 2),
    }


def compare_with_previous(
    current: ReplayAggregate,
    previous_report: dict[str, object],
) -> dict[str, float]:
    """Compare current aggregate with previous report summary."""
    previous_summary = previous_report.get("summary", {})
    if not isinstance(previous_summary, dict):
        return {}

    previous_success_rate = float(previous_summary.get("success_rate", 0.0))
    previous_gate_rate = float(previous_summary.get("gate_pass_rate", 0.0))
    previous_duration = float(previous_summary.get("avg_duration_ms", 0.0))

    return {
        "success_rate_delta_pp": round(current.success_rate - previous_success_rate, 2),
        "gate_pass_rate_delta_pp": round(current.gate_pass_rate - previous_gate_rate, 2),
        "avg_duration_ms_delta": round(current.avg_duration_ms - previous_duration, 2),
    }


def report_payload(
    dataset_path: Path,
    aggregate: ReplayAggregate,
    strategy_comparison: dict[str, float],
) -> dict[str, object]:
    """Build report payload for JSON output."""
    return {
        "generated_at": int(time.time()),
        "dataset": str(dataset_path),
        "strategy": aggregate.strategy,
        "summary": {
            "total": aggregate.total,
            "success_count": aggregate.success_count,
            "success_rate": aggregate.success_rate,
            "gate_pass_count": aggregate.gate_pass_count,
            "gate_pass_rate": aggregate.gate_pass_rate,
            "avg_duration_ms": aggregate.avg_duration_ms,
        },
        "failure_categories": aggregate.failure_categories,
        "comparison": strategy_comparison,
    }


def markdown_summary(payload: dict[str, object]) -> str:
    """Render markdown summary for PR/issue comments."""
    summary = payload.get("summary", {})
    failure_categories = payload.get("failure_categories", {})
    comparison = payload.get("comparison", {})

    lines = [
        "## Offline Eval Replay Summary",
        "",
        f"- dataset: `{payload.get('dataset', '')}`",
        f"- strategy: `{payload.get('strategy', '')}`",
        f"- total: `{summary.get('total', 0)}`",
        f"- success_rate: `{summary.get('success_rate', 0)}%`",
        f"- gate_pass_rate: `{summary.get('gate_pass_rate', 0)}%`",
        f"- avg_duration_ms: `{summary.get('avg_duration_ms', 0)}`",
        "",
        "### Failure Categories",
    ]

    if isinstance(failure_categories, dict) and failure_categories:
        for category, count in sorted(failure_categories.items(), key=lambda item: item[0]):
            lines.append(f"- {category}: {count}")
    else:
        lines.append("- none")

    lines.extend(["", "### Comparison"])
    if isinstance(comparison, dict) and comparison:
        lines.append(f"- success_rate_delta_pp: `{comparison.get('success_rate_delta_pp', 0)}`")
        lines.append(f"- gate_pass_rate_delta_pp: `{comparison.get('gate_pass_rate_delta_pp', 0)}`")
        lines.append(f"- avg_duration_ms_delta: `{comparison.get('avg_duration_ms_delta', 0)}`")
    else:
        lines.append("- none")

    return "\n".join(lines) + "\n"


def write_report(payload: dict[str, object], report_path: Path) -> None:
    """Write JSON report file."""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_markdown(summary: str, summary_path: Path) -> None:
    """Write markdown summary file."""
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(summary, encoding="utf-8")


def main() -> None:
    """CLI entrypoint."""
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()

    dataset_path = Path(args.dataset)
    if not dataset_path.is_absolute():
        dataset_path = repo_root / dataset_path

    report_path = Path(args.report_file)
    if not report_path.is_absolute():
        report_path = repo_root / report_path

    summary_path = Path(args.summary_file)
    if not summary_path.is_absolute():
        summary_path = repo_root / summary_path

    samples = load_dataset(dataset_path)
    aggregate = aggregate_for_strategy(samples, args.strategy)

    comparison: dict[str, float] = {}
    if args.baseline_strategy.strip():
        baseline_aggregate = aggregate_for_strategy(samples, args.baseline_strategy.strip())
        comparison = compare_aggregates(baseline_aggregate, aggregate)
    elif args.compare_to.strip():
        compare_path = Path(args.compare_to)
        if not compare_path.is_absolute():
            compare_path = repo_root / compare_path
        previous_report = json.loads(compare_path.read_text(encoding="utf-8"))
        comparison = compare_with_previous(aggregate, previous_report)

    payload = report_payload(dataset_path, aggregate, comparison)
    summary = markdown_summary(payload)
    write_report(payload, report_path)
    write_markdown(summary, summary_path)

    print("Offline replay completed")
    print(f"Report: {report_path}")
    print(f"Summary: {summary_path}")
    print(f"Success rate: {aggregate.success_rate}%")
    print(f"Gate pass rate: {aggregate.gate_pass_rate}%")


if __name__ == "__main__":
    main()
