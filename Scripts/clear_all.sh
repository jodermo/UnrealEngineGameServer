#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ ! -f "$SCRIPT_DIR/clear_build.sh" ]]; then
  echo "Missing clear_build.sh"
  exit 1
fi

if [[ ! -f "$SCRIPT_DIR/clear_engine.sh" ]]; then
  echo "Missing clear_engine.sh"
  exit 1
fi

echo "Running clear_build.sh..."
"$SCRIPT_DIR/clear_build.sh"

echo "Running clear_engine.sh..."
"$SCRIPT_DIR/clear_engine.sh"

echo "All cleanup completed."
