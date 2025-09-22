#!/bin/bash
set -e

# -----------------------------
# Config (override via .env)
# -----------------------------
PROJECT_NAME=${PROJECT_NAME:-UnrealProject}
UE_PORT=${UE_PORT:-7777}
UE_QUERY_PORT=${UE_QUERY_PORT:-27015}
UE_MAP=${UE_MAP:-/Game/Maps/StartMap}
UE_LOGGING=${UE_LOGGING:-1}
BUILD_CONFIG=${BUILD_CONFIG:-Shipping}
UE_DEBUG=${UE_DEBUG:-0}

# -----------------------------
# Binary path resolution
# -----------------------------
BASE_DIR="./LinuxServer/${PROJECT_NAME}/Binaries/Linux"

if [ "$BUILD_CONFIG" == "Development" ]; then
    # Development builds do not carry a suffix
    BINARY="${BASE_DIR}/${PROJECT_NAME}Server"
elif [ "$BUILD_CONFIG" == "Shipping" ]; then
    # Shipping builds have explicit suffix
    BINARY="${BASE_DIR}/${PROJECT_NAME}Server-Linux-Shipping"
else
    # Fallback for other configs (Test, DebugGame, etc.)
    BINARY="${BASE_DIR}/${PROJECT_NAME}Server-Linux-${BUILD_CONFIG}"
fi

LOG_FILE="/home/ue-server/logs/Server.log"

echo "========== Unreal Engine Dedicated Server Startup =========="
echo " Project Name : $PROJECT_NAME"
echo " Binary Path  : $BINARY"
echo " Map          : $UE_MAP"
echo " Ports        : Game=$UE_PORT, Query=$UE_QUERY_PORT"
echo " Build Config : $BUILD_CONFIG"
echo " Logging      : $UE_LOGGING"
echo " Debug Mode   : $UE_DEBUG"
echo "============================================================"

# -----------------------------
# Binary sanity check
# -----------------------------
if [ ! -f "$BINARY" ]; then
  echo "[ERROR] Could not find server binary at $BINARY"
  echo "[DEBUG] Available contents under ./LinuxServer:"
  ls -R ./LinuxServer 2>/dev/null || echo "[ERROR] LinuxServer directory not found"
  exit 1
fi

echo "[DEBUG] Binary info:"
ls -lh "$BINARY"
if command -v file >/dev/null 2>&1; then
    file "$BINARY"
else
    echo "[WARN] 'file' command not available"
fi

# -----------------------------
# Engine config check
# -----------------------------
if [ ! -d "./LinuxServer/Engine/Config" ]; then
  echo "[WARN] Engine config directory missing!"
  ls -R ./LinuxServer/Engine 2>/dev/null || echo "[WARN] Engine directory not found"
fi

# -----------------------------
# Ensure logs dir + core dumps
# -----------------------------
mkdir -p /home/ue-server/logs
ulimit -c unlimited || echo "[WARN] Failed to enable core dumps"

# Set core dump pattern to include timestamp
echo "core.%e.%p.%t" > /proc/sys/kernel/core_pattern 2>/dev/null || echo "[WARN] Cannot set core dump pattern"

# -----------------------------
# Dependency check
# -----------------------------
echo "[DEBUG] Checking binary dependencies..."
if command -v ldd >/dev/null 2>&1; then
    MISSING=$(ldd "$BINARY" 2>/dev/null | grep "not found" || true)
    if [ -n "$MISSING" ]; then
        echo "[ERROR] Missing shared libraries:"
        echo "$MISSING"
        exit 1
    else
        echo "[OK] All required shared libraries found."
    fi
else
    echo "[WARN] ldd command not available, skipping dependency check"
fi

# -----------------------------
# Environment diagnostics
# -----------------------------
echo "[DEBUG] Environment diagnostics:"
uname -a
ldd --version 2>/dev/null | head -n 1 || echo "[WARN] ldd version unavailable"
df -h / || echo "[WARN] df command failed"
free -h 2>/dev/null || echo "[WARN] free command not available"

