# Prototype media

This page separates original physical-prototype records from a new Blender concept animation. No successful hardware operation or sorting accuracy is claimed.

## Prototype photo

![Physical prototype with a blue conveyor belt, wooden side rails, mounted electronics, and wiring](prototype-photo.jpeg)

[Original prototype photo](prototype-photo.jpeg) — supplied as `oss_demo_model.jpeg`, copied without changing its bytes.

## Unsuccessful prototype test

[Watch or download the original test video](prototype-test-not-working.mp4) — 9.79 seconds, 480 × 864 pixels. Supplied as `oss_demo_video_notworking.mp4`, copied without changing its bytes.

The robot did **not** work as intended during this test. This is a test record, not a successful sorting demonstration.

The visible sequence includes an object placed on the blue belt, belt movement, and a long metal arm changing angle across the belt. Wooden side rails, wired electronics, and a board mounted above the belt are visible. These observations do not establish successful detection, classification, routing, or accuracy.

Checksums and source basenames are recorded in [source-media.json](source-media.json).

## Intended sorting animation

[![Blender concept preview with a conveyor, camera, routing guide, and three bins](simulation-preview.png)](intended-sorting-simulation.mp4)

[Watch or download the concept video](intended-sorting-simulation.mp4) — 15 seconds, 1280 × 720, 24 fps, with no audio.

This animation was rendered in Blender. It shows intended motion: load an object, move to the camera, pause, route toward one of three bins, and reset. Its persistent on-screen label says **KINEMATIC CONCEPT / NOT A HARDWARE TEST**. Routes A/B/C and their colors are illustrative; they do not establish a trained-model label mapping. Timing and dimensions are presentation assumptions.

The [editable scene](../../hardware/mechanical/oss_simulation.blend), [generation/render instructions](../../hardware/mechanical/README.md), [native scene checks](simulation-validation.json), and [generated-file hashes](generated-assets.json) are included. This scene does not run physical dynamics, firmware, sensor emulation, or inference.
