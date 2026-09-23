# D114 exact passive capture review

PASS_SCOPED_D114_PINNED_CAPTURE_SOURCE_AND_TESTS. No open BLOCKER, MAJOR or MINOR in this scope.
Reused separate same-model source-aware reviewer, distinct from this capture implementation and its test author. This is not a human gate or an actual upload/readout result.

- `tools/ui_adc_capture.py:259` decodes exact immutable 9892-byte inputs, preserves raw public fields, compares all original bytes and distinguishes COMPLETE128, frozen FAULT, nonterminal and unavailable evidence. Physical acceptance stays false.
- `tools/ui_adc_capture.py:136` validates timing, enums/booleans, successful source cadence, unconfigured decoder provenance and complete-summary consistency without imposing successful-source rules on failed diagnostic samples/history.
- `tools/ui_adc_capture.py:545` pins the target, helper/config/loader/tool bytes before commands. Real p0.file_hash enforces regular files and nonsymlink ancestry; first/last flash checks compare the whole loader PT_LOAD image and exact sketch package.
- `tools/ui_adc_capture.py:599` requires the exact enabled ET_REL/BSS/symbol layout. Runner raw st_value0 means relocated BSS+0, not nm VMA0x1690; full BSS9893 and Runner9892 bounds are enforced.
- `tools/ui_adc_capture.py:415` permits at most three distinct valid nodes, exact unique sketch/tail, two full Runner snapshots and unchanged list/descriptor bytes afterward. Only previously verified node addresses are revisited.
- `tools/ui_adc_capture.py:331` admits four ordered metadata commands or one internally armed MEM-AP dump_image/shutdown command. The unchanged pinned config has no Cortex target, reset, halt, write or peripheral transport path.
- The finite maximum is 22 reads, 588016 bytes and 26 commands; fixed 48/2MiB/16KiB-RAM/64-command/600s/30s ceilings remain. The 64-command branch is unreachable through the valid fixed sequence and was source-reviewed, not falsely exercised by replaying version queries.
- `tools/ui_adc_capture.py:477` counts read attempts before execution, consumes failed purposes, preserves original partial files/commands and stops without retry. VERIFIED requires both flash and mapping brackets; failed/unstable/nonterminal diagnostics never become successful acquisition.
- Frozen independent final suite `02b14721` passes 42/42 methods with zero skips in author and private reviewer runs. No capture production change occurred. Original failures and exact approved fixture amendments remain preserved: diagnostic code/path classification, exact-path normalization, real pinned loader fixtures, delegated file guards and admitted command-order/deadline stimuli.

Pins: capture `f4b3db265bdf2d5a5fdada19ed9f51a44304d9ba5da8be78e598365afa2c4444`; contract `0e8ead402ac3ddd247a986790d793d4126141d7d283e38665e6fce411c51b689`; target source `396bcc45`; final ELF `76e23fe0`; ZSK `567fb90d` (full hashes in JSON).
Evidence: `state/analysis/P2_ui_adc_probe_raw/capture_reviewer/final_review.json`, `source_findings.md`, and `private_1790201890768352679.json`.
Upload guard approval, fixed identified run record and actual deployed/ADC admission evidence remain separate. Sampled equality is not atomicity or a future lease; no calibrated timing, buttons/STOP, SC-AJ closure, WCET, physical acceptance or phase pass follows.
