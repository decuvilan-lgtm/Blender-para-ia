"""Localhost-only command bridge running inside the Blender GUI process."""
from __future__ import annotations
import json, os, queue, secrets, socket, threading, time, traceback
from pathlib import Path
import bpy
from mathutils import Vector

HOST = "127.0.0.1"
PORT = int(os.environ.get("BLENDER_BRIDGE_PORT", "8765"))
TOKEN = os.environ.get("BLENDER_BRIDGE_TOKEN", "")
ARTIFACT_DIR = Path(os.environ.get("BLENDER_ARTIFACT_DIR", "/tmp/blender-artifacts"))
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
_REQUESTS = queue.Queue()
_STOP = threading.Event()

def _scene_info():
    scene = bpy.context.scene
    return {"scene": scene.name, "project_file": bpy.data.filepath or None,
        "active_camera": scene.camera.name if scene.camera else None,
        "object_count": len(scene.objects),
        "objects": [{"name": o.name, "type": o.type, "location": [round(float(v), 4) for v in o.location]} for o in scene.objects],
        "render": {"engine": scene.render.engine, "resolution_x": scene.render.resolution_x, "resolution_y": scene.render.resolution_y},
        "blender_version": bpy.app.version_string}

def _create_demo_scene():
    bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
    cube=bpy.context.object; cube.name="AI_Test_Cube"
    mat=bpy.data.materials.new("AI_Test_Material"); mat.diffuse_color=(0.12,0.42,0.85,1); cube.data.materials.append(mat)
    bpy.ops.object.camera_add(location=(6,-8,5)); cam=bpy.context.object; cam.name="AI_Test_Camera"
    cam.rotation_euler=(cube.location-cam.location).to_track_quat("-Z","Y").to_euler(); bpy.context.scene.camera=cam
    bpy.ops.object.light_add(type="AREA", location=(1,-4,6)); light=bpy.context.object
    light.name="AI_Test_Area_Light"; light.data.energy=850; light.data.shape="DISK"; light.data.size=5
    scene=bpy.context.scene; scene.render.engine="BLENDER_EEVEE_NEXT"
    scene.render.resolution_x=960; scene.render.resolution_y=540; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"; scene.render.filepath=str(ARTIFACT_DIR/"preview.png")
    return {"created":[cube.name,cam.name,light.name],"scene":scene.name}

def _vector(value, field):
    if not isinstance(value, (list, tuple)) or len(value)!=3:
        raise ValueError(field+" must be a 3-number array")
    vals=[float(x) for x in value]
    if not all(abs(x)<1e6 for x in vals): raise ValueError(field+" values out of range")
    return vals

def _object(request):
    name=request.get("name")
    if not isinstance(name,str) or not name.strip(): raise ValueError("name is required")
    obj=bpy.data.objects.get(name)
    if obj is None: raise ValueError("Object not found: "+name)
    return obj

def _execute(req):
    cmd=req.get("command")
    if cmd=="ping": return {"pong":True,"time":time.time(),"blender_version":bpy.app.version_string}
    if cmd=="scene-info": return _scene_info()
    if cmd=="create-demo": return _create_demo_scene()
    if cmd=="save":
        path=ARTIFACT_DIR/"session-project.blend"; bpy.ops.wm.save_as_mainfile(filepath=str(path)); return {"saved":str(path)}
    if cmd=="render":
        path=ARTIFACT_DIR/"preview.png"; bpy.context.scene.render.filepath=str(path)
        bpy.ops.render.render(write_still=True); return {"rendered":str(path),"engine":bpy.context.scene.render.engine}
    if cmd=="visual-test":
        _create_demo_scene(); scene=bpy.context.scene
        path=ARTIFACT_DIR/"visual-test.blend"; bpy.ops.wm.save_as_mainfile(filepath=str(path))
        render=ARTIFACT_DIR/"preview.png"; scene.render.filepath=str(render)
        try: bpy.ops.render.render(write_still=True); engine=scene.render.engine
        except Exception:
            scene.render.engine="BLENDER_WORKBENCH"; bpy.ops.render.render(write_still=True); engine=scene.render.engine
        return {"project":str(path),"render":str(render),"engine":engine,"scene":_scene_info()}
    if cmd=="add-primitive":
        kind=str(req.get("primitive","cube")).lower()
        if kind not in {"cube","uv_sphere","cylinder","cone","plane","torus"}: raise ValueError("Unsupported primitive")
        location=_vector(req.get("location",[0,0,0]),"location")
        if kind=="cube": bpy.ops.mesh.primitive_cube_add(size=float(req.get("size",2)), location=location)
        elif kind=="uv_sphere": bpy.ops.mesh.primitive_uv_sphere_add(radius=float(req.get("size",1)), location=location)
        elif kind=="cylinder": bpy.ops.mesh.primitive_cylinder_add(radius=float(req.get("size",1)), location=location)
        elif kind=="cone": bpy.ops.mesh.primitive_cone_add(radius1=float(req.get("size",1)), location=location)
        elif kind=="plane": bpy.ops.mesh.primitive_plane_add(size=float(req.get("size",2)), location=location)
        else: bpy.ops.mesh.primitive_torus_add(location=location)
        obj=bpy.context.object
        if req.get("name"): obj.name=str(req["name"])[:120]
        return {"created":obj.name,"type":obj.type,"location":list(obj.location)}
    if cmd in {"move-object","scale-object","rotate-object"}:
        obj=_object(req)
        field={"move-object":"location","scale-object":"scale","rotate-object":"rotation_euler"}[cmd]
        setattr(obj,field,_vector(req.get("value"),"value"))
        return {"updated":obj.name,field:list(getattr(obj,field))}
    if cmd=="delete-object":
        obj=_object(req); name=obj.name; bpy.data.objects.remove(obj,do_unlink=True); return {"deleted":name}
    raise ValueError("Unsupported command: %r"%cmd)

def _send(conn, data):
    conn.sendall((json.dumps(data,ensure_ascii=False)+"\n").encode("utf-8"))

def _server_loop():
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM); server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server.bind((HOST,PORT)); server.listen(8); server.settimeout(.5)
    while not _STOP.is_set():
        try: conn,_=server.accept()
        except socket.timeout: continue
        except OSError: break
        with conn:
            conn.settimeout(5)
            try:
                raw=conn.makefile("rb").readline(1024*1024); req=json.loads(raw.decode("utf-8"))
                supplied=str(req.pop("token",""))
                if not TOKEN or not secrets.compare_digest(supplied,TOKEN):
                    _send(conn,{"ok":False,"error":"unauthorized"}); continue
                dup=conn.dup(); dup.settimeout(300); _REQUESTS.put((req,dup))
            except Exception as exc:
                try: _send(conn,{"ok":False,"error":str(exc)})
                except OSError: pass
    server.close()

def _process_queue():
    while not _REQUESTS.empty():
        req,conn=_REQUESTS.get()
        try: _send(conn,{"ok":True,"result":_execute(req)})
        except Exception as exc: _send(conn,{"ok":False,"error":str(exc),"traceback":traceback.format_exc()})
        finally: conn.close()
    return .05 if not _STOP.is_set() else None

def start_bridge():
    if not TOKEN:
        print("[AI Bridge] ERROR: BLENDER_BRIDGE_TOKEN is required; bridge not started."); return
    threading.Thread(target=_server_loop,name="BlenderAIBridge",daemon=True).start()
    bpy.app.timers.register(_process_queue,first_interval=.1,persistent=True)
    print("[AI Bridge] Listening on %s:%s"%(HOST,PORT))
start_bridge()
