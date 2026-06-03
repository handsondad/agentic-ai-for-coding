#!/usr/bin/env sh
set -eu

WORKFLOW_PATH="${1:-WORKFLOW.md}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"
PYTHON_EXE="${PYTHON_EXE:-python3}"
ONCE_FLAG="${ONCE:-false}"
BROKER="${BROKER:-}"
BACKEND="${BACKEND:-}"
QUEUE="${QUEUE:-}"

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

if [ -n "$BROKER" ]; then
  export AUTOMATION_CELERY_BROKER_URL="$BROKER"
fi
if [ -n "$BACKEND" ]; then
  export AUTOMATION_CELERY_RESULT_BACKEND="$BACKEND"
fi
if [ -n "$QUEUE" ]; then
  export AUTOMATION_CELERY_QUEUE="$QUEUE"
fi

if [ "$ONCE_FLAG" = "true" ] || [ "$ONCE_FLAG" = "1" ]; then
  exec "$PYTHON_EXE" ".github/automation/cli.py" --once --workflow "$WORKFLOW_PATH" --log-level "$LOG_LEVEL"
fi

exec "$PYTHON_EXE" ".github/automation/cli.py" --workflow "$WORKFLOW_PATH" --log-level "$LOG_LEVEL"
