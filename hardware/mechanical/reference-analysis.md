# Reference analysis and reconstruction decisions

This revision follows the supplied [Excalidraw concept](../../docs/media/oss-conceptual-model.png), [prototype photograph](../../docs/media/prototype-photo.jpeg), and original `conveyer_belt.blend`. It completes that assembly rather than replacing it with a generic conveyor.

## Observed evidence

Blender 5.2.2 evaluated mesh vertices were measured in world coordinates. The original scene uses metres, with X along the belt, Y across it, and Z upward.

| Source feature | Observed value |
| --- | --- |
| Timber frame | Approximately 600.08 × 110 × 40.67 mm |
| Rails | 10 mm thick, with a 90 mm clear gap |
| Original closed-loop belt | 56.67 mm wide; carrying surface at Z≈17.085 mm |
| Rail top | Z≈20.797 mm |
| Camera bridge | Approximately 41.82 × 117.25 × 196.33 mm; at the negative-X end |
| NEMA17 | Original imported mesh: 25,378 vertices, six materials |
| Servo assembly | Original imported geometry: approximately 20.31 × 54.15 × 52.46 mm |
| Original servo shaft | Centre (.12357648, −.07464294, .03429335) m; axis Z |

The original motor and servo include import transforms. Their evaluated world-space meshes were baked before placement, preserving the actual detailed geometry and materials. This avoids losing the servo's scale or orientation by copying only local mesh coordinates.

The five missing oak-image datablocks in the old scene are unused: the active source materials have no Image Texture nodes. They were removed as unused data in the new scene; they were not a reason to replace the source model.

The [independent geometry comparison](../../docs/media/source-geometry-validation.json) confirms exact polygon connectivity for all 12 retained parts, with corresponding vertices matching the documented transforms within 4.10e-8 m.

## Completion choices

- Widen the existing oval belt to 88 mm, centred within the 90 mm rail gap. Raise the **entire belt/roller/shaft/bearing/motor group together by 4 mm**, so belt and roller wraps remain aligned and the carrying surface clears the rail lips.
- Keep the timber frame, camera bridge, full motor mesh, PVC rollers, shafts, bearings, and detailed servo geometry.
- Position Bin A at negative Y, Bin B at positive Y, and Bin C beyond positive X, matching the drawing. The two side bins share the same sorting station rather than forming a fan at the outlet.
- Reposition the source servo slightly along the negative-Y rail and attach a long aluminium sweep strip about its actual output-shaft axis. Its nominal 230 mm arm length and placement allow a viewable side sweep; they are not measured fabrication dimensions.
- Use the supplied blue belt and paper/cardboard appearance as visual references. The tape seams, bin walls, wiring, and controller proxy are modeled details, not recovered CAD parts.
- Append the actual downloaded Freenove board and IR sensor libraries. The Freenove STEP provides physical units; the IR working scale is inferred from pin spacing. The Freenove download omits a fitted camera sensor, so that small housing/lens/ribbon is explicitly a simplified photograph-based addition.

## What the motion demonstrates

The three six-second cycles show camera travel, a scan pause, left-side A routing, opposite-side B routing, and straight-through C routing. Side routing uses the long rotating arm, not the previous rotating outlet chute. Object paths and arm angles are keyframed for explanation. There is no claim of contact dynamics, calibrated servo mapping, sensor emulation, physical fit, or working AI integration.

The [native validation](../../docs/media/simulation-validation.json) checks retained source parts, imported assets, bin layout, timeline, scan holds, and final positions. Physical clearances and loads require measurement and testing on the assembly.

## Downloaded assets

[Asset provenance and conversion notes](../assets/README.md) identify the original STEP, GLB, textures, and SKP. The SKP is preserved as supplied but is not falsely described as imported: no reliable SKP geometry conversion was available. Source URLs, authors, and licenses were not supplied, and no new third-party license is invented.
