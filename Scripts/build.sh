#!/bin/bash
set -e


# -----------------------------
# Timestamped logging helper
# -----------------------------
log() {
  local level=$1
  shift
  echo "[$level $(date +'%H:%M:%S')] $*"
}

ROOT_DIR="$(pwd)"
log INFO "ROOT_DIR=$ROOT_DIR"


# -----------------------------
# Load .env
# -----------------------------
ENV_FILE="$(dirname "$0")/../.env"
if [ -f "$ENV_FILE" ]; then
    set -a
    # ignore comments and empty lines, require KEY=VALUE format
    source <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' "$ENV_FILE" | sed 's/\r$//')

    set +a
else
    log ERROR "Missing .env file at $ENV_FILE"
    exit 1
fi

log INFO "Loaded .env from $ENV_FILE"
log INFO "UNREAL_ENGINE_PATH=$UNREAL_ENGINE_PATH"


# -----------------------------
# Parse args
# -----------------------------
MODE=$1  # full, code, blueprints, content, server
if [[ "$MODE" == "--help" ]]; then
  echo "Usage: ./build.sh [mode]"
  echo "Modes:"
  echo "  full        - Build + cook + stage + pak + archive (default)"
  echo "  code        - Build only (C++)"
  echo "  content     - Cook + pak only"
  echo "  blueprints  - Cook only, no compile"
  echo "  server      - Server binaries only"
  exit 0
fi
if [[ -z "$MODE" ]]; then
  log INFO "No build mode specified. Defaulting to 'full'."
  MODE="full"
fi

# -----------------------------
# Validate required env vars
# -----------------------------
REQUIRED_VARS=("PROJECT_NAME" "BUILD_DIR" "BUILD_CONFIG" "PROJECT_DIR" "UNREAL_ENGINE_PATH")
for VAR in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!VAR}" ]; then
    log ERROR "Missing env var: $VAR"
    exit 1
  fi
done

# -----------------------------
# Set paths
# -----------------------------
ROOT_DIR="$(pwd)"
UPROJECT="$ROOT_DIR/$PROJECT_DIR/$PROJECT_NAME.uproject"
UAT_SCRIPT="$ROOT_DIR/$UNREAL_ENGINE_PATH/Engine/Build/BatchFiles/RunUAT.sh"
UBT_SCRIPT="$ROOT_DIR/$UNREAL_ENGINE_PATH/Engine/Build/BatchFiles/Linux/Build.sh"

BUILD_TRACK_FILE="$ROOT_DIR/.last_build_${MODE}"

log INFO "UBT_SCRIPT='$UBT_SCRIPT'"
ls -l "$UBT_SCRIPT" || log ERROR "File not found: $UBT_SCRIPT"


# -----------------------------
# ShaderCompileWorker check
# -----------------------------
SCW_DIR="$ROOT_DIR/$UNREAL_ENGINE_PATH/Engine/Binaries/Linux"
if [[ ! -f "$SCW_DIR/ShaderCompileWorker" && ! -f "$SCW_DIR/ShaderCompileWorker-Linux-Development" ]]; then
  log WARN "ShaderCompileWorker binary not found. Rebuilding..."
  "$UBT_SCRIPT" ShaderCompileWorker Development Linux -clean -waitmutex -nointellisense
else
  log INFO "ShaderCompileWorker already built, skipping."
fi

# -----------------------------
# Editor check (required for cooking)
# -----------------------------
if [[ "$MODE" =~ ^(full|content|blueprints)$ ]]; then
  EDITOR_BIN="$ROOT_DIR/$PROJECT_DIR/Binaries/Linux/${PROJECT_NAME}Editor-Linux-Development"
  if [[ ! -f "$EDITOR_BIN" ]]; then
    log INFO "Building Editor target (Development) for cook..."
    "$UBT_SCRIPT" "${PROJECT_NAME}Editor" Development Linux -project="$UPROJECT" -waitmutex -nointellisense
  fi
fi

# -----------------------------
# Check for source changes
# -----------------------------
check_changes() {
    if [ -f "$BUILD_TRACK_FILE" ]; then
        if find "$PROJECT_DIR/Source" -newer "$BUILD_TRACK_FILE" | grep -q .; then
            return 0
        else
            return 1
        fi
    else
        return 0
    fi
}
if ! check_changes; then
    log INFO "No source changes detected. Skipping compile step."
