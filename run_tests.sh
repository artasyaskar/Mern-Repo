#!/bin/sh
set -eu
TASK_ID="${1:-BASE}"

if [ "$TASK_ID" = "BASE" ]; then
  echo "== Running base tests (Jest) =="
  npm ci --no-audit --no-fund --prefer-offline || npm i --no-audit --no-fund --prefer-offline
  npx jest tests/base
else
  echo "== Running task tests for ${TASK_ID} (Jest base + pytest task) =="
  npm ci --no-audit --no-fund --prefer-offline || npm i --no-audit --no-fund --prefer-offline

  # First run base tests to ensure starter remains intact
  npx jest tests/base

  # If the task provides a diff, apply it so a null agent can pass
  DIFF_FILE="tasks/${TASK_ID}/task_diff.txt"
  if [ -f "$DIFF_FILE" ]; then
    echo "Applying task diff: $DIFF_FILE"
    # Ensure we are in a git repo with a baseline commit
    if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
      git init >/dev/null 2>&1 || true
    fi
    git config user.email "runner@example.com" >/dev/null 2>&1 || true
    git config user.name "Runner" >/dev/null 2>&1 || true
    git config core.autocrlf false >/dev/null 2>&1 || true
    git config core.safecrlf false >/dev/null 2>&1 || true
    # Create baseline commit if none exists
    if ! git rev-parse HEAD >/dev/null 2>&1; then
      git add -A >/dev/null 2>&1 || true
      git commit -m "baseline" >/dev/null 2>&1 || true
    fi
    # Try to apply the diff
    if ! git apply --index --reject --whitespace=fix "$DIFF_FILE"; then
      echo "git apply failed; attempting without --index..." 1>&2
      if ! git apply --reject --whitespace=fix "$DIFF_FILE"; then
        echo "Failed to apply task diff: $DIFF_FILE" 1>&2
        exit 2
      fi
    fi
  fi

  PY_TEST_FILE="tasks/${TASK_ID}/task_tests.py"
  if [ ! -f "$PY_TEST_FILE" ]; then
    echo "Task tests not found: ${PY_TEST_FILE}" 1>&2
    exit 1
  fi

  # Start server in background for HTTP-based pytest
  node server/index.js &
  SERVER_PID=$!
  cleanup() {
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  }
  trap cleanup EXIT INT TERM

  # Wait for health endpoint
  i=0
  until curl -sf "http://localhost:3000/health" >/dev/null 2>&1; do
    i=$((i+1))
    [ $i -gt 50 ] && echo "Server failed to start" 1>&2 && exit 1
    sleep 0.2
  done

  # Ensure pytest available; if missing, attempt user-level install
  if ! python3 - <<'PY'
import sys
try:
    import pytest  # type: ignore
    sys.exit(0)
except Exception:
    sys.exit(1)
PY
  then
    echo "Installing pytest locally for current user..."
    (python3 -m pip install --user --quiet pytest requests || pip3 install --user --quiet pytest requests) || true
  fi

  # Run pytest for the task (use python3 -m to avoid missing entrypoint issues)
  if python3 -c "import pytest" 2>/dev/null; then
    python3 -m pytest -q "$PY_TEST_FILE"
  else
    echo "pytest is not available. To run tasks deterministically, please use: docker compose run --rm app ./run_tests.sh ${TASK_ID}" 1>&2
    exit 127
  fi
fi
