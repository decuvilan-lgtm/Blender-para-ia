"""Validate a .blend file in the independent headless environment.

Run after the project path has been opened by Blender:
  ./run_headless.sh /path/to/project.blend --python scripts/validate_project.py
"""
from __future__ import annotations

import bpy
import sys
from pathlib import Path

path = Path(bpy.data.filepath)
if not path.is_file():
    raise SystemExit("FAIL: Blender has no saved project path.")

objects = list(bpy.context.scene.objects)
camera = bpy.context.scene.camera
print(f"PROJECT={path}")
print(f"BLENDER={bpy.app.version_string}")
print(f"SCENE={bpy.context.scene.name}")
print(f"OBJECTS={len(objects)}")
print(f"CAMERA={camera.name if camera else 'NONE'}")
print(f"RENDER={bpy.context.scene.render.resolution_x}x{bpy.context.scene.render.resolution_y}")

if len(objects) < 5:
    raise SystemExit(f"FAIL: expected at least 5 scene objects, found {len(objects)}.")
if camera is None:
    raise SystemExit("FAIL: scene has no active camera.")

required = {"LAB_Floor", "A_Test_Cube", "A_Test_Sphere", "A_Test_Torus", "A_Environment_Label"}
missing = required - {obj.name for obj in objects}
if missing:
    raise SystemExit("FAIL: missing validation scene objects: " + ", ".join(sorted(missing)))

print("PASS: validation scene loaded and contains the expected objects.")
