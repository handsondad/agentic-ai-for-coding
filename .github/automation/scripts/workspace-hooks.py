"""Cross-platform workspace hook helpers for automation worktrees."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> None:
    """Run a workspace hook command."""
    parser = argparse.ArgumentParser(description="Run workspace automation hooks")
    subparsers = parser.add_subparsers(dest="hook_name", required=True)

    subparsers.add_parser("after-create", help="Install workspace dependencies")

    before_run = subparsers.add_parser("before-run", help="Sync the latest base branch")
    before_run.add_argument("--base-branch", default="main", help="Base branch to fetch")

    subparsers.add_parser("after-run", help="Clean generated Python cache files")

    args = parser.parse_args()
    cwd = Path.cwd()

    if args.hook_name == "after-create":
        run_after_create(cwd)
        return

    if args.hook_name == "before-run":
        run_before_run(cwd, base_branch=args.base_branch)
        return

    run_after_run(cwd)


def run_after_create(cwd: Path) -> None:
    """Install project dependencies for a newly created worktree."""
    requirements_file = cwd / "requirements.txt"
    pyproject_file = cwd / "pyproject.toml"

    if requirements_file.exists():
        _run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd)

    if pyproject_file.exists():
        _run_command([sys.executable, "-m", "pip", "install", "-e", ".[dev]"], cwd)

    print("工作空间初始化完成")


def run_before_run(cwd: Path, base_branch: str = "main") -> None:
    """Fetch the latest upstream base branch before the agent starts."""
    _run_command(["git", "fetch", "origin", base_branch], cwd)
    print("代码同步完成")


def run_after_run(cwd: Path) -> None:
    """Remove Python cache artifacts after the agent finishes."""
    for pyc_file in cwd.rglob("*.pyc"):
        pyc_file.unlink(missing_ok=True)

    for cache_dir in cwd.rglob("__pycache__"):
        shutil.rmtree(cache_dir, ignore_errors=True)

    print("清理完成")


def _run_command(command: list[str], cwd: Path) -> None:
    subprocess.run(  # noqa: S603
        command,
        cwd=str(cwd),
        check=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


if __name__ == "__main__":
    main()
