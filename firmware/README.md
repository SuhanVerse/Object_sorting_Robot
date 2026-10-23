# Firmware guide

Each directory contains a separate Arduino sketch. Open one `.ino` at a time; do not combine all seven into one program. This classification is based on recovered source. Copies retain their original code apart from Wi-Fi credential placeholders in two files. See [validation](../docs/validation.md) for compile results; hardware behavior has not been tested during recovery.

## Standalone conveyor: start here

[OSS_NEW_TEST](standalone/OSS_NEW_TEST/OSS_NEW_TEST.ino) runs on an Uno with a step/direction driver, two active-low sensors, and a servo. It needs **Servo** and has no camera, UART, or recognition dependency.

`IDLE → MOVING → SCANNING → DISPATCHING → IDLE`:

- Start sensor A1 enables the driver; scan sensor A2 stops step pulses.
- Each scan selects the next gate angle: 45°, 135°, 180°. Initial/idle angle is 180°.
- After a 600 ms servo delay, 3,000 pulses move the object onward. Each pulse has 800 µs high and 800 µs low time: about 4.8 seconds plus overhead.
- DIR is LOW and ENABLE is active LOW. Serial is intentionally unused.

This is the simplest recovered conveyor demonstration. Its filename does not establish that it is final production firmware.

## Paired controller and camera test

Use these two sketches together, on different boards:

| Role | Sketch | Dependencies |
| --- | --- | --- |
| Actuator controller | [OSS_UNO_TEST](paired/arduino_uno/OSS_UNO_TEST/OSS_UNO_TEST.ino) | Servo; AVR core's SoftwareSerial |
| Video stream and dummy decision responder | [OSS_CAM_TEST](paired/esp32_s3/OSS_CAM_TEST/OSS_CAM_TEST.ino) | ESP32 core camera, WiFi, and HTTP server |

The Uno moves from the start sensor to the scan sensor, stops step pulses, and transmits `?`. The S3 replies with the next single byte A, B, or C, cycling regardless of the image. A browser can view MJPEG at the printed `http://<ip>/` address when Wi-Fi connects.

| Protocol item | Recovered value |
| --- | --- |
| Link | 115200 baud, 8N1; no newline framing |
| Uno RX / TX | A0 / A3, SoftwareSerial |
| S3 RX / TX | GPIO44 / GPIO43, Serial1 |
| Request / response | `?` / next `A`, `B`, or `C` |
| Uno gate angles A / B / C | 0° / 50° / 140° |
| No response | After 3,000 ms, reject angle 90° |
| Dispatch | About 4 seconds by timer, including the preceding 600 ms servo wait because the timestamp precedes that wait |
| Idle angle | 140° |

The Uno uses DIR HIGH and 1,200 µs per half pulse. These settings differ from the standalone sketch. There is no recovered mapping between A/B/C, model labels, colors, and physical bins.

SoftwareSerial at 115200 can be unreliable on an Uno. The controller treats any received byte as a completed response: an unexpected byte leaves the previous angle and still starts dispatch. It does not explicitly flush stale replies. These limitations are preserved.

## Camera inference experiment

[OSS_Three_Object](vision/OSS_Three_Object/OSS_Three_Object.ino) includes **OwlV2_Test_inferencing.h**, not `EdgeImpulse_OSS_inferencing.h`. Install the matching [model export](../models/README.md).

Its selected pinout is `CAMERA_MODEL_AI_THINKER`. It captures QVGA JPEG, converts to RGB888, resizes, runs inference, and prints results at 115200. The supplied model is FOMO object detection with 96 × 96 grayscale input and labels `0`, `1`, `2`. There is no actuator control or `?`/A/B/C responder.

The source comment names ESP32 core 2.0.4 as a template baseline, not a verified version for this recovery. The classifier-error path returns before freeing the snapshot buffer; repeated errors can consume memory. The original Edge Impulse example notice remains intact.

## Image collection

[OV3660_Collect_Images_for_EdgeImpulse](data_collection/OV3660_Collect_Images_for_EdgeImpulse/OV3660_Collect_Images_for_EdgeImpulse.ino) uses **EloquentEsp32cam 2.7.15** and a browser collection server. It requests 240 × 240 images, slows XCLK to 10 MHz, uses low JPEG quality, flips vertically, and adjusts OV3660 brightness/saturation. Serial at 115200 prints the collection URL.

The default is AI Thinker pinout: `USE_AITHINKER_PINOUT=1`, `USE_WROOM_S3_PINOUT=0`. Check the actual board before changing the macros. It collects images rather than performing inference or conveyor control. Wi-Fi/camera/server initialization retry indefinitely.

## Calibration tools

| Sketch | Use | Details |
| --- | --- | --- |
| [SimpleStepperTest](calibration/SimpleStepperTest/SimpleStepperTest.ino) | Check motor/driver independently | D2 STEP, D5 DIR, D8 ENABLE; 800 pulses forward, 1 second wait, 800 reverse, 1 second wait. Driver stays enabled. Four revolutions assumes 200 steps/revolution at full stepping; microstepping changes that. |
| [servo_test](calibration/servo_test/servo_test.ino) | Find gate positions | D9 servo, initial angle 90°. Serial at 115200 accepts integers 0–180. It uses parseInt(), so malformed input can become 0. |

## Integration still missing

Automatic AI sorting needs a chosen board/model, verified class-to-bin mapping, inference-to-UART integration, and hardware validation. The sketches do not implement a dedicated emergency-stop input or LCD interface. See [architecture](../docs/architecture.md).
