#!/bin/bash
# run.sh
echo "Starting Station Gateway on port 8080..."
uvicorn main:app --reload --port 8080 --host 0.0.0.0
