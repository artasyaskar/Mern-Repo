#!/bin/sh
set -eu
TASK_ID="${1:-BASE}"

if [ "$TASK_ID" = "BASE" ]; then
  echo "== Running base tests =="
  npm ci --no-audit --no-fund --prefer-offline || npm i --no-audit --no-fund --prefer-offline
  npx jest tests/base
else
  echo "== Running task tests for ${TASK_ID} =="
  npm ci --no-audit --no-fund --prefer-offline || npm i --no-audit --no-fund --prefer-offline
  TEST_FILE="tasks/${TASK_ID}/task_tests.js"
  if [ ! -f "$TEST_FILE" ]; then
    echo "Task tests not found: ${TEST_FILE}" 1>&2
    exit 1
  fi
  npx jest tests/base "$TEST_FILE"
fi
