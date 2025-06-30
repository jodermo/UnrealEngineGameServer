#!/bin/bash

# Optional: enable logging
if [[ "$UE_LOGGING" == "1" ]]; then
    LOG_FLAG="-log"
else
    LOG_FLAG=""
fi

# Default to LobbyMap if not set
DEFAULT_MAP="${UE_MAP:-LobbyMap}"
PORT="${UE_PORT:-7777}"

PERFORMANCE_FLAGS="-USEALLAVAILABLECORES -NoVerifyGC -NoSound -NoPak"
eval "$LOG_CMD $PERFORMANCE_FLAGS" >> "$LOG_PATH" 2>&1

# Validate PROJECT_NAME
if [ -z "$PROJECT_NAME" ]; then
    echo "Error: PROJECT_NAME environment variable not set"
    exit 1
fi

# Correct path to packaged server binary
SERVER_BINARY="./UnrealProjects/${PROJECT_NAME}/LinuxServer/${PROJECT_NAME}/Binaries/Linux/${PROJECT_NAME}Server-Linux-Shipping"

# ls "./UnrealProjects/${PROJECT_NAME}/"
# Show config
echo "Starting server:"
echo "  Binary: $SERVER_BINARY"
echo "  Map: $DEFAULT_MAP"
echo "  Port: $PORT"
echo "  Logging: $LOG_FLAG"

mkdir -p /var/log/ue
LOG_PATH="/var/log/ue/server.log"

# Show full command for clarity
echo "Executing: $SERVER_BINARY $DEFAULT_MAP -port=$PORT -skiploadplugins -noutiltrace $LOG_FLAG"

# Run the Unreal server binary with the selected map, port, and optional logging.
LOG_CMD="$SERVER_BINARY -port=$PORT -skiploadplugins -noutiltrace $LOG_FLAG"
echo "Executing: $LOG_CMD"
eval "$LOG_CMD" >> "$LOG_PATH" 2>&1


# Fallback if exec fails
echo "Server exited. Sleeping for inspection..."
sleep infinity
