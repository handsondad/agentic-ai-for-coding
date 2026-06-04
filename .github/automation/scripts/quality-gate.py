"""Unified quality-gate runner for local and CI workflows."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(slots=True)
class GateStep:
    """A single quality-gate command step."""

    name: str
    command: list[str]


@dataclass(slots=True)
class GateResult:
    """Execution result of one gate step."""

    name: str
    command: list[str]
    exit_code: int
    duration_ms: int
    output: str

    @property
    def status(self) -> str:
        """Return step status as pass/fail."""
        return "pass" if self.exit_code == 0 else "fail"


def build_steps(mode: str) -> list[GateStep]:
    """Build quality-gate steps by mode."""
    steps = [
        GateStep(
            name="format-check",
            command=[
                "python",
                "-m",
                "ruff",
                "format",
                "--check",
                "src",
                "tests",
                ".github",
            ],
        ),
        GateStep(
            name="lint",
            command=["python", "-m", "ruff", "check", "src", "tests", ".github"],
        ),
        GateStep(
            name="type-check",
            command=["python", "-m", "mypy", "src", "--ignore-missing-imports"],
        ),
        GateStep(
            name="unit-test",
            command=["python", "-m", "pytest", "tests/unit", "-v"],
        ),
    ]

    if mode in {"full", "ci"}:
        steps.append(
            GateStep(
                name="integration-test",
                command=[
                    "python",
                    "-m",
                    "pytest",
                    "tests/integration",
                    "-v",
                    "--timeout=60",
                ],
            )
        )

    return steps


def run_step(step: GateStep, cwd: Path) -> GateResult:
    """Execute one gate step and return structured result."""
    start = time.perf_counter()
    process = subprocess.run(  # noqa: S603
        step.command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
        encoding="utf-8",
        errors="replace",
    )
    duration_ms = int((time.perf_counter() - start) * 1000)
    output = (process.stdout or "") + (process.stderr or "")

    return GateResult(
        name=step.name,
        command=step.command,
        exit_code=process.returncode,
        duration_ms=duration_ms,
        output=output,
    )


def run_quality_gates(mode: str, cwd: Path, continue_on_error: bool) -> list[GateResult]:
    """Run all configured quality-gate steps."""
    results: list[GateResult] = []
    for step in build_steps(mode):
        result = run_step(step, cwd)
        results.append(result)
        if result.exit_code != 0 and not continue_on_error:
            break
    return results


def report_payload(results: list[GateResult], mode: str) -> dict[str, object]:
    """Build JSON payload for gate report output."""
    failed = [item for item in results if item.exit_code != 0]
    return {
        "mode": mode,
        "generated_at": int(time.time()),
        "summary": {
            "total": len(results),
            "passed": len(results) - len(failed),
            "failed": len(failed),
            "overall_status": "pass" if not failed else "fail",
        },
        "steps": [
            {
                **asdict(item),
                "status": item.status,
            }
            for item in results
        ],
    }


def markdown_summary(results: list[GateResult], mode: str) -> str:
    """Render a PR/issue-friendly markdown summary."""
    failed = [item for item in results if item.exit_code != 0]
    lines = [
        "## Quality Gate Summary",
        "",
        f"- mode: `{mode}`",
        f"- total: `{len(results)}`",
        f"- failed: `{len(failed)}`",
        f"- overall: `{'pass' if not failed else 'fail'}`",
        "",
        "### Steps",
    ]

    for result in results:
        icon = "PASS" if result.exit_code == 0 else "FAIL"
        lines.append(f"- [{icon}] `{result.name}` ({result.duration_ms} ms)")

    if failed:
        first = failed[0]
        lines.extend(
            [
                "",
                "### First Failure",
                f"- step: `{first.name}`",
                f"- exit_code: `{first.exit_code}`",
                "- output:",
                "```text",
                first.output.strip(),
                "```",
            ]
        )

    return "\n".join(lines) + "\n"


def write_report(results: list[GateResult], mode: str, report_path: Path) -> None:
    """Write the quality-gate JSON report file."""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    payload = report_payload(results, mode)
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_markdown_summary(results: list[GateResult], mode: str, summary_path: Path) -> None:
    """Write markdown summary for reuse in PR/issue comments."""
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(markdown_summary(results, mode), encoding="utf-8")


def print_summary(results: list[GateResult], report_path: Path) -> None:
    """Print concise terminal summary for humans and logs."""
    print("Quality gate summary")
    print(f"Report: {report_path}")
    for result in results:
        status = "PASS" if result.exit_code == 0 else "FAIL"
        print(f"- [{status}] {result.name} ({result.duration_ms} ms)")

    failed = [item for item in results if item.exit_code != 0]
    if failed:
        first = failed[0]
        print("\nFirst failure detail")
        print(f"step: {first.name}")
        print(f"exit_code: {first.exit_code}")
        print("output:")
        print(first.output.strip())


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run unified quality gates")
    parser.add_argument("--mode", choices=["quick", "full", "ci"], default="quick")
    parser.add_argument("--repo-root", default=".", help="Repository root to execute commands in")
    parser.add_argument(
        "--report-file",
        default=".automation/quality-gate-report.json",
        help="JSON report output path, relative to repo root when not absolute",
    )
    parser.add_argument(
        "--summary-file",
        default=".automation/quality-gate-summary.md",
        help="Markdown summary output path, relative to repo root when not absolute",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue running remaining steps after a failure",
    )
    return parser.parse_args()


def main() -> None:
    """CLI entrypoint."""
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    report_path = Path(args.report_file)
    if not report_path.is_absolute():
        report_path = repo_root / report_path

    summary_path = Path(args.summary_file)
    if not summary_path.is_absolute():
        summary_path = repo_root / summary_path

    results = run_quality_gates(args.mode, repo_root, args.continue_on_error)
    write_report(results, args.mode, report_path)
    write_markdown_summary(results, args.mode, summary_path)
    print_summary(results, report_path)
    print(f"Markdown summary: {summary_path}")

    failed = any(item.exit_code != 0 for item in results)
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
