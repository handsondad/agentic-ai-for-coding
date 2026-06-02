"""Tests for offline eval replay runner."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


def _load_module() -> object:
    script_path = (
        Path(__file__).resolve().parents[2]
        / ".github"
        / "automation"
        / "scripts"
        / "replay-eval.py"
    )
    spec = importlib.util.spec_from_file_location("replay_eval", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _sample(index: int, *, baseline_success: bool, candidate_success: bool) -> dict[str, object]:
    failure_message = "connection timeout to api server" if not candidate_success else ""
    return {
        "id": f"eval-{index:03d}",
        "title": f"sample-{index}",
        "type": "task",
        "risk": "low",
        "issue_body": "body",
        "expected_output": "output",
        "replays": {
            "baseline": {
                "success": baseline_success,
                "gate_passed": baseline_success,
                "duration_ms": 1000 + index,
                "failure_message": "quality gate failed due to lint error" if not baseline_success else "",
            },
            "candidate": {
                "success": candidate_success,
                "gate_passed": candidate_success,
                "duration_ms": 800 + index,
                "failure_message": failure_message,
            },
        },
    }


def _build_dataset() -> dict[str, object]:
    samples = [
        _sample(1, baseline_success=False, candidate_success=True),
        _sample(2, baseline_success=False, candidate_success=True),
        _sample(3, baseline_success=True, candidate_success=True),
        _sample(4, baseline_success=True, candidate_success=False),
        _sample(5, baseline_success=False, candidate_success=True),
        _sample(6, baseline_success=True, candidate_success=True),
        _sample(7, baseline_success=False, candidate_success=True),
        _sample(8, baseline_success=True, candidate_success=True),
        _sample(9, baseline_success=False, candidate_success=True),
        _sample(10, baseline_success=True, candidate_success=True),
        _sample(11, baseline_success=False, candidate_success=True),
        _sample(12, baseline_success=True, candidate_success=False),
        _sample(13, baseline_success=False, candidate_success=True),
        _sample(14, baseline_success=True, candidate_success=True),
        _sample(15, baseline_success=False, candidate_success=False),
        _sample(16, baseline_success=True, candidate_success=True),
        _sample(17, baseline_success=False, candidate_success=True),
        _sample(18, baseline_success=True, candidate_success=True),
        _sample(19, baseline_success=False, candidate_success=True),
        _sample(20, baseline_success=True, candidate_success=True),
    ]
    return {"version": 1, "name": "test-dataset", "samples": samples}


def test_load_dataset_rejects_small_dataset(tmp_path: Path) -> None:
    module = _load_module()
    dataset_path = tmp_path / "dataset.json"
    dataset_path.write_text(json.dumps({"samples": [1]}), encoding="utf-8")

    with pytest.raises(ValueError, match="至少需要 20 条"):
        module.load_dataset(dataset_path)


def test_aggregate_for_strategy_and_compare(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    dataset_path = tmp_path / "dataset.json"
    dataset_path.write_text(json.dumps(_build_dataset(), ensure_ascii=False), encoding="utf-8")

    samples = module.load_dataset(dataset_path)
    aggregate = module.aggregate_for_strategy(samples, "candidate")
    baseline = module.aggregate_for_strategy(samples, "baseline")
    comparison = module.compare_aggregates(baseline, aggregate)

    assert aggregate.total == 20
    assert aggregate.success_count == 17
    assert aggregate.gate_pass_count == 17
    assert aggregate.success_rate == 85.0
    assert aggregate.gate_pass_rate == 85.0
    assert aggregate.failure_categories["environment_blocker"] == 3
    assert comparison["success_rate_delta_pp"] == 35.0
    assert comparison["gate_pass_rate_delta_pp"] == 35.0
    assert comparison["avg_duration_ms_delta"] == -200.0


def test_compare_with_previous_report(tmp_path: Path) -> None:
    module = _load_module()
    current = module.ReplayAggregate(
        strategy="candidate",
        total=20,
        success_count=17,
        success_rate=85.0,
        gate_pass_count=17,
        gate_pass_rate=85.0,
        avg_duration_ms=812.0,
        failure_categories={"environment_blocker": 1},
    )
    previous_report = {
        "summary": {
            "success_rate": 70.0,
            "gate_pass_rate": 75.0,
            "avg_duration_ms": 900.0,
        }
    }

    comparison = module.compare_with_previous(current, previous_report)

    assert comparison == {
        "success_rate_delta_pp": 15.0,
        "gate_pass_rate_delta_pp": 10.0,
        "avg_duration_ms_delta": -88.0,
    }


def test_main_writes_report_and_summary(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    dataset_path = tmp_path / "dataset.json"
    dataset_path.write_text(json.dumps(_build_dataset(), ensure_ascii=False), encoding="utf-8")

    report_file = tmp_path / "report.json"
    summary_file = tmp_path / "summary.md"

    monkeypatch.setattr(
        module,
        "parse_args",
        lambda: module.argparse.Namespace(
            dataset=str(dataset_path),
            strategy="candidate",
            baseline_strategy="baseline",
            compare_to="",
            repo_root=str(tmp_path),
            report_file=str(report_file),
            summary_file=str(summary_file),
        ),
    )

    module.main()

    payload = json.loads(report_file.read_text(encoding="utf-8"))
    assert payload["strategy"] == "candidate"
    assert payload["summary"]["total"] == 20
    assert payload["comparison"]["success_rate_delta_pp"] == 35.0
    assert "Offline Eval Replay Summary" in summary_file.read_text(encoding="utf-8")
