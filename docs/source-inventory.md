# Source inventory

Recovery date: **2026-10-23**. Existing repository history and GPL license are retained. Both supplied source folders remain unchanged.

## Imported assets

| Source within asset root | Repository destination |
| --- | --- |
| Object Sorting Conveyor Readme.pdf | [Reference PDF](references/object-sorting-conveyor.pdf) |
| blender/conveyer_belt.blend | [Primary scene](../hardware/mechanical/conveyer_belt.blend) |
| blender/conveyer_belt.blend1 | [Backup scene](../hardware/mechanical/conveyer_belt.blend1) |
| blender/Untitled.png | [Conveyor render](assets/conveyor-render.png) |

All seven top-level Arduino sketches are imported with their original sketch/folder names under the purpose-based folders in the [firmware guide](../firmware/README.md).

## Imported-file changes

- OSS_CAM_TEST.ino: embedded network SSID/password replaced with YOUR_WIFI_SSID and YOUR_WIFI_PASSWORD.
- OV3660_Collect_Images_for_EdgeImpulse.ino: the same credential substitutions.
- Other imported files retain identical bytes. No control logic, pins, models, or angles were changed.

[source-inventory.json](source-inventory.json) records original and repository SHA-256 hashes, source paths, destinations, and changes. Original credentials are not stored in the inventory. Private administrative and financial materials are excluded from the public repository and its inventory.

## Libraries

The shared sketchbook libraries serve several projects. The two relevant generated libraries, **OwlV2_Test_inferencing** and **EdgeImpulse_OSS_inferencing**, are preserved in full as [model exports](../models/README.md), including examples and license notices. ZIP timestamps/container metadata are normalized; content-tree hashes verify file contents independently of ZIP packaging.

**Servo 1.3.0** and **EloquentEsp32cam 2.7.15** are documented installable dependencies. SoftwareSerial comes from the AVR core, while camera, Wi-Fi, and HTTP-server APIs come from the ESP32 core. Other installed libraries are not referenced by these seven sketches and are excluded. The JSON lists all excluded library directories and reasons, including VisioBot's gesture model, Marlin, display/sensor libraries, and Blynk.

## Recheck

```sh
python3 scripts/check_repository.py
```

When the original source folders are available, compare against them too:

```sh
python3 scripts/check_repository.py --check-sources \
  --source-root oss_assets=/path/to/oss-assets \
  --source-root arduino_sketchbook=/path/to/arduino-sketchbook
```

The optional source check verifies source hashes, exact credential substitutions, and live model-library trees without printing credentials. Repeat `--source-root NAME=PATH` for each original folder; relative override paths are resolved from the current working directory. These overrides do not modify the inventory. Without overrides, the public inventory uses `.source-assets/oss` and `.source-assets/arduino` relative to the repository root. The `.source-assets/` directory is ignored by Git. Default checks work on a clone without the original folders.

Source photos and video are recorded separately in `docs/media/source-media.json`. Generated visual assets are recorded in `docs/media/generated-assets.json` when present. The portable check validates both manifest formats and asset hashes, and rejects excluded private document paths from the public tree and Git index.
