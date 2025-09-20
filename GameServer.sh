#!/bin/bash
set -e

# -----------------------------
# Config (override via .env)
# -----------------------------
PROJECT_NAME=${PROJECT_NAME:-EvolutionGame}
UE_PORT=${UE_PORT:-7777}
UE_QUERY_PORT=${UE_QUERY_PORT:-27015}
UE_MAP=${UE_MAP:-/Game/EvolutionGame/Levels/LobbyMap}
UE_LOGGING=${UE_LOGGING:-1}
BUILD_CONFIG=${BUILD_CONFIG:-Shipping}
UE_DEBUG=${UE_DEBUG:-0}   # Set to 1 for gdb backtrace

BINARY="./LinuxServer/${PROJECT_NAME}/Binaries/Linux/${PROJECT_NAME}Server-Linux-${BUILD_CONFIG}"
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
  ls -R ./LinuxServer || true
  exit 1
fi

echo "[DEBUG] Binary info:"
ls -lh "$BINARY"
command -v file >/dev/null 2>&1 && file "$BINARY" || echo "[WARN] 'file' command not available"

# -----------------------------
# Engine config check
# -----------------------------
if [ ! -d "./LinuxServer/Engine/Config" ]; then
  echo "[WARN] Engine config directory missing!"
  ls -R ./LinuxServer/Engine || true
fi

# -----------------------------
# Ensure logs dir + core dumps
# -----------------------------
mkdir -p /home/ue-server/logs
ulimit -c unlimited || echo "[WARN] Failed to enable core dumps"

# -----------------------------
# Dependency check
# -----------------------------
echo "[DEBUG] Checking binary dependencies..."
MISSING=$(ldd "$BINARY" 2>/dev/null | grep "not found" || true)
if [ -n "$MISSING" ]; then
  echo "[ERROR] Missing shared libraries:"
  echo "$MISSING"
  exit 1
else
  echo "[OK] All required shared libraries found."
fi

# -----------------------------
# Environment diagnostics
# -----------------------------
echo "[DEBUG] Environment diagnostics:"
uname -a
ldd --version | head -n 1 || true
df -h /
free -h || true

# Verify map exists in cooked paks
if ! strings ./LinuxServer/${PROJECT_NAME}/Content/Paks/*.pak | grep -q "$(basename $UE_MAP)"; then
  echo "[ERROR] Map $UE_MAP not found in cooked content! Check Project Settings -> Packaging -> Maps to Cook."
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

if [ "$UE_LOGGING" = "1" ]; then
  ARGS+=(-AbsLog="$LOG_FILE")
fi

echo "[INFO] Launching server with arguments:"
for arg in "${ARGS[@]}"; do
  echo "   $arg"
done

# -----------------------------
# Run with or without gdb
# -----------------------------
if [ "$UE_DEBUG" -eq 1 ]; then
  echo "[DEBUG] Running under gdb for backtrace..."
  gdb -batch -ex "run" -ex "bt" --args "$BINARY" "${ARGS[@]}"
  EXIT_CODE=$?
  echo "[INFO] Server exited with code $EXIT_CODE"
else
  exec "$BINARY" "${ARGS[@]}"
fi

# -----------------------------
# Log output (exec path won't reach here, only gdb path)
# -----------------------------
if [ -f "$LOG_FILE" ]; then
  echo "--- Last 100 lines of log ---"
  tail -n 100 "$LOG_FILE" | sed 's/^/[UE] /'
else
  echo "[WARN] No log file created! Falling back to stdout only."
fi

# -----------------------------
# Core dump check
# -----------------------------
if ls core* &>/dev/null; then
  echo "[DEBUG] Core dump(s) detected:"
  ls -lh core*
fi

exit $EXIT_CODE
