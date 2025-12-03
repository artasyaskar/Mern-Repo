#!/bin/sh
set -eu
TASK_ID="${TASK_ID:-calc-evaluator}"
echo "[Task ${TASK_ID}] Running tests..."

# Ensure deps
npm ci --no-audit --no-fund --prefer-offline || npm i --no-audit --no-fund --prefer-offline

# Run base + task tests
npx jest tests/base "tasks/${TASK_ID}/task_tests.js"
