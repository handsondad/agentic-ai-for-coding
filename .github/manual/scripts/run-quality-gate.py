"""Manual mode quality gate runner (independent from automation scripts)."""

from __future__ import annotations

import argparse
import os
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

    if mode == "full":
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


def _run_git(args: list[str], repo_root: Path) -> CommandResult:
    process = subprocess.run(  # noqa: S603
        args,
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
        encoding="utf-8",
        errors="replace",
    )
    output = (process.stdout or "") + (process.stderr or "")
    return CommandResult(exit_code=process.returncode, output=output)


@dataclass(slots=True)
class CommandResult:
    """Command execution result."""

    exit_code: int
    output: str


def _check_issue_policy(repo_root: Path) -> tuple[bool, str]:
    """Block manual execution when no issue context is present.

    The manual implementation flow must be issue-driven:
    1) create/publish backlog issue
    2) prepare single issue workspace
    3) implement and run quality gate
    """
    bypass = os.getenv("MANUAL_ALLOW_NO_ISSUE", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }
    if bypass:
        return True, "Issue policy bypassed by MANUAL_ALLOW_NO_ISSUE"

    branch = _run_git(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo_root)
    if branch.exit_code != 0:
        return False, f"无法读取当前分支：\n{branch.output.strip()}"

    branch_name = branch.output.strip()
    if not branch_name.startswith("ai/issue-"):
        message = (
            "阻断：当前不是 issue 实现分支，禁止直接进入修复/实现。\n"
            f"当前分支：{branch_name}\n"
            "请先按规范创建并发布 issue，再进入实现：\n"
            "1) pwsh .github/manual/scripts/start-backlog-issue.ps1 "
            '-Type task -Title "你的问题描述"\n'
            "2) pwsh .github/manual/scripts/publish-backlog-issue.ps1 <backlog-file>\n"
            "3) pwsh .github/manual/scripts/prepare-single-issue.ps1 -IssueNumber <issue-number>"
        )
        return False, message

    prompt_path = repo_root / ".manual" / "issue-prompt.md"
    if not prompt_path.exists():
        message = (
            "阻断：未检测到 issue prompt，上下文不完整。\n"
            f"缺失文件：{prompt_path}\n"
            "请先执行 prepare-single-issue 再实现。"
        )
        return False, message

    return True, f"Issue policy check passed on branch {branch_name}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run manual quality gate")
    parser.add_argument("--mode", choices=["quick", "full"], default="full")
    parser.add_argument("--repo-root", default="", help="Repository root path")
    args = parser.parse_args()

    repo_root = _resolve_repo_root(args.repo_root)

    passed, policy_message = _check_issue_policy(repo_root)
    if not passed:
        print(policy_message)
        raise SystemExit(2)
    print(policy_message)

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
