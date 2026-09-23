# D084 estimator-to-Robot evidence review

2026-09-23 Asia/Dubai. Fresh separate same-model read-only review against baseline
`c72921c`, frozen contract/public interfaces `aef3be2`, and final implementation/
independent tests `2c16023`. This reviewer owns only
this report and `P2_imu_integration_raw/`, authors no production/spec/test changes,
and performs no board connection or operation. Independent context is not
cross-model review or physical acceptance.

AGENTS, current PROGRESS, handoff/resume, relevant FACTS and HARDWARE, PLAN section3,
the P2 bench scope, D059/D082/D083/D084 and BEHAVIOR B3/B5/B15 were read. The actual
date is the PLAN's Wednesday23 September; D075 does not pass the scheduled P0 or
later human gates. Contract/header review found no blocking inconsistency.

## Findings

No open BLOCKER, MAJOR or MINOR in the bounded D084 software scope.

- CLOSED MAJOR: `src/core/fsm_imu.cpp:32` originally checked `contract_valid=false`
  only in explicit mode, contrary to the unconditional contract. The coordinator
  corrected the predicate before the final freeze. The independent author added
  the legacy false-contract case; it passes in the independent normal/sanitizer
  reproduction. Existing legacy callers retain their default true value.
- CLOSED MINOR: `tests/test_imu_integration.cpp:253` and the allocation fixture in
  `tests/tooling/test_imu_integration.py` originally omitted BusStatus::OK and the
  unchanged sequence from synthetic NO_NEW reports. The actual estimator correctly
  rejected those malformed reports. Both first behavioral runs compiled and failed
  only that case; the allocation run also failed at NO_NEW. The author corrected
  the fixtures from the D082 contract without reading production CPP or weakening
  assertions. Original freezes, failed runs and correction note remain in the
  coordinator's author receipts.
- CLOSED MINOR: `tests/tooling/test_imu_integration.py:30` originally initialized
  the allocation guard false, excluding global probe constructors. Its final
  constant true initialization and pre-setup zero-allocation assertion include
  constructor execution. Both macro variants pass with the corrected guard.

## Source and safety review

`scope_audit.json` binds the reviewed production, four new test files and contract.
All188 pre-existing test/config/app/board-tool paths match `c72921c` after explicit
CRLF normalization. No old ordinary/locked assertion or config value changed.
The new interface fields are appended; legacy overloads and defaults remain.

Robot checks duplicate decision timestamps before admission or receipt mutation.
Each admitted tick resolves one input copy, then preserves existing receipt,
history, sensor, lifecycle, edge, motion, stall, final-request, governor and
recording order. Invalid/mixed metadata latches HEADING_CONTRACT and inhibits
motion while buttons and STOP remain processed. MotorGate, motor backends and the
app are unchanged. All outputs still pass through the governor and existing gate.

Explicit admission checks known presence pairs, used finite/range values, delivery
and source age, forward checked-time order and both source/sequence identity.
Unavailable payload/source fields are ignored and cleared without discarding
history. Exact replay becomes retained heading with absent gyro/acceleration;
changed or partial/reversed identities reject. Current bias is deliberately not
part of replay identity because Estimator::applyBias preserves prior report values.
Both Robot and HeadingReference saturate accumulated history age across unavailable
ticks, preventing old retained data from becoming eligible after clock wraps.

Typed GO selects current fresh source time, actual retained history time, or the
existing nominal pending origin. Fresh recovery resolves pending origin once.
Continuous provider/Fusion yaw does not reset at GO. Retained bounded heading
remains usable by motion; only new yaw updates stuck extrema or starts candidates,
creates phantom/inward evidence, or supplies stall anchor/deflection angles.
Qualified stuck and stall timers continue on retained ticks. New valid horizontal
acceleration alone supplies impact, while visual contact/debounce proceed on each
actual opponent observation. Phantom event expiry remains separate from stored
heading source time. World memory initializes its age from the actual heading
source; relative/front recency stays on the opponent clock.

The thin actual Estimate adapter validates report state/fault/presence/age shape,
finite/range values and canonical absent/invalid fields, preserves unrelated Robot
inputs and sets explicit invalid metadata on rejection. It performs no acquisition,
clock, allocation, callback, motor operation or Robot invocation. The integrated
host stream calls the actual Estimator, adapter and Robot with transaction receipts.

B15 remains25bytes with unchanged offsets. Legacy high flags still reject.
Explicit gyro/acceleration groups must both be nonzero; nonvalid sensor fields
must be numeric zero. Measured zero remains distinguishable through VALID.
Pending stores the presence flags and values together before a later application
receipt. CSV schema1 remains raw-byte transport, not a semantic or provenance
validator. No capacity or logging-rate change occurred.

All added or extended production functions inspected remain below60 lines. New
work is fixed/bounded pure C++ with no added I/O, dynamic allocation or remote
motion path. This is a source/host result, not physical1kHz/WCET qualification.

## Independent reproduction

`review_run.py` copied329 source/test/build-tool/contract files into an isolated
Linux `/dev/shm` snapshot. All329 still matched the workspace after the run.
`final_focused/` retains command arrays, timestamps, return codes, raw output bytes
and SHA256 values. Nested test-tool receipts explicitly identify normalized text.

