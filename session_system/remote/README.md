# Blender Live Session (temporal)

## Start
Open **Actions → Blender Live Session → Run workflow**. Optionally provide a repository-relative `.blend` project. The workflow creates one Blender 4.5.3 GUI instance on an ephemeral Ubuntu runner, starts password-protected VNC/noVNC, exposes the authenticated control page through a temporary Cloudflare Quick Tunnel, and records the session.

## Command and visual-evidence contract
POST `/api/command` with `Authorization: Bearer <session-token>` and JSON such as:

```json
{"command":"add-primitive","primitive":"uv_sphere","name":"Neon_Sphere","location":[0,0,1]}
```

A successful command is not acknowledged until Blender has executed it and the gateway has captured both:
- a JPEG screenshot of the actual X11 desktop;
- a short MP4 clip of the same desktop immediately after the command.

The response shape is:

```json
{
  "success": true,
  "command_id": "uuid",
  "command": "add-primitive",
  "result": {"created": "Neon_Sphere"},
  "evidence": {
    "captured_at": 0,
    "screenshot": {"mime_type": "image/jpeg", "encoding": "base64", "data": "..."},
    "video": {"mime_type": "video/mp4", "encoding": "base64", "data": "..."}
  }
}
```

Failures return `success:false` and do not claim that evidence exists. Evidence is returned inline with the command response; GitHub artifacts are not part of this command/evidence transport. The full-session recording remains an optional archive.

## Supported commands
`ping`, `scene-info`, `create-demo`, `render`, `save`, `visual-test`, `add-primitive`, `move-object`, `scale-object`, `rotate-object`, `delete-object`.

Object transforms require `name` and a three-number `value`. Primitive creation accepts `primitive` (cube, uv_sphere, cylinder, cone, plane, torus), optional `name`, `location`, and `size`.

## Connect
Open the workflow run logs and find the **Blender Live URL** and **VNC password** notices. Open the complete URL (including its fragment token). The control page also displays the returned screenshot and MP4 after each successful command.

## End and security
Cancel the workflow to end the temporary session. The bridge listens only on 127.0.0.1 inside the runner; the public gateway uses a random per-run bearer token. Do not publish session URLs or credentials. GitHub-hosted runners have a six-hour maximum job runtime.
