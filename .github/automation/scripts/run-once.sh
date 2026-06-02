#!/usr/bin/env sh
set -eu

WORKFLOW_PATH="${1:-WORKFLOW.md}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"
PYTHON_EXE="${PYTHON_EXE:-python3}"

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../../.." && pwd)"

if [ -z "${GITHUB_TOKEN:-}" ]; then
  echo "GITHUB_TOKEN is required" >&2
  exit 1
fi

if [ -z "${GITHUB_REPOSITORY:-}" ]; then
  echo "GITHUB_REPOSITORY is required, e.g. owner/repo" >&2
  exit 1
fi

cd "$REPO_ROOT"
exec "$PYTHON_EXE" ".github/automation/cli.py" --once --workflow "$WORKFLOW_PATH" --log-level "$LOG_LEVEL"
