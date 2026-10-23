# OSS mechanical reconstruction

![Completed source-based assembly with opposite side bins and an end bin](../../docs/media/simulation-preview.png)

Open [oss_simulation.blend](oss_simulation.blend) in **Blender 5.2.2 LTS**. Press Space to play frames 1–432 at 24 fps. Numpad 0 selects the assembly camera. Collections separate the recovered conveyor, downloaded electronics, sweep arm/bins, animated objects, and presentation setup. Viewport overlays are hidden initially; use the viewport overlays toggle if needed.

The model completes the [original conveyor](conveyer_belt.blend) using the real prototype and [user concept](../../docs/media/oss-conceptual-model.png). It retains the frame, loop belt, rollers, shafts, bearings, camera bridge, NEMA17, and detailed servo. **A and B are on opposite sides; C is at the end.** A long side-mounted sweep arm replaces the previous outlet chute.

Read [reference analysis](reference-analysis.md) for measured geometry and reconstruction decisions. [Downloaded asset notes](../assets/README.md) explain STEP conversion, IR scale, textures, and the retained native SKP.

## Animation and playback

- [Animated GIF](../../docs/media/intended-sorting-preview.gif) plays directly in the main README.
- Download [H.264 MP4](../../docs/media/intended-sorting-simulation.mp4) or [VP9 WebM](../../docs/media/intended-sorting-simulation.webm).
- Run `python3 -m http.server 8765` from the repository root, then open [the local player](http://localhost:8765/docs/media/player.html).

The three six-second cycles are keyframed explanations, not physics or firmware tests. Colors and A/B/C paths do not establish a trained-model mapping. The internal Blender text block records these assumptions.

## Rebuild

With Blender and FFmpeg installed, from the repository root:

```sh
blender --background --factory-startup --disable-autoexec --python scripts/blender/create_simulation.py -- --still docs/media/simulation-preview.png --frames-dir /tmp/oss-frames
python3 scripts/media/encode_animation.py /tmp/oss-frames
blender --background --disable-autoexec hardware/mechanical/oss_simulation.blend --python scripts/blender/validate_simulation.py -- docs/media/simulation-validation.json
```

The generator reads the original model and the two prepared asset libraries. [The original scene](conveyer_belt.blend), [backup](conveyer_belt.blend1), and [original render](../../docs/assets/conveyor-render.png) remain unchanged. Source checksums are recorded in the [inventory](../../docs/source-inventory.json).

To render a scene you edited manually, use Blender's Render Animation command or:

```sh
blender --background --disable-autoexec hardware/mechanical/oss_simulation.blend --render-output /tmp/oss-frames/frame_ --frame-start 1 --frame-end 432 --render-anim
python3 scripts/media/encode_animation.py /tmp/oss-frames
```

Refresh `docs/media/generated-assets.json` after deliberate changes. No STL, measured fabrication drawing, or calibrated hardware geometry is claimed. Local pre-rebuild edits were backed up under the ignored `.local-backups/` directory.
