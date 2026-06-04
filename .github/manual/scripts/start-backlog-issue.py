"""Start backlog issue workflow: sync base branch, create branch, and create draft file."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

_FRONT_MATTER_PATTERN = re.compile(r"^\ufeff?---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)
_BACKFILL_PREFIX_PATTERN = re.compile(r"^backfill-\d{8}(?:-\d{8})?-")


class StartBacklogError(RuntimeError):
    """Raised when starting a backlog issue workflow fails."""


@dataclass(slots=True)
class CommandResult:
    """Shell command result wrapper."""

    exit_code: int
    output: str


@dataclass(slots=True)
class StartOptions:
    """Input options for backlog issue startup."""

    issue_type: str
    title: str
    date_token: str
    folder_date_token: str
    slug: str
    base_branch: str
    branch_prefix: str
    output_root: Path
    template_path: Path
    dry_run: bool
    allow_dirty: bool


@dataclass(slots=True)
class StartResult:
    """Output details for started backlog issue workflow."""

    branch_name: str
    backlog_file: Path


def run_command(args: list[str], cwd: Path) -> CommandResult:
    """Run shell command with UTF-8 output handling."""
    process = subprocess.run(  # noqa: S603
        args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
        encoding="utf-8",
        errors="replace",
    )
    output = (process.stdout or "") + (process.stderr or "")
    return CommandResult(exit_code=process.returncode, output=output)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Sync base branch, create dedicated branch, and create backlog issue draft"
    )
    parser.add_argument("--type", required=True, choices=["feature", "bug", "task"])
    parser.add_argument("--title", required=True)
    parser.add_argument("--date", default="", help="YYYYMMDD, default is today")
    parser.add_argument(
        "--folder-date",
        default="",
        help="YYYYMMDD folder token for backlog path, defaults to --date",
    )
    parser.add_argument("--slug", default="", help="Custom file slug, default from title")
    parser.add_argument("--base-branch", default="main")
    parser.add_argument("--branch-prefix", default="backlog")
    parser.add_argument("--output-root", default=".github/issues-backlog")
    parser.add_argument("--template", default=".github/issues-backlog/TEMPLATE.md")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Allow branch creation even when working tree has uncommitted changes",
    )
    return parser.parse_args()


def detect_repo_root(start: Path) -> Path:
    """Detect repository root by searching .git directory upward."""
    current = start.resolve()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    raise StartBacklogError("Cannot locate git repository root")


def ensure_clean_worktree(repo_root: Path) -> None:
    """Ensure working tree is clean before switching branches."""
    result = run_command(["git", "status", "--porcelain"], repo_root)
    if result.exit_code != 0:
        raise StartBacklogError(f"git status failed: {result.output}")
    if result.output.strip():
        details = result.output.strip()
        raise StartBacklogError(
            "Working tree has uncommitted changes; commit/stash first, "
            "or re-run with --allow-dirty.\n"
            f"Changed files:\n{details}"
        )


def slugify(text: str, max_length: int = 48) -> str:
    """Generate branch/file-safe slug."""
    normalized = "".join(ch.lower() if ch.isalnum() else "-" for ch in text)
    while "--" in normalized:
        normalized = normalized.replace("--", "-")
    normalized = normalized.strip("-") or "issue"
    return normalized[:max_length].strip("-") or "issue"


def normalize_slug(raw: str, max_length: int = 64) -> str:
    """Normalize slug and remove legacy backfill date prefix when present."""
    cleaned = raw.strip().lower()
    if cleaned.startswith("backfill-"):
        cleaned = _BACKFILL_PREFIX_PATTERN.sub("", cleaned)
    return slugify(cleaned or "issue", max_length=max_length)


def normalize_date_token(raw: str) -> str:
    """Validate or generate YYYYMMDD token."""
    value = raw.strip()
    if not value:
        return dt.datetime.now().strftime("%Y%m%d")
    if not re.fullmatch(r"\d{8}", value):
        raise StartBacklogError("--date must be YYYYMMDD")
    return value


def load_template(path: Path) -> tuple[dict[str, Any], str]:
    """Load front matter and body from template file."""
    if not path.exists():
        return ({}, "## 背景与动机\n\n## 任务范围\n\n## 完成标准\n")

    text = path.read_text(encoding="utf-8")
    match = _FRONT_MATTER_PATTERN.match(text)
    if match is None:
        raise StartBacklogError("Template must include YAML front matter")

    raw_meta, body = match.groups()
    try:
        meta = yaml.safe_load(raw_meta) or {}
    except yaml.YAMLError as exc:
        raise StartBacklogError(f"Invalid template YAML: {exc}") from exc

    if not isinstance(meta, dict):
        raise StartBacklogError("Template front matter root must be object")

    return meta, body.strip()


def build_backlog_content(options: StartOptions) -> str:
    """Render backlog markdown content from template and options."""
    meta, body = load_template(options.template_path)

    meta["title"] = options.title
    meta["type"] = options.issue_type
    meta["status"] = "draft"
    labels = meta.get("labels")
    if not isinstance(labels, list) or not labels:
        meta["labels"] = [options.issue_type]
    meta.setdefault("priority", "P2")
    meta.setdefault("assignee", "")
    meta.setdefault("milestone", "")
    meta.setdefault("acceptance_criteria", [""])
    meta.setdefault("ai_context", "")
    meta.setdefault("related_docs", ["WORKFLOW.md", "README.md"])
    meta["github_issue_number"] = ""
    meta["github_issue_url"] = ""

    meta_text = yaml.safe_dump(
        meta,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    ).strip()
    return f"---\n{meta_text}\n---\n\n{body}\n"


def sync_base_and_create_branch(repo_root: Path, options: StartOptions) -> str:
    """Sync base branch and create dedicated issue branch."""
    branch_name = (
        f"{options.branch_prefix}/{options.issue_type}-{options.date_token}-{options.slug}"
    )

    commands = [
        ["git", "fetch", "origin", options.base_branch],
        ["git", "checkout", options.base_branch],
        ["git", "pull", "--ff-only", "origin", options.base_branch],
        ["git", "checkout", "-b", branch_name],
    ]

    for command in commands:
        result = run_command(command, repo_root)
        if result.exit_code != 0:
            joined = " ".join(command)
            raise StartBacklogError(f"Command failed: {joined}\n{result.output}")

    return branch_name


def start_backlog_issue(repo_root: Path, options: StartOptions) -> StartResult:
    """Execute backlog issue startup workflow."""
    if not options.dry_run and not options.allow_dirty:
        ensure_clean_worktree(repo_root)

    relative_dir = Path(options.output_root) / options.issue_type / options.folder_date_token
    backlog_dir = (repo_root / relative_dir).resolve()
    backlog_dir.mkdir(parents=True, exist_ok=True)

    backlog_file = backlog_dir / f"{options.slug}.md"
    if backlog_file.exists():
        raise StartBacklogError(f"Backlog file already exists: {backlog_file}")

    content = build_backlog_content(options)

    if options.dry_run:
        branch_name = (
            f"{options.branch_prefix}/{options.issue_type}-{options.date_token}-{options.slug}"
        )
        return StartResult(branch_name=branch_name, backlog_file=backlog_file)

    branch_name = sync_base_and_create_branch(repo_root, options)
    backlog_file.write_text(content, encoding="utf-8")

    return StartResult(branch_name=branch_name, backlog_file=backlog_file)


def main() -> None:
    """CLI entrypoint."""
    args = parse_args()
    repo_root = detect_repo_root(Path.cwd())

    title = args.title.strip()
    if not title:
        raise SystemExit("--title cannot be empty")

    date_token = normalize_date_token(args.date)
    folder_date_token = normalize_date_token(args.folder_date) if args.folder_date else date_token
    slug = normalize_slug(args.slug.strip() or title, max_length=64)

    options = StartOptions(
        issue_type=args.type,
        title=title,
        date_token=date_token,
        folder_date_token=folder_date_token,
        slug=slug,
        base_branch=args.base_branch.strip() or "main",
        branch_prefix=args.branch_prefix.strip() or "backlog",
        output_root=Path(args.output_root),
        template_path=Path(args.template),
        dry_run=args.dry_run,
        allow_dirty=args.allow_dirty,
    )

    try:
        result = start_backlog_issue(repo_root, options)
    except StartBacklogError as exc:
        raise SystemExit(str(exc)) from exc

    if options.dry_run:
        print("[DRY-RUN] repo:", repo_root)
        print("[DRY-RUN] branch:", result.branch_name)
        print("[DRY-RUN] file:", result.backlog_file)
        return

    print("Backlog issue branch created")
    print("Branch:", result.branch_name)
    print("Backlog file:", result.backlog_file)
    print("Next:")
    print("1) Edit backlog draft content")
    print("2) Set status to ready")
    print("3) Run publish-backlog-issue script")


if __name__ == "__main__":
    main()
