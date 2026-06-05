"""Manual mode helper to create pull requests with a body file.

This script intentionally enforces --body-file usage for gh CLI to avoid
multiline body truncation in some shells.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
from pathlib import Path


def _resolve_repo_root(value: str) -> Path:
    if value.strip():
        return Path(value).resolve()
    return Path(__file__).resolve().parents[3]


def _run_command(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        args,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
        encoding="utf-8",
        errors="replace",
    )


def _current_branch(repo_root: Path) -> str:
    result = _run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo_root)
    if result.returncode != 0:
        output = (result.stdout or "") + (result.stderr or "")
        raise SystemExit(f"无法获取当前分支: {output.strip()}")
    return (result.stdout or "").strip()


def _render_default_body(repo_root: Path, issue_number: str) -> Path:
    template_path = repo_root / ".github" / "pull_request_template.md"
    if not template_path.exists():
        raise SystemExit(f"未找到 PR 模板文件: {template_path}")

    body = template_path.read_text(encoding="utf-8")
    if issue_number:
        body += f"\n\nCloses #{issue_number}\n"

    temp = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".md",
        prefix="pr-body-",
        encoding="utf-8",
        delete=False,
    )
    with temp:
        temp.write(body)
    return Path(temp.name)


def _validate_body(repo_root: Path, body_file: Path) -> None:
    checker = (
        repo_root / ".github" / "automation" / "scripts" / "check-pr-template.py"
    )
    if not checker.exists():
        return

    result = _run_command(
        ["python", str(checker), "--body-file", str(body_file)],
        repo_root,
    )
    if result.returncode != 0:
        output = (result.stdout or "") + (result.stderr or "")
        raise SystemExit(
            "PR 描述模板校验失败，请先完善内容后再创建 PR:\n"
            f"{output.strip()}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create PR with gh CLI using --body-file only"
    )
    parser.add_argument("--title", required=True, help="PR title")
    parser.add_argument("--body-file", default="", help="PR body markdown file path")
    parser.add_argument("--base", default=os.getenv("GITHUB_BASE_BRANCH", "main"))
    parser.add_argument("--head", default="", help="Head branch (default current)")
    parser.add_argument("--repo-root", default="", help="Repository root path")
    parser.add_argument("--draft", action="store_true", help="Create as draft PR")
    parser.add_argument(
        "--issue-number",
        default="",
        help="Optional issue number appended as Closes #<n> when auto-generating body",
    )
    args = parser.parse_args()

    repo_root = _resolve_repo_root(args.repo_root)
    head = args.head.strip() or _current_branch(repo_root)

    generated_body = False
    body_file = Path(args.body_file).resolve() if args.body_file.strip() else None
    if body_file is None:
        body_file = _render_default_body(repo_root, args.issue_number.strip())
        generated_body = True

    if not body_file.exists():
        raise SystemExit(f"PR body file 不存在: {body_file}")

    _validate_body(repo_root, body_file)

    command = [
        "gh",
        "pr",
        "create",
        "--base",
        args.base.strip() or "main",
        "--head",
        head,
        "--title",
        args.title,
        "--body-file",
        str(body_file),
    ]
    if args.draft:
        command.append("--draft")

    result = _run_command(command, repo_root)
    output = (result.stdout or "") + (result.stderr or "")

    if generated_body:
        try:
            body_file.unlink(missing_ok=True)
        except OSError:
            pass

    if result.returncode != 0:
        raise SystemExit(f"gh pr create 失败:\n{output.strip()}")

    print(output.strip())


if __name__ == "__main__":
    main()
