#!/bin/bash
set -euo pipefail

# -----------------------------
# Load .env
# -----------------------------
ENV_FILE="$(dirname "$0")/../.env"
if [[ -f "$ENV_FILE" ]]; then
    # shellcheck disable=SC2046
    export $(grep -v '^#' "$ENV_FILE" | sed 's/\r$//' | xargs)
else
    echo "[ERROR] Missing .env file at $ENV_FILE"
    exit 1
fi

# -----------------------------
# Validate and resolve paths
# -----------------------------
if [[ -z "${PROJECT_DIR:-}" ]]; then
    echo "[ERROR] PROJECT_DIR not set in .env"
    exit 1
fi

PROJECT_PATH="$(pwd)/$PROJECT_DIR"

if [[ ! -d "$PROJECT_PATH" ]]; then
    echo "[ERROR] Project directory not found: $PROJECT_PATH"
    exit 1
fi

# -----------------------------
# Cleanup
# -----------------------------
echo "[INFO] Clearing project build artifacts in: $PROJECT_PATH"

for DIR in Binaries Build Intermediate Saved DerivedDataCache; do
    TARGET="$PROJECT_PATH/$DIR"
    if [[ -d "$TARGET" ]]; then
        echo "  - Removing $TARGET"
        rm -rf "$TARGET"
    else
        echo "  - Skipping $DIR (not found)"
    fi
done

echo "[INFO] Project build folders cleared successfully."
