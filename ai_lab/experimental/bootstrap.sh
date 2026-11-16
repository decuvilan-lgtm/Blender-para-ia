#!/usr/bin/env bash
set -euo pipefail

BLENDER_VERSION="${BLENDER_VERSION:-4.5.3}"
BLENDER_MAJOR_MINOR="${BLENDER_MAJOR_MINOR:-4.5}"
CACHE_DIR="${BLENDER_CACHE_DIR:-$HOME/.cache/blender-for-ai}"
mkdir -p "$CACHE_DIR"

ARCHIVE="$CACHE_DIR/blender-${BLENDER_VERSION}-linux-x64.tar.xz"
BIN="$CACHE_DIR/blender-${BLENDER_VERSION}-linux-x64/blender"
URL="https://download.blender.org/release/Blender${BLENDER_MAJOR_MINOR}/blender-${BLENDER_VERSION}-linux-x64.tar.xz"

if [[ ! -f "$ARCHIVE" ]]; then
  echo "Downloading Blender ${BLENDER_VERSION}..." >&2
  curl --fail --location --retry 3 --retry-all-errors --retry-delay 5 "$URL" -o "$ARCHIVE"
fi

if [[ ! -x "$BIN" ]]; then
  echo "Extracting Blender ${BLENDER_VERSION}..." >&2
  tar -xf "$ARCHIVE" -C "$CACHE_DIR"
fi

if [[ ! -x "$BIN" ]]; then
  echo "Could not locate executable at expected path: $BIN" >&2
  exit 1
fi

# stdout is reserved for the executable path because run_headless.sh captures it.
printf '%s\n' "$BIN"
