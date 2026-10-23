"""Build an editable, keyframed OSS concept in Blender 5.2.

Run with Blender, not system Python. This is a visual explanation of intended
motion, not a physics model, recovered firmware behavior, or hardware test.
"""
import argparse
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
FPS = 24
CYCLE = 120
END = CYCLE * 3
LENGTH = 0.60
WIDTH = 0.11
SURFACE_Z = 0.105
BLOCK_SIZE = 0.023


def material(name, color, metallic=0.0, roughness=0.4, glow=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    if glow:
        shader.inputs['Emission Color'].default_value = (*color, 1)
        shader.inputs['Emission Strength'].default_value = glow
    return mat


def finish(obj, name, mat, bevel=0):
    obj.name = name
    if mat:
        obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Manufactured edge radius', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return obj


def box(name, location, size, mat, bevel=0.002, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    finish(obj, name, mat, bevel)
    if parent:
        obj.parent = parent
    return obj


def cylinder(name, location, radius, depth, mat, rotation=(0, 0, 0), parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=40, radius=radius, depth=depth,
                                      location=location, rotation=rotation)
    obj = finish(bpy.context.object, name, mat, 0.0008)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    if parent:
        obj.parent = parent
    return obj


def text(name, body, location, size, mat, rotation=(0, 0, 0), parent=None, align='LEFT'):
    curve = bpy.data.curves.new(name, 'FONT')
    curve.body = body
    curve.size = size
    curve.align_x = align
    curve.extrude = 0.00003
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = rotation
    curve.materials.append(mat)
    if parent:
        obj.parent = parent
    return obj


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


def visible_between(obj, start, stop):
    for frame, hidden in [(1, start > 1), (max(1, start - 1), True),
                          (start, False), (stop, False), (stop + 1, True)]:
        obj.hide_render = hidden
        obj.hide_viewport = hidden
        obj.keyframe_insert('hide_render', frame=frame)
        obj.keyframe_insert('hide_viewport', frame=frame)


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = 'OSS | intended sorting sequence'
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.length_unit = 'METERS'
    scene['simulation_type'] = 'Keyframed kinematic concept; no rigid-body or control simulation'
    scene['dimensions'] = 'Nominal 0.60 m belt length; proportions from source scene, not measured fabrication dimensions'
    scene['routing'] = 'Illustrative A/B/C routes; colors are not a recovered trained-label mapping'
    scene['timing'] = 'Three 5-second presentation cycles; not firmware timing'
    scene.render.engine = 'BLENDER_EEVEE'
    scene.eevee.taa_render_samples = 24
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = 1, END
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = False
    scene.render.filepath = '//renders/frame_'
    scene.render.use_file_extension = True
    scene.world = bpy.data.worlds.new('Soft studio environment')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.12, 0.16, 0.22, 1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.35
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = -0.65

    aluminum = material('Brushed aluminum', (0.50, 0.57, 0.64), 0.75, 0.3)
    dark = material('Graphite powder coat', (0.025, 0.040, 0.060), 0.35, 0.33)
    wood = material('Timber frame | texture-free', (0.27, 0.12, 0.045), 0.0, 0.55)
    belt = material('Blue prototype belt', (0.016, 0.18, 0.48), 0.05, 0.5)
    rubber = material('Roller rubber', (0.027, 0.035, 0.043), 0.0, 0.7)
    pale = material('Warm white polymer', (0.78, 0.83, 0.87), 0.05, 0.4)
    floor = material('Studio floor', (0.045, 0.065, 0.092), 0.1, 0.6)
    cyan = material('Cyan status', (0.025, 0.66, 0.85), glow=1.8)
    white_text = material('White annotation', (0.82, 0.9, 1), glow=1)
    muted = material('Muted annotation', (0.32, 0.47, 0.62), glow=0.8)
    colors = [(0.80, 0.065, 0.035), (0.05, 0.63, 0.25), (0.035, 0.25, 0.90)]
    block_mats = [material('Object ' + label, color, 0.05, 0.25)
                  for label, color in zip('ABC', colors)]

    # Local procedural belt texture: no external images or drivers.
    nodes = belt.node_tree.nodes
    links = belt.node_tree.links
    coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    mapping.name = 'Animated belt travel'
    wave = nodes.new('ShaderNodeTexWave')
    wave.bands_direction = 'X'
    wave.inputs['Scale'].default_value = 8
    wave.inputs['Distortion'].default_value = 0
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.80
    ramp.color_ramp.elements[0].color = (0.005, 0.065, 0.27, 1)
    ramp.color_ramp.elements[1].position = 0.92
    ramp.color_ramp.elements[1].color = (0.009, 0.16, 0.48, 1)
    links.new(coord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], wave.inputs['Vector'])
    links.new(wave.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], nodes.get('Principled BSDF').inputs['Base Color'])

    box('Studio plinth', (0.08, 0, -0.025), (1.15, 0.66, 0.03), floor, 0.015)
    # Uprights and rails preserve the original model's approximate 0.6 m layout.
    for x in [-0.245, 0.245]:
        for y in [-0.070, 0.070]:
            box(f'Frame leg {x} {y}', (x, y, 0.033), (0.016, 0.016, 0.085), aluminum)
            box(f'Rubber foot {x} {y}', (x, y, -0.005), (0.027, 0.027, 0.008), rubber)
    for side in [-1, 1]:
        y = side * 0.066
        box(f'Timber side rail {side}', (0, y, 0.079), (0.625, 0.014, 0.055), wood)
        box(f'Rail cap {side}', (0, y, 0.108), (0.625, 0.014, 0.003), aluminum, 0.0008)
        for x in [-0.28, -0.20, 0.20, 0.28]:
            cylinder(f'Rail fastener {side} {x}', (x, y, 0.111), 0.0028, 0.002, dark)
    box('Belt | top run', (0, 0, SURFACE_Z - 0.003), (0.560, WIDTH, 0.006), belt)
    box('Belt | return run', (0, 0, 0.063), (0.560, WIDTH, 0.005), rubber)
    rollers = []
    for x, label in [(-0.28, 'Idler'), (0.28, 'Drive')]:
        rollers.append(cylinder(label + ' roller', (x, 0, 0.084), 0.022, WIDTH, rubber,
                                (math.pi / 2, 0, 0)))
        for y in [-0.076, 0.076]:
            cylinder(f'{label} bearing {y}', (x, y, 0.084), 0.013, 0.013,
                     aluminum, (math.pi / 2, 0, 0))
    box('NEMA17 stepper body', (0.28, -0.110, 0.084), (0.043, 0.050, 0.043), dark)
    box('Stepper end plate', (0.28, -0.139, 0.084), (0.043, 0.006, 0.043), aluminum)
    for dx in [-0.015, 0.015]:
        for dz in [-0.015, 0.015]:
            cylinder('Motor bolt', (0.28 + dx, -0.143, 0.084 + dz), 0.0023, 0.003,
                     dark, (math.pi / 2, 0, 0))

    # Camera station and two conceptual digital sensors.
    for y in [-0.089, 0.089]:
        box('Camera gantry upright', (-0.115, y, 0.188), (0.012, 0.012, 0.196), aluminum)
    box('Camera gantry crossbar', (-0.115, 0, 0.283), (0.020, 0.190, 0.012), aluminum)
    box('ESP camera enclosure', (-0.115, 0, 0.263), (0.047, 0.054, 0.026), dark)
    cylinder('Downward camera lens', (-0.115, 0, 0.244), 0.0105, 0.015, aluminum)
    cylinder('Lens glass', (-0.115, 0, 0.2355), 0.0078, 0.002, cyan)
    for x, name in [(-0.255, 'Start sensor'), (-0.115, 'Scan sensor')]:
        box(name + ' housing', (x, -0.061, 0.121), (0.023, 0.010, 0.014), dark)
        cylinder(name + ' eye', (x, -0.054, 0.121), 0.0037, 0.004,
                 cyan, (math.pi / 2, 0, 0))
    for y in [-0.040, 0.040]:
        box('Scan-position marker', (-0.115, y, 0.109), (0.003, 0.022, 0.001), cyan, 0)

    # A small electronics tray communicates the two-board architecture.
    box('Controller mounting tray', (-0.03, -0.153, 0.038), (0.115, 0.082, 0.006), aluminum)
    pcb = material('Controller PCB', (0.025, 0.18, 0.15), 0.15, 0.4)
    box('Uno controller concept', (-0.025, -0.15, 0.047), (0.070, 0.050, 0.004), pcb, 0.001)
    box('USB connector', (-0.067, -0.15, 0.054), (0.018, 0.014, 0.014), aluminum, 0.001)
    box('Controller processor', (-0.019, -0.15, 0.052), (0.027, 0.011, 0.006), dark, 0.0005)
    for y in [-0.174, -0.126]:
        box('Header socket row', (-0.023, y, 0.054), (0.053, 0.004, 0.009), dark, 0.0004)
    cylinder('Controller power indicator', (0.004, -0.163, 0.054), 0.0018, 0.002, cyan)

    # Three-bin fan-out is a visualization choice, not recovered fabrication data.
    bin_ys = [-0.128, 0, 0.128]
    for label, y, accent in zip('ABC', bin_ys, block_mats):
        box('Bin ' + label + ' floor', (0.505, y, 0.014), (0.135, 0.110, 0.006), pale)
        for side in [-1, 1]:
            box('Bin ' + label + ' side', (0.505, y + side * 0.055, 0.041),
                (0.139, 0.005, 0.060), pale)
        box('Bin ' + label + ' end', (0.574, y, 0.041), (0.005, 0.11, 0.06), pale)
        box('Bin ' + label + ' accent', (0.574, y, 0.074), (0.007, 0.105, 0.005), accent)
        text('Bin ' + label + ' top label', label, (0.545, y, 0.075), 0.027,
             dark, align='CENTER')

    box('SG90 servo concept', (0.277, 0, 0.072), (0.030, 0.025, 0.035),
        material('Servo blue', (0.025, 0.09, 0.32), 0.05, 0.3))
    pivot = bpy.data.objects.new('Servo routing pivot | animated', None)
    bpy.context.collection.objects.link(pivot)
    pivot.location = (0.277, 0, 0.112)
    cylinder('Servo pivot hub', (0, 0, 0), 0.008, 0.014, aluminum, parent=pivot)
    box('Rotating guide floor', (0.093, 0, -0.011), (0.190, 0.050, 0.004), aluminum,
        0.001, parent=pivot)
    for side in [-1, 1]:
        box('Rotating guide side', (0.093, side * 0.026, 0.001), (0.190, 0.003, 0.026),
            dark, 0.001, parent=pivot)

    # Three presentation cycles: stop at camera, set guide, dispatch, reset.
    for index, (label, y, mat) in enumerate(zip('ABC', bin_ys, block_mats)):
        start = 1 + CYCLE * index
        obj = box('Object ' + label + ' | animated', (-0.273, 0, SURFACE_Z + BLOCK_SIZE / 2),
                  (BLOCK_SIZE,) * 3, mat, 0.002)
        obj['route'] = label
        obj['meaning'] = 'Illustrative color and bin choice, not a trained-label mapping'
        visible_between(obj, start, END)
        angle = math.atan2(y, 0.505 - 0.277)
        positions = [(0, -0.273, 0, 0.117), (9, -0.273, 0, 0.117),
                     (34, -0.115, 0, 0.117), (51, -0.115, 0, 0.117),
                     (77, 0.277, 0, 0.117), (97, 0.440, y * 0.74, 0.116),
                     (109, 0.505, y, 0.029), (119, 0.505, y, 0.029)]
        for offset, x, yy, z in positions:
            obj.location = (x, yy, z)
            obj.rotation_euler[2] = angle if offset >= 97 else 0
            obj.keyframe_insert('location', frame=start + offset)
            obj.keyframe_insert('rotation_euler', frame=start + offset)
        for offset, yaw in [(0, 0), (34, 0), (51, angle), (109, angle), (119, 0)]:
            pivot.rotation_euler[2] = yaw
            pivot.keyframe_insert('rotation_euler', frame=start + offset)
        for offset, title in [(0, '01  LOAD OBJECT'), (10, '02  MOVE TO CAMERA'),
                              (35, '03  SCAN / PAUSE'), (52, '04  ROUTE TO BIN ' + label),
                              (110, '05  RESET')]:
            stop = start + {0: 9, 10: 34, 35: 51, 52: 109, 110: 119}[offset]
            scene.timeline_markers.new(title + ' | ' + label, frame=start + offset)

    travel = 0
    for frame in range(1, END + 1):
        phase = (frame - 1) % CYCLE
        if 9 <= phase < 34 or 51 <= phase < 98:
            travel += 0.007
        mapping.inputs['Location'].default_value[0] = -travel
        mapping.inputs['Location'].keyframe_insert('default_value', frame=frame)
        for roller in rollers:
            roller.rotation_euler[1] = travel * 12
            roller.keyframe_insert('rotation_euler', frame=frame)

    # Fixed orthographic camera keeps mechanism and destinations legible.
    bpy.ops.object.camera_add(location=(1.03, -1.20, 0.96))
    camera = bpy.context.object
    camera.name = 'Presentation camera'
    aim(camera, (0.10, 0, 0.10))
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 1.19
    camera.data.lens = 45
    camera.data.clip_start = 0.01
    camera.data.clip_end = 30
    scene.camera = camera
    text('Film title', 'OBJECT SORTING SYSTEM', (-0.55, 0.292, -0.45), 0.026,
         white_text, parent=camera)
    text('Persistent simulation disclosure', 'KINEMATIC CONCEPT  /  NOT A HARDWARE TEST',
         (-0.55, 0.261, -0.45), 0.012, cyan, parent=camera)
    text('Assumption disclosure', 'Illustrative A/B/C routes  |  Nominal dimensions  |  Timing for presentation',
         (-0.55, -0.311, -0.45), 0.011, muted, parent=camera)
    for index, label in enumerate('ABC'):
        start = 1 + CYCLE * index
        phases = [(0, 9, '01  LOAD OBJECT ' + label), (10, 34, '02  MOVE TO CAMERA'),
                  (35, 51, '03  SCAN / PAUSE'), (52, 109, '04  ROUTE TO BIN ' + label),
                  (110, 119, '05  RESET FOR NEXT OBJECT')]
        for lo, hi, title in phases:
            obj = text('Phase ' + label + ' ' + str(lo), title, (-0.55, -0.271, -0.45),
                       0.019, white_text, parent=camera)
            visible_between(obj, start + lo, start + hi)
    for name, location, energy, size in [
        ('Large key', (0.1, -0.45, 1.2), 70, 0.9),
        ('Soft fill', (0.3, 0.75, 0.8), 55, 0.7),
        ('Rim', (-0.7, 0.1, 0.7), 35, 0.5)]:
        bpy.ops.object.light_add(type='AREA', location=location)
        light = bpy.context.object
        light.name = name
        light.data.energy = energy
        light.data.shape = 'DISK'
        light.data.size = size
        aim(light, (0.05, 0, 0.05))

    # Make the saved file immediately useful when opened interactively.
    scene.frame_set(90)
    bpy.ops.object.select_all(action='DESELECT')
    pivot.select_set(True)
    bpy.context.view_layer.objects.active = pivot
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.region_3d.view_perspective = 'CAMERA'
                area.spaces.active.shading.type = 'MATERIAL'
    note = bpy.data.texts.new('READ ME | animation assumptions')
    note.write('OSS visualization\n\nPress Space to play frames 1-360 at 24 fps.\n'
               'Three 5-second illustrative cycles, not firmware timing.\n'
               'A/B/C colors and bins are conceptual, not a trained model mapping.\n'
               'Geometry uses nominal proportions; no fabrication fit is validated.\n'
               'All movement is keyframed. No physics, sensor, or inference solver is run.\n'
               'Original scene remains alongside this generated revision.\n')
    return scene


def main():
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'hardware/mechanical/oss_simulation.blend')
    parser.add_argument('--still', type=Path)
    parser.add_argument('--frames-dir', type=Path)
    parser.add_argument('--preview-frame', type=int, default=90)
    opts = parser.parse_args(args)
    scene = build()
    opts.output.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(opts.output.resolve()))
    print('OSS_BUILD', json.dumps({'objects': len(scene.objects), 'frames': END,
                                  'fps': FPS, 'blend': opts.output.as_posix()}), flush=True)
    if opts.still:
        opts.still.parent.mkdir(parents=True, exist_ok=True)
        scene.frame_set(opts.preview_frame)
        scene.render.filepath = str(opts.still.resolve())
        bpy.ops.render.render(write_still=True)
    if opts.frames_dir:
        opts.frames_dir.mkdir(parents=True, exist_ok=True)
        scene.render.filepath = str(opts.frames_dir.resolve() / 'frame_')
        bpy.ops.render.render(animation=True)


if __name__ == '__main__':
    main()
