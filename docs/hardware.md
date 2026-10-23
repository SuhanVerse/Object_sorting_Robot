# Hardware and pin maps

These maps describe recovered code constants. Check physical wiring, sensor polarity, current limits, and camera identity against the assembly. No hardware was operated during organization.

## Uno conveyor pins

| Connection | Pin | Notes |
| --- | --- | --- |
| Stepper STEP | D2 | X-axis assignment used by the sketches |
| Stepper DIR | D5 | Standalone LOW; paired HIGH |
| Driver ENABLE | D8 | Active LOW |
| Servo signal | D9 | Power the servo from a suitable regulated supply |
| Start sensor | A1 | Active LOW |
| Scan-position sensor | A2 | Stops belt for decision; not an exit sensor in recovered code |
| UART RX / TX | A0 / A3 | Paired Uno only, SoftwareSerial |

Standalone sensors use INPUT_PULLUP; paired Uno uses INPUT. Check the output circuit and any external pull-ups needed. Both sketches generate pulses directly and do not use AccelStepper. D9 can be a limit input on a CNC shield; inspect shield routing instead of assuming a dedicated servo connector.

## Paired UART

| Signal | Connection |
| --- | --- |
| Camera reply | ESP32-S3 GPIO43 TX → Uno A0 RX |
| Controller request | Uno A3 TX → suitable 5 V-to-3.3 V level translation → ESP32-S3 GPIO44 RX |
| Reference | Common ground between boards and supplies |

ESP32 GPIO is 3.3 V logic: do not directly drive its input with Uno 5 V TX. The link is 115200 baud, 8N1. S3 Serial1 is separate from debug Serial.

## Camera assignments

The paired stream and inference use different board pinouts. OV2640/OV3660 sensor names alone do not identify board wiring.

| Signal | OSS_CAM_TEST: S3 | OSS_Three_Object: AI Thinker |
| --- | --- | --- |
| PWDN / RESET | -1 / -1 | 32 / -1 |
| XCLK | 15 | 0 |
| SCCB SDA / SCL | 4 / 5 | 26 / 27 |
| D0 / D1 | 11 / 9 | 5 / 18 |
| D2 / D3 | 8 / 10 | 19 / 21 |
| D4 / D5 | 12 / 18 | 36 / 39 |
| D6 / D7 | 17 / 16 | 34 / 35 |
| VSYNC / HREF / PCLK | 6 / 7 / 13 | 25 / 23 / 22 |

The collection sketch defaults to EloquentEsp32cam's AI Thinker map, with a selectable WROOM S3 map. Confirm the board before choosing either.

## Power and calibration

The reference describes 12 V motor power and a regulated 5 V module supply. Keep driver motor power separate from logic power, use common ground, and follow each module's specified input. Never connect 12 V to a 5 V/3.3 V input. Camera/servo current transients require an adequate supply; the Uno signal pin does not power the servo.

Match driver current limit and coil wiring to the actual motor/driver. Calibrate gate clearance, angles, belt direction, microstepping, and travel. The recovered sketches have no dedicated emergency-stop input or motion timeout while traveling to the scan sensor. No enclosure or stop-performance validation was performed.

See [parts](bill-of-materials.md) and [mechanical design](../hardware/mechanical/README.md).
