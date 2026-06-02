"""Validate PR body completeness against required template sections."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REQUIRED_SECTIONS = ["背景", "变更摘要", "变更详情", "测试计划", "审查重点"]


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Check PR body completeness")
    parser.add_argument("--body-file", default="", help="PR body markdown file path")
    parser.add_argument("--event-path", default="", help="GitHub event JSON path")
    parser.add_argument("--body-text", default="", help="Inline PR body text")
    return parser.parse_args()


def load_pr_body(args: argparse.Namespace) -> str:
    """Load PR body from one of supported sources."""
    if args.body_text.strip():
        return args.body_text.strip()

    if args.body_file.strip():
        return Path(args.body_file).read_text(encoding="utf-8").strip()

    if args.event_path.strip():
        payload = json.loads(Path(args.event_path).read_text(encoding="utf-8"))
        pull_request = payload.get("pull_request", {})
        return str(pull_request.get("body", "")).strip()

    raise ValueError("Provide one of --body-text, --body-file, or --event-path")


def find_missing_sections(body: str) -> list[str]:
    """Find required markdown sections missing from body."""
    missing: list[str] = []
    for section in REQUIRED_SECTIONS:
        heading = f"## {section}"
        if heading not in body:
            missing.append(section)
    return missing


def has_placeholder_comments(body: str) -> bool:
    """Return true when template placeholder comments remain in PR body."""
    return "<!--" in body or "-->" in body


def extract_section(body: str, section: str) -> str:
    """Extract section body text by heading title."""
    pattern = rf"##\s+{re.escape(section)}\s*\n(?P<content>[\s\S]*?)(?:\n##\s+|\Z)"
    match = re.search(pattern, body)
    if not match:
        return ""
    return match.group("content").strip()


def validate_test_plan(section_text: str) -> list[str]:
    """Validate test-plan section includes both executed and unexecuted disclosures."""
    issues: list[str] = []
    lowered = section_text.lower()

    has_executed = "[x]" in lowered or "已执行" in section_text
    has_not_executed = "未执行" in section_text or "[ ]" in lowered

    if not has_executed:
        issues.append("测试计划缺少已执行项说明")
    if not has_not_executed:
        issues.append("测试计划缺少未执行项说明")
    return issues


def validate_pr_body(body: str) -> tuple[bool, list[str]]:
    """Run full PR body validation and return (ok, messages)."""
    messages: list[str] = []

    if not body.strip():
        return False, ["PR 描述为空"]

    missing = find_missing_sections(body)
    if missing:
        messages.append(f"缺少必填章节: {', '.join(missing)}")

    if has_placeholder_comments(body):
        messages.append("仍包含模板注释占位符（<!-- -->）")

    test_plan_text = extract_section(body, "测试计划")
    if test_plan_text:
        messages.extend(validate_test_plan(test_plan_text))

    return len(messages) == 0, messages


def main() -> None:
    """CLI entrypoint."""
    args = parse_args()
    body = load_pr_body(args)
    ok, messages = validate_pr_body(body)

    if ok:
        print("PR 模板检查通过")
        raise SystemExit(0)

    print("PR 模板检查失败:")
    for item in messages:
        print(f"- {item}")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
