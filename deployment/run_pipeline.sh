#!/bin/bash

cd /home/csaetang/retail-data-integration-platform || exit 1
source venv/bin/activate

echo "========================================"
echo "Pipeline started: $(date)"

python -m pipeline.main

EXIT_CODE=$?

echo "Pipeline finished: $(date)"
echo "Exit code: $EXIT_CODE"

exit $EXIT_CODE