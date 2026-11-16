"""Generate a clearly visible validation scene in the independent headless lab.

Run with:
  ./run_headless.sh --python scripts/create_validation_scene.py -- /path/to/output.blend
"""
from __future__ import annotations

import sys
from pathlib import Path

import bpy
from mathutils import Vector


def material(name: str, color: tuple[float, float, float, float], metallic: float = 0.0, roughness: float = 0.45):
    mat = bpy.data.materials.new(name=name)
    mat.diffuse_color = color
    mat.use_nodes = True
    principled = mat.node_tree.nodes.get("Principled BSDF")
    if principled:
        principled.inputs["Base Color"].default_value = color
        principled.inputs["Metallic"].default_value = metallic
        principled.inputs["Roughness"].default_value = roughness
    return mat


def point_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def main(output_path: Path):
    output_path = output_path.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False

    floor_mat = material("Lab_Floor", (0.055, 0.075, 0.11, 1.0), roughness=0.8)
    blue_mat = material("Test_Cube_Blue", (0.035, 0.28, 0.85, 1.0), metallic=0.15)
    orange_mat = material("Test_Sphere_Orange", (1.0, 0.22, 0.035, 1.0), metallic=0.05)
    green_mat = material("Test_Torus_Green", (0.08, 0.72, 0.32, 1.0), metallic=0.25)

    bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 0, 0))
    floor = bpy.context.object
    floor.name = "LAB_Floor"
    floor.data.materials.append(floor_mat)

    bpy.ops.mesh.primitive_cube_add(size=2, location=(-2.1, 0, 1))
    cube = bpy.context.object
    cube.name = "A_Test_Cube"
    cube.data.materials.append(blue_mat)
    bevel = cube.modifiers.new("Soft_Edges", "BEVEL")
    bevel.width = 0.12
    bevel.segments = 4
    cube.modifiers.new("Weighted_Normals", "WEIGHTED_NORMAL")

    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=1, location=(0, 0, 1))
    sphere = bpy.context.object
    sphere.name = "A_Test_Sphere"
    sphere.data.materials.append(orange_mat)
    bpy.ops.object.shade_smooth()

    bpy.ops.mesh.primitive_torus_add(major_radius=0.8, minor_radius=0.22, major_segments=48, minor_segments=16, location=(2.2, 0, 1.15), rotation=(0.35, 0.2, 0.25))
    torus = bpy.context.object
    torus.name = "A_Test_Torus"
    torus.data.materials.append(green_mat)
    bpy.ops.object.shade_smooth()

    bpy.ops.object.text_add(location=(-2.65, 2.0, 0.025), rotation=(0, 0, 0))
    label = bpy.context.object
    label.name = "A_Environment_Label"
    label.data.body = "EXPERIMENTAL LAB  /  A -> B"
    label.data.size = 0.42
    label.data.extrude = 0.004
    label.data.materials.append(material("Label_White", (0.88, 0.93, 1.0, 1.0)))

    bpy.ops.object.camera_add(location=(7.5, -11, 7.2))
    camera = bpy.context.object
    camera.name = "A_Validation_Camera"
    camera.data.lens = 52
    point_at(camera, (0, 0.3, 0.8))
    scene.camera = camera

    bpy.ops.object.light_add(type="AREA", location=(1, -4, 7))
    key = bpy.context.object
    key.name = "A_Key_Light"
    key.data.energy = 1250
    key.data.shape = "DISK"
    key.data.size = 6
    point_at(key, (0, 0, 0.5))

    bpy.ops.object.light_add(type="AREA", location=(-5, 2, 4))
    fill = bpy.context.object
    fill.name = "A_Fill_Light"
    fill.data.energy = 700
    fill.data.color = (0.35, 0.55, 1.0)
    fill.data.size = 5
    point_at(fill, (0, 0, 1))

    scene.world.color = (0.12, 0.12, 0.12)
    scene.render.filepath = str(output_path.with_suffix(".png"))
    scene.camera.data.dof.use_dof = False

    # Store a useful camera/material preview when the project opens.
    for obj in scene.objects:
        obj.select_set(False)
    cube.select_set(True)
    bpy.context.view_layer.objects.active = cube

    bpy.ops.wm.save_as_mainfile(filepath=str(output_path))
    bpy.ops.render.render(write_still=True)
    print(f"VALIDATION_SCENE_SAVED={output_path}")
    print(f"VALIDATION_RENDER_SAVED={scene.render.filepath}")
    print(f"OBJECT_COUNT={len(scene.objects)}")


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) != 1:
        raise SystemExit("Usage: create_validation_scene.py -- /absolute/path/output.blend")
    main(Path(args[0]))
