"""Rebuild reusable component libraries from the preserved downloaded geometry.

Run: blender --background --factory-startup --python hardware/assets/prepare_libraries.py
First convert the Freenove STEP with scripts/blender/convert_cad_asset.py.
No downloaded geometry is replaced; the IR working scale is explicitly inferred.
"""

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent


def mesh_bounds(objects):
    points = [
        obj.matrix_world @ vertex.co
        for obj in objects
        if obj.type == "MESH"
        for vertex in obj.data.vertices
    ]
    minimum = [min(point[i] for point in points) for i in range(3)]
    maximum = [max(point[i] for point in points) for i in range(3)]
    return {
        "min": minimum,
        "max": maximum,
        "size": [maximum[i] - minimum[i] for i in range(3)],
    }


def prepare(asset, source, collection_name, scale=1.0, rotate_x_degrees=0, inferred=False):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version = 0
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    bpy.ops.import_scene.gltf(filepath=str(ROOT / asset / source))
    objects = list(scene.objects)
    meshes = [obj for obj in objects if obj.type == "MESH"]
    source_mesh_count = len(meshes)
    bpy.context.view_layer.update()
    original_bounds = mesh_bounds(meshes)
    removed_duplicates = []
    if asset == "ir_sensor":
        original = bpy.data.objects["ir top"]
        duplicate = bpy.data.objects["ir top.001"]
        def signature(obj):
            return (
                tuple(tuple(vertex.co) for vertex in obj.data.vertices),
                tuple(tuple(polygon.vertices) for polygon in obj.data.polygons),
                tuple(tuple(tuple(value.uv) for value in layer.data) for layer in obj.data.uv_layers),
                tuple(material.name for material in obj.data.materials),
            )
        if original.matrix_world != duplicate.matrix_world or signature(original) != signature(duplicate):
            raise RuntimeError("IR source top-plane duplicate changed; inspect before cleanup")
        # This exact coplanar copy makes the supplied texture render black in
        # Cycles. Removing its redundant surface preserves all unique geometry.
        removed_duplicates.append(duplicate.name)
        objects.remove(duplicate)
        meshes.remove(duplicate)
        bpy.data.objects.remove(duplicate, do_unlink=True)

    collection = bpy.data.collections.new(collection_name)
    scene.collection.children.link(collection)
    for obj in objects:
        for old_collection in list(obj.users_collection):
            old_collection.objects.unlink(obj)
        collection.objects.link(obj)

    handle = bpy.data.objects.new(collection_name + "_ROOT", None)
    collection.objects.link(handle)
    handle.empty_display_type = "PLAIN_AXES"
    handle.empty_display_size = 0.01
    for obj in objects:
        if obj.parent is None:
            obj.parent = handle
    handle.scale = (scale,) * 3
    handle.rotation_euler.x = math.radians(rotate_x_degrees)
    bpy.context.view_layer.update()
    transformed_bounds = mesh_bounds(meshes)
    center = Vector([
        (transformed_bounds["min"][i] + transformed_bounds["max"][i]) / 2
        for i in range(3)
    ])
    handle.location = (-center.x, -center.y, -transformed_bounds["min"][2])
    bpy.context.view_layer.update()

    evidence = (
        "Inferred working scale: 0.012 m per authored unit; male header pitch "
        "approximately 2.54 mm. Physical dimensions are not independently verified."
        if inferred else "STEP declares millimeters; OpenCascade exported meters."
    )
    handle["source_asset"] = asset
    handle["source_file"] = source
    handle["license_status"] = "Unknown; no supplied license statement found"
    handle["source_uniform_scale_to_m"] = scale
    handle["scale_evidence"] = evidence
    handle["geometry_origin"] = "Downloaded asset geometry; no primitive reconstruction"
    handle["orientation"] = "PCB in XY plane; component side +Z"
    for image in bpy.data.images:
        if image.source == "FILE" and not image.packed_file:
            image.pack()
    bpy.ops.object.select_all(action="DESELECT")
    handle.select_set(True)
    bpy.context.view_layer.objects.active = handle
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / asset / (asset + ".blend")), compress=True)

    report = {
        "collection": collection_name,
        "root_object": handle.name,
        "source_bounds_blender_m": original_bounds,
        "component_bounds_m": mesh_bounds(meshes),
        "source_uniform_scale": scale,
        "scale_is_inferred": inferred,
        "scale_evidence": evidence,
        "orientation": "PCB in XY; component side +Z; centered XY; lowest point Z=0",
        "mesh_object_count": len(meshes),
        "source_mesh_object_count": source_mesh_count,
        "removed_exact_duplicate_objects": removed_duplicates,
        "vertex_count": sum(len(obj.data.vertices) for obj in meshes),
        "polygon_count": sum(len(obj.data.polygons) for obj in meshes),
        "material_count": len(bpy.data.materials),
        "material_names": [material.name for material in bpy.data.materials],
        "object_names": [obj.name for obj in objects],
        "packed_images": [image.name for image in bpy.data.images if image.packed_file],
        "transforms": {
            "scale": list(handle.scale),
            "rotation_x_degrees": rotate_x_degrees,
            "location": list(handle.location),
        },
        "license": "Unknown; no license statement was supplied with the model.",
    }
    (ROOT / asset / "blender_inspection.json").write_text(json.dumps(report, indent=2) + "\n")
    print(collection_name, report["component_bounds_m"], len(meshes), "mesh objects")


prepare(
    "freenove_esp32_s3_cam", "freenove_esp32_s3_cam.glb",
    "ASSET_Freenove_ESP32_S3_CAM", rotate_x_degrees=90,
)
prepare(
    "ir_sensor", "source/ir sensor.glb", "ASSET_IR_Sensor",
    scale=0.012, inferred=True,
)
