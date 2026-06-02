"""Tests for unified quality-gate runner."""

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
        / "quality-gate.py"
    )
    spec = importlib.util.spec_from_file_location("quality_gate_runner", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_build_steps_quick_contains_expected_gate_names() -> None:
    module = _load_module()

    steps = module.build_steps("quick")

    assert [step.name for step in steps] == [
        "format-check",
        "lint",
        "type-check",
        "unit-test",
    ]


def test_build_steps_full_includes_integration() -> None:
    module = _load_module()

    steps = module.build_steps("full")

    assert steps[-1].name == "integration-test"


def test_run_quality_gates_stops_on_first_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    module = _load_module()
    calls: list[str] = []

    def fake_run_step(step: object, cwd: Path) -> object:
        calls.append(step.name)
        exit_code = 1 if step.name == "lint" else 0
        return module.GateResult(
            name=step.name,
            command=step.command,
            exit_code=exit_code,
            duration_ms=1,
            output="failed" if exit_code else "ok",
        )

    monkeypatch.setattr(module, "run_step", fake_run_step)

    results = module.run_quality_gates("quick", tmp_path, continue_on_error=False)

    assert [item.name for item in results] == ["format-check", "lint"]
    assert calls == ["format-check", "lint"]


def test_write_report_creates_expected_summary(tmp_path: Path) -> None:
    module = _load_module()

    results = [
        module.GateResult(
            name="format-check",
            command=["python", "-m", "ruff", "format", "--check"],
            exit_code=0,
            duration_ms=10,
            output="ok",
        ),
        module.GateResult(
            name="lint",
            command=["python", "-m", "ruff", "check"],
            exit_code=1,
            duration_ms=20,
            output="error",
        ),
    ]
    report_file = tmp_path / "gate-report.json"

    module.write_report(results, "quick", report_file)

    payload = json.loads(report_file.read_text(encoding="utf-8"))
    assert payload["mode"] == "quick"
    assert payload["summary"]["total"] == 2
    assert payload["summary"]["passed"] == 1
    assert payload["summary"]["failed"] == 1
    assert payload["summary"]["overall_status"] == "fail"


def test_markdown_summary_contains_first_failure_block() -> None:
    module = _load_module()

    results = [
        module.GateResult(
            name="format-check",
            command=["python", "-m", "ruff", "format", "--check"],
            exit_code=0,
            duration_ms=10,
            output="ok",
        ),
        module.GateResult(
            name="lint",
            command=["python", "-m", "ruff", "check"],
            exit_code=1,
            duration_ms=20,
            output="line 1: fail",
        ),
    ]

    markdown = module.markdown_summary(results, "quick")

    assert "## Quality Gate Summary" in markdown
    assert "- [PASS] `format-check`" in markdown
    assert "- [FAIL] `lint`" in markdown
    assert "### First Failure" in markdown
    assert "```text" in markdown


def test_write_markdown_summary_writes_file(tmp_path: Path) -> None:
    module = _load_module()
    results = [
        module.GateResult(
            name="format-check",
            command=["python", "-m", "ruff", "format", "--check"],
            exit_code=0,
            duration_ms=10,
            output="ok",
        )
    ]
    summary_file = tmp_path / "summary.md"

    module.write_markdown_summary(results, "quick", summary_file)

    text = summary_file.read_text(encoding="utf-8")
    assert "Quality Gate Summary" in text
    assert "overall: `pass`" in text
