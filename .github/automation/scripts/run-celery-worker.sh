#!/usr/bin/env sh
set -eu

QUEUE="${QUEUE:-automation_issues}"
BROKER="${BROKER:-redis://localhost:6379/0}"
BACKEND="${BACKEND:-redis://localhost:6379/1}"
CONCURRENCY="${CONCURRENCY:-2}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"
PYTHON_EXE="${PYTHON_EXE:-python3}"

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../../.." && pwd)"

cd "$REPO_ROOT"

export PYTHONPATH="$REPO_ROOT/.github/automation"
export AUTOMATION_CELERY_BROKER_URL="$BROKER"
export AUTOMATION_CELERY_RESULT_BACKEND="$BACKEND"
export AUTOMATION_CELERY_QUEUE="$QUEUE"

exec "$PYTHON_EXE" -m celery -A celery_tasks:celery_app worker --loglevel "$LOG_LEVEL" --concurrency "$CONCURRENCY" --queues "$QUEUE"
