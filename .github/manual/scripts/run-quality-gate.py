"""Manual mode quality gate runner (independent from automation scripts)."""

from __future__ import annotations

import argparse
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class GateStep:
    """A single quality-gate step."""

    name: str
    command: list[str]


def _build_steps(mode: str) -> list[GateStep]:
    steps = [
        GateStep(
            name="format-check",
            command=["python", "-m", "ruff", "format", "--check", "src", "tests", ".github"],
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

    if mode == "full":
        steps.append(
            GateStep(
                name="integration-test",
                command=["python", "-m", "pytest", "tests/integration", "-v", "--timeout=60"],
            )
        )

    return steps


def _run_step(step: GateStep, repo_root: Path) -> tuple[int, str, int]:
    start = time.perf_counter()
    process = subprocess.run(  # noqa: S603
        step.command,
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
        encoding="utf-8",
        errors="replace",
    )
    duration_ms = int((time.perf_counter() - start) * 1000)
    output = (process.stdout or "") + (process.stderr or "")
    return process.returncode, output, duration_ms


def _resolve_repo_root(value: str) -> Path:
    if value.strip():
        return Path(value).resolve()
    return Path(__file__).resolve().parents[3]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run manual quality gate")
    parser.add_argument("--mode", choices=["quick", "full"], default="full")
    parser.add_argument("--repo-root", default="", help="Repository root path")
    args = parser.parse_args()

    repo_root = _resolve_repo_root(args.repo_root)
    steps = _build_steps(args.mode)

    print(f"Manual quality gate mode={args.mode} repo={repo_root}")
    for step in steps:
        exit_code, output, duration_ms = _run_step(step, repo_root)
        status = "PASS" if exit_code == 0 else "FAIL"
        print(f"- [{status}] {step.name} ({duration_ms} ms)")
        if exit_code != 0:
            print("\nFirst failure output:")
            print(output.strip())
            raise SystemExit(exit_code)

    print("All manual quality gate checks passed")


if __name__ == "__main__":
    main()
