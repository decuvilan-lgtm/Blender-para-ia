#!/usr/bin/env bash
set -euo pipefail

BLENDER_VERSION="${BLENDER_VERSION:-4.5.3}"
BLENDER_MAJOR_MINOR="${BLENDER_MAJOR_MINOR:-4.5}"
CACHE_DIR="${BLENDER_CACHE_DIR:-$HOME/.cache/blender-for-ai}"
mkdir -p "$CACHE_DIR"
ARCHIVE="$CACHE_DIR/blender-${BLENDER_VERSION}-linux-x64.tar.xz"
URL="https://download.blender.org/release/Blender${BLENDER_MAJOR_MINOR}/blender-${BLENDER_VERSION}-linux-x64.tar.xz"

if [[ ! -f "$ARCHIVE" ]]; then
  echo "Downloading Blender ${BLENDER_VERSION}..."
  curl --fail --location --retry 3 "$URL" -o "$ARCHIVE"
fi

tar -xf "$ARCHIVE" -C "$CACHE_DIR"
BIN="$(find "$CACHE_DIR" -maxdepth 2 -type f -name blender -perm -u+x | head -n 1)"
if [[ -z "$BIN" ]]; then
  echo "Could not locate Blender executable after extraction." >&2
  exit 1
fi
echo "$BIN"
