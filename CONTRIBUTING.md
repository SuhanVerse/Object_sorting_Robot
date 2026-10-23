# Contributing

Identify the sketch and board you are changing. Keep calibration, standalone control, the paired test, and inference experiments separate unless explicitly integrating them.

Report core/library versions, compile results, and whether physical hardware was tested. Document changes to pins, UART, angles, and model labels. Compilation does not prove motion or recognition performance.

Do not commit Wi-Fi credentials, build products, or unrelated libraries. Keep private administrative and financial materials out of the public repository. Preserve third-party notices. Add clearly named revisions rather than overwriting recovered mechanical files. Deliberate changes to imported code or model exports must update repository checksums and change notes in `docs/source-inventory.json`, retaining original source hashes.

Run `python3 scripts/check_repository.py` before submitting. It validates contents and links; it does not compile or flash firmware.
