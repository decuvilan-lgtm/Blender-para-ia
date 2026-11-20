# Blender Session Viewer

## Purpose

The Blender installation in environment A is the development toolchain. The Actions runner (environment B) runs the real Blender GUI and produces visual evidence. This viewer is deliberately lightweight: it does not emulate Blender or create a substitute scene.

## Evidence pipeline

1. GitHub Actions starts Xvfb/Openbox and launches the pinned Blender 4.5.3 GUI.
2. The in-process bridge executes allowlisted `bpy` operations on Blender's main thread.
3. FFmpeg records the actual X11 desktop at 1600x900 and 6 fps while the session is active.
4. At the end, Actions packages `full-session.mp4`, `desktop.png`, `preview.png` (when a render was requested), the `.blend` project and diagnostic logs.
5. `index.html` is a local browser viewer for the downloaded evidence artifact.

## Current limitation

The MP4 is an end-of-session artifact, not a live stream. GitHub-hosted runners do not provide an inbound desktop address by default. A later remote-viewing layer must use an authenticated, short-lived connection; do not expose VNC, the bridge port, or an unauthenticated command endpoint publicly.

## Open the evidence

Download the `blender-session-evidence` artifact from the Actions run, extract it, and open `index.html` in a browser. The video is the primary evidence because it records the real editor over time; still images are supporting checkpoints.

## Keep the environments distinct

- **A:** persistent development environment with the installed Blender binary; used to develop and test the controller and scripts.
- **B:** temporary GitHub Actions machine running the actual GUI session; used to create and record the visible result.
