#!/bin/bash
set -e

ENV_FILE="$(dirname "$0")/../.env"
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | sed 's/\r$//' | xargs)
else
    echo "Missing .env file at $ENV_FILE"
    exit 1
fi

ENGINE_PATH="$(pwd)/$UNREAL_ENGINE_PATH"

echo "Clearing engine build: $ENGINE_PATH"

rm -rf "$ENGINE_PATH/Engine/Binaries"
rm -rf "$ENGINE_PATH/Engine/Intermediate"
rm -rf "$ENGINE_PATH/Engine/Saved"
rm -rf "$ENGINE_PATH/Engine/DerivedDataCache"

echo "Engine build folders cleared."
