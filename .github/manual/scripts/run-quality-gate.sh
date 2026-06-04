#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PYTHON_EXE="${PYTHON_EXE:-python3}"

exec "$PYTHON_EXE" "$SCRIPT_DIR/run-quality-gate.py" "$@"
