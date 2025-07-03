#!/bin/bash

set -e

# Enable optional logging
LOG_FLAG=""
if [[ "$UE_LOGGING" == "1" ]]; then
    LOG_FLAG="-log"
fi

DEFAULT_MAP="${UE_MAP:-LobbyMap}"
PORT="${UE_PORT:-7777}"
PERFORMANCE_FLAGS="-USEALLAVAILABLECORES -NoVerifyGC -NoSound -NoPak"
BUILD_CONFIG="${BUILD_CONFIG:Shipping}"

# Validate required variables
if [[ -z "$PROJECT_NAME" ]]; then
    echo "Error: PROJECT_NAME environment variable not set"
    exit 1
fi

SEARCH_ROOT="/home/ue-server/${PROJECT_NAME}Server/Build/Linux/${PROJECT_NAME}/Binaries/Linux"
SERVER_BINARY=$(find "$SEARCH_ROOT" -type f -name "${PROJECT_NAME}-Linux-${BUILD_CONFIG}" | head -n 1)

if [[ -z "$SERVER_BINARY" ]]; then
    echo "Error: Could not find server binary in $SEARCH_ROOT"
    find "$SEARCH_ROOT" -name "*Server*" -type f || echo "No server files found"
    sleep infinity
    exit 1
fi

echo "Starting server:"
echo "  Binary: $SERVER_BINARY"
echo "  Map: $DEFAULT_MAP"
echo "  Port: $PORT"
echo "  Logging: $LOG_FLAG"

mkdir -p /var/log/ue
LOG_PATH="/var/log/ue/server.log"

cd "$(dirname "$SERVER_BINARY")"

echo "Executing from: $(pwd)"
echo "Command: $(basename "$SERVER_BINARY") $DEFAULT_MAP -port=$PORT -skiploadplugins -noutiltrace $PERFORMANCE_FLAGS $LOG_FLAG"

# Run the server and log both to console and file
"./$(basename "$SERVER_BINARY")" "$DEFAULT_MAP" -port="$PORT" -skiploadplugins -noutiltrace $PERFORMANCE_FLAGS "$LOG_FLAG" \
  2>&1 | tee -a "$LOG_PATH"


echo "Server exited."
exit 0 ... version: '3.8'
