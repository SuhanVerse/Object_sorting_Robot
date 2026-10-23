"""Check source-based geometry, opposite-side bins, and the saved animation."""
import json
import math
from pathlib import Path
import sys

import bpy

scene = bpy.context.scene
assert (scene.frame_start, scene.frame_end, scene.render.fps) == (1, 432, 24)
assert scene.camera and scene.camera.type == 'CAMERA'
assert not scene.rigidbody_world
assert not any(obj.animation_data and obj.animation_data.drivers for obj in bpy.data.objects)
assert all(not image.filepath or image.packed_file for image in bpy.data.images)
retained = [obj for obj in scene.objects if obj.get('retained_geometry')]
assert len(retained) == 12
motor = bpy.data.objects['Source NEMA17 motor']
assert len(motor.data.vertices) == 25378
belt = bpy.data.objects['Source oval belt']
width = max(v.co.y for v in belt.data.vertices) - min(v.co.y for v in belt.data.vertices)
assert abs(width - 0.088) < 1e-5
asset_instances = [obj for obj in scene.objects if obj.get('asset_library')]
assert len(asset_instances) == 3
asset_report = []
for obj in asset_instances:
    meshes = [member for member in obj.instance_collection.all_objects if member.type == 'MESH']
    expected = 223 if 'Freenove' in obj.name else 34
    assert len(meshes) == expected, (obj.name, len(meshes))
    asset_report.append({'instance': obj.name, 'mesh_count': len(meshes),
                         'library': obj['asset_library']})

bins = {label: bpy.data.objects['Bin ' + label + ' floor'] for label in 'ABC'}
assert bins['A'].location.y < -0.055
assert bins['B'].location.y > 0.055
assert abs(bins['A'].location.x - bins['B'].location.x) < 1e-6
assert bins['C'].location.x > 0.300 and abs(bins['C'].location.y) < 0.01
samples = []
for index, label in enumerate('ABC'):
    start = 1 + 144 * index
    obj = bpy.data.objects['Object ' + label + ' | animated']
    scene.frame_set(start)
    assert not obj.hide_render
    scene.frame_set(start + 31)
    scan = obj.location.copy()
    assert abs(scan.x + 0.207) < 1e-5
    scene.frame_set(start + 49)
    assert (obj.location - scan).length < 1e-5
    finish = start + (127 if label == 'C' else 121)
    scene.frame_set(finish)
    assert abs(obj.location.x - bins[label].location.x) < 1e-5
    assert abs(obj.location.y - bins[label].location.y) < 1e-5
    samples.append({'object': label, 'scan_frames': [start + 31, start + 49],
                    'destination_frame': finish,
                    'destination_m': [round(value, 5) for value in obj.location]})
for frame in range(1, 433):
    scene.frame_set(frame)
    angle = bpy.data.objects['Servo sweep pivot | animated'].rotation_euler.z
    assert -1e-5 <= angle <= math.pi + 1e-5
scene.frame_set(432)
assert all(not bpy.data.objects['Object ' + label + ' | animated'].hide_render for label in 'ABC')
report = {'blender_version': bpy.app.version_string, 'scene': scene.name,
          'frame_count': 432, 'fps': 24, 'duration_seconds': 18,
          'resolution': [1280, 720], 'retained_source_meshes': len(retained),
          'source_motor_vertices': len(motor.data.vertices), 'completed_belt_width_m': round(width, 5),
          'downloaded_asset_instances': asset_report, 'external_image_dependencies': 0,
          'bin_layout': {'A': 'negative Y side', 'B': 'positive Y side', 'C': 'positive X end'},
          'validated': 'Source geometry retained, downloaded asset counts, opposite-side/end bins, scan holds, final poses, servo angle range, packed textures',
          'not_validated': 'Physics, contact forces, collision clearance, fabrication fit, hardware calibration, firmware timing or AI accuracy',
          'samples': samples}
if '--' in sys.argv:
    output = Path(sys.argv[sys.argv.index('--') + 1])
    output.write_text(json.dumps(report, indent=2) + '\n')
print('OSS_VALIDATION', json.dumps(report), flush=True)
