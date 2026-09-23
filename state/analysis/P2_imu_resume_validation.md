# D094 resumable IMU validation

2026-09-23 Asia/Dubai. Contract commit `e507c42`; previous checkpoint `2f0981c`.
Active P2 software under D051/D075. IMPLEMENTED / HOST-TESTED / TARGET-COMPILED;
fresh review disposition is recorded in `state/reviews/P2_imu_resume_review.md`.
Final scoped review PASS with no open BLOCKER, MAJOR or MINOR. The one MAJOR was
fixed and independently verified; this is separate same-model review, not cross-model.
Physical timing, sensor acceptance, actual app integration and human gates remain
pending. The full P0-P7 goal remains ACTIVE, incomplete.

## Implemented boundary

The existing Bus and Acquirer now support bounded runtime advances. Each native
advance performs at most one guarded protocol action with at most three counted
observation passes; cleanup retains its separate existing bound. All advances and
caller interleaving share the original 600 us exclusive wall-clock deadline and
8192-observation budget. The 8192nd observation is allowed; attempting another
fails. No value in config.h, established test, core behavior or motor backend changed.

Pending envelopes carry no sample. A terminal pulse admits one completed source
to the estimator; actual source timestamps, sequence, gap and silence checks remain.
Explicit cancellation and supported mixed legacy calls terminate the native owner
once. Legacy invalid requests still perform no work; ordinary idle legacy behavior
and isolated legacy linkage remain valid. No allocation, background service, new
clock source, retry, bus router or unmeasured scheduling allowance was added.

The public contract visibly amends D079/D081 and records two clarifications:
the existing poll boundary above, and malformed IDLE/unknown response states must
cancel rather than claim native termination. A true COMPLETE/FAULT envelope keeps
the original nonOK transport precedence. Preserved failures and the single
production correction are detailed in `P2_imu_resume_failures.md`.

## Executed host evidence

Exact arguments, exits, tool versions, source hashes and outputs are retained in
`P2_imu_resume_raw/` (abbreviated `raw/` below). WSL g++13.3.0, CMake3.28.3,
Python3.12.3 and Git2.43.0 were
observed this turn; sanitizer build uses AddressSanitizer and UndefinedBehaviorSanitizer.

- Full normal and sanitizer suites each pass 1349 main cases / 24,501,424 assertions
  plus 111 enabled-MotorGate cases / 3,850,460 assertions, with no failures/skips.
  See `host_normal_03`, `host_sanitized_03`, exact final LastTest logs and
  `host_final_counts.json`. Earlier failed runs remain separately named.
- Independent public-contract author: 22 Acquirer/Estimator/Robot cases / 17,259
  assertions pass in both motor configurations under UBSan. Actual native resume
  tests pass 21 cases / 728 parent assertions; 44 established native cases / 932
  parent assertions pass unchanged. Process-isolated child assertions are enforced
  but these summary numbers count parent assertions only.
- Current actual probe constructors/setup/10,000 empty loops pass 1 case / 13
  assertions in each motor configuration. Eight upload combinations refuse before
  target or transport lookup. All five new Python methods have successful executions
  in `raw/author`; they are controlled host tests, not physical board measurements.
- All 61 established controlled tool methods pass, covering staging, arguments,
  SSH/ADB transport, compile/upload separation and matrix/recorder upload guards;
  see `tools_regression_01`.
- Fresh separate same-model reviewer independently exercises event disappearance,
  the exact cumulative poll boundary and malformed/terminal response precedence.
  Native 4 cases / 48 parent assertions and Acquirer ASan/UBSan 2 cases / 156
  assertions pass. Review fixes and final disposition belong to the separate report.

## Actual target build and identity

Bare UNO Q is visible over ADB serial2629958581. Actual board-Linux compile-only
`bench/p2_imu_resume_compile`, FQBN `arduino:zephyr:unoq`, pinned core1.0.0,
MATCH0/MOTORS_ALLOWED0/default startup exits0 for source:

`b495f085a5e9d0277e0837b5fdf1e8da32f7149e0be3945bc706ebb9e85ec485`

Compiler reports 330844 program bytes and 247564 global bytes, leaving 14580 nominal
bytes with the low-memory warning preserved. These are compiler estimates, not
loaded free RAM, minimum heap or measured stack use. The earlier successful
`d1d724dc` compilation predates the cancellation fix and is superseded, not final evidence.

78 current/staged/target source files and all three ELF artifacts are checked in
`raw/source_integrity.json` and `raw/target_b495f085_bench-default.json`. Actual native
Bus/Acquirer, estimator/projection, Robot, native MotorGate and AttemptRecorder
methods are retained. The strong loop hook is empty. The sketch only stores an
exercise pointer at setup; its loop and global construction perform no peripheral
operation. All188 undefined imports and loader hash are unchanged from D092;
40native and42AEABI exports are nonzero with no missing math symbol. Independent
review verified the loader/export and constructor evidence, including all13 init
array entries and the retained native/probe startup paths. See its target identity
receipt and disassembly/relocation excerpt.
Final Git-index audit matches all78 compiled source bytes and108 raw evidence files
exactly (`raw/index_integrity.json`, excluding that receipt's self-hash). Established
tests, core sources and config.h are unchanged against `2f0981c`.

Seven existing inert manifest values were independently reconstructed, then matched
against actual Windows staging before refresh (`raw/manifest_refresh.json`). No
new upload key exists for this probe, and no upload/reset/MCU operation occurred.
The previously deployed D091 source1502e948 remains the last known MCU image;
its synthetic200s recorder measurements do not validate this source or full HAL.

## Next task and limitations

`P2_app_schedule_dependencies.md` now records a fresh public-interface integration
map. The app remains an inert scaffold. Next freeze the fixed app transaction and
resource-admission contract: setup/readiness, QTR sub-tick service, IMU progress,
ADC grants, truthful retained/expired evidence, actual Gate/recorder receipts and
failure cleanup. Every executed service must belong to D092's complete interval.

No result here establishes a useful IMU service cadence, physical clock stretching,
QTR color separation, full <800 us WCET, loaded RAM minimum, native UART framing,
button circuit/windows, physical motor safety, PINMAP/EXPLAINED or a human gate.
No extra hardware is requested now. Preserve original deadlines and continue the
eligible software task without repeating this completed validation.
