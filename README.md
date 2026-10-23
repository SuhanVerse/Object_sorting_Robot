# Object Sorting System (OSS)

A conveyor-based object-sorting project built as an exhibition project for **YATRA 5.0**, a national event. An Arduino Uno controls the belt and servo; ESP32 camera experiments provide image collection and object-recognition work.

<p align="center">
  <img src="docs/media/prototype-photo.jpeg" width="340" alt="The real OSS exhibition prototype: blue belt, timber rails, camera bridge, Arduino controller, and wiring">
</p>

*The physical prototype built for the exhibition. The [original hardware test video](docs/media/prototype-test-not-working.mp4) records a test when it did not work as intended.*

## Intended mechanism

![Original Excalidraw concept: camera over the input, side-mounted servo sweep arm, bins A and B on opposite sides, and bin C at the end](docs/media/oss-conceptual-model.png)

The drawing places **Bin A on one side of the conveyor, Bin B on the other, and Bin C at the end**. A long arm driven by a side-mounted servo moves objects into the side bins; objects assigned to C continue to the end.

## Reconstructed Blender model

[![Animation reconstructed from the original conveyor model and the concept drawing](docs/media/intended-sorting-preview.gif)](https://github.com/SuhanVerse/Object_sorting_Robot/raw/refs/heads/main/docs/media/intended-sorting-simulation.mp4)

The original frame, loop belt, rollers, bearings, camera bridge, NEMA17, and servo meshes are retained. Downloaded IR sensor and Freenove board models supply the electronics detail. The [reconstruction notes](hardware/mechanical/reference-analysis.md) record measured source geometry, changes, and assumptions.

[Download MP4](https://github.com/SuhanVerse/Object_sorting_Robot/raw/refs/heads/main/docs/media/intended-sorting-simulation.mp4) · [Download WebM](https://github.com/SuhanVerse/Object_sorting_Robot/raw/refs/heads/main/docs/media/intended-sorting-simulation.webm) · [Editable Blender scene](hardware/mechanical/oss_simulation.blend)

The GIF plays directly in this README. To use the browser player after cloning, run `python3 -m http.server 8765` from the repository root and open [http://localhost:8765/docs/media/player.html](http://localhost:8765/docs/media/player.html). GitHub's repository file links are downloads, not an embedded video player.

*The 18-second animation illustrates intended motion. It is keyframed, with no physical dynamics, firmware, or inference solver running.*

The repository includes seven Arduino sketches and two recovered model exports. A complete AI-to-conveyor firmware was not found: the paired camera test sends dummy A/B/C decisions, while the inference sketch prints predictions. See the [architecture](docs/architecture.md) for current implementation status.

## Which code should I use?

| Task | Sketch | Board |
| --- | --- | --- |
| Run the conveyor without a camera; cycle through three gate positions | [OSS_NEW_TEST](firmware/standalone/OSS_NEW_TEST/OSS_NEW_TEST.ino) | Uno |
| Test the conveyor with camera UART requests | [OSS_UNO_TEST](firmware/paired/arduino_uno/OSS_UNO_TEST/OSS_UNO_TEST.ino) | Uno |
| Stream video and reply to that Uno with dummy A/B/C decisions | [OSS_CAM_TEST](firmware/paired/esp32_s3/OSS_CAM_TEST/OSS_CAM_TEST.ino) | ESP32-S3 camera board |
| Run the recovered three-label model and print detections | [OSS_Three_Object](firmware/vision/OSS_Three_Object/OSS_Three_Object.ino) | AI Thinker ESP32-CAM pinout |
| Collect camera images for Edge Impulse | [OV3660_Collect_Images_for_EdgeImpulse](firmware/data_collection/OV3660_Collect_Images_for_EdgeImpulse/OV3660_Collect_Images_for_EdgeImpulse.ino) | AI Thinker pinout by default |
| Check stepper direction and movement | [SimpleStepperTest](firmware/calibration/SimpleStepperTest/SimpleStepperTest.ino) | Uno |
| Find servo angles using Serial Monitor | [servo_test](firmware/calibration/servo_test/servo_test.ino) | Uno |

Read the [firmware guide](firmware/README.md) for behavior, pairing, dependencies, and limitations. Original sketch names are retained so they remain recognizable in Arduino IDE.

## Start with the standalone conveyor

```sh
git clone https://github.com/SuhanVerse/Object_sorting_Robot.git
cd Object_sorting_Robot
```

1. Install Arduino IDE, **Arduino AVR Boards**, and **Servo** by Arduino. The recovery checks use AVR core 1.8.8 and Servo 1.3.0.
2. Open `firmware/standalone/OSS_NEW_TEST/OSS_NEW_TEST.ino` and select **Arduino Uno**.
3. Verify the sketch. Before uploading, check the [pin map and power connections](docs/hardware.md) and calibrate the gate for your assembly.
4. An active-low start sensor starts the belt. The scan sensor pauses it, the gate cycles through 45°, 135°, and 180°, and the belt advances 3,000 pulses before returning to idle. These positions are test settings, not recognized object classes.

Use the [setup guide](docs/setup.md) for camera boards, library installation, and compile commands. Wi-Fi credentials in the two network sketches are placeholders; configure your local copies before use.

## Project contents

- [Hardware and wiring](docs/hardware.md), [bill of materials](docs/bill-of-materials.md), and [system architecture](docs/architecture.md).
- [Animated Blender scene, generation script, and original backup](hardware/mechanical/README.md).
- [Edge Impulse exports and model labels](models/README.md).
- [Technical reference](docs/references/README.md), with intended features distinguished from recovered code.
- [Source inventory](docs/source-inventory.md), including checksums and credential substitutions.
- [Validation results and remaining gaps](docs/validation.md).

To check the repository contents without connecting hardware:

```sh
python3 scripts/check_repository.py
```

The original folders were left unchanged. The existing [GPL v3 license](LICENSE) is retained; third-party notices inside the sketches and model exports remain in place. See [third-party notices](THIRD_PARTY_NOTICES.md). Contributions should identify the board and sketch tested; see [CONTRIBUTING.md](CONTRIBUTING.md).
