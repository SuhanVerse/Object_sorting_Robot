# Bill of materials

This technical parts guide is based on recovered code and the technical reference; it is not a verified as-built inventory. Choose the camera board matching your sketch.

| Part | Quantity | Role |
| --- | --- | --- |
| Arduino Uno | 1 | Conveyor and calibration sketches |
| NEMA17 stepper | 1 | Belt drive in camera-based design |
| STEP/DIR driver, described as A4988 in reference | 1 | D2 STEP, D5 DIR, D8 ENABLE |
| CNC Shield V3 or equivalent wiring | Optional | Named by standalone sketch; direct wiring can expose the same pins |
| SG90 or suitable position servo | 1 | Diverter; calibrate load and travel |
| Digital sensors, described as IR modules in code | 2 | Start and scan position |
| ESP32 camera board with PSRAM | 1 for camera experiments | AI Thinker for default inference/collection; S3 layout for paired streaming |
| USB/programming interface | As needed | Depends on board |
| 12 V DC supply | 1 | Motor power; capacity depends on load |
| Regulated 5 V supply/buck converter | 1 | Camera, servo, compatible modules |
| UART level translation | At least 1 channel | Uno TX to ESP32 RX |
| Decoupling, wiring, connectors | As needed | Match actual driver/supply specifications |
| Belt, rollers/PVC, shafts, bearings, coupling, frame, fasteners | As needed | Dimensions are not validated fabrication drawings |

Verify component ratings and the actual assembly before selecting parts. See [implementation status](architecture.md) for differences between the technical reference and recovered code.
