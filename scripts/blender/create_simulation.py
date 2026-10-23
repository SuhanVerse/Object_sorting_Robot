"""Complete the recovered OSS assembly using source geometry and downloaded CAD.

Blender 5.2.2. This is a keyframed reconstruction of the user's drawing,
not a rigid-body or firmware simulation. Dimensions not measured on hardware
remain nominal. The original scene is read-only and remains alongside this file.
"""
import argparse
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[2]
FPS = 24
CYCLE = 144
END = CYCLE * 3
BELT_TOP = 0.021085
CENTER_Y = 0.0003957
PIVOT = Vector((0.060, -0.07464294, 0.03429335))
BLOCK = 0.018
ROUTES = {'A': (0.18, -0.115, -0.008),
          'B': (0.18, 0.115, -0.008),
          'C': (0.375, CENTER_Y, -0.008)}


def collection(name):
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


def move_to(obj, col):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    col.objects.link(obj)
    return obj


def material(name, rgb, roughness=0.6, metallic=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*rgb, 1)
    mat.use_nodes = True
    node = mat.node_tree.nodes.get('Principled BSDF')
    node.inputs['Base Color'].default_value = (*rgb, 1)
    node.inputs['Roughness'].default_value = roughness
    node.inputs['Metallic'].default_value = metallic
    return mat


def box(name, location, size, mat, col, bevel=0.0004):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = move_to(bpy.context.object, col)
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        modifier = obj.modifiers.new('Small physical edge radius', 'BEVEL')
        modifier.width, modifier.segments = bevel, 2
        obj.modifiers.new('Corner normals', 'WEIGHTED_NORMAL')
    return obj


def cylinder(name, location, radius, depth, mat, col, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth,
                                      location=location, rotation=rotation)
    obj = move_to(bpy.context.object, col)
    obj.name = name
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj


def text(name, body, location, size, mat, col, rotation=(0, 0, 0)):
    curve = bpy.data.curves.new(name, 'FONT')
    curve.body, curve.size = body, size
    curve.align_x = 'CENTER'
    curve.extrude = 0.00001
    curve.materials.append(mat)
    obj = bpy.data.objects.new(name, curve)
    col.objects.link(obj)
    obj.location, obj.rotation_euler = location, rotation
    return obj


def wire(name, points, radius, mat, col):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 12
    curve.bevel_depth = radius
    curve.bevel_resolution = 2
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    for node, point in zip(spline.bezier_points, points):
        node.co = point
        node.handle_left_type = node.handle_right_type = 'AUTO'
    obj = bpy.data.objects.new(name, curve)
    col.objects.link(obj)
    curve.materials.append(mat)
    return obj


def bounds(obj):
    vertices = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    return [min(v[i] for v in vertices) for i in range(3)], \
           [max(v[i] for v in vertices) for i in range(3)]


def copy_source(source_file, destination):
    """Bake evaluated meshes in world coordinates, preserving source geometry/materials."""
    temporary = collection('TEMP source dependency graph')
    with bpy.data.libraries.load(str(source_file), link=False) as (available, requested):
        requested.objects = available.objects
    original = [obj for obj in requested.objects if obj]
    for obj in original:
        temporary.objects.link(obj)
    bpy.context.view_layer.update()
    graph = bpy.context.evaluated_depsgraph_get()
    names = {'wood_body': 'Source timber side rails', 'Plane.001': 'Source oval belt',
             'Cylinder': 'Source roller axles', 'bearings': 'Source bearings',
             'pvc_outer': 'Source PVC bearing sleeve', 'pvc_outer.001': 'Source idler roller',
             'pvc_outer.004': 'Source drive roller', 'Plane.002': 'Source camera bridge',
             'NEMA 17 17HD40': 'Source NEMA17 motor', 'Cube': 'Source workbench'}
    drive = {'Plane.001', 'Cylinder', 'bearings', 'pvc_outer', 'pvc_outer.001',
             'pvc_outer.004', 'NEMA 17 17HD40'}
    retained = {}
    for obj in original:
        is_servo = obj.type == 'MESH' and any(mat and mat.name in {'Material.020', 'Material.021'}
                                             for mat in obj.data.materials)
        if obj.name not in names and not is_servo:
            continue
        evaluated = obj.evaluated_get(graph)
        mesh = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True,
                                              depsgraph=graph)
        mesh.transform(obj.matrix_world)
        name = names.get(obj.name, 'Source SG90 ' + ('shaft and detail' if
                     any(mat and mat.name == 'Material.021' for mat in obj.data.materials) else 'body'))
        out = bpy.data.objects.new(name, mesh)
        destination.objects.link(out)
        out['source_scene'] = 'conveyer_belt.blend'
        out['source_object'] = obj.name
        out['retained_geometry'] = True
        if obj.name in drive:
            for v in mesh.vertices:
                v.co.z += 0.004
            out['completion_change'] = 'Belt and complete drive group raised together by 4 mm to clear rail lips'
        if obj.name == 'Plane.001':
            low, high = bounds(out)
            width, center = high[1] - low[1], (high[1] + low[1]) / 2
            for v in mesh.vertices:
                v.co.y = (v.co.y - center) * 0.088 / width + CENTER_Y
            out['completion_change'] += '; source loop widened to 88 mm inside measured 90 mm rail gap'
        if is_servo:
            delta = PIVOT - Vector((0.12357648, -0.07464294, 0.03429335))
            for v in mesh.vertices:
                v.co += delta
            out['completion_change'] = 'Full evaluated source servo geometry translated to the side-mounted sweep station'
        retained[obj.name] = out
    for obj in original:
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(temporary)
    return retained


