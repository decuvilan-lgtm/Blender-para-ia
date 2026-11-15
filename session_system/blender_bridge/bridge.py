"""Localhost-only command bridge running inside the Blender GUI process.

Only allowlisted operations are accepted. Blender API calls are executed from
a bpy timer on Blender's main thread; the TCP server itself runs in a daemon
thread and never touches bpy data.
"""
from __future__ import annotations

import json
import os
import queue
import secrets
import socket
import threading
import time
import traceback
from pathlib import Path

import bpy

HOST = "127.0.0.1"
PORT = int(os.environ.get("BLENDER_BRIDGE_PORT", "8765"))
TOKEN = os.environ.get("BLENDER_BRIDGE_TOKEN", "")
ARTIFACT_DIR = Path(os.environ.get("BLENDER_ARTIFACT_DIR", "/tmp/blender-artifacts"))
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

_REQUESTS: "queue.Queue[tuple[dict, socket.socket]]" = queue.Queue()
_STOP = threading.Event()
_SERVER = None


def _scene_info():
    scene = bpy.context.scene
    return {
        "scene": scene.name,
        "objects": [
            {"name": obj.name, "type": obj.type, "location": [round(float(v), 4) for v in obj.location]}
            for obj in scene.objects
        ],
        "render": {
            "engine": scene.render.engine,
            "resolution_x": scene.render.resolution_x,
            "resolution_y": scene.render.resolution_y,
        },
        "blender_version": bpy.app.version_string,
    }


def _create_demo_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
    cube = bpy.context.object
    cube.name = "AI_Test_Cube"
    material = bpy.data.materials.new("AI_Test_Material")
    material.diffuse_color = (0.12, 0.42, 0.85, 1.0)
    cube.data.materials.append(material)

    bpy.ops.object.camera_add(location=(6, -8, 5))
    camera = bpy.context.object
    camera.name = "AI_Test_Camera"
    direction = cube.location - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = camera

    bpy.ops.object.light_add(type="AREA", location=(1, -4, 6))
    light = bpy.context.object
    light.name = "AI_Test_Area_Light"
    light.data.energy = 850
    light.data.shape = "DISK"
    light.data.size = 5

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 960
    scene.render.resolution_y = 540
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(ARTIFACT_DIR / "preview.png")
    return {"created": ["AI_Test_Cube", "AI_Test_Camera", "AI_Test_Area_Light"], "scene": scene.name}


def _execute(request):
    command = request.get("command")
    if command == "ping":
        return {"pong": True, "time": time.time(), "blender_version": bpy.app.version_string}
    if command == "scene-info":
        return _scene_info()
    if command == "create-demo":
        return _create_demo_scene()
    if command == "save":
        path = ARTIFACT_DIR / "session-project.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        return {"saved": str(path)}
    if command == "render":
        path = ARTIFACT_DIR / "preview.png"
        bpy.context.scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        return {"rendered": str(path)}
    if command == "shutdown":
        _STOP.set()
        return {"shutdown": True}
    raise ValueError("Unsupported command: %r" % command)


def _send(conn, payload):
    conn.sendall((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))


def _server_loop():
    global _SERVER
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _SERVER = server
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(8)
    server.settimeout(0.5)
    while not _STOP.is_set():
        try:
            conn, _ = server.accept()
        except socket.timeout:
            continue
        except OSError:
            break
        with conn:
            conn.settimeout(5)
            try:
                raw = conn.makefile("rb").readline(1024 * 1024)
                request = json.loads(raw.decode("utf-8"))
                supplied = str(request.pop("token", ""))
                if not TOKEN or not secrets.compare_digest(supplied, TOKEN):
                    _send(conn, {"ok": False, "error": "unauthorized"})
                    continue
                response_conn = conn.dup()
                response_conn.settimeout(300)
                _REQUESTS.put((request, response_conn))
                # The duplicate is answered by the Blender main-thread timer.
            except Exception as exc:
                try:
                    _send(conn, {"ok": False, "error": str(exc)})
                except OSError:
                    pass
    try:
        server.close()
    except OSError:
        pass


def _process_queue():
    while not _REQUESTS.empty():
        request, conn = _REQUESTS.get()
        try:
            result = _execute(request)
            _send(conn, {"ok": True, "result": result})
        except Exception as exc:
            _send(conn, {"ok": False, "error": str(exc), "traceback": traceback.format_exc()})
        finally:
            conn.close()
    return 0.05 if not _STOP.is_set() else None


def start_bridge():
    global _SERVER
    if not TOKEN:
        print("[AI Bridge] ERROR: BLENDER_BRIDGE_TOKEN is required; bridge not started.")
        return
    thread = threading.Thread(target=_server_loop, name="BlenderAIBridge", daemon=True)
    thread.start()
    bpy.app.timers.register(_process_queue, first_interval=0.1, persistent=True)
    print("[AI Bridge] Listening on %s:%s" % (HOST, PORT))


start_bridge()