- The three new D084 suites plus established HeadingReference, Robot, Robot safety
  and codec tests pass118cases/1,727,511assertions in each of normal and ASan/UBSan
  builds, zero failures/skips. Warnings are errors; RTTI/exceptions remain disabled.
- All5 new tooling methods pass in34.243s. Their isolated behavioral executables
  each pass27cases/165,477assertions normally and under ASan/UBSan.
- Actual global constructors, setup and10,000 loops in both inert probe macro
  modes retain zero exercise/allocation/I/O counts. Separately,10,000 actual local
  estimator/adapter/Robot transactions have no allocations or I/O.
- All8 upload combinations reject before transport/board lookup; mocks prevent
  any connection. All15 existing strict config methods pass.

The tests cover unknown enums, presence shapes, exact numeric/time limits, replay
with bias changes, ordering and wrap, saturated history age, reset/token retention,
GO origins/recovery, explicit calibration and acceleration loss, full hold, STOP,
edge inhibition, centered-contact/governor limits, retained steering/stall timing,
stuck/phantom/world/inward evidence, all256 flags and delayed recording receipts.

The coordinator's separate full-host receipt passes2/2 in6.39s. Its full sanitizer
receipt passes2/2 in31.38s, with1151main cases/22,813,536assertions and37enabled-gate
cases/3,796,846assertions, all zero failures/skips. Its two staged core/public-header
tooling methods pass in2.722s. After exact manifest adoption, its25 existing safety/
staging tool methods pass in14.709s. These are coordinator runs, not additional
independent full regressions. No complete new all-tooling run is claimed.

## Actual target boundary

The coordinator's board-Linux compile-only command exits0:135536program bytes and
66352compiler global-memory bytes. These figures do not measure free RAM.
Source identity is `f3bc1f7f7fac3f027d5daa2cdcadc9981acfc14d9d3c3f130946ed6c4e2fcb55`.
This reviewer independently reconstructs all51 staged-file hashes and the exact
aggregate. `identity_audit.json` binds the supplied three ELF records and installed
base ELF identity; the reviewer has not connected to the board or executed them.

The upload-format ELF retains real Robot admission, routing, recording, typed
HeadingReference and applyEstimate paths. Setup at0x6c stores only the unused
exercise pointer; loop at0x7c returns. Probe initializer0x2490 has no call; literals
0x24ac/0x24b0/0x24b4 bind inherited HCI guard/storage and Bridge initialization
stores. No new core/adapter initializer invokes the retained computation.
Inherited Bridge/Serial/loop-hook paths remain unqualified under F091.

`target_binding_audit.json` independently checks all42 AEABI base-export addresses
against matching Thumb function addresses, all20 actually retained numerical
wrappers' MOVW/MOVT relocation pairs, and36 nonzero native exports. Supplemental
evidence binds the same base/upload ELF identities and verifies fmod0xc76c and
sqrt0xc774 wrappers through literals0xc770/0xc778 to installed-base Thumb addresses
0x0801504d/0x08014ed1. These are offline binding checks, not loader execution or
numerical timing. The supplemental collector's selected stdout line separators
are explicitly normalized for parsing; original receipts remain unchanged.

The first reviewer binding script incorrectly expected every imported AEABI name
to have a retained wrapper. Its d2lz assertion failure and original script remain
in the raw directory. The corrected script checks every export while distinguishing
unused imports from20 retained wrappers, and passes. No production/test change was
made for this reviewer-script repair. The coordinator also retained its initial
supplemental receipt-name collision and recollected the read-only detailed payload
under distinct receipt names; no source change or target rebuild followed.

`inert_approval.json` approves exactly these existing source identities. The
coordinator adopted them; `manifest_adoption_check.json` independently confirms
the current manifest matches exactly, with no added key. This grants no new
upload/run authority and does not qualify inherited runtime paths.

| Existing key | Approved SHA256 |
|---|---|
| `bench/p0_matrix` | `9c026a5ab3066488b789c352b2a66fac700c36edd6a039e8b3b7583642f89d76` |
| `bench/p0_timing` | `07f0bd0563bacac81398be0b257ceb6c17ba49be19542a4ce3e6cad8be3fc739` |
| `bench/p0_adc` | `3bc1a4443188a3ba7a64dcf29720e273252ba5c4196e0ba1334b97701a9dcbe1` |
| `bench/p0_gpio` | `e99323af20ee65fc8dcd3a8a1576e73a08888cb0c80f936f48dba81dc0cb7e37` |
| `bench/p0_qtr` | `4f0f8509fafd8ddbac7a2e7e15c7ba97f59a6d41122147cc5532469691ebf3ca` |

## Verdict

PASS for D084's complete estimator-to-Robot software evidence routing and the
inspected inert compile-only boundary. No open software findings. Physical mounting,
heading accuracy/drift, sample rate, loader/runtime, SC-AJ/F091, whole-loop WCET,
QTR acquisition/app integration and every PINMAP/EXPLAINED/human phase gate remain
unverified. This review grants no upload, MCU/sensor/motor run or physical acceptance
and does not complete B3, P2 or P0-P7.