def asset_instance(name, library_path, collection_name, target, location, rotation=(0, 0, 0)):
    with bpy.data.libraries.load(str(library_path), link=False) as (available, requested):
        requested.collections = [collection_name]
    asset = requested.collections[0]
    obj = bpy.data.objects.new(name, None)
    obj.instance_type = 'COLLECTION'
    obj.instance_collection = asset
    obj.location, obj.rotation_euler = location, rotation
    obj['asset_library'] = library_path.relative_to(ROOT).as_posix()
    target.objects.link(obj)
    return obj


def visibility(obj, start):
    for frame, hidden in [(1, start > 1), (max(1, start - 1), True), (start, False)]:
        obj.hide_render = obj.hide_viewport = hidden
        obj.keyframe_insert('hide_render', frame=frame)
        obj.keyframe_insert('hide_viewport', frame=frame)


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = 'OSS | reconstructed side-bin assembly'
    scene.unit_settings.system = 'METRIC'
    scene['reference'] = 'Original conveyor scene + real prototype photograph + user Excalidraw concept'
    scene['simulation_type'] = 'Keyframed mechanical illustration; no physics, firmware or inference solver'
    scene['bin_layout'] = 'A negative Y side; B positive Y side; C positive X end'
    scene['scale'] = 'Source scene nominal metres; IR scale inferred; hardware fit not independently measured'
    source_col = collection('01 | Recovered conveyor geometry')
    electronics = collection('02 | Downloaded electronics assets')
    additions = collection('03 | Sweep arm and collection bins')
    demo = collection('04 | Animated test objects')
    presentation = collection('05 | Camera and lights')
    source = copy_source(ROOT / 'hardware/mechanical/conveyer_belt.blend', source_col)
    assert len(source) == 12, len(source)
    blue = material('Blue prototype belt | photo reference', (0.008, 0.16, 0.47), 0.72)
    source['Plane.001'].data.materials.clear()
    source['Plane.001'].data.materials.append(blue)
    # Two restrained tape seams follow the hand-built blue belt in the photo.
    nodes, links = blue.node_tree.nodes, blue.node_tree.links
    coordinate = nodes.new('ShaderNodeTexCoord')
    separate = nodes.new('ShaderNodeSeparateXYZ')
    frequency = nodes.new('ShaderNodeMath'); frequency.operation = 'MULTIPLY'
    frequency.inputs[1].default_value = 2.0
    travel = nodes.new('ShaderNodeMath'); travel.operation = 'ADD'; travel.name = 'Belt travel'
    repeat = nodes.new('ShaderNodeMath'); repeat.operation = 'FRACT'
    tape = nodes.new('ShaderNodeMath'); tape.operation = 'LESS_THAN'; tape.inputs[1].default_value = 0.035
    mix = nodes.new('ShaderNodeMixRGB')
    mix.inputs[1].default_value = (0.008, 0.16, 0.47, 1)
    mix.inputs[2].default_value = (0.28, 0.31, 0.32, 1)
    links.new(coordinate.outputs['Generated'], separate.inputs[0])
    links.new(separate.outputs['X'], frequency.inputs[0])
    links.new(frequency.outputs[0], travel.inputs[0])
    links.new(travel.outputs[0], repeat.inputs[0])
    links.new(repeat.outputs[0], tape.inputs[0])
    links.new(tape.outputs[0], mix.inputs[0])
    links.new(mix.outputs[0], nodes.get('Principled BSDF').inputs['Base Color'])
    # Reuse source workbench rather than the discarded presentation podium.
    bench_mat = material('Workbench surface', (0.11, 0.073, 0.055), 0.75)
    source['Cube'].data.materials.clear()
    source['Cube'].data.materials.append(bench_mat)
    metal = material('Aluminum sweep strip', (0.45, 0.49, 0.53), 0.38, 0.75)
    dark = material('Black polymer / cable', (0.018, 0.021, 0.024), 0.6)
    card = material('White cardboard face', (0.66, 0.65, 0.60), 0.88)
    edge = material('Cardboard cut edges', (0.26, 0.18, 0.095), 0.9)
    ink = material('Printed bin label', (0.018, 0.02, 0.025), 0.8)
    red = material('Red paper marker', (0.58, 0.025, 0.018), 0.75)
    green = material('Green paper marker', (0.025, 0.29, 0.09), 0.75)
    white = material('White paper object', (0.65, 0.65, 0.60), 0.85)

    # Actual downloaded board, not the previous generic camera box.
    asset_instance('Downloaded Freenove ESP32-S3 board', ROOT / 'hardware/assets/freenove_esp32_s3_cam/freenove_esp32_s3_cam.blend',
                   'ASSET_Freenove_ESP32_S3_CAM', electronics, (-0.207, 0, 0.183))
    for yy in [-0.010, 0.010]:
        cylinder('Board standoff', (-0.207, yy, 0.180), 0.002, 0.006, metal, electronics)
    camera = box('Camera sensor | photo-inferred housing', (-0.207, 0, 0.162),
                 (0.020, 0.021, 0.012), dark, electronics)
    camera['basis'] = 'Sensor geometry omitted from downloaded board; simplified from prototype photo'
    cylinder('Downward camera lens', (-0.207, 0, 0.153), 0.0055, 0.008, dark, electronics)
    wire('Camera ribbon around bridge', [(-0.193, 0.005, 0.188), (-0.180, 0.005, 0.183),
         (-0.179, 0.005, 0.164), (-0.196, 0.005, 0.163)], 0.0016, dark, electronics)
    for name, x, y, rz in [('Start', -0.260, -0.087, 0), ('Scan', -0.207, 0.087, math.pi)]:
        obj = asset_instance('Downloaded IR sensor | ' + name, ROOT / 'hardware/assets/ir_sensor/ir_sensor.blend',
                             'ASSET_IR_Sensor', electronics, (x, y, 0.023), (0, 0, rz))
        obj['scale_note'] = 'Prepared IR asset scale is inferred from header pitch'
        side = -1 if y < 0 else 1
        box(name + ' IR sheet bracket', (x, side * 0.080, 0.021),
            (0.019, 0.065, 0.002), metal, electronics, 0.0002)
        for xx in [x - 0.005, x + 0.005]:
            cylinder(name + ' bracket screw', (xx, side * 0.050, 0.0225),
                     0.0013, 0.001, dark, electronics)

    # A modest shield proxy follows the real prototype photo, not a vendor model.
    pcb = material('Red CNC shield PCB', (0.31, 0.018, 0.018), 0.6)
    controller = box('Uno / CNC shield | photo-derived proxy', (-0.035, -0.177, -0.013),
                     (0.069, 0.054, 0.003), pcb, electronics)
    controller['basis'] = 'Simplified component layout from supplied prototype photograph'
    for x in [-0.060, -0.010]:
        box('Shield header row', (x, -0.177, -0.005), (0.005, 0.046, 0.010), dark, electronics)
    box('Stepper driver module', (-0.035, -0.173, -0.007), (0.016, 0.022, 0.006), green, electronics)
    for x in [-0.040, -0.037, -0.034, -0.031]:
        box('Driver heatsink fin', (x, -0.173, 0.0005), (0.0013, 0.014, 0.008), metal, electronics, 0)
    for i, mat in enumerate([red, dark, green]):
        wire('Jumper wire ' + str(i), [(-0.035 + i * 0.008, -0.151, -0.003),
             (-0.015, -0.125 + i * 0.003, 0.012), (0.045, -0.112, 0.017),
             (0.059, -0.093 + i * 0.003, 0.006)], 0.00055, mat, electronics)

    # Side-mounted strip rotates about the actual source servo shaft geometry.
    pivot = bpy.data.objects.new('Servo sweep pivot | animated', None)
    additions.objects.link(pivot)
    pivot.location = PIVOT
    pivot['axis'] = 'Z; one rotational degree of freedom'
    cylinder('Servo horn hub', PIVOT + Vector((0, 0, 0.001)), 0.006, 0.003, metal, additions)
    arm = box('Long aluminum sweep arm', (0.115, 0, 0.0025), (0.230, 0.010, 0.003),
              metal, additions, 0.00025)
    arm.parent = pivot
    arm['basis'] = 'Side-mounted long shaft from user concept; length nominal'
    for x in [0.015, 0.035, 0.055, 0.075]:
        hole = cylinder('Horn fastener', (x, 0, 0.0042), 0.0013, 0.0005, dark, additions)
        hole.parent = pivot

    # Bins are beside the belt, with the third directly beyond the output end.
    bin_specs = [('A', (0.18, -0.115), (0.14, 0.105)),
                 ('B', (0.18, 0.115), (0.14, 0.105)),
                 ('C', (0.375, CENTER_Y), (0.14, 0.105))]
    for label, (x, y), (sx, sy) in bin_specs:
        bottom = box('Bin ' + label + ' floor', (x, y, -0.019), (sx, sy, 0.002), card, additions)
        bottom['destination'] = label
        for sign in [-1, 1]:
            box('Bin ' + label + ' side wall', (x, y + sign * sy / 2, -0.0035),
                (sx + 0.002, 0.002, 0.033), card, additions, 0.0001)
            box('Bin ' + label + ' end wall', (x + sign * sx / 2, y, -0.0035),
                (0.002, sy, 0.033), card, additions, 0.0001)
        for sign in [-1, 1]:
            box('Bin ' + label + ' cut rim', (x, y + sign * sy / 2, 0.0134),
                (sx, 0.002, 0.0005), edge, additions, 0)
        text('Bin label ' + label, 'BIN ' + label, (x, y, -0.0178), 0.016, ink, additions)

    # Match the photo's hand-built paper samples, without glossy toy blocks.
    for index, (label, marker) in enumerate(zip('ABC', [red, green, white])):
        start = 1 + CYCLE * index
        obj = box('Object ' + label + ' | animated', (-0.270, CENTER_Y, BELT_TOP + BLOCK / 2 + 0.0005),
                  (BLOCK, BLOCK, BLOCK), white, demo, 0.0002)
        cap = box('Object ' + label + ' colored paper', (0, 0, BLOCK / 2 + 0.0001),
                  (BLOCK * 0.96, BLOCK * 0.96, 0.0002), marker, demo, 0)
        cap.parent = obj
        visibility(obj, start)
        visibility(cap, start)
        z = BELT_TOP + BLOCK / 2 + 0.0005
        sequence = [(0, (-0.270, CENTER_Y, z)), (9, (-0.270, CENTER_Y, z)),
                    (31, (-0.207, CENTER_Y, z)), (49, (-0.207, CENTER_Y, z)),
                    (73, (0.180, CENTER_Y, z))]
        if label == 'A':
            sequence += [(90, (0.180, -0.010, z)), (109, (0.180, -0.081, z)),
                         (121, ROUTES[label]), (143, ROUTES[label])]
            angles = [(0, 180), (73, 180), (90, 36), (109, 0), (143, 0)]
        elif label == 'B':
            sequence += [(90, (0.180, 0.012, z)), (109, (0.180, 0.086, z)),
                         (121, ROUTES[label]), (143, ROUTES[label])]
            angles = [(0, 0), (73, 0), (90, 28), (109, 54), (126, 54), (143, 180)]
        else:
            sequence += [(100, (0.294, CENTER_Y, z)), (112, (0.329, CENTER_Y, z - 0.011)),
                         (127, ROUTES[label]), (143, ROUTES[label])]
            angles = [(0, 180), (143, 180)]
        for offset, position in sequence:
            obj.location = position
            obj.keyframe_insert('location', frame=start + offset)
        for offset, degrees in angles:
            pivot.rotation_euler[2] = math.radians(degrees)
            pivot.keyframe_insert('rotation_euler', frame=start + offset)
        for offset, phase in [(0, 'LOAD'), (10, 'MOVE TO CAMERA'), (32, 'SCAN / PAUSE'),
                              (50, 'MOVE TO SORTING STATION'), (74, 'SWEEP ' + label if label != 'C' else 'PASS TO END C'),
                              (122, 'CLEAR / RESET')]:
            scene.timeline_markers.new(label + ' | ' + phase, frame=start + offset)

    distance = 0.0
    for frame in range(1, END + 1):
        phase, cycle = (frame - 1) % CYCLE, (frame - 1) // CYCLE
        if 9 <= phase < 31:
            distance += 0.063 / 22
        elif 49 <= phase < 73:
            distance += 0.387 / 24
        elif cycle == 2 and 73 <= phase < 112:
            distance += 0.15 / 39
        travel.inputs[1].default_value = -2 * distance / 0.5907
        travel.inputs[1].keyframe_insert('default_value', frame=frame)

    # Render setup: restrained workshop view, without the old podium and HUD.
    scene.render.engine = 'BLENDER_EEVEE'
    scene.eevee.taa_render_samples = 32
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.resolution_percentage = 100
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = 1, END
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = '//renders/frame_'
    scene.world = bpy.data.worlds.new('Neutral room')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.32, 0.35, 0.39, 1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.6
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.exposure = -0.2
    for name, pos, power, size in [('Window', (-0.3, -0.45, 1.0), 32, 0.9),
                                   ('Room fill', (0.3, 0.5, 0.6), 18, 0.8)]:
        bpy.ops.object.light_add(type='AREA', location=pos)
        light = move_to(bpy.context.object, presentation)
        light.name, light.data.energy, light.data.size = name, power, size
        light.rotation_euler = (Vector((0.05, 0, 0.02)) - light.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.ops.object.camera_add(location=(0.82, -1.05, 0.92))
    view = move_to(bpy.context.object, presentation)
    view.name = 'Assembly presentation camera'
    view.rotation_euler = (Vector((0.055, 0, 0.045)) - view.location).to_track_quat('-Z', 'Y').to_euler()
    view.data.type, view.data.ortho_scale = 'ORTHO', 0.88
    view.data.clip_start, view.data.clip_end = 0.01, 10
    scene.camera = view
    notes = bpy.data.texts.new('READ ME | reference-based reconstruction')
    notes.write('Original source frame, loop belt, shafts, bearings, PVC rollers, camera bridge, NEMA17 and SG90 meshes retained.\n'
                'Belt widened from 56.67 to88mm; entire drive group raised4mm.\n'
                'Downloaded IR and Freenove board meshes are appended, not linked.\n'
                'Bins A/B at opposite sides, C beyond end, per supplied Excalidraw.\n'
                'Sweep arm rotates about the recovered servo shaft; location adjusted nominally.\n'
                'Three six-second cycles are keyframed; no contact dynamics, firmware or AI solver runs.\n'
                'Source image dimensions and CAD scales do not validate fabrication fit.\n')
    for image in list(bpy.data.images):
        if image.users == 0:
            bpy.data.images.remove(image)
    bpy.ops.file.pack_all()
    scene.frame_set(110)
    bpy.ops.object.select_all(action='DESELECT')
    pivot.select_set(True)
    bpy.context.view_layer.objects.active = pivot
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.region_3d.view_perspective = 'CAMERA'
                area.spaces.active.shading.type = 'MATERIAL'
                area.spaces.active.overlay.show_overlays = False
    return scene


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'hardware/mechanical/oss_simulation.blend')
    parser.add_argument('--still', type=Path)
    parser.add_argument('--frames-dir', type=Path)
    parser.add_argument('--preview-frame', type=int, default=110)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    scene = build()
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output.resolve()))
    print('OSS_RECONSTRUCTION', json.dumps({'frames': END, 'fps': FPS,
          'objects': len(scene.objects), 'bin_layout': scene['bin_layout']}), flush=True)
    if args.still:
        scene.frame_set(args.preview_frame)
        scene.render.filepath = str(args.still.resolve())
        bpy.ops.render.render(write_still=True)
    if args.frames_dir:
        args.frames_dir.mkdir(parents=True, exist_ok=True)
        scene.render.filepath = str(args.frames_dir.resolve() / 'frame_')
        bpy.ops.render.render(animation=True)


if __name__ == '__main__':
    main()
