#!/usr/bin/env bash
# Prepare the pinned Blender build and run it without a GUI.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLENDER_BIN="$("$HERE/bootstrap.sh")"
exec "$BLENDER_BIN" --background "$@"
