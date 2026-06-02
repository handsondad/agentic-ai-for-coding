#!/usr/bin/env sh
set -eu

if [ "$#" -lt 1 ]; then
  echo "usage: publish-backlog-issue.sh <file> [--repo owner/repo] [--allow-draft] [--dry-run]" >&2
  exit 1
fi

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PYTHON_EXE="${PYTHON_EXE:-python3}"

exec "$PYTHON_EXE" "$SCRIPT_DIR/publish-backlog-issue.py" "$@"
