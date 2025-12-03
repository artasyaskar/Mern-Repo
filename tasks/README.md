Each task lives in its own folder under tasks/<task-id>/ with:
- task_description.txt
- task_tests.js (Jest)
- task_diff.txt
- run-tests.sh (optional override)
- docker-compose.yaml (optional override)

Run tests with:
./run_tests.sh <task-id>
