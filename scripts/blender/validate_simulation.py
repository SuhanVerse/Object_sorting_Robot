"""Inspect the saved OSS concept scene without rendering or operating hardware."""
import json
from pathlib import Path
import sys

import bpy

scene = bpy.context.scene
assert scene.frame_start == 1 and scene.frame_end == 360
assert scene.render.fps == 24
assert scene.camera and scene.camera.type == 'CAMERA'
assert not any(image.filepath and not image.packed_file for image in bpy.data.images)
assert not any(obj.animation_data and obj.animation_data.drivers for obj in scene.objects)
assert not scene.rigidbody_world
assert 'not physics' in bpy.data.texts.get('READ ME | animation assumptions').as_string().lower() or \
       'no physics' in bpy.data.texts.get('READ ME | animation assumptions').as_string().lower()

samples = []
for index, (label, expected_y) in enumerate(zip('ABC', [-0.128, 0, 0.128])):
    start = 1 + index * 120
    obj = bpy.data.objects['Object ' + label + ' | animated']
    scene.frame_set(start)
    assert not obj.hide_render and abs(obj.location.x + 0.273) < 1e-5
    scene.frame_set(start + 34)
    scan_position = obj.location.copy()
    assert abs(scan_position.x + 0.115) < 1e-5
    scene.frame_set(start + 51)
    assert (obj.location - scan_position).length < 1e-5
    scene.frame_set(start + 109)
    assert abs(obj.location.x - 0.505) < 1e-5
    assert abs(obj.location.y - expected_y) < 1e-5
    assert 0.026 < obj.location.z < 0.032
    samples.append({'object': label, 'scan_frames': [start + 34, start + 51],
                    'destination_frame': start + 109,
                    'destination_m': [round(v, 4) for v in obj.location]})
scene.frame_set(360)
assert all(not bpy.data.objects['Object ' + label + ' | animated'].hide_render for label in 'ABC')
result = {'blender_version': bpy.app.version_string, 'scene': scene.name,
          'frame_count': 360, 'fps': 24, 'duration_seconds': 15,
          'resolution': [scene.render.resolution_x, scene.render.resolution_y],
          'external_image_dependencies': 0, 'scripted_drivers': 0,
          'validated': 'Native scene opens; required objects, keyframe holds and three destinations match the concept specification',
          'not_validated': 'Physics, collisions, structural fit, electrical behavior, firmware timing, sensor response or AI accuracy',
          'samples': samples}
if '--' in sys.argv:
    output = Path(sys.argv[sys.argv.index('--') + 1])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + '\n')
print('OSS_VALIDATION', json.dumps(result), flush=True)
