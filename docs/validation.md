# Validation results

Checked **2026-10-23**. This records repository recovery and compilation, not physical-system acceptance.

## Firmware compilation

All seven recovered sketches compiled successfully using Arduino CLI **1.4.1**, AVR core **1.8.8**, ESP32 core **3.3.11**, Servo **1.3.0**, and EloquentEsp32cam **2.7.15** where used. The inference build used OwlV2_Test_inferencing **1.0.1** extracted from the repository's ZIP.

| Sketch | FQBN | Result | Flash / static RAM bytes |
| --- | --- | --- | --- |
| OSS_NEW_TEST | arduino:avr:uno | PASS | 2,488 / 54 |
| OSS_UNO_TEST | arduino:avr:uno | PASS | 4,880 / 388 |
| SimpleStepperTest | arduino:avr:uno | PASS | 1,052 / 9 |
| servo_test | arduino:avr:uno | PASS | 3,636 / 417 |
| OSS_CAM_TEST | esp32:esp32:esp32s3:PSRAM=opi | PASS | 957,362 / 55,816 |
| OSS_Three_Object | esp32:esp32:esp32cam | PASS | 452,565 / 41,916 |
| OV3660_Collect_Images_for_EdgeImpulse | esp32:esp32:esp32cam | PASS | 1,069,029 / 62,280 |

Machine-readable results are in [compile-results.json](validation/compile-results.json). Builds ran in an isolated temporary directory, without installing or changing the original sketchbook's libraries. No binary files are committed. The S3 OPI PSRAM compile target is an explicit test setting; it does not identify the physical module or its memory type.

Reproduce Uno commands from [setup](setup.md). Camera compile commands, after installing the matching core and libraries:

```sh
arduino-cli compile --fqbn esp32:esp32:esp32s3:PSRAM=opi firmware/paired/esp32_s3/OSS_CAM_TEST
arduino-cli compile --fqbn esp32:esp32:esp32cam firmware/vision/OSS_Three_Object
arduino-cli compile --fqbn esp32:esp32:esp32cam firmware/data_collection/OV3660_Collect_Images_for_EdgeImpulse
```

## Repository checks

```sh
python3 scripts/check_repository.py
python3 scripts/check_repository.py --check-sources \
  --source-root oss_assets=/path/to/oss-assets \
  --source-root arduino_sketchbook=/path/to/arduino-sketchbook
git diff --cached --check -- . ':!firmware/**/*.ino'
```

The Python check covers imported-file hashes, both ZIPs and their 2,668 preserved member files, seven sketch/folder names, Wi-Fi placeholders, local Markdown targets, and code-fence balance. It validates the source-media manifest's metadata and hashes, and validates generated-asset paths and hashes when their manifest exists. It also rejects excluded private document paths in the working tree and Git index.

The optional source check compares the original files, verifies only the documented credential substitutions, and compares both original model trees. Supply local folder paths using the repeatable `--source-root NAME=PATH` option, or use the ignored placeholder folders described in the [inventory](source-inventory.md). Overrides do not rewrite the public inventory. Imported sketches retain their original whitespace, including trailing spaces; the staged whitespace check excludes those preserved files. GitHub Actions runs the portable check on pushes and pull requests; it does not compile firmware.

The supplied render, actual prototype photo, and contact sheet of the unsuccessful test video were visually inspected. The retained technical reference was reviewed by text extraction. The original Blender scene opens in Blender 5.2.2 LTS but has missing texture dependencies. Its source bytes are preserved. The new visualization uses procedural materials and no external image dependencies.

## Blender visualization

The [updated scene](../hardware/mechanical/oss_simulation.blend) was created and reopened in Blender **5.2.2 LTS**. [Native scene validation](media/simulation-validation.json) checks 360 frames at 24 fps, the presentation camera, scan-position holds, three final bin positions, and absence of external image dependencies or scripted drivers. It explicitly does not validate physics, collision clearance, electrical behavior, firmware timing, or AI accuracy.

The [concept video](media/intended-sorting-simulation.mp4) is rendered at 1280 × 720 for 15 seconds with a persistent simulation label. It is separate from the original [unsuccessful prototype test](media/prototype-test-not-working.mp4). See the [media guide](media/README.md) for provenance and checksums.

## Remaining gaps

- No hardware was flashed, energized, or moved. Power, pinout, camera startup, sensor operation, UART reliability, servo calibration, motion limits, and timing remain to be validated on the actual assembly.
- AI predictions are not connected to the recovered paired controller. No accuracy, recognition-to-bin mapping, or unattended-operation claim is made.
- Measured fabrication dimensions, complete training data, and a final model choice remain unavailable. The new animation uses nominal dimensions and presentation timing.
- The original source's runtime limitations are documented in the [firmware guide](../firmware/README.md) and [setup](setup.md); organization did not silently change control behavior.
