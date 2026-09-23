# D083 countdown gyro-admission review

2026-09-23 Asia/Dubai. Separate fresh same-model review against baseline
`06e7d0d`, frozen contract/header `3c356ec`, and final implementation/test/probe
commit `5516bef`. This reviewer authored no
production, specification or test changes. Review ownership is this report and
`P2_calibration_presence_raw/` only. This is independent context, not cross-model
review or physical acceptance. The reviewer made no board connection, upload,
MCU, pin, sensor or motor operation.

AGENTS, PROGRESS, FACTS, handoff/resume, PLAN schedule, P2 bench requirements,
D024/D051/D059/D075/D083, BEHAVIOR B3 and the frozen admission contract were read.
The current date is the original PLAN's Wednesday 23 September. D075 permits
software work but does not satisfy the scheduled P0 or later human gates.

## Findings

No open BLOCKER, MAJOR or MINOR in the bounded D083 software scope.

- CLOSED MINOR: the new analytic-stream comment originally described both LCG
  constants as congruent to one modulo four. Its increment is congruent to three.
  The reviewer reported this before freeze; the author corrected the explanation.
  The independently expected 125 absent and 375 distinct slots, all expressions
  and all assertions were already correct and unchanged by that correction.
- The first author behavioral build and coordinator full host/sanitizer builds
  failed on missing `<initializer_list>` and the new tests' use of unsupported
  `REQUIRE` with the existing no-exceptions doctest policy. The author added the
  include and replaced five identical `REQUIRE` expressions with `CHECK`; no
  unsafe follow-on access required fatal assertions. No expectation, old test,
  compiler warning, sanitizer option or production policy was weakened. Original
  author receipts and coordinator `host`/`sanitize_build` receipts remain; the
  corrected receipts have distinct names. This reviewer ran the corrected freeze.
- The first coordinator staged-core test invocation failed its sibling-module
  import. The corrected unittest-discovery invocation passed with no test edit.
  Both invocation receipts remain in the coordinator's raw evidence.

## Source, compatibility and ordering

Frozen production CPP SHA256:
`09174efe38003245c635237bdd489454efc86b9ec1e65b089fcc167a2106eb7d`.
Frozen new C++ test SHA256:
`e3cf267e15ab43a5ecedf87028f998f721d66ce057ebe0bf6d0729efb793403f`.
`scope_audit.json` binds the header, contract and inert probe. It compares all
246 protected pre-existing source, test and build files against the baseline:
no semantic or Git diff. Twenty-eight working-copy CRLF versus Git-LF differences
are recorded separately. Existing locked and ordinary tests, config defaults,
HAL, app, Robot, Fusion, HeadingReference and B15 remain unchanged.

The public sample fields are appended with LEGACY defaults and existing five-field
aggregate callers remain valid. Known in-window presence selects one attempt
mode; unknown values reject without selecting. Mixing explicit and legacy inputs
rejects without contributing that call. ABSENT ignores payload and source fields;
INVALID rejects; explicit VALID uses raw finite gyro independently of `imu_ok`.

Admission checks delivery age before source identity, accepts exactly 2000 us and
rejects older, future or ambiguous timestamps. Exact same source time/sequence
with equal finite raw value is ignored, including signed-zero equality. Partial,
changed, reversed or half-range identities reject without replacing history.
Forward sequence gaps and uint32 wrap work without fabricating readings. A valid
pre-window source identity is consumed but excluded from aggregation. Both source
and decision must qualify for an actual contribution.

The original Services step still ignores duplicate decision timestamps wholly,
advances elapsed time, and closes calibration before examining gyro at CAL_END.
Late delivery cannot reopen it or delay GO. Mean, spread, minimum count and
previous-bias retention are unchanged. Warning, snapshot and hold services still
advance with absence. Start, cancel and reset clear admission state through the
existing reset path. Controller and Lifecycle are untouched; cancellation/STOP
still precede pending service processing and heading reset remains the existing
logical GO pulse. D059 continuous-yaw/bias application remains separately owned.

The two added helpers are below 60 lines with no loop, clock, I/O, allocation,
motor write or remote path. R1/R5 arbitration and R6 governor routing are unchanged.
No R3/R4 runtime exception follows from this pure-C++ source review.

## Independently reproduced checks

`review_run.py` copied 318 source/test/build-tool files into an isolated Linux
`/dev/shm` snapshot. All 318 still matched after execution. `final_focused/` retains
exact commands, statuses, timestamps, output hashes and raw combined output bytes.
Nested author-style tooling receipts explicitly identify their text capture.

- New plus established locked Gate/Services/Lifecycle checks pass 94 cases and
  3,507,334 assertions in each of normal and ASan/UBSan builds, with zero failed
  or skipped cases. Compiler warnings are errors; exceptions and RTTI are disabled.
