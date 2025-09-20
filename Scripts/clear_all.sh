#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

CLEAR_BUILD="$SCRIPT_DIR/clear_build.sh"
CLEAR_ENGINE="$SCRIPT_DIR/clear_engine.sh"

# -----------------------------
# Validate scripts exist
# -----------------------------
if [[ ! -x "$CLEAR_BUILD" ]]; then
  echo "[ERROR] clear_build.sh not found or not executable: $CLEAR_BUILD"
  exit 1
fi

if [[ ! -x "$CLEAR_ENGINE" ]]; then
  echo "[ERROR] clear_engine.sh not found or not executable: $CLEAR_ENGINE"
  exit 1
fi

# -----------------------------
# Run cleanup
# -----------------------------
echo "[INFO] Running project cleanup..."
"$CLEAR_BUILD"

echo "[INFO] Running engine cleanup..."
"$CLEAR_ENGINE"

echo "[INFO] All cleanup completed successfully."
