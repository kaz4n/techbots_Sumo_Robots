# D082 body coordinates and continuous-heading review

2026-09-23 Asia/Dubai. Separate same-model review against baseline `2ab0f6e`
and frozen contract/header/ADR `00f0cc2`. This reviewer did not author the
contract, implementation or specification tests. The review began with the
contract before the implementation was ready. It is independent context, not
cross-model review. Ownership is this report and `P2_imu_heading_raw/` only.

AGENTS, current PROGRESS, D024/D051/D059/D075/D081/D082, relevant HARDWARE/
BEHAVIOR sections, FACTS, P2 bench requirements and the prior B3 integration
audit were read. The actual date is the original PLAN's Wednesday 23 September;
D075 authorizes software progress without implying its scheduled human gate.
The reviewer performed no board connection, MCU operation, upload or motor run.

## Findings

No open BLOCKER, MAJOR or MINOR in the bounded D082 software scope.

- CLOSED MINOR, `state/analysis/P2_imu_heading_target_audit.py:64`: the first
  collector removed `__real_` when constructing numerical export names. That
  produced 42 apparent missing exports, although the same base-symbol receipt
  showed the literal `__llext_sym___real___aeabi_*` entries. The coordinator
  corrected the lookup and included the actual bare `__aeabi_*` wrapper
  disassembly. Original/intermediate receipts remain as
  `target_a746b27b_initial_lookup.json` and `target_a746b27b_bound_exports.json`.
  Final independent binding checks below pass. No production repair or target
  rebuild followed this evidence-only correction.

The independent test author also preserved ten failed configuration compiles:
its original `-DVALID` collided with `Presence::VALID`. The replacement
`D082_EXPECT_VALID` changes no predicate, expected result or warning/sanitizer
policy. The first 22 behavioral cases, allocation harness and both inert probes
had already passed. These author failures and the original runner are retained
under `state/analysis/P2_imu_heading_raw/author/`; no production defect was
established. The reviewer ran only the final frozen runner.

## Source and contract assessment

Actual estimator CPP SHA256:
`e314f57b78980993f782cf85aa48f0cd6ffadf1cb1ae99fb801c7981f1736411`.
`scope_audit.json` binds the public header and independent tests. Sixty-one
protected files were compared: no Git/content change in core, app, locked tests,
existing MPU setup/acquisition/transport or board wrapper. Twenty existing
working-copy CRLF versus Git-LF differences are recorded separately. Config
adds only `IMU_HEADING_MAX_GAP_US=2000`; prior strict defaults remain checked.

The implementation follows the specified admission order and reset-only
lifecycle. It requires confirmed proper signed-axis mapping, anchors the first
accepted observation at zero and rejects sequence discontinuities. Unsigned
half-range checks retain the last validated timestamp on reversal. Completion
age is checked before later sequence/payload checks; exactly 2000 us is accepted,
2001 us faults. This heading policy remains distinct from D081's 20 ms silence.

Mapped raw gyro endpoints feed the specified double trapezoidal accumulator.
Bias changes affect future increments without changing yaw or prior report
fields other than bias. NO_NEW does not integrate, replay gyro/acceleration,
or refresh the original observation time. Selected yaw-axis rails fault the
heading; horizontal acceleration rails invalidate acceleration independently.
Fault reports clear measured payload and preserve only bias, accepted sequence
and the last validated checked time. No GO reset, physical mounting choice,
clock, Bus call, motor write, heap operation or new remote path was introduced.
Loops are fixed bounds; implementation functions remain below 60 lines.

D024 calibration averaging and D059 logical GO origin are untouched. The existing
combined `imu_ok` cannot yet route fresh gyro, current acceleration and retained
heading correctly; the contract explicitly leaves that core/app integration
for the next task. This scope does not claim an integrated B3 driver or bench pass.

## Independently reproduced checks

`P2_imu_heading_raw/review_run.py` copied 315 source/test/build-tool files to an
isolated Linux `/dev/shm` snapshot. All 315 still matched after execution. Exact
commands, return codes, hashes and raw combined output bytes are retained in
`final_focused/`. The new tooling's nested receipts identify their text capture.

- Actual Estimator normal and ASan/UBSan builds each pass 22 cases and 64,370
  assertions, with zero failed/skipped cases.
- All six new tooling methods pass in 11.682 s. Their 28 compiler/executable
  receipts all exit 0: the 22 cases, ten configuration variants, a 10,000-observation
  allocation/I/O exercise, and both actual inert probe macro configurations.
