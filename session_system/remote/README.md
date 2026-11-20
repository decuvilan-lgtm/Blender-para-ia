# Blender Live Session (temporal)

## Start
Open **Actions → Blender Live Session → Run workflow**. Optionally provide a repository-relative `.blend` project. The workflow creates one Blender 4.5.3 GUI instance on an ephemeral Ubuntu runner, starts a password-protected VNC server, serves noVNC over a temporary Cloudflare Quick Tunnel, and records the real X11 desktop to `full-session.mp4`.

## Connect
Open the workflow run logs and find the **Blender Live URL** and **VNC password** notices from the “Start Blender GUI and authenticated remote desktop” step. Open the complete URL (including its fragment token). Enter the VNC password in the noVNC connection prompt. Keep the workflow running while using the session.

The page also has direct command buttons. They call a loopback-only HTTP gateway which authenticates a per-run random bearer token and forwards allowlisted commands to the bridge inside the already-running Blender process. The bridge itself remains bound to 127.0.0.1:8765; it is never exposed publicly.

## End and artifacts
Cancel the workflow to end the temporary session. Cleanup stops the recorder, Blender, VNC, tunnel and virtual desktop, then uploads `blender-live-session-evidence` with the final MP4, desktop capture, logs and saved .blend project. GitHub-hosted runners have a six-hour maximum job runtime.

## Security notes
The Cloudflare Quick Tunnel URL is public and temporary. The control page uses a cryptographically random per-run API token in the URL fragment; VNC requires a separate random password. Do not paste either credential into public issues or commit them. The tunnel is not intended as a permanent service.
