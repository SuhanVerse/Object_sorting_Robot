# Setup and operation

Choose one path from the [firmware guide](../firmware/README.md). Each sketch folder matches its `.ino` filename and opens directly in Arduino IDE.

## Uno sketches

Install Arduino IDE, **Arduino AVR Boards** through Boards Manager, and **Servo** by Arduino through Library Manager. SoftwareSerial comes with the AVR core. Recovery checks use AVR core **1.8.8** and Servo **1.3.0**.

Open the standalone, paired Uno, stepper, or servo sketch; select **Arduino Uno**; then Verify. Review [wiring](hardware.md) and calibrate before uploading. No board was flashed during recovery.

Optional CLI compilation from the repository root, after installing core and Servo:

```sh
arduino-cli compile --fqbn arduino:avr:uno firmware/standalone/OSS_NEW_TEST
arduino-cli compile --fqbn arduino:avr:uno firmware/paired/arduino_uno/OSS_UNO_TEST
arduino-cli compile --fqbn arduino:avr:uno firmware/calibration/SimpleStepperTest
arduino-cli compile --fqbn arduino:avr:uno firmware/calibration/servo_test
```

## ESP32 board support

Follow Espressif's [installation guide](https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html) to install **esp32 by Espressif Systems**. Stable Boards Manager URL:

```text
https://espressif.github.io/arduino-esp32/package_esp32_index.json
```

The recovery environment has ESP32 core **3.3.11**. The inference template's comment mentions **2.0.4**, a historical note rather than a tested guarantee. See [actual validation](validation.md).

### Streaming and dummy decisions

Open [OSS_CAM_TEST](../firmware/paired/esp32_s3/OSS_CAM_TEST/OSS_CAM_TEST.ino). Its pins describe an S3 WROOM camera layout. Select a profile matching your module and PSRAM; generic **ESP32S3 Dev Module** is a compile target, not proof of physical board identity. Camera, WiFi, and HTTP-server APIs come with the ESP32 core.

Replace YOUR_WIFI_SSID and YOUR_WIFI_PASSWORD locally. Serial Monitor at **115200** prints the browser stream address. Pair with OSS_UNO_TEST using the documented UART wiring. Wi-Fi is attempted for about 10 seconds; UART service continues even if Wi-Fi fails. The loop does not retry Wi-Fi.

The responder sends dummy decisions. Installing an inference library does not add recognition. The original camera configuration is not zero-initialized and esp_camera_init() is not checked; compilation does not validate camera startup.

### Inference

Install [OwlV2_Test_inferencing.zip](../models/exports/OwlV2_Test_inferencing.zip) via **Sketch → Include Library → Add .ZIP Library**. See [Arduino's instructions](https://support.arduino.cc/hc/en-us/articles/5145457742236-Install-libraries-in-the-Arduino-IDE).

Open [OSS_Three_Object](../firmware/vision/OSS_Three_Object/OSS_Three_Object.ino), select **AI Thinker ESP32-CAM**, and ensure PSRAM is available. Serial at **115200** prints FOMO detections for labels 0, 1, 2. Their physical meanings were not recovered.

The OSS-named export is a different two-label model, not a replacement established by changing an include. See [model notes](../models/README.md).

### Image collection

Install **EloquentEsp32cam 2.7.15** from Library Manager. Open the [OV3660 collection sketch](../firmware/data_collection/OV3660_Collect_Images_for_EdgeImpulse/OV3660_Collect_Images_for_EdgeImpulse.ino), configure Wi-Fi placeholders, and select **AI Thinker ESP32-CAM** for the default pinout. Check actual S3 wiring before changing pinout macros.

Serial at **115200** prints PSRAM status and collection-server address. The sketch uses 10 MHz XCLK to reduce OV3660 overflow. It disables brownout detection; diagnose supply issues rather than treating that as a power fix.

## Blender visualization

Open [oss_simulation.blend](../hardware/mechanical/oss_simulation.blend) in Blender **5.2.2 LTS**. It reconstructs the original model and the supplied concept: two side bins, one end bin, and a long servo sweep arm. Press Space to play frames 1–432 at 24 fps.

The [mechanical guide](../hardware/mechanical/README.md) explains retained source parts, downloaded CAD assets, nominal dimensions, and rebuilding. The [media guide](media/README.md) provides MP4/WebM downloads, an inline GIF, and a local browser player. This is a keyframed illustration; it does not run physics, firmware, or AI inference.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Belt will not start | A1 polarity/wiring, power, enable LOW |
| Belt runs past scan point | A2 output/position; no travel timeout in recovered code |
| Backward movement | DIR differs between variants; inspect wiring/mechanism |
| Wrong gate position | Angle sets differ; calibrate with servo_test |
| No UART reply | Crossed TX/RX, common ground, voltage translation, baud, SoftwareSerial reliability |
| Camera or PSRAM fails | Board pinout, PSRAM type/settings, power, core compatibility |
| Missing inference header | Install OwlV2_Test export |
| Wi-Fi fails | Credentials and network compatibility; stream makes one bounded attempt |
| Predictions print but conveyor does not respond | Inference sketch has no sorting-protocol integration |
