# Object Sorting System (OSS)

A conveyor sorting project for embedded-systems and machine-vision experiments. An Arduino Uno drives the conveyor and servo gate; camera experiments explore object recognition with an ESP32 and Edge Impulse.

![Updated Blender visualization showing the conveyor, camera station, servo routing guide, and three bins](docs/media/simulation-preview.png)

[Watch the intended sorting animation](docs/media/intended-sorting-simulation.mp4) · [Open the editable Blender scene](hardware/mechanical/oss_simulation.blend)

*Concept simulation of intended motion. It does not demonstrate working hardware or AI accuracy.*

This repository brings together a technical reference, mechanical designs, seven Arduino sketches, and two recovered model exports. The sketches represent different experiments. **A complete camera-to-AI-to-conveyor firmware was not found:** the paired camera test sends dummy A/B/C decisions, and the inference sketch only prints predictions.

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

## Prototype photo and test video

[View the actual prototype photo](docs/media/prototype-photo.jpeg) and [the original unsuccessful test video](docs/media/prototype-test-not-working.mp4). The robot did **not** work as intended in that footage; it is retained as a test record. [Media notes](docs/media/README.md) distinguish this recording from the Blender animation.

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
