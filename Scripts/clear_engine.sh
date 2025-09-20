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
# Validate engine path
# -----------------------------
if [[ -z "${UNREAL_ENGINE_PATH:-}" ]]; then
    echo "[ERROR] UNREAL_ENGINE_PATH not set in .env"
    exit 1
fi

ENGINE_PATH="$(pwd)/$UNREAL_ENGINE_PATH"

if [[ ! -d "$ENGINE_PATH/Engine" ]]; then
    echo "[ERROR] Engine directory not found: $ENGINE_PATH/Engine"
    exit 1
fi

# -----------------------------
# Cleanup
# -----------------------------
echo "[INFO] Clearing engine build artifacts in: $ENGINE_PATH"

for DIR in Binaries Intermediate Saved DerivedDataCache; do
    TARGET="$ENGINE_PATH/Engine/$DIR"
    if [[ -d "$TARGET" ]]; then
        echo "  - Removing $TARGET"
        rm -rf "$TARGET"
    else
        echo "  - Skipping $DIR (not found)"
    fi
done

echo "[INFO] Engine build folders cleared successfully."
