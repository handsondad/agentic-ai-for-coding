"""Publish a local backlog markdown file to GitHub Issue and backfill metadata."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

_FRONT_MATTER_PATTERN = re.compile(r"^\ufeff?---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)
_ISSUE_URL_PATTERN = re.compile(r"/issues/(\d+)$")
_DEFAULT_LABEL_COLOR = "0366d6"
_LABEL_COLOR_MAP = {
    "ai-ready": "1d76db",
    "task": "5319e7",
    "feature": "0e8a16",
    "bug": "d73a4a",
}


class PublishError(RuntimeError):
    """Raised when publish flow cannot continue."""


@dataclass(slots=True)
class BacklogIssue:
    """Backlog file model containing metadata and markdown body."""

    path: Path
    meta: dict[str, Any]
    body: str


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    """Run a command and capture UTF-8 output reliably across Windows locales."""
    return subprocess.run(  # noqa: S603
        command,
        text=True,
        capture_output=True,
        check=False,
        encoding="utf-8",
        errors="replace",
    )


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Publish backlog markdown to GitHub Issue"
    )
    parser.add_argument("file", help="Path to backlog markdown file")
    parser.add_argument("--repo", default="", help="Target repo in owner/name format")
    parser.add_argument(
        "--allow-draft",
        action="store_true",
        help="Allow publishing files with draft status",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print action, but do not call GitHub API",
    )

    args = parser.parse_args()

    issue = load_backlog_issue(Path(args.file).resolve())
    validate_backlog_issue(issue, allow_draft=args.allow_draft)

    repo = args.repo.strip() or detect_git_repo(issue.path)
    title = str(issue.meta.get("title", "")).strip()
    labels = normalize_labels(issue.meta.get("labels"))

    if args.dry_run:
        print("[DRY-RUN] file=", issue.path)
        print("[DRY-RUN] repo=", repo)
        print("[DRY-RUN] title=", title)
        print("[DRY-RUN] labels=", ",".join(labels))
        return

    issue_url, created = create_github_issue(
        repo=repo,
        title=title,
        labels=labels,
        body=issue.body,
    )
    issue_number = extract_issue_number(issue_url)

    issue.meta["status"] = "published"
    issue.meta["github_issue_number"] = str(issue_number)
    issue.meta["github_issue_url"] = issue_url

    write_backlog_issue(issue)

    if created:
        print(f"Created issue: {issue_url}")
    else:
        print(f"Reused existing issue: {issue_url}")
    print(f"Updated backlog: {issue.path}")


def load_backlog_issue(path: Path) -> BacklogIssue:
    """Parse markdown file with YAML front matter."""
    if not path.exists():
        raise PublishError(f"Backlog file not found: {path}")

    text = path.read_text(encoding="utf-8")
    match = _FRONT_MATTER_PATTERN.match(text)
    if match is None:
        raise PublishError("Backlog file must include YAML front matter")

    front_matter_raw, body = match.groups()
    try:
        meta = yaml.safe_load(front_matter_raw)
    except yaml.YAMLError as exc:
        raise PublishError(f"Invalid YAML front matter: {exc}") from exc

    if not isinstance(meta, dict):
        raise PublishError("Front matter root must be an object")

    return BacklogIssue(path=path, meta=meta, body=body.strip())


def validate_backlog_issue(issue: BacklogIssue, allow_draft: bool = False) -> None:
    """Validate required metadata before publish."""
    title = str(issue.meta.get("title", "")).strip()
    if not title:
        raise PublishError("Missing front matter: title")

    issue_type = str(issue.meta.get("type", "")).strip()
    if issue_type not in {"feature", "bug", "task"}:
        raise PublishError("Front matter type must be one of: feature, bug, task")

    status = str(issue.meta.get("status", "")).strip()
    if status == "published":
        raise PublishError("Backlog issue is already published")
    if status != "ready" and not allow_draft:
        raise PublishError(
            "Backlog status must be ready (use --allow-draft to override)"
        )

    labels = issue.meta.get("labels")
    if not isinstance(labels, list) or not labels:
        raise PublishError("Front matter labels must be a non-empty list")

    if not issue.body.strip():
        raise PublishError("Issue body cannot be empty")


def detect_git_repo(backlog_file: Path) -> str:
    """Detect GitHub repository from current git remote."""
    repo_root = backlog_file.parent
    while repo_root != repo_root.parent and not (repo_root / ".git").exists():
        repo_root = repo_root.parent

    if not (repo_root / ".git").exists():
        raise PublishError("Cannot locate git repository root")

    git_path = shutil.which("git")
    if git_path is None:
        raise PublishError("git executable not found in PATH")

    result = run_command(
        [git_path, "-C", str(repo_root), "remote", "get-url", "origin"]
    )
    if result.returncode != 0:
        raise PublishError(
            f"Failed to detect git remote: {result.stdout}{result.stderr}"
        )

    remote = result.stdout.strip()
    match = re.search(
        r"github.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$", remote
    )
    if match is None:
        raise PublishError(f"Unsupported remote URL: {remote}")

    return f"{match.group('owner')}/{match.group('repo')}"


def normalize_labels(raw: Any) -> list[str]:
    """Normalize labels from front matter."""
    if not isinstance(raw, list):
        return []
    labels = [str(item).strip() for item in raw if str(item).strip()]
    return labels


def create_github_issue(
    repo: str, title: str, labels: list[str], body: str
) -> tuple[str, bool]:
    """Create GitHub issue using gh CLI and return (url, created_new)."""
    gh_path = shutil.which("gh")
    if gh_path is None:
        raise PublishError("gh CLI not found in PATH")

    existing_issue_url = find_existing_issue_by_title(
        gh_path=gh_path,
        repo=repo,
        title=title,
    )
    if existing_issue_url is not None:
        return existing_issue_url, False

    ensure_labels_exist(gh_path=gh_path, repo=repo, labels=labels)

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".md",
        delete=False,
    ) as file:
        file.write(body)
        body_file = Path(file.name)

    try:
        command = [
            gh_path,
            "issue",
            "create",
            "--repo",
            repo,
            "--title",
            title,
            "--body-file",
            str(body_file),
        ]

        for label in labels:
            command.extend(["--label", label])

        result = run_command(command)
    finally:
        body_file.unlink(missing_ok=True)

    if result.returncode != 0:
        raise PublishError(f"gh issue create failed: {result.stdout}{result.stderr}")

    issue_url = result.stdout.strip()
    if not issue_url:
        raise PublishError("GitHub issue URL is empty")
    return issue_url, True


def find_existing_issue_by_title(gh_path: str, repo: str, title: str) -> str | None:
    """Find an open issue in target repo with the same title and return URL."""
    result = run_command(
        [
            gh_path,
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            "open",
            "--json",
            "number,title,url",
            "--limit",
            "100",
        ]
    )
    if result.returncode != 0:
        raise PublishError(f"gh issue list failed: {result.stdout}{result.stderr}")

    try:
        payload = json.loads(result.stdout or "[]")
    except json.JSONDecodeError as exc:
        raise PublishError(f"Failed to parse issue list output: {exc}") from exc

    target = normalize_title(title)
    matches: list[dict[str, Any]] = []
    if isinstance(payload, list):
        for item in payload:
            if not isinstance(item, dict):
                continue
            item_title = item.get("title")
            item_url = item.get("url")
            item_number = item.get("number")
            if not isinstance(item_title, str) or not isinstance(item_url, str):
                continue
            if normalize_title(item_title) != target:
                continue
            if not isinstance(item_number, int):
                continue
            matches.append(item)

    if not matches:
        return None

    matches.sort(key=lambda item: int(item["number"]), reverse=True)
    selected = matches[0]
    return str(selected["url"]).strip() or None


def normalize_title(title: str) -> str:
    """Normalize title for robust duplicate comparison."""
    return " ".join(title.split()).casefold()


def ensure_labels_exist(gh_path: str, repo: str, labels: list[str]) -> None:
    """Ensure all required labels exist in target repo."""
    if not labels:
        return

    list_result = run_command(
        [gh_path, "label", "list", "--repo", repo, "--json", "name", "--limit", "200"]
    )
    if list_result.returncode != 0:
        raise PublishError(
            f"gh label list failed: {list_result.stdout}{list_result.stderr}"
        )

    try:
        payload = yaml.safe_load(list_result.stdout)
    except yaml.YAMLError as exc:
        raise PublishError(f"Failed to parse label list output: {exc}") from exc

    existing: set[str] = set()
    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict) and isinstance(item.get("name"), str):
                existing.add(item["name"].strip().lower())

    for label in labels:
        normalized = label.strip().lower()
        if normalized in existing:
            continue

        color = _LABEL_COLOR_MAP.get(normalized, _DEFAULT_LABEL_COLOR)
        create_result = run_command(
            [
                gh_path,
                "label",
                "create",
                label,
                "--repo",
                repo,
                "--color",
                color,
            ]
        )
        if create_result.returncode != 0:
            raise PublishError(
                f"gh label create failed for '{label}': "
                f"{create_result.stdout}{create_result.stderr}"
            )

        existing.add(normalized)


def extract_issue_number(issue_url: str) -> int:
    """Extract issue number from canonical issue URL."""
    matched = _ISSUE_URL_PATTERN.search(issue_url.strip())
    if matched is None:
        raise PublishError(f"Cannot parse issue number from URL: {issue_url}")
    return int(matched.group(1))


def write_backlog_issue(issue: BacklogIssue) -> None:
    """Write metadata and body back to markdown file."""
    front = yaml.safe_dump(issue.meta, sort_keys=False, allow_unicode=True).strip()
    content = f"---\n{front}\n---\n\n{issue.body.rstrip()}\n"
    issue.path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
