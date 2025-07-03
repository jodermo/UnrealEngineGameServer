#!/bin/bash
set -e

# -- Load .env
ENV_FILE="$(dirname "$0")/../.env"
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | sed 's/\r$//' | xargs)
else
    echo "Missing .env file at $ENV_FILE"
    exit 1
fi

# -- Parse args
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
  echo "No build mode specified. Defaulting to 'full'."
  MODE="full"
fi

# -- Validate required env vars
REQUIRED_VARS=("PROJECT_NAME" "BUILD_DIR" "BUILD_CONFIG" "PROJECT_DIR" "UNREAL_ENGINE_PATH")
for VAR in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!VAR}" ]; then
    echo "Missing env var: $VAR"
    exit 1
  fi
done

# -- Set paths
ROOT_DIR="$(pwd)"
UPROJECT="$ROOT_DIR/$PROJECT_DIR/$PROJECT_NAME.uproject"
UAT_SCRIPT="$ROOT_DIR/$UNREAL_ENGINE_PATH/Engine/Build/BatchFiles/RunUAT.sh"
UBT_SCRIPT="$ROOT_DIR/$UNREAL_ENGINE_PATH/Engine/Build/BatchFiles/Linux/Build.sh"

BUILD_TRACK_FILE="$ROOT_DIR/.last_build_${MODE}"
EDITOR_TARGET_PATH="$ROOT_DIR/$PROJECT_DIR/Binaries/Linux/${PROJECT_NAME}Editor.target"

# -- Ensure EvolutionGameEditor.target exists (required for full cook)
if [[ "$MODE" == "full" && ! -f "$EDITOR_TARGET_PATH" ]]; then
  echo "Missing EvolutionGameEditor.target. Building editor target..."
  "$UBT_SCRIPT" ${PROJECT_NAME}Editor Linux  "$BUILD_CONFIG" "$UPROJECT"
fi

# -- Check for source changes
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
    echo "No changes detected. Skipping build for mode '$MODE'."
    # exit 0
fi

# -- BuildCookRun common args
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

# -- Mode-specific args
case "$MODE" in
  code)
    echo "Building: C++ only (no cook, no pak, no archive)"
    EXTRA_ARGS=(-build -basedir="$ROOT_DIR/$PROJECT_DIR" -skipcook -archive -skipstage -pak -archivedirectory="$ROOT_DIR/$BUILD_DIR" -trace=default)
    ;;
  blueprints)
    echo "Building: Blueprint-only changes (cook without rebuild)"
    EXTRA_ARGS=(-cook -basedir="$ROOT_DIR/$PROJECT_DIR" -stage -archive -pak -skipbuild -nocompile -archivedirectory="$ROOT_DIR/$BUILD_DIR" -trace=default)
    ;;
  content)
    echo "Building: Content-only (cook + pak only)"
    EXTRA_ARGS=(-cook -basedir="$ROOT_DIR/$PROJECT_DIR" -stage -archive -pak -skipbuild -nocompileeditor -allcontent -cookall -includeenginecontent -archivedirectory="$ROOT_DIR/$BUILD_DIR" -trace=default)
    ;;
  server)
    echo "Building: Server binaries only (no cook, no pak)"
    EXTRA_ARGS=(-build -basedir="$ROOT_DIR/$PROJECT_DIR" -server -archive -allcontent -includeenginecontent -skipcook -skipstage -skippackage -noclean -nocompileeditor -archivedirectory="$ROOT_DIR/$BUILD_DIR" -trace=default)
    ;;
  full | *)
    echo "Building: Full package"
    EXTRA_ARGS=(-cook -build -basedir="$ROOT_DIR/$PROJECT_DIR" -stage -server -pak -archive -allcontent -cookall -includeenginecontent -nocompileeditor -archivedirectory="$ROOT_DIR/$BUILD_DIR" -trace=default)
    ;;
esac

# -- Optional: Log to timestamped file
LOG_DIR="$ROOT_DIR/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/build_${MODE}_$(date +%F_%H-%M-%S).log"

# -- Run UAT
echo "Ensuring Editor target is built in Development configuration (required for cook)..."
"$ROOT_DIR/$UNREAL_ENGINE_PATH/Engine/Build/BatchFiles/Linux/Build.sh" \
  "${PROJECT_NAME}Editor" \
  Development \
  Linux \
  -project="$UPROJECT" \
  -waitmutex \
  -nointellisense

echo "Running BuildCookRun..."
"$UAT_SCRIPT" BuildCookRun "${COMMON_ARGS[@]}" "${EXTRA_ARGS[@]}" 2>&1 | tee "$LOG_FILE"


# -- Stamp build time
touch "$BUILD_TRACK_FILE"

echo "Build complete: $MODE"
echo "Log saved to: $LOG_FILE"
