#!/usr/bin/env bash
set -euo pipefail

BLENDER_VERSION="${BLENDER_VERSION:-4.5.3}"
CACHE_DIR="${BLENDER_CACHE_DIR:-$HOME/.cache/blender-for-ai}"
mkdir -p "$CACHE_DIR"

ARCHIVE="$CACHE_DIR/blender-${BLENDER_VERSION}-linux-x64.tar.xz"
BIN="$CACHE_DIR/blender-${BLENDER_VERSION}-linux-x64/blender"
URL="https://github.com/decuvilan-lgtm/Blender-para-ia/releases/download/blender-${BLENDER_VERSION}-linux-x64/blender-${BLENDER_VERSION}-linux-x64.tar.xz"
EXPECTED_SHA256="975c58fcb244273838534bba771e64ad87739216b0f9b39a888531a49a72d845"

if [[ "$BLENDER_VERSION" != "4.5.3" ]]; then
  echo "No pinned GitHub runtime asset is registered for Blender $BLENDER_VERSION." >&2
  exit 1
fi

if [[ ! -f "$ARCHIVE" ]]; then
  echo "Downloading Blender ${BLENDER_VERSION} from the project's GitHub Release..." >&2
  curl --fail --location --retry 5 --retry-all-errors --retry-delay 5 "$URL" -o "$ARCHIVE"
fi

ACTUAL_SHA256="$(sha256sum "$ARCHIVE" | awk '{print $1}')"
if [[ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]]; then
  echo "Blender archive checksum mismatch; refusing to extract." >&2
  rm -f "$ARCHIVE"
  exit 1
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
printf '%s\\n' "$BIN"
