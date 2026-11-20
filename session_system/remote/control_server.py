#!/usr/bin/env python3
"""Authenticated HTTP gateway. Each successful Blender command returns visual evidence."""
import base64, json, os, secrets, subprocess, sys, tempfile, time, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from io import BytesIO
import mss
from PIL import Image

API_TOKEN=os.environ["BLENDER_REMOTE_API_TOKEN"]
BRIDGE_TOKEN=os.environ["BLENDER_BRIDGE_TOKEN"]
ROOT=Path(__file__).resolve().parent/"web"
WORKSPACE=Path(os.environ["GITHUB_WORKSPACE"])
PYTHON=os.environ.get("BLENDER_CLIENT",sys.executable)
ALLOWED={"ping","scene-info","create-demo","render","save","visual-test","add-primitive","move-object","scale-object","rotate-object","delete-object"}

def capture_visual_evidence(command_id):
    """Capture actual X11 desktop image plus a short MP4 after the Blender operation."""
    evidence_dir=Path(tempfile.mkdtemp(prefix="blender-evidence-"))
    screenshot=evidence_dir/"screen.jpg"
    video=evidence_dir/"clip.mp4"
    with mss.mss() as sct:
        monitor=sct.monitors[0]
        shot=sct.grab(monitor)
        image=Image.frombytes("RGB",shot.size,shot.rgb)
        image.thumbnail((1280,720))
        image.save(screenshot,"JPEG",quality=78,optimize=True)
    display=os.environ.get("DISPLAY",":99")
    proc=subprocess.run(["ffmpeg","-y","-loglevel","error","-f","x11grab","-draw_mouse","1",
        "-video_size","1600x900","-framerate","6","-i",display+".0","-t","1.5",
        "-vf","scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2",
        "-an","-c:v","libx264","-preset","ultrafast","-crf","32","-pix_fmt","yuv420p","-movflags","+faststart",str(video)],
        capture_output=True,text=True,timeout=20)
    if proc.returncode or not video.exists() or video.stat().st_size<1000:
        raise RuntimeError("Video evidence capture failed: "+proc.stderr[-1200:])
    return {
        "command_id":command_id,
        "captured_at":time.time(),
        "screenshot":{"mime_type":"image/jpeg","encoding":"base64","data":base64.b64encode(screenshot.read_bytes()).decode("ascii")},
        "video":{"mime_type":"video/mp4","encoding":"base64","data":base64.b64encode(video.read_bytes()).decode("ascii")},
    }

class Handler(BaseHTTPRequestHandler):
    def _send(self,code,data,content_type="application/json"):
        raw=data if isinstance(data,bytes) else json.dumps(data,ensure_ascii=False).encode()
        self.send_response(code); self.send_header("Content-Type",content_type)
        self.send_header("Content-Length",str(len(raw))); self.send_header("Cache-Control","no-store")
        self.send_header("Access-Control-Allow-Origin","null")
        self.end_headers(); self.wfile.write(raw)
    def do_OPTIONS(self):
        self.send_response(204); self.send_header("Access-Control-Allow-Headers","Authorization, Content-Type")
        self.send_header("Access-Control-Allow-Methods","POST, OPTIONS"); self.end_headers()
    def do_GET(self):
        if self.path in ("/","/index.html"): return self._send(200,(ROOT/"index.html").read_bytes(),"text/html; charset=utf-8")
        if self.path=="/api/health": return self._send(200,{"success":True,"service":"blender-live-gateway"})
        self._send(404,{"success":False,"error":"not_found"})
    def do_POST(self):
        if self.path!="/api/command": return self._send(404,{"success":False,"error":"not_found"})
        supplied=self.headers.get("Authorization","").removeprefix("Bearer ").strip()
        if not secrets.compare_digest(supplied,API_TOKEN): return self._send(401,{"success":False,"error":"unauthorized"})
        try:
            size=int(self.headers.get("Content-Length","0"))
            if size<1 or size>16384: raise ValueError("Invalid request size")
            request=json.loads(self.rfile.read(size))
            if not isinstance(request,dict): raise ValueError("JSON body must be an object")
            command=request.get("command")
            if command not in ALLOWED: raise ValueError("Command not allowed")
            params={k:v for k,v in request.items() if k not in {"command","command_id"}}
            command_id=str(request.get("command_id") or uuid.uuid4())
            env=os.environ.copy(); env["BLENDER_BRIDGE_TOKEN"]=BRIDGE_TOKEN
            proc=subprocess.run([PYTHON,str(WORKSPACE/"session_system/repo_headless/client.py"),
                command,"--timeout","300","--payload",json.dumps(params)],
                cwd=str(WORKSPACE),env=env,capture_output=True,text=True,timeout=310)
            if proc.returncode:
                return self._send(502,{"success":False,"command_id":command_id,"error":proc.stderr[-2500:],"output":proc.stdout[-1500:]})
            lines=[line for line in proc.stdout.splitlines() if line.strip()]
            result=json.loads(lines[-1]) if lines else {}
            if not result.get("ok"): return self._send(502,{"success":False,"command_id":command_id,"error":result.get("error","Blender command failed")})
            evidence=capture_visual_evidence(command_id)
            return self._send(200,{"success":True,"command_id":command_id,"command":command,
                "result":result.get("result"),"evidence":evidence})
        except subprocess.TimeoutExpired:
            self._send(504,{"success":False,"error":"Blender command timed out"})
        except Exception as exc:
            self._send(500,{"success":False,"error":str(exc)})
    def log_message(self,*_): pass

ThreadingHTTPServer(("127.0.0.1",8766),Handler).serve_forever()
