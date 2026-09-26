# D222 completed native commissioning build matrix

All 14 fixed-profile variants returned COMPILE_CHECKED on the connected UNO Q. Each used exactly one property query and one compiler process, 25 successful transports and nine passing closing checks. No image was uploaded.

Original firmware source SHA256: `9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a`. This matrix predates D224 session changes and is not qualification of later firmware. Static/default startup and MATCH0 apply throughout. M1 compilation grants no motor-run permission.

| Profile | Motors allowed | Package bytes | Package SHA256 | Evidence commit |
|---|---:|---:|---|---|
| b4_stand | 0 | 82912 | `84667b0a22ff7701059a266b6c82bb61de1f7ccec96280e4f13b5692bf785a28` | `56fb7aba` |
| b4_stand | 1 | 83284 | `b9ecf795d0293f2200c7b824570f655aeff099852ee186f2ae1dc40f88ffd232` | `07b47afb` |
| p3_drive | 0 | 85688 | `611521a497ed7b51c8f93b1f698c1111c2e7eb04b291e72c0818837f2db181af` | `7779f818` |
| p3_drive | 1 | 86056 | `25f29f1b35eff9ef2ff5b0b3909606552983f150aa3b5aca783128d0a6b91c50` | `3d7ce7ef` |
| p3_turn | 0 | 84748 | `b0312eb72ee1ff7be86d6903f6658e4b555764fd7d3fc43b6e8648a7ff0ba063` | `57b45d1c` |
| p3_turn | 1 | 85120 | `e647b0bb49c79011cd570fc4dc9ad7ba665c09aa48f1d57e75fb6f1dc9458517` | `3c8d3506` |
| p3_stop | 0 | 84308 | `6da22c0bc788346d94660fbb1852d42b92d26aab5cf0cd2162f57bb88d0ea57a` | `d2f58113` |
| p3_stop | 1 | 84680 | `ff7a25580d89e97b2419c676d09e092d277790bf8c1b1f538215e4259df0bd47` | `90a97dc4` |
| p4_reactive | 0 | 89616 | `c2ef5a2bf86c9f880510540d21bc62b34b8400353e96b52c24fcce5b02ad0c23` | `3b4525b6` |
| p4_reactive | 1 | 89984 | `8b6973c5224ded6193ca531ad8a9600e1411adc9eef3ccfaac16777e1e1aaa50` | `02d5cdc5` |
| p4_timing | 0 | 90888 | `0ee572efad35fc8e115e85e1012170f4de320213d45afe42799f0b2c9d1ac4ab` | `de552914` |
| p4_timing | 1 | 91256 | `c2c747b406c5a0b88c7bf07a7ef81ad0a3e48b06091976f1a3f078b0263426a5` | `4e1cb04c` |
| p5_abort_timing | 0 | 94496 | `eeb641564a0ad027e49f846c332d603ce6d17223a2770ff63dff7d07fab4be87` | `ab830648` |
| p5_abort_timing | 1 | 94872 | `d330d5ba809221224a4313063e7934c970a5ab6e730eba7a76b678c214dac5b6` | `c29e7bba` |

The separate reviewer manually reconciled the first eleven closures. After the final three closed, root executed the reviewer-authored unchanged reconciler across all fourteen before changing main source. It checked 134 current/Git input files and 104 staged files per tuple, flags/paths/commands, child/transport closure, native ELF/TLS/layout/package reports and the sequential evidence-commit chain. All checks passed; maximum command length was 29376 UTF-16 units. Raw summary and exact reconciler are in `P7_commissioning_build_raw/matrix_closure01`. The reviewer then independently reconciled the final three historical HEAD/stage records and all 28 result/artifact hashes; FINAL PASS is recorded in `../reviews/P7_commissioning_build_actual_review.md` (SHA256 22264320f6b86aeafb75f155495356f78897007215ffc441acb4a60d602f97ab).

The 94352-byte structural RAM tail reported for each variant is a linker-layout result, not measured runtime stack/heap headroom. Reports contain board-side artifact hashes; this audit did not newly retrieve artifact bytes or run the MCU. Separate outer check-only outputs exist in the tool transcript, not duplicated saved receipts. Sensor/motor acceptance, initialized timing/memory and human gates remain open.
