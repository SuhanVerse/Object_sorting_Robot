#!/usr/bin/env python3
"""Convert a STEP assembly to a colored, meter-scale GLB with OpenCascade.

Run using a separate Python environment, not Blender's Python::

    python3 -m venv /tmp/object-sorter-cad-venv
    /tmp/object-sorter-cad-venv/bin/pip install cadquery-ocp==8.0.1.1.0
    /tmp/object-sorter-cad-venv/bin/python scripts/blender/convert_cad_asset.py \
        input.step output.glb --report output.conversion.json

XCAF retains the input assembly, part names, and face/part colors. STEP length
units are read by OpenCascade; its internal millimeters are exported as meters.
The GLB uses glTF Y-up; Blender's importer restores the original CAD Z-up frame.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct


def convert(source: Path, output: Path, report: Path, deflection_mm: float) -> dict:
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.Message import Message_ProgressRange
    from OCP.RWGltf import RWGltf_CafWriter
    from OCP.RWMesh import (
        RWMesh_CoordinateSystem_glTF,
        RWMesh_CoordinateSystem_Zup,
        RWMesh_NameFormat_ProductAndInstance,
    )
    from OCP.STEPCAFControl import STEPCAFControl_Reader
    from OCP.TCollection import TCollection_AsciiString, TCollection_ExtendedString
    from OCP.TDocStd import TDocStd_Document
    from OCP.XCAFDoc import XCAFDoc_DocumentTool
    from OCP.collections import (
        IndexedDataMap_TCollection_AsciiString_TCollection_AsciiString,
        Sequence_TDF_Label,
    )

    source = source.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    document = TDocStd_Document(TCollection_ExtendedString("BinXCAF"))
    reader = STEPCAFControl_Reader()
    reader.SetColorMode(True)
    reader.SetNameMode(True)
    reader.SetMatMode(True)
    if reader.ReadFile(str(source)) != IFSelect_RetDone:
        raise RuntimeError(f"OpenCascade could not read {source}")
    if not reader.Transfer(document):
        raise RuntimeError("STEP transfer failed")

    shapes = XCAFDoc_DocumentTool.ShapeTool_s(document.Main())
    roots = Sequence_TDF_Label()
    shapes.GetFreeShapes(roots)
    if roots.Length() == 0:
        raise RuntimeError("STEP contains no top-level shapes")
    bounds = Bnd_Box()
    for i in range(1, roots.Length() + 1):
        shape = shapes.GetShape_s(roots.Value(i))
        BRepBndLib.AddOptimal_s(shape, bounds, False, False)
        mesh = BRepMesh_IncrementalMesh(shape, deflection_mm, False, 0.35, True)
        if not mesh.IsDone():
            raise RuntimeError(f"Meshing failed for root {i}")

    writer = RWGltf_CafWriter(TCollection_AsciiString(str(output)), True)
    converter = writer.ChangeCoordinateSystemConverter()
    converter.SetInputLengthUnit(0.001)
    converter.SetOutputLengthUnit(1.0)
    converter.SetInputCoordinateSystem(RWMesh_CoordinateSystem_Zup)
    converter.SetOutputCoordinateSystem(RWMesh_CoordinateSystem_glTF)
    writer.SetNodeNameFormat(RWMesh_NameFormat_ProductAndInstance)
    writer.SetMeshNameFormat(RWMesh_NameFormat_ProductAndInstance)
    writer.SetMergeFaces(True)
    writer.SetParallel(True)
    metadata = IndexedDataMap_TCollection_AsciiString_TCollection_AsciiString()
    metadata.Add(
        TCollection_AsciiString("title"), TCollection_AsciiString(source.stem)
    )
    if not writer.Perform(document, metadata, Message_ProgressRange()):
        raise RuntimeError("GLB export failed")

    data = output.read_bytes()
    json_length, chunk_type = struct.unpack_from("<II", data, 12)
    if chunk_type != 0x4E4F534A:
        raise RuntimeError("Export does not contain a glTF JSON chunk")
    gltf = json.loads(data[20 : 20 + json_length])
    # OCP 8's Get() exposes an unregistered Bnd_Box::Limits overload;
    # the corner API returns the same values through supported gp_Pnt bindings.
    lower, upper = bounds.CornerMin(), bounds.CornerMax()
    b = (lower.X(), lower.Y(), lower.Z(), upper.X(), upper.Y(), upper.Z())
    result = {
        "source_filename": source.name,
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "output_filename": output.name,
        "output_sha256": hashlib.sha256(data).hexdigest(),
        "output_size_bytes": len(data),
        "converter": "cadquery-ocp 8.0.1.1.0 / OpenCascade XCAF RWGltf_CafWriter",
        "units": {
            "opencascade_internal": "millimeter",
            "export": "meter",
            "input_length_scale_to_m": 0.001,
        },
        "coordinates": {
            "input": "CAD Z-up, preserved on Blender glTF import",
            "glb": "glTF Y-up",
        },
        "tessellation": {"linear_deflection_mm": deflection_mm, "angular_deflection_radians": 0.35},
        "cad_bounds_mm": {
            "min": list(b[:3]),
            "max": list(b[3:]),
            "size": [b[i + 3] - b[i] for i in range(3)],
        },
        "root_count": roots.Length(),
        "gltf_node_count": len(gltf.get("nodes", [])),
        "gltf_mesh_count": len(gltf.get("meshes", [])),
        "gltf_material_count": len(gltf.get("materials", [])),
        "gltf_materials": gltf.get("materials", []),
        "license": "Unknown; no license statement was present in the supplied STEP header.",
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--deflection-mm", type=float, default=0.05)
    args = parser.parse_args()
    if args.deflection_mm <= 0:
        parser.error("--deflection-mm must be positive")
    report_path = args.report or args.output.with_suffix(".conversion.json")
    result = convert(args.source, args.output, report_path, args.deflection_mm)
    print(json.dumps({k: v for k, v in result.items() if k != "gltf_materials"}, indent=2))
