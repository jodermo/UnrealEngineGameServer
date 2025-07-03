#!/bin/bash
set -e

ENV_FILE="$(dirname "$0")/../.env"
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | sed 's/\r$//' | xargs)
else
    echo "Missing .env file at $ENV_FILE"
    exit 1
fi

PROJECT_PATH="$(pwd)/$PROJECT_DIR"

echo "Clearing project build: $PROJECT_PATH"

rm -rf "$PROJECT_PATH/Binaries"
rm -rf "$PROJECT_PATH/Build"
rm -rf "$PROJECT_PATH/Intermediate"
rm -rf "$PROJECT_PATH/Saved"

echo "Project build folders cleared."
