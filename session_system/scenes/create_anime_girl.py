import bpy
import math
import os
from mathutils import Vector

# Create a clean, self-contained stylized anime character scene in the live GUI.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name, color, metallic=0.0, roughness=0.55):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1.0)
    bs.inputs["Metallic"].default_value = metallic
    bs.inputs["Roughness"].default_value = roughness
    return m

skin = mat("Skin | warm porcelain", (0.96, 0.66, 0.52))
hair = mat("Hair | midnight violet", (0.105, 0.075, 0.24), 0.08)
hair_hi = mat("Hair highlights", (0.32, 0.22, 0.55), 0.12)
white = mat("Eye whites", (0.97, 0.97, 1.0))
iris = mat("Iris | ocean blue", (0.055, 0.36, 0.82), 0.12)
pupil = mat("Pupils", (0.012, 0.018, 0.05))
shine = mat("Eye sparkle", (1.0, 1.0, 1.0), 0.0, 0.2)
dress = mat("Dress | cherry blossom", (0.86, 0.20, 0.43))
dress_light = mat("Dress trim", (1.0, 0.68, 0.79))
sock = mat("Socks", (0.94, 0.91, 1.0))
shoe = mat("Shoes", (0.12, 0.10, 0.20))
ground = mat("Stage", (0.075, 0.09, 0.16))

def uv(name, loc, scale, material, seg=32, rings=20):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.shade_smooth()
    if material: o.data.materials.append(material)
    return o

def cylinder(name, loc, radius, depth, material, vertices=48, bevel=0.06):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    if material: o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new("Soft rounded edges","BEVEL")
        mod.width=bevel
        mod.segments=3
        o.modifiers.new("Weighted corner normals","WEIGHTED_NORMAL")
    return o

def cone(name, loc, r1, r2, depth, material):
    bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=r1, radius2=r2, depth=depth, location=loc)
    o=bpy.context.object
    o.name=name
    o.data.materials.append(material)
    bevel=o.modifiers.new("Soft hem","BEVEL"); bevel.width=0.035; bevel.segments=3
    o.modifiers.new("Weighted normals","WEIGHTED_NORMAL")
    return o

# Feet, legs and socks
for side, x in (("L",-0.22),("R",0.22)):
    uv("Shoe "+side,(x,-0.07,0.16),(0.17,0.29,0.13),shoe)
    cylinder("Sock "+side,(x,0,0.43),0.105,0.43,sock,bevel=0.035)
    uv("Knee "+side,(x,0,0.64),(0.105,0.11,0.12),skin)
    # legs taper visually with two overlapping capsules
    uv("Leg "+side,(x,0,0.88),(0.105,0.115,0.34),skin)

# Flared skirt and torso
cone("Pleated skirt",(0,0,1.38),0.49,0.25,0.43,dress)
cylinder("Waist ribbon",(0,0,1.62),0.265,0.09,dress_light,bevel=0.025)
uv("Torso",(0,0,1.91),(0.29,0.19,0.39),dress)
uv("Collar",(0,-0.01,2.18),(0.22,0.18,0.11),dress_light)

# Arms, slightly away from the body
for side, x, rot in (("L",-0.39,-0.22),("R",0.39,0.22)):
    arm=uv("Upper arm "+side,(x,-0.005,1.98),(0.105,0.12,0.31),dress)
    arm.rotation_euler[1]=rot
    fore=uv("Forearm "+side,(x*1.18,-0.035,1.68),(0.085,0.095,0.25),skin)
    fore.rotation_euler[1]=rot*0.6
    uv("Hand "+side,(x*1.18,-0.05,1.46),(0.105,0.095,0.12),skin)

# Neck and oversized anime head
cylinder("Neck",(0,0,2.29),0.105,0.24,skin,bevel=0.025)
head=uv("Head",(0,-0.005,2.76),(0.52,0.43,0.61),skin,48,32)

# Hair cap and long side locks
cap=uv("Hair cap",(0,0.055,3.00),(0.545,0.455,0.48),hair,48,32)
for side,x in (("L",-0.43),("R",0.43)):
    lock=uv("Long hair lock "+side,(x,0.075,2.55),(0.16,0.19,0.64),hair)
    lock.rotation_euler[1]=(-0.10 if x<0 else 0.10)
    uv("Hair tip "+side,(x*1.03,0.07,2.05),(0.145,0.17,0.19),hair)
# Front bangs as soft tapered clumps
for i,x in enumerate((-0.34,-0.17,0.0,0.17,0.34)):
    y=-0.365
    z=3.02 - 0.08*(1-abs(x)/0.34)
    bang=uv("Fringe %02d"%i,(x,y,z),(0.17,0.12,0.28 if i%2==0 else 0.23),hair)
    bang.rotation_euler[1]=x*0.45
# Hair ornaments
uv("Pink hair clip",(-0.37,-0.39,2.93),(0.12,0.035,0.045),dress_light)