- Runtime counters cover construction, observations, absence, bias updates,
  fault handling and destruction without allocation or I/O. Probe checks run
  real constructors/setup/10,000 loops; the candidate mounting remains
  zeros/unconfirmed and Estimator stays NOT_STARTED. Allocation guards exclude
  process startup; I/O counters are zero-initialized and never reset.
- All eight probe upload combinations reject before target or transport lookup.
  No actual connection is made by those mocked tooling checks.
- All 15 strict configuration methods pass. Existing B16 values, declarations,
  types and extents remain checked.

Coverage includes all 24 proper maps and 24 reflections, analytic constant/ramp
traces, yaw beyond both 360-degree directions, 40,001 observations preserving
small double increments, finite/range boundaries, explicit absence, rail
separation, fault clearing/latching, exact gap boundaries, clock wrap/reversal,
sequence metadata and no reset through repeated begin.

A full 2^32-observation sequence rollover and float-maximum yaw overflow were
not dynamically executed. Their defensive arithmetic was reviewed; no private
state mutation or reset hook was added to manufacture reachability. These
limits are also disclosed by the test author. The parent's broader host,
sanitizer and tooling receipts are separate from these independent checks.

## Actual compile-only source, startup and numerical bindings

The coordinator's actual board-Linux compile receipt exits0 with 79,060 program
bytes and 32,208 compiler global-memory bytes. Those are compiler figures, not
measured runtime free RAM. Target source identity is
`a746b27b7628deaca5b809d0ecdf333b27d98b7c7d50d0a26e299ea5942779af`.
The reviewer independently reconstructed all 48 staged files and the aggregate
identity. `identity_audit.json` binds all three artifact identities and the
installed base ELF hash
`39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd`.

The final ELF retains Estimator begin/observe/applyBias and the actual validation/
integration paths. Setup at 0x6c stores only entry/exercise, loop at 0x7c returns, and
the probe initializer at 0x2490 has no call instruction. Its relocations 24ac/24b0/
24b4 bind the inherited HCI guard/storage and Bridge memory initialization.
There is no initializer from `imu_heading.cpp` or Estimator method call during
startup. Existing Bridge/Serial/loop-hook paths remain within F091's unresolved
runtime boundary; this is not a whole-program runtime qualification.

`math_binding_audit.json` follows all ten numerical helpers used by
Estimator::publish from its 2a1c..2a50 literal relocations through the bare
`__aeabi_*` wrappers. Each wrapper's MOVW/MOVT pair targets the corresponding
`__real___aeabi_*` import. All 42 collected literal math exports are present,
nonzero and equal to the installed base function's Thumb address. All 36 collected
native exports are nonzero. No unresolved new numerical binding was found.
This verifies offline symbol/export consistency, not executed loader success,
numerical timing or full-tick WCET. Raw disassembly and selected relocations
are retained in `target_disassembly.txt`.

## Exact existing inert-source replacements

`inert_approval.json` approves exactly the following five existing keys after
source/startup review. No new key, upload authority, integration permission or
runtime qualification follows. Existing P0 sketches omit the heading probe
globals and the new estimator implementation adds no initializer.

| Existing key | Reviewed SHA256 |
|---|---|
| `bench/p0_matrix` | `fe9d6ebe7e263fe53f9e79881cc5589210768a18141325e29163359158c8f2e1` |
| `bench/p0_timing` | `2da7c5fcd49ee3de2dc3b134438621ace8b631c9fbd5ca23929362cb7f4f8c9e` |
| `bench/p0_adc` | `f7286eab46ff316da398d8ee015e4ec13300c3cacd1f520365977cc4a4839115` |
| `bench/p0_gpio` | `eb361162b75351aaef3ea67b0f36842f793b94e01a25d9239b7342c7bd60e224` |
| `bench/p0_qtr` | `568851737b717bbd3db74d73bd4b665d502a536369052cdfbbdbb984b6a591b2` |

## Verdict

PASS for bounded D082 heading-estimation software and its inert compile-only
boundary, with no open software findings. Physical mounting, planar accuracy,
drift, healthy acquisition rate, actual loader/runtime behavior, SC-AJ/F091,
full-loop WCET and all physical/human gates remain pending. Next work is the
separate presence/heading/calibration routing contract before core/app integration.
