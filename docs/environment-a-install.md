# Environment A — Blender runtime installation and transfer

This guide records the reproducible installation of the pinned Blender runtime in the assistant's own experimental workspace (Environment A). Environment A is **not** the Blender GUI runner in GitHub Actions (Environment B).

## Permanent binary source

- GitHub Release: https://github.com/decuvilan-lgtm/Blender-para-ia/releases/tag/blender-4.5.3-linux-x64
- Asset: `blender-4.5.3-linux-x64.tar.xz`
- Size: 377,397,328 bytes
- SHA-256: `975c58fcb244273838534bba771e64ad87739216b0f9b39a888531a49a72d845`

The Release asset is the durable copy. Actions artifacts are only a temporary transport bridge (30-day retention), not the permanent source.

## Why the transfer uses chunks

The assistant's file-materialization path accepts files up to 100 MiB. The 377 MB archive cannot be materialized as one file. The repository workflow downloads the Release asset, verifies its SHA-256, splits it into five pieces of 80 MiB or less, and publishes five individual Actions artifacts plus a checksum artifact.

Workflow: [export-blender-runtime-artifact.yml](../.github/workflows/export-blender-runtime-artifact.yml)

## Transfer procedure

1. Run **Actions → Export Blender runtime for Environment A transfer** (or push a change to the workflow file).
2. Wait for a successful run. It produces `blender-runtime-part-00` through `blender-runtime-part-04`, plus `blender-runtime-parts-checksums`.
3. Download each artifact ZIP through the GitHub Actions artifact-download connector.
4. Materialize the six ZIP files into one directory in A's working filesystem.
5. Extract each ZIP. Verify all five parts with `sha256sum -c parts.sha256`.
6. Join the parts in order: `cat part-00 part-01 part-02 part-03 part-04 > blender-4.5.3-linux-x64.tar.xz`.
7. Verify the assembled archive's exact byte size (377397328) and SHA-256 (above).
8. Extract the full TAR.XZ archive to the chosen installation directory.
9. Run `blender --version` and a background `bpy` smoke test.

The repository assembly script is [assemble_transferred_runtime.sh](../ai_lab/experimental/assemble_transferred_runtime.sh). Its default destination is `~/.cache/blender-for-ai`; the successful full installation recorded below used `/opt/blender-full-test`.

## Acceptance test

A complete installation is considered successful when all of these are true:

- The reconstructed archive has the expected exact size and SHA-256.
- Blender prints the pinned 4.5.3 LTS version.
- Background Python can import `bpy` and access a scene.
- A test `.blend` file can be saved and reopened.
- A render image is produced and verified as a PNG.

An Actions run or Blender execution in Environment B does **not** count as proof that A can run Blender.

## Verified Environment A installation (2026-11-17)

**Status: FULL INSTALLATION AND HEADLESS SCENE TEST PASSED.**

- Environment A shell recovered and reported a 32 GB overlay filesystem, about 30 GB available, and 5.8 GiB RAM (about 4.7 GiB available before installation).
- Direct DNS resolution of `download.blender.org` failed inside A. The six unexpired artifacts from workflow run [43805163265](https://github.com/decuvilan-lgtm/Blender-para-ia/actions/runs/43805163265) were instead downloaded through GitHub and materialized in A.
- All five chunk checksums passed.
- Reassembled archive: 377,397,328 bytes; SHA-256 matched the pinned Release asset exactly.
- Full extraction path: `/opt/blender-full-test/blender-4.5.3-linux-x64`.
- Extracted installation footprint: **1.2 GB**.
- `blender --version`: **Blender 4.5.3 LTS**.
- `bpy` smoke test passed and found the default scene.
- Created `/mnt/data/blender-a-full-install-proof/full-install-test.blend`, reopened it successfully, and verified 4 objects and camera `A_Test_Camera`.
- Rendered `render-workbench.png` at 320×180; Blender completed the Workbench render in 0.69 seconds.
- Render and project evidence are stored in A under `/mnt/data/blender-a-full-install-proof/`.

### Rendering note

The first 640×360 Eevee Next render emitted EGL `EGL_BAD_MATCH` warnings and did not finish within the command's 300-second limit. This did not prevent Blender startup, Python execution, scene creation, saving, reopening, or Workbench rendering. For this headless environment, Workbench is currently the confirmed rendering path; Eevee/Cycles need separate diagnosis.

### Reproduction commands

```bash
BLENDER=/opt/blender-full-test/blender-4.5.3-linux-x64/blender
"$BLENDER" --version
"$BLENDER" -b --factory-startup --python-expr \
  'import bpy; print("BLENDER_VERSION=" + bpy.app.version_string); print("SCENE=" + bpy.context.scene.name)'
"$BLENDER" -b /mnt/data/blender-a-full-install-proof/full-install-test.blend \
  --python-expr 'import bpy; print("REOPEN_OK", len(bpy.context.scene.objects))'
```

## Keep the source durable

The GitHub Release asset remains available unless the Release is deleted. Actions transfer artifacts expire after 30 days and can be regenerated by rerunning the export workflow. Do not commit the 377 MB binary or its chunks into Git history.
