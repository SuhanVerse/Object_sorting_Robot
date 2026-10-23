# Recovered Edge Impulse models

Both exports were found in the Arduino sketchbook and are bundled as ZIP libraries, preserving generated model code, SDK, examples, and notices. These are repackaged installed-library snapshots, not newly downloaded deployments.

| Export | Library version | Project / deployment | Model | Labels | Top-level sketch |
| --- | --- | --- | --- | --- | --- |
| [OwlV2_Test_inferencing.zip](exports/OwlV2_Test_inferencing.zip) | 1.0.1 | OwlV2_Test, ID 1005088, deployment 1 | 96 × 96 grayscale, FOMO detection, threshold 0.5 | `0`, `1`, `2` | OSS_Three_Object |
| [EdgeImpulse_OSS_inferencing.zip](exports/EdgeImpulse_OSS_inferencing.zip) | 1.0.5 | EdgeImpulse_OSS, ID 887458, deployment 5 | 96 × 96 grayscale, FOMO detection, threshold 0.5 | `red`, `white` | None of the seven recovered sketches |

Values come from each library's `library.properties`, `src/model-parameters/model_metadata.h`, and `model_variables.h`. The exported threshold is not a validated sorting threshold. Each archive contains 1,334 files with unchanged contents.

## Installation

Use Arduino IDE's **Sketch → Include Library → Add .ZIP Library**, or extract the single top-level folder into your sketchbook's `libraries` directory and restart the IDE. See [Arduino's instructions](https://support.arduino.cc/hc/en-us/articles/5145457742236-Install-libraries-in-the-Arduino-IDE).

Install OwlV2_Test_inferencing for OSS_Three_Object. The OSS-named export is retained as project-specific evidence, but changing a header does not establish equivalent recognition or add sorting-protocol integration.

## Limits

Training images, annotations, descriptions of labels 0/1/2, training settings, evaluation reports, and a verified final model choice were not present in the supplied assets. No recognition accuracy or bin mapping is claimed. The reference PDF's proposed red/green/blue design does not match either recovered label set.

Archive and content-tree checksums are in [source-inventory.json](../docs/source-inventory.json). Run `python3 scripts/check_repository.py` from the root to validate them. Original third-party notices remain inside the archives; see [notices](../THIRD_PARTY_NOTICES.md).