# -----------------------------
# Improved content validation
# -----------------------------
echo "[DEBUG] Validating game content..."
PAK_DIR="./LinuxServer/${PROJECT_NAME}/Content/Paks"
if [ -d "$PAK_DIR" ]; then
    PAK_COUNT=$(find "$PAK_DIR" -name "*.pak" | wc -l)
    if [ "$PAK_COUNT" -eq 0 ]; then
        echo "[ERROR] No PAK files found in $PAK_DIR"
        echo "[DEBUG] Content directory structure:"
        ls -la "$PAK_DIR" 2>/dev/null || echo "Directory does not exist"
        exit 1
    else
        echo "[OK] Found $PAK_COUNT PAK file(s)"
        # List PAK files for debugging
        ls -lh "$PAK_DIR"/*.pak
    fi
else
    echo "[ERROR] PAK directory not found: $PAK_DIR"
    echo "[DEBUG] Available content structure:"
    find "./LinuxServer/${PROJECT_NAME}" -name "Content" -type d 2>/dev/null || echo "No Content directories found"
    exit 1
fi

# -----------------------------
# Build argument list
# -----------------------------
ARGS=(
    "$UE_MAP?listen"
    -Port="$UE_PORT"
    -QueryPort="$UE_QUERY_PORT"
    -unattended
    -NoCrashDialog
    -nobeautifuloutput
    -logtimes
    -log
)

# Add logging arguments
if [ "$UE_LOGGING" = "1" ]; then
    ARGS+=(-AbsLog="$LOG_FILE")
fi

# Enable query port explicitly (UE5+ requirement)
ARGS+=(-EnableQueryPort)

echo "[INFO] Launching server with arguments:"
for arg in "${ARGS[@]}"; do
    echo "   $arg"
done

# -----------------------------
# Signal handlers for graceful shutdown
# -----------------------------
cleanup() {
    echo "[INFO] Received shutdown signal, cleaning up..."
    if [ -n "$SERVER_PID" ]; then
        kill -TERM "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
    show_logs_and_cores
    exit 0
}

show_logs_and_cores() {
    # Show logs if available
    if [ -f "$LOG_FILE" ]; then
        echo "--- Last 50 lines of log ---"
        tail -n 50 "$LOG_FILE" | sed 's/^/[UE] /'
    else
        echo "[WARN] No log file created at $LOG_FILE"
    fi
    
    # Check for core dumps
    if ls core* >/dev/null 2>&1; then
        echo "[DEBUG] Core dump(s) detected:"
        ls -lh core*
        # If in debug mode, try to get stack trace
        if [ "$UE_DEBUG" -eq 1 ] && command -v gdb >/dev/null 2>&1; then
            for core in core*; do
                echo "[DEBUG] Stack trace from $core:"
                gdb -batch -ex "bt" "$BINARY" "$core" 2>/dev/null || echo "Failed to analyze core dump"
            done
        fi
    fi
}

trap cleanup SIGTERM SIGINT

# -----------------------------
# Run with or without gdb
# -----------------------------
if [ "$UE_DEBUG" -eq 1 ] && command -v gdb >/dev/null 2>&1; then
    echo "[DEBUG] Running under gdb for debugging..."
    # Use gdb with proper signal handling
    gdb -batch \
        -ex "handle SIGTERM nostop noprint pass" \
        -ex "handle SIGINT nostop noprint pass" \
        -ex "run" \
        -ex "thread apply all bt" \
        -ex "quit" \
        --args "$BINARY" "${ARGS[@]}"
    EXIT_CODE=$?
    echo "[INFO] Server exited with code $EXIT_CODE"
    show_logs_and_cores
else
    echo "[INFO] Starting server..."
    "$BINARY" "${ARGS[@]}" &
    SERVER_PID=$!
    
    # Wait for server to finish
    wait $SERVER_PID
    EXIT_CODE=$?
    echo "[INFO] Server exited with code $EXIT_CODE"
    show_logs_and_cores
fi

exit $EXIT_CODE