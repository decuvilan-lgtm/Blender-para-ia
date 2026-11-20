#!/usr/bin/env python3
"""Short-lived HTTP command gateway for the existing Blender GUI bridge."""
import json, os, secrets, subprocess, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

API_TOKEN = os.environ["BLENDER_REMOTE_API_TOKEN"]
BRIDGE_TOKEN = os.environ["BLENDER_BRIDGE_TOKEN"]
CLIENT = os.environ.get("BLENDER_CLIENT", "python session_system/repo_headless/client.py")
ALLOWED = {"ping", "scene-info", "create-demo", "render", "save"}
ROOT = Path(__file__).resolve().parent / "web"

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, data, content_type="application/json"):
        raw = data if isinstance(data, bytes) else json.dumps(data).encode()
        self.send_response(code); self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            return self._send(404, {"error":"not_found"})
        self._send(200, (ROOT / "index.html").read_bytes(), "text/html; charset=utf-8")
    def do_POST(self):
        if self.path != "/api/command":
            return self._send(404, {"error":"not_found"})
        supplied = self.headers.get("Authorization", "").removeprefix("Bearer ").strip()
        if not secrets.compare_digest(supplied, API_TOKEN):
            return self._send(401, {"error":"unauthorized"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size < 1 or size > 4096: raise ValueError("Invalid request size")
            payload = json.loads(self.rfile.read(size))
            command = payload.get("command")
            if command not in ALLOWED: raise ValueError("Command not allowed")
            env = os.environ.copy(); env["BLENDER_BRIDGE_TOKEN"] = BRIDGE_TOKEN
            proc = subprocess.run([sys.executable, "session_system/repo_headless/client.py",
                command, "--timeout", "300"], cwd=os.environ["GITHUB_WORKSPACE"],
                env=env, capture_output=True, text=True, timeout=310)
            if proc.returncode: return self._send(502, {"error":proc.stderr[-3000:], "output":proc.stdout[-3000:]})
            try: result = json.loads(proc.stdout)
            except Exception: result = {"output":proc.stdout}
            self._send(200, result)
        except Exception as exc:
            self._send(400, {"error":str(exc)})
    def log_message(self, *_): pass

ThreadingHTTPServer(("127.0.0.1", 8766), Handler).serve_forever()
