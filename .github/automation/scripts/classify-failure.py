"""CLI helper for classifying failures from logs or direct text."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
AUTOMATION_DIR = SCRIPT_DIR.parent

if str(AUTOMATION_DIR) not in sys.path:
    sys.path.insert(0, str(AUTOMATION_DIR))

from failure_reporting import classify_failure, render_failure_markdown  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Classify automation failure text")
    parser.add_argument("--input", default="", help="Path to log file")
    parser.add_argument("--text", default="", help="Direct error text")
    parser.add_argument("--step", default="pipeline", help="Failure step label")
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="json",
        help="Output format",
    )
    return parser.parse_args()


def main() -> None:
    """CLI entrypoint."""
    args = parse_args()
    raw_text = args.text.strip()

    if not raw_text and args.input:
        raw_text = Path(args.input).read_text(encoding="utf-8")

    if not raw_text:
        raise SystemExit("Provide --text or --input")

    if args.format == "markdown":
        print(render_failure_markdown(step=args.step, raw_error=raw_text))
        return

    classification = classify_failure(raw_text)
    print(
        json.dumps(
            {
                "category": classification.category,
                "reason": classification.reason,
                "suggestion": classification.suggestion,
                "retryable": classification.retryable,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