- All five new tooling methods pass in 12.926 s. Their ten compiler/executable
  receipts all exit zero. Standalone behavioral runs each pass 31 new cases and
  2,283 assertions, normally and under ASan/UBSan.
- Both actual inert-probe macro configurations retain zero exercise, allocation
  and clock calls through constructors, setup and 10,000 loops. The runtime
  exercise passes 10,000 attempts without allocation or clock calls. These are
  host instrumentation results, not measurements of the installed Arduino core.
- All eight upload combinations reject before board or transport lookup; the
  test mocks those paths and makes no connection. All 15 strict config methods pass.

Coverage includes every presence/unknown enum, both directions of mode mixing,
legacy aggregates, exact source/decision boundaries, age equality/overflow/future,
duplicates and changed/partial/reversed identities, sequence gaps/half-range/wrap,
excluded pre-window identity retention, finite/minimum/spread thresholds, reset
and restart, closed-result immutability, all absent ancillary services, MODE/STOP
priority, complete qualified hold and the independently counted fixed-seed stream.
Large source-time jumps already fail the stronger delivery-age check; those cases
do not claim isolated dynamic coverage of otherwise unreachable later branches.

Separately, the coordinator's final receipts were read: full host 2/2 PASS in
12.51 s; full ASan/UBSan 2/2 PASS in 24.57 s, covering 1,124 cases/22,648,059
assertions and enabled-MotorGate 37 cases/3,796,846 assertions. Selected existing
tooling passes 25 methods in 47.651 s; staged-core checks pass two in 2.931 s.
These are the coordinator's runs, not additional independently executed full
regressions. No complete new all-tooling run is claimed.

## Actual target and inert-source boundary

The coordinator's board-Linux compile-only receipt exits zero with 79,248 program
bytes and 31,916 compiler global-memory bytes. These are compiler figures, not
measured free RAM. Source identity is
`9a7c64323e59555b327395c27227d1fa53ca7955a1a08c5a152932335a91ffe1`.
The reviewer independently reconstructed all 46 staged-file hashes and the full
aggregate identity. `identity_audit.json` binds the three supplied ELF identities,
their inspected metadata and installed base ELF SHA256
`39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.

The upload-format ELF retains actual Services admission/aggregation/finish and
Lifecycle paths. Setup at 0xcc only stores the exercise entry pointer; loop at
0xdc returns. The probe initializer at 0x24f0 makes no call. Its literals
250c/2510/2514 bind inherited HCI guard/storage and Bridge initialization stores.
There is no countdown.cpp initializer or service invocation during startup.
Existing P0 sketches omit the probe globals. Inherited Bridge/Serial/loop-hook
runtime paths remain under F091; no whole-program runtime qualification follows.

`target_binding_audit.json` independently follows all nine numerical helpers
used by calibration aggregation/finish through MOVW/MOVT wrappers to the matching
installed-base imports. All 42 collected literal math exports match their base
function's Thumb address; all 36 collected native exports are nonzero. This is
offline source/ELF/export consistency, not executed loader success or numerical
timing. Selected raw disassembly and relocations are retained.

`inert_approval.json` approves exactly these five existing source identities.
The coordinator's manifest adoption was independently checked to match exactly;
no new key, upload authority, integration permission or physical result follows.

| Existing key | Approved SHA256 |
|---|---|
| `bench/p0_matrix` | `49a06f2025aaa73ba35993e749f5985bc36002a50d590ab4b3a92f60f89e7969` |
| `bench/p0_timing` | `f2fae99862ea314314b299a1ef8d9b107c1d4fe86bb88e17893791a5a0d2f7af` |
| `bench/p0_adc` | `ff7d616d40f36517a3b73ffa7f51ec0682c0f7dec2e6e10c6c39f8b6dc03cbca` |
| `bench/p0_gpio` | `b6bba27707b0415b13a74d6c190124c7626a7ebf73db6a6658bdf3b662b7b3e2` |
| `bench/p0_qtr` | `61c8a1e4ac0d1e9b3e86fbb364d7623eb9cad3448db5d75f7f0d7229e407dd47` |

## Verdict

PASS for bounded D083 Services/Lifecycle explicit gyro admission and the inspected
inert compile-only boundary. No open software findings. Robot/Fusion/
HeadingReference/B15 routing and app integration remain separate next work.
Physical gyro validity, mounting, calibration, drift, sample rate, runtime loader,
SC-AJ/F091, full-loop WCET, PINMAP/EXPLAINED and all human/physical gates remain
pending. No motor-run permission or completion of B3/P2/P0-P7 is implied.
