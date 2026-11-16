#!/usr/bin/env bash
# Assemble the five Actions transport ZIPs and install the pinned Blender runtime.
# Usage: bash assemble_transferred_runtime.sh /path/to/transfer-directory
set -euo pipefail

TRANSFER_DIR="${1:-}"
if [[ -z "$TRANSFER_DIR" || ! -d "$TRANSFER_DIR" ]]; then
  echo "Usage: bash $0 /path/to/transfer-directory" >&2
  exit 2
fi

VERSION="4.5.3"
ARCHIVE_NAME="blender-${VERSION}-linux-x64.tar.xz"
EXPECTED_SHA256="975c58fcb244273838534bba771e64ad87739216b0f9b39a888531a49a72d845"
WORK_DIR="$TRANSFER_DIR/assembled"
PARTS_DIR="$WORK_DIR/parts"
ARCHIVE="$WORK_DIR/$ARCHIVE_NAME"
INSTALL_ROOT="${BLENDER_CACHE_DIR:-$HOME/.cache/blender-for-ai}"
BLENDER_BIN="$INSTALL_ROOT/blender-${VERSION}-linux-x64/blender"

for command in unzip sha256sum cat tar; do
  command -v "$command" >/dev/null || { echo "Missing required command: $command" >&2; exit 1; }
done

mkdir -p "$PARTS_DIR"
for i in 00 01 02 03 04; do
  zip="$TRANSFER_DIR/blender-part-$i.zip"
  [[ -s "$zip" ]] || { echo "Missing transfer artifact: $zip" >&2; exit 1; }
  unzip -oq "$zip" -d "$PARTS_DIR"
done

checksum_zip="$TRANSFER_DIR/blender-parts-checksums.zip"
[[ -s "$checksum_zip" ]] || { echo "Missing checksum artifact: $checksum_zip" >&2; exit 1; }
unzip -oq "$checksum_zip" -d "$PARTS_DIR"
(
  cd "$PARTS_DIR"
  sha256sum --check parts.sha256
)

for i in 00 01 02 03 04; do
  [[ -s "$PARTS_DIR/part-$i" ]] || { echo "Missing extracted part-$i" >&2; exit 1; }
done
cat "$PARTS_DIR"/part-00 "$PARTS_DIR"/part-01 "$PARTS_DIR"/part-02 "$PARTS_DIR"/part-03 "$PARTS_DIR"/part-04 > "$ARCHIVE"
echo "$EXPECTED_SHA256  $ARCHIVE" | sha256sum --check
[[ "$(stat -c%s "$ARCHIVE")" -eq 377397328 ]]

mkdir -p "$INSTALL_ROOT"
if [[ ! -x "$BLENDER_BIN" ]]; then
  tar -xJf "$ARCHIVE" -C "$INSTALL_ROOT"
fi
[[ -x "$BLENDER_BIN" ]] || { echo "Blender executable not found: $BLENDER_BIN" >&2; exit 1; }
"$BLENDER_BIN" --version
"$BLENDER_BIN" --background --factory-startup --python-expr "import bpy; print('A_RUNTIME_OK', bpy.app.version_string)"