# Big expressive eyes facing camera (-Y)
for side,x in (("L",-0.205),("R",0.205)):
    uv("Eye white "+side,(x,-0.399,2.79),(0.145,0.075,0.205),white)
    uv("Blue iris "+side,(x,-0.465,2.78),(0.092,0.043,0.145),iris)
    uv("Pupil "+side,(x,-0.501,2.77),(0.048,0.025,0.105),pupil)
    uv("Eye sparkle "+side,(x-0.032,-0.526,2.84),(0.028,0.015,0.04),shine,20,12)
    # upper lash line
    lash=uv("Upper lash "+side,(x,-0.43,2.965),(0.15,0.035,0.035),hair,24,12)
    lash.rotation_euler[1]=(-0.08 if x<0 else 0.08)

# Tiny nose and smiling mouth
uv("Nose",(0,-0.439,2.65),(0.035,0.028,0.045),skin,20,12)
smile=uv("Smile",(0,-0.423,2.54),(0.075,0.018,0.025),dress,24,12)

# Bow at the back/side of hair, plus small dress buttons
for side,x in (("L",-0.13),("R",0.13)):
    uv("Bow loop "+side,(x,0.12,3.18),(0.16,0.10,0.095),dress_light)
uv("Bow knot",(0,0.09,3.18),(0.075,0.09,0.075),dress)
for z in (2.05,1.94,1.83):
    uv("Dress button",(0,-0.19,z),(0.025,0.018,0.025),dress_light,16,8)

# Stage and pastel backdrop
cylinder("Display plinth",(0,0,-0.08),1.15,0.16,mat("Plinth",(0.19,0.21,0.34)),vertices=96,bevel=0.07)
bpy.ops.mesh.primitive_plane_add(size=200, location=(0,0,-0.17))
floor=bpy.context.object; floor.name="Backdrop floor"; floor.data.materials.append(ground)

# Camera and studio lights
bpy.ops.object.camera_add(location=(4.5,-8.5,3.35))
cam=bpy.context.object; cam.name="Portrait camera"
target=Vector((0,-0.02,1.65))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'; cam.data.ortho_scale=4.35
bpy.context.scene.camera=cam

def area(name, loc, power, color, size):
    bpy.ops.object.light_add(type='AREA', location=loc)
    l=bpy.context.object; l.name=name; l.data.energy=power; l.data.color=color; l.data.shape='DISK'; l.data.size=size
    l.rotation_euler=(Vector((0,0,1.7))-l.location).to_track_quat('-Z','Y').to_euler()
area("Key softbox",(4,-5,6),650,(1.0,0.78,0.86),4.0)
area("Fill softbox",(-4,-3,3.5),420,(0.55,0.72,1.0),3.5)
area("Hair rim",(0,3,5),800,(0.72,0.55,1.0),3.0)

scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE_NEXT'
scene.eevee.taa_render_samples=32
scene.render.resolution_x=720
scene.render.resolution_y=720
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.world.color=(0.12,0.12,0.12)
scene.view_settings.view_transform='AgX'
scene.render.image_settings.color_mode='RGBA'
scene.camera.data.lens=50

# Animate a gentle greeting: right forearm/hand wave and subtle head tilt.
wave=bpy.data.objects.get("Forearm R")
hand=bpy.data.objects.get("Hand R")
head_obj=bpy.data.objects.get("Head")
scene.frame_start=1
scene.frame_end=120
scene.render.fps=24
for frame, angle in ((1,0.0),(24,0.0),(42,-0.7),(60,0.45),(78,-0.65),(96,0.25),(120,0.0)):
    scene.frame_set(frame)
    wave.rotation_euler[1]=angle
    wave.keyframe_insert(data_path="rotation_euler",frame=frame)
    hand.rotation_euler[1]=angle*0.6
    hand.keyframe_insert(data_path="rotation_euler",frame=frame)
for frame, angle in ((1,0.0),(60,0.045),(120,0.0)):
    scene.frame_set(frame)
    head_obj.rotation_euler[2]=angle
    head_obj.keyframe_insert(data_path="rotation_euler",frame=frame)
if scene.animation_data and scene.animation_data.action:
    for fc in scene.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation='BEZIER'

# Save native editable project, render a still preview and H.264 MP4.
out=os.environ.get("BLENDER_ARTIFACT_DIR", "/tmp")
os.makedirs(out,exist_ok=True)
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out,"anime_girl.blend"))
scene.render.filepath=os.path.join(out,"anime_girl_preview.png")
bpy.ops.render.render(write_still=True)
scene.render.image_settings.file_format='FFMPEG'
scene.render.ffmpeg.format='MPEG4'
scene.render.ffmpeg.codec='H264'
scene.render.ffmpeg.constant_rate_factor='MEDIUM'
scene.render.filepath=os.path.join(out,"anime_girl_animation")
bpy.ops.render.render(animation=True)
print("ANIME_GIRL_SCENE_COMPLETE", len(bpy.data.objects), out)