fi

# -----------------------------
# Map args from .env
# -----------------------------
MAP_ARGS=()
MAP_LIST=()

if [ -n "$UE_MAPS" ]; then
  IFS=',' read -ra MAP_LIST <<< "$UE_MAPS"

  for MAP in "${MAP_LIST[@]}"; do


    # Preflight: validate file exists
    MAP_FILE="$ROOT_DIR/$PROJECT_DIR/Content${MAP#/Game}.umap"
    if [ ! -f "$MAP_FILE" ]; then
      log ERROR "Map not found on disk: $MAP_FILE"
      exit 1
    fi
  done

  # Write cook list file
  COOK_LIST="$ROOT_DIR/CookMaps.txt"
  printf "%s\n" "${MAP_LIST[@]}" > "$COOK_LIST"
  log INFO "Wrote cook list to $COOK_LIST"
  cat "$COOK_LIST"

  MAP_ARGS=(-maplist="$COOK_LIST")
else
  log WARN "No UE_MAPS defined in .env — relying only on Project Settings -> Packaging."
fi

# -----------------------------
# BuildCookRun args
# -----------------------------
COMMON_ARGS=(
  -project="$UPROJECT"
  -noP4
  -platform=Linux
  -targetplatform=Linux
  -clientconfig=$BUILD_CONFIG
  -serverconfig=$BUILD_CONFIG
  -server
  -serverplatform=Linux
)

case "$MODE" in
  code)
    EXTRA_ARGS=(-build -skipcook -skipstage -pak -archive -archivedirectory="$ROOT_DIR/$BUILD_DIR")
    ;;
  blueprints)
    EXTRA_ARGS=(-cook -stage -archive -pak -skipbuild -nocompile -archivedirectory="$ROOT_DIR/$BUILD_DIR")
    ;;
  content)
    EXTRA_ARGS=(-cook -stage -archive -pak -skipbuild -nocompileeditor -allcontent -archivedirectory="$ROOT_DIR/$BUILD_DIR")
    ;;
  server)
    EXTRA_ARGS=(-build -server -archive -skipcook -skipstage -skippackage -noclean -archivedirectory="$ROOT_DIR/$BUILD_DIR")
    ;;
  full | *)
    EXTRA_ARGS=(-cook -build -stage -server -pak -archive -allcontent -archivedirectory="$ROOT_DIR/$BUILD_DIR")
    ;;
esac

# -----------------------------
# Logging
# -----------------------------
LOG_DIR="$ROOT_DIR/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/build_${MODE}_$(date +%F_%H-%M-%S).log"

# -----------------------------
# Run UAT
# -----------------------------
log INFO "Running BuildCookRun..."
"$UAT_SCRIPT" BuildCookRun "${COMMON_ARGS[@]}" "${EXTRA_ARGS[@]}" "${MAP_ARGS[@]}" 2>&1 | tee "$LOG_FILE"

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    log ERROR "UAT BuildCookRun failed! Check $LOG_FILE"
    exit 1
fi

# -----------------------------
# Verify cooked maps
# -----------------------------
PAK_DIR="$ROOT_DIR/$BUILD_DIR/LinuxServer/$PROJECT_NAME/Content/Paks"
log INFO "Verifying cooked maps in $PAK_DIR"

if [ -d "$PAK_DIR" ]; then
    if command -v strings >/dev/null 2>&1 && [ ${#MAP_LIST[@]} -gt 0 ]; then
        for MAP in "${MAP_LIST[@]}"; do
            MAP_NAME=$(basename "$MAP" .umap)
            if strings "$PAK_DIR"/*.pak | grep -q "$MAP"; then
                log INFO "✅ Map $MAP found in cooked .pak"
            else
                log ERROR "❌ Map $MAP missing in cooked .pak!"
                exit 1
            fi
        done
    else
        log WARN "Skipping verification (no maps listed or 'strings' not installed)."
    fi
else
    log ERROR "No Paks directory found at $PAK_DIR"
    exit 1
fi

# -----------------------------
# Stamp build time
# -----------------------------
touch "$BUILD_TRACK_FILE"

log INFO "Build complete: $MODE"
log INFO "Log saved to: $LOG_FILE"
