# D101 Runtime dump checkpoint

2026-09-23 Asia/Dubai. IMPLEMENTED / HOST-TESTED / TARGET-COMPILED;
target acceptance BLOCKED by D101-R1, not a phase gate or complete B8.

The actual Runtime now owns the existing Transfer, binds one native dump owner,
and services it after the actual MotorGate receipt within the complete S..C
interval. Setup grants remain absent. Active transfer aborts on actual output
receipt failure or terminal owner failure, without replaying a Robot decision.
STOP passivity, UART poison and recorder capacity/rate remain unchanged.

Initial source96c80701 passed compilation but exceeded the pinned pristine
loader-pool model: default262576B and MATCH262960B against262144B. This is a
source-derived allocation failure, not an observed failed load. Exact source,
ELF, startup, dependency and allocation-order evidence is in
P2_app_dump_target_audit.md and P2_app_dump_raw/target_*.

Removing Runtime's redundant400-byte RobotResult copy retains only the prior
state and calibration-context bit. Current display/bias/calibration/STOP use
the Transaction's actual result. Separate review confirmed the original update
point and BOOT/false initialization. Final85-file source836008588522b81c0f94435725a9b93cbd3cf826b871caf960285797b17b9db0
MATCH compile exits0, program171336B/static257784B. Conditional loader peak
262400B remains256B too large; the symbol allocation first lacks240B and a
later export copy adds16B. No final-cache default build is claimed.

## Verification actually completed

- Full normal and ASan/UBSan suites:1423main cases/25218985assertions and
  178enabled-Gate cases/4536548assertions, all pass. Exact CTest logs copied to
  P2_app_dump_raw/host; command/status receipts P2_app_build_raw/d101_*.
- Independent spec/public-header author: both default motor profiles each pass
  5cases/166assertions; both synthetic-button profiles each pass21/6085 under
  UBSan. Actual Runtime streams pass strict byte-fragment receiver parsing and
  exact frames/events/summary CSV comparison. These author runs preceded the
  cache-only reduction; their source hashes preserve that distinction.
- Separate reviewer reran the final cache source with D101 and established D096
  configured Runtime/projection cases under ASan/UBSan:61/111569 per motor
  profile. The actual native factory passes193instrumented checks. This is
  separate same-model review, not cross-model review.
- Existing D096 tooling passes all6cases, including four actual Runtime build
  profiles and no-allocation probes. Only its three newly required link sources
  changed; all6test-method ASTs remain identical. The first discovery command
  omitted package context and failed4relative imports. Its original exit1 is
  preserved; invoking tests.tooling.test_app_runtime fixes the invocation with
  no assertion change.
- Original author fixture compiler errors, unsupported DrvFS no-overwrite rename
  and reviewer fixture compilation are preserved. Final publication used native
  Linux /dev/shm then copied the evidence bundle. No firmware failure was hidden.

No existing locked test, core behavior, config value or build policy changed.
Seven existing inert source keys remain at their prior values: shared-source
changes deliberately fail upload identity checks until a final reviewed refresh.
The actual app remains excluded from the inert upload path. No upload/reset/run,
physical UART or sensor qualification, measured loadedRAM/stack/full800us, human
gate or new motor authority occurred. Last MCU image remains D0911502e948.

Next bounded task: lossless frame-storage packing to close D101-R1 without
reducing retained frames/events, cadence or evidence fidelity. Freeze and test
the necessary explicit read-API migration before implementation. Post-STOP local
service/source lifetime and calibration-snippet delivery still follow separately.
