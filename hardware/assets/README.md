# Downloaded hardware assets

These are the user's supplied downloaded models, with originals retained under
each `source/` folder. Prepared geometry comes from those files. Creator, source
URL, and license were not supplied or found in the inspected metadata; see each
folder's `SOURCE.json`. Do not infer a license from this repository's license.

| Component library | Collection | Overall X × Y × Z | Scale evidence |
| --- | --- | --- | --- |
| `freenove_esp32_s3_cam/freenove_esp32_s3_cam.blend` | `ASSET_Freenove_ESP32_S3_CAM` | 57.21755 × 28.20000 × 17.47000 mm | Original STEP declares millimeters; converted to meters. |
| `ir_sensor/ir_sensor.blend` | `ASSET_IR_Sensor` | 15.37768 × 47.76943 × 7.78370 mm | **Inferred working scale**, approximately 2.54 mm male header pitch. |

Both libraries use meters, PCB in XY, component side +Z, XY-centered origins,
and their lowest geometry point at Z=0. The IR optical pair faces +Y. Freenove
USB ports are at +X. Complete pin geometry is included in the stated bounds.
These dimensions are model measurements, without independent physical validation.

The Freenove source is the ESP32-S3 board with a camera connector. It contains no
fitted camera sensor module. The separate `esp32_sketchup/source/esp32.skp`
thumbnail shows an ESP32-CAM board, but native SKP geometry is not imported:
Blender 5.2.2 has no installed supported SketchUp importer. Its original SKP,
extracted original thumbnails, and inspected archive metadata are preserved.

## Use in Blender

Use **File → Append → selected `.blend` → Collection → collection name**.
For reusable collection instances from Python:

```python
from pathlib import Path
import bpy

assets = Path("/absolute/path/to/Object_sorting_Robot/hardware/assets")
library = assets / "freenove_esp32_s3_cam/freenove_esp32_s3_cam.blend"
with bpy.data.libraries.load(str(library), link=False) as (available, loaded):
    loaded.collections = ["ASSET_Freenove_ESP32_S3_CAM"]
component = bpy.data.objects.new("Freenove board", None)
component.instance_type = "COLLECTION"
component.instance_collection = loaded.collections[0]
bpy.context.scene.collection.objects.link(component)
component.location = (0, 0, 0)  # meters; collection already has physical scale
```

Keep the loaded collection unlinked when using an instance. The IR library uses
the same code with `ir_sensor/ir_sensor.blend` and `ASSET_IR_Sensor`.

The original IR GLB and prepared Freenove GLB can also be imported directly with
`bpy.ops.import_scene.gltf(filepath=...)`. The Freenove GLB retains original CAD
orientation: PCB lies in XZ and component side is +Y after Blender import; the
component library supplies a +90° X rotation. The original IR GLB has arbitrary
authoring scale (1.28147 × 3.98079 × 0.64864 Blender meters overall). Its library
uses a documented uniform factor of 0.012. To revise that inferred scale, change
the root empty's uniform scale or the setting in `prepare_libraries.py`.

## Rebuild and verify

Run the STEP converter with an isolated Python environment:

```bash
python3 -m venv /tmp/object-sorter-cad-venv
/tmp/object-sorter-cad-venv/bin/pip install cadquery-ocp==8.0.1.1.0
/tmp/object-sorter-cad-venv/bin/python scripts/blender/convert_cad_asset.py \
  'hardware/assets/freenove_esp32_s3_cam/source/Freenove ESP32-S3-WROOM-CAM.step' \
  hardware/assets/freenove_esp32_s3_cam/freenove_esp32_s3_cam.glb \
  --report hardware/assets/freenove_esp32_s3_cam/conversion.json
/snap/bin/blender --background --factory-startup \
  --python hardware/assets/prepare_libraries.py
```

OpenCascade XCAF preserves the STEP assembly names and face/part colors.
Tessellation uses 0.05 mm linear and 0.35 rad angular deflection. The Blender
library retains those 223 mesh objects and 35 materials. The IR library retains
34 meshes, six materials, and two packed textures. Its original GLB contains
35 meshes: the prepared library removes only the verified exact duplicate
`ir top.001` texture plane, which otherwise makes the PCB texture render black
in Cycles. All unique source geometry is retained. Separate source PNGs are also
retained in `ir_sensor/textures/`.

`conversion.json` records CAD bounds and output hashes. Per-component
`blender_inspection.json` records names, transforms, packed textures, and final
bounds. `verification.json` records successful independent append-and-instance
checks in Blender 5.2.2, material and mesh counts, packed texture availability,
and agreement between CAD and imported bounds within 0.001 mm.
