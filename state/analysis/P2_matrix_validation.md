# D088 P2 B6 matrix implementation and validation

2026-09-23 Asia/Dubai. Contract8fd11dd, implementation385c46c. P2 software work
under D051/D075; user additionally permits a bare-board built-in-matrix test.
No human gate, physical input distinction, wiring change or motor permission.

## Implemented result

Actual ui_display renderer completely overwrites one fixed104-byte8x13 frame.
It renders B13 modes, B3 countdown including the inhibited margin, service
selection/sensor view, battery scale/unknown marker and persistent fault markers.
Its pure current-input/result adapter uses actual Robot diagnostic evidence,
including validated preGO IMU availability; it never grants motion or refreshes
sensor evidence. Existing core behavior and locked tests are unchanged.

Actual ui_matrix_unoq owns one explicit normal-startup setup grant. It checks
privileged Thread context and the installed counter_matrix device, initializes
a blank3-bit frame, validates every submitted pixel and limits submissions to
one per40000us without catch-up. Each native104-byte copy saves PRIMASK, masks
IRQ, writes, issues DMB and restores the exact prior mask. Void native APIs are
reported INIT_UNCONFIRMED/SUBMITTED_UNCONFIRMED, never optical success. No postsetup
allocation/wait/scroll/Bridge call is added to these project paths. Platform
inherited hooks remain a separately documented limitation.

bench/ui_matrix exercises this actual renderer/adapter using synthetic scenes,
MOTORS_ALLOWED0/MATCH0, no external inputs or motor calls. Its script allowlist is
normal-startup-only and exact-source-hash checked. All five old inert identities
were independently re-reviewed after shared-source changes; only this new sixth
key was added. Source maps, approval and adoption receipts are preserved.

## Validation actually run

- Full frozen normal host:2/2 PASS6.69s. Full ASan/UBSan:2/2 PASS31.71s.
  Each contains1224main cases/24475290assertions and38enabled MotorGate cases/
  3843482assertions. Receipts host_frozen/sanitizer_frozen and both frozen detail
  logs under P2_matrix_raw; their commands and exit statuses are recorded.
- Independent author15new renderer/actualRobot cases1521100assertions PASS.
  Exhaustive8192sensor frames,127fault masks/pages, literal mode/service pixels,
  thresholds/adjacent ticks/wrap, invalid data/guards, actual menu/IMU mapping.
- Actual native CPP compiled against controlled native/CMSIS/device substitutes:
  15methods,866successful subprocess scenarios across normal and sanitizer;
  all104invalid-byte positions, ownership/context/readiness/fault/cadence/wrap
  and exact PRIMASK restoration. Eight independent runtime-capture methods also
  PASS. These are host/script tests, never successful native board measurements.
- New upload5methods PASS across SSH/ADB substitutes: default exact-source path,
  compile-only argument combinations, Immediate/motor refusal, changed-source
  refusal and compile-failure propagation. Existing25tool methods+2staging PASS.
  Scoped tooling total55methods (23native/capture+5upload+27existing).
- Board Linux actual CLI/core compilation exits0: source e50c6da38bba5131e426d8c076e7aa7c8aad5961f60a6eb1387b1f2412aab6af.
  80592program bytes/32244compiler global-memory report, not measured free RAM.
  Exact61source files match both physical bytes and385c46c Git blobs. Three ELF
  artifacts,40nonzero native exports and42AEABI bindings inspected. Both real
  begin/submit retain CONTROL/IPSR and exact PRIMASK/cpsid/DMB/restore sequence.
  ELF14023aa1e0b788edbbfe92e6b6b8aeed0afff6e0b329360af212c9df3688a7ab.
- Fresh separate Codex context independently reviewed actual source/diff/tests/
  target/allowlist/capture: PASS/no open BLOCKER/MAJOR/MINOR. Same model, not
  cross-model or human gate. See P2_matrix_review.md and raw/review.

## Preserved failed checks and repairs

Author's first strict syntax check caught three new-fixture issues (doctest macro,
class memset warning, mixed enum conditional); all corrected before host build.
Initial fullhost failed two new fixtures because the invalid-frame right glyph
was not explicit: D088 now states blank. Tests were updated to the clarified
new contract; no established assertion or production behavior changed. Later,
one newly added retained-IMU fixture incorrectly used20ms silence instead of the
already-specified2000us heading-age bound; fixed from D084/publicconfig, with
failed focused receipt retained. Final fullnormal/sanitizer include that repair.
Reviewer approval-helper path error and correction also remain in raw evidence.
LF normalization of board_tool/CMake was checked to preserve their reviewed Git
blobs; no source61hash changed. No failed result was substituted for board proof.

## Runtime scope and remaining work

The authorized normal-startup upload completed exit0 for serial2629958581 at
2026-09-23T11:39:55.940799Z. Read-only identity/counter capture is separately
recorded in P2_matrix_raw/runtime_report.json when complete; do not infer its
result from the upload. Run target/source/binary/grant are in P2_matrix_run_scope.
Synthetic scenes are not measurements; counters cannot establish visibility,
orientation/brightness, independent clock accuracy, masked-copy duration, ISR
interference or complete800us WCET. SC-A/SC-AJ/F091, external sensors/physical
acceptance, application scheduler/service consumers and human gates remain open.


## Run1 observed result

TARGET-UPLOADED and BOARD-RUN-COUNTER-VERIFIED: actual deployment exit0;
read-only capture exit0, COUNTER-ADVANCED in106.208485s under120s. All9raw reads
match their saved hashes/sizes. Full deployed loader PT_LOAD bytes and80592-byte
sketch match the pinned artifacts; exact symbol/BSS and final list/node identity
checks passed. Submission scalar3341->3418,advance77, with monotonic observation
bounds3.000409..3.145330s. Both samples initialized1/failures0/status2(render0),
scene7 then8. Native status2 means SUBMITTED_UNCONFIRMED; no optical claim.
max_call_us37 is the bench's accumulated renderer+submit MCU-clock diagnostic,
not IRQ-mask duration, an independently calibrated time or whole-tick WCET.
Board and Windows UTC clocks are not synchronized (about2s offset); use the
capture's own monotonic bounds, not cross-machine UTC subtraction. Current known
MCU image is this inert ui_matrix sourcee50c6da3, replacing priorQTR61d7a2d0.
No external sensor or motor run occurred. Optical/full B6/human gates remain open.
