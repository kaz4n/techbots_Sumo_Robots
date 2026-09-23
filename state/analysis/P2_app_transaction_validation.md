# D095 actual application transaction validation

2026-09-23 Asia/Dubai. Baseline `1b5bc3a`, public contract `c17f6d6`.
Active P2 software under D051/D075. IMPLEMENTED / HOST-TESTED / TARGET-COMPILED.
Fresh separate same-model review PASS with no open BLOCKER, MAJOR or MINOR:
`state/reviews/P2_app_transaction_review.md`. This is not cross-model review.
The full P0-P7 objective remains ACTIVE; physical acceptance and all human gates
remain pending. This implements the actual transaction owner, not the native
source scheduler or the currently inert app.ino runtime.

## Implemented behavior

`app::Transaction` owns the actual Robot, MotorGate and AttemptRecorder. It records
real acquisition-start, decision, application and completion times, replaces
caller-provided timing/previous-receipt fields, and invokes each production
component once per admitted epoch. Closing a valid epoch supplies its actual
complete duration to the next real Robot decision. The final stopped decision
requires a real later tail epoch to seal deferred evidence.

Invalid order, clock or identity terminally inhibits through the new non-token
`MotorGate::halt`. It preserves diagnostic token/time/duty while invalidating
ordinary acknowledgement, and interrupts active recording without inventing a
Robot reset, new decision or sealed attempt. Halt attempts all zero writes and
settle once; repeated calls are passive. An explicit successful existing Gate
reset clears its halt cache; the application owner has no reset API.

Ordinary 800/1000 us timing retains B14 count/log behavior. No timing threshold,
config value, core strategy, established test or source admission was changed.
Shared app sources stage under `src/app`; sketch-local shadowing fails before
transport. A new compile-only probe retains the actual owner and native motor
backend but setup stores a function pointer only. It has no inert upload key.

## Actual host verification

Exact argv, exit status, tool versions, hashes and original failures are in
`P2_app_transaction_raw/`. WSL g++13.3.0/CMake3.28.3/Python3.12.3/Git2.43.0
were observed; sanitizer build enables AddressSanitizer and UndefinedBehaviorSanitizer.

- Full normal and sanitizer runs each pass 1377 main cases /25,118,683 assertions
  plus 139 enabled-MotorGate cases /4,467,720 assertions, zero failures/skips.
  See `host_normal_02`, `host_sanitized_02`, copied final LastTest logs and
  `host_final_counts.json`.
- Independent public-contract author passes 28 new cases /617,259 assertions in
  default mode and /617,260 enabled, under strict C++17/UBSan. Nine new halt cases
  become established locked tests with this implementation commit. The author
  did not inspect production CPP bodies; no existing locked test was changed.
- The 200-second host simulation executes 200000 actual owner epochs plus the
  real final tail, retains 5001 frames and 194901 GO-through-STOP timing members,
  and reports no lost evidence. Synthetic clocks/sensors are not MCU measurements.
- Actual native probe constructor/setup/10000 empty loops and 1000 owner cycles
  plus terminal abort pass two cases/nine assertions in each motor configuration,
  including allocation/deallocation silence. Eight controlled upload combinations
  refuse before target/transport lookup. Eight new Python methods have passing
  evidence, six together and two additive; see `author/README.md`.
- Existing Gate/native backend regressions pass unchanged in both motor modes;
  exact commands/counts are in `halt_worker/summary.md`. Worker transaction smoke
  and its preserved initial compiler error are in `transaction_worker/`.
- All61 established controlled tool methods pass, including actual local staging,
  arguments, compile/upload separation and SSH/ADB/inert-upload guards. See
  `tools_regression_01`; its simulated upload messages are fixture output only.
- The fresh reviewer independently passes 47703 checks per motor setting with
  ASan/UBSan, including1458 S/D/A/C combinations each and a real dense GO/STOP/tail
  host lifecycle. Its source audit independently verifies startup and all80 files.
  A reviewer aggregate-hash sorting mistake is preserved and corrected to Windows
  Path ordering; no source or expected checksum changed.

Initial full runs found only two provisional author expectations: common S..C
half-range invalidity is CLOCK, and a sparse countdown fixture had really skipped
recording frames. The author corrected the enum expectation and used a genuine
1kHz countdown while retaining the no-loss assertion. Original full/scoped
failures remain. The unsupported doctest expression and over-specific diagnostic
substring were also corrected before test establishment. No production behavior
or old assertion changed to obtain a pass. See `author/README.md` for exact receipts.

## Actual target compilation

Board Linux compile-only through ADB serial2629958581, pinned core1.0.0/FQBN
`arduino:zephyr:unoq`, MATCH0/MOTORS_ALLOWED0/default startup exits0 for:

`9d6c0005a3708df1df8f8d9dc885d1fbcd595aad97b90ad3826b20484116580a`

Compiler reports 149120 program bytes and 238628 global bytes, leaving 23516
nominal bytes with its low-memory warning preserved. These are compiler estimates,
not loaded RAM, stack headroom or measured worst-case timing. This smaller probe
does not retain every native sensor owner and is not a full-application RAM result.

`source_integrity.json` checks 80 current/staged/target files and three ELF
artifacts. Final `index_integrity.json` additionally matches all80 compiled source
files and113 raw evidence files to exact Git-index bytes (excluding its self-hash).
All188 imports and loader hash are unchanged from D092;40 native and42
AEABI exports are present/nonzero, with no missing math symbol. Target receipts
retain init-array relocations and startup assembly. `target_startup_additive.json`
adds actual main/startup disassembly with relocations without overwriting the
original audit. Independent review records its own final interpretation.

Seven existing inert source trees were independently reconstructed and matched
against actual Windows staging, per-file and aggregate, before refreshing only
their seven existing manifest values (`manifest_refresh.json`). No new key,
upload, reset, MCU execution, sensor or motor operation occurred. The last known
deployed MCU image remains D091 source1502e948; its synthetic measurements apply
only to that older image.

## Remaining integration

Next select and freeze native source scheduling/resource admission under D051,
then independent tests and implementation using this owner. Setup truth, QTR
charge/discharge servicing, shared 600us IMU lifetime, ADC grants, retained-source
expiry, calibration/output work and fault cleanup must all have explicit owners
inside actual S..C intervals. No accepted source timestamp may be refreshed by
replay. Ordinary overruns remain B14 logging, not a new stop policy.

SC-AL schedule, SC-A physical button circuit/windows, SC-AJ physical clock,
sensors/motors, native UART, loaded memory/full <800us and human gates remain
pending. No additional hardware is requested. No motor authority, PINMAP,
EXPLAINED, phase approval, push, tag or history rewrite is implied.
