"""CLI client for the Blender AI Bridge."""
from __future__ import annotations
import argparse, json, os, socket, sys

COMMANDS = ["ping", "scene-info", "create-demo", "save", "render", "visual-test",
            "add-primitive", "move-object", "scale-object", "rotate-object", "delete-object"]

def send(command: str, host: str, port: int, token: str, timeout: float, params=None):
    if not token:
        raise RuntimeError("Set BLENDER_BRIDGE_TOKEN before connecting.")
    request = {"command": command, "token": token, **(params or {})}
    payload = json.dumps(request, ensure_ascii=False).encode("utf-8") + b"\n"
    with socket.create_connection((host, port), timeout=timeout) as conn:
        conn.settimeout(timeout)
        conn.sendall(payload)
        stream = conn.makefile("rb")
        line = stream.readline(16 * 1024 * 1024)
    if not line:
        raise RuntimeError("Bridge closed the connection without a response.")
    response = json.loads(line.decode("utf-8"))
    print(json.dumps(response, ensure_ascii=False))
    if not response.get("ok"):
        raise RuntimeError(response.get("error", "Bridge operation failed"))
    return response

def main():
    parser = argparse.ArgumentParser(description="Send an allowlisted command to an active Blender GUI session.")
    parser.add_argument("command", choices=COMMANDS)
    parser.add_argument("--host", default=os.environ.get("BLENDER_BRIDGE_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("BLENDER_BRIDGE_PORT", "8765")))
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--payload", default="{}", help="JSON object with command parameters")
    args = parser.parse_args()
    try:
        params = json.loads(args.payload)
        if not isinstance(params, dict):
            raise ValueError("--payload must be a JSON object")
        send(args.command, args.host, args.port, os.environ.get("BLENDER_BRIDGE_TOKEN", ""), args.timeout, params)
    except Exception as exc:
        print("ERROR:", exc, file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
