#!/bin/bash
set -e

ENV_FILE="$(dirname "$0")/../.env"
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | sed 's/\r$//' | xargs)
else
    echo "Missing .env file at $ENV_FILE"
    exit 1
fi

# Arguments
MODE=$1  # full (default), code, blueprints, content

# Required
REQUIRED_VARS=("PROJECT_NAME" "BUILD_CONFIG" "PROJECT_DIR" "UNREAL_ENGINE_PATH")
for VAR in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!VAR}" ]; then
    echo "Missing env var: $VAR"
    exit 1
  fi
done

ROOT_DIR="$(pwd)"
UAT_SCRIPT="$ROOT_DIR/$UNREAL_ENGINE_PATH/Engine/Build/BatchFiles/RunUAT.sh"
UPROJECT="$ROOT_DIR/$PROJECT_DIR/$PROJECT_NAME.uproject"

# Mode-specific options
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
    echo "Building: C++ only (no cook, no pak, no archive)"
    EXTRA_ARGS=(-build -skipcook -skipstage -pak)
    ;;
  blueprints)
    echo "Building: Blueprint-only changes (cook without rebuild)"
    EXTRA_ARGS=(-cook -stage -pak -skipbuild -nocompile)
    ;;
  content)
    echo "Building: Content-only (cook + pak only)"
    EXTRA_ARGS=(-cook -stage -pak -skipbuild -nocompileeditor)
    ;;
  full | *)
    echo "Building: Full package"
    EXTRA_ARGS=(-cook -build -stage -pak -archive -archivedirectory="$ROOT_DIR/$ARCHIVE_DIR")
    ;;
esac

echo "Running BuildCookRun..."
"$UAT_SCRIPT" BuildCookRun "${COMMON_ARGS[@]}" "${EXTRA_ARGS[@]}"
