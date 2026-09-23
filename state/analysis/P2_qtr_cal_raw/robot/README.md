# D089 Robot implementation evidence

2026-09-23. Scope: implement actual Robot raw-only BOOT/IDLE admission, source
identity preservation, distinct later-source threshold handover and fresh START
rearming. Root owns public contracts, adapter, aggregate testing and decisions.

Modified production files: `src/core/fsm_line.cpp`, `src/core/fsm_robot.cpp`,
new `src/core/fsm_qtr_cal.cpp`, and private declarations/state in `src/core/fsm.h`.
No established or locked test was changed. No native, board, upload or motor run.

Validation:

- Strict C++17 syntax with `-Wall -Wextra -Wpedantic -Werror -fno-exceptions
  -fno-rtti`: exit 0. Empty `syntax_final.txt` means no compiler diagnostics.
- Isolated CMake build of `sumox26_tests`: exit 0 (`configure.txt`, `build.txt`).
- Existing focused filter `*D085*,*D087*,*Robot*`: 143 cases and 1,951,544
  assertions passed (`focused_existing.txt`); 1,081 unrelated cases skipped.
- Supplemental actual-Robot implementation probe: five cases, 6,464 assertions
  passed (`handover_probe.cc`, `probe_build.txt`, `probe_results.txt`). It covers
  raw START suppression followed by the entire 5100ms hold, cached bank handover,
  uninterrupted BOTH/STOP timing across rearming, raw absence/full-wrap replay
  rejection, active countdown rejection and native-invalid evidence rejection.
- `source_hashes.json` records source snapshots and confirms LF on all four files.

Limits: probes supply synthetic evidence and synthetic application receipts.
They do not prove physical source timing, threshold quality, native sensor or
MotorGate operation, full scheduler timing, board runtime or a human phase gate.
Independent adapter/Robot/Calibration/MotorGate pipeline tests and nondefault
confirmation variants remain with the root's separate test author.
