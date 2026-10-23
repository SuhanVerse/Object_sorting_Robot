# Object Sorting System (OSS)

A conveyor-based object sorting project built for **YATRA 5.0**. The design combines an ESP32 camera, an Arduino Uno, and a servo-controlled arm to sort objects into three bins.

<p align="center">
  <img src="docs/media/prototype-photo.jpeg" width="340" alt="OSS prototype with a blue conveyor belt, timber rails, camera bridge, Arduino controller, and wiring">
</p>

*The OSS prototype built for the exhibition.*

## Design

![Concept drawing showing the camera, conveyor, servo arm, two side bins, and one end bin](docs/media/oss-conceptual-model.png)

Bins A and B sit on opposite sides of the conveyor. A long servo arm directs objects into either side bin, while objects assigned to Bin C continue to the end of the belt.

## 3D model

![Sorting sequence in the Blender model](docs/media/intended-sorting-preview.gif)

*Animation of the intended sorting sequence.*

[Open the Blender model](hardware/mechanical/oss_simulation.blend)

## Firmware

The sketches cover conveyor control, camera testing, object detection, image collection, and calibration. The camera/controller demo uses test A/B/C responses; object detection runs in a separate sketch.

| Sketch | Purpose | Board |
| --- | --- | --- |
| [OSS_NEW_TEST](firmware/standalone/OSS_NEW_TEST/OSS_NEW_TEST.ino) | Standalone conveyor demo with three gate positions | Uno |
| [OSS_UNO_TEST](firmware/paired/arduino_uno/OSS_UNO_TEST/OSS_UNO_TEST.ino) | Conveyor controller with camera UART requests | Uno |
| [OSS_CAM_TEST](firmware/paired/esp32_s3/OSS_CAM_TEST/OSS_CAM_TEST.ino) | Video stream and test A/B/C replies | ESP32-S3 camera board |
| [OSS_Three_Object](firmware/vision/OSS_Three_Object/OSS_Three_Object.ino) | Object detection and prediction output | AI Thinker ESP32-CAM |
| [OV3660_Collect_Images_for_EdgeImpulse](firmware/data_collection/OV3660_Collect_Images_for_EdgeImpulse/OV3660_Collect_Images_for_EdgeImpulse.ino) | Training-image collection | AI Thinker pinout by default |
| [SimpleStepperTest](firmware/calibration/SimpleStepperTest/SimpleStepperTest.ino) | Stepper direction and movement checks | Uno |
| [servo_test](firmware/calibration/servo_test/servo_test.ino) | Servo angle calibration through Serial Monitor | Uno |

See the [firmware guide](firmware/README.md) for dependencies and details about each sketch.

## Getting started

```sh
git clone https://github.com/SuhanVerse/Object_sorting_Robot.git
cd Object_sorting_Robot
```

1. Install Arduino IDE, **Arduino AVR Boards**, and the **Servo** library by Arduino.
2. Open `firmware/standalone/OSS_NEW_TEST/OSS_NEW_TEST.ino` and select **Arduino Uno**.
3. Check the [wiring and pin assignments](docs/hardware.md), calibrate the arm, and upload the sketch.

In the standalone demo, the start sensor begins belt movement. The scan sensor pauses the belt, the arm selects the next gate position, and the belt moves the object onward.

Camera setup and library installation are covered in the [setup guide](docs/setup.md). Configure the Wi-Fi placeholders in your local copy before using a network sketch.

## Documentation

- [Hardware and wiring](docs/hardware.md) and [parts list](docs/bill-of-materials.md)
- [3D model files and animation](hardware/mechanical/README.md)
- [Edge Impulse models](models/README.md)
- [System architecture](docs/architecture.md)

## License

[GNU GPL v3](LICENSE). See [third-party notices](THIRD_PARTY_NOTICES.md) for included assets and dependencies.
