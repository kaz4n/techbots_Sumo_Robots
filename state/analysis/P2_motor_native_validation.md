# D077 native MotorGate backend - software validation

2026-09-23 Asia/Dubai; baseline e814af7, contracts b979172/8d252f0,
implementation 99f8668.
D051/D075 permit actual P2 software development before physical acceptance.
This task implements native callbacks behind the existing MotorGate; it does
not integrate the app or establish physical B4 acceptance.

## Implementation and source prerequisites

`src/hal/motor_port_unoq.cpp` validates the full proposed pin bank before GPIO
configuration, acknowledges EN LOW and uses checked native per-channel routing
and PWM setters. Immutable period candidates come from the installed clock
lineage; setup verifies initialized metadata and prescaler/mode ownership.
After four successful writes it clears stale update flags and requires a fresh
update from each of TIM1/3/4 before admitting EN HIGH. One wrap-safe 150 us
deadline and a 4096-pass bound cover settling. Failures remain failures and
the existing Gate attempts LOW/all-zero cleanup and latches its fault.

The new development constants are 10 kHz, 150 us and 4096 passes, plus names for
unchanged proposed D3/D5/D6/D9 PWM and D10 EN pins. D077 records these choices;
no B16 value changed. Source prerequisites and primary-document provenance are
in P2_motor_clock_audit.md, P2_motor_update_audit.md and F095. Register/readback
checks do not measure physical waveform, actual timer frequency or driver EN.

The compile-only probe retains real native/Gate code through a never-called
begin/apply/reset function. Its constructor/factory perform no I/O, setup only
retains a function address and loop is empty. Neither build configuration is
in the upload allowlist. Existing app/core/locked tests remain unchanged.

## Validation status

Final native tests, target builds and fresh review PASS. Full controlled tooling
regression: 410 tests PASS in 432.397 s, command exit 0. native_tooling.json/txt
preserve exact command/timestamps/output; final_subprocess holds this run's
native build/run receipts. No failed or skipped test is treated as success.

Normal host CTest: 2/2 PASS, 5.91 s; verbose ASan+UBSan: 2/2 PASS, 36.49 s.
The default suite has 1030 cases/20982541 assertions and the host-only enabled
MotorGate suite has 37 cases/3796846 assertions, zero failures/skips. Exact
commands, dates and exit status 0 are in native_host, native_sanitize_build and
native_sanitize_tests receipts. Native target-conditioned code has its own
independent installed-header fixture tests; these counts are not its coverage.

Independent test author used the frozen contracts/public headers/API facts
without reading implementation cpp. Actual native source is compiled with
installed-shaped headers, counted MMIO/API substitutes and UBSan. The default
native binary passes 38 cases/108417 assertions; the host-only enabled binary
passes 38/108603. The real Robot countdown and Gate write boundary are composed,
including post-HIGH readback failures, per-read failures, cleanup, ownership,
stale/missing/late timer events, deadlines, wrap/frozen clocks and no allocation.

Fresh same-model reviewer independently replayed all nine native Python methods:
PASS in 229.624 s. All 167 subprocesses returned zero: 78 executable variants,
152 doctest case executions and 217368 assertions, no failures/skips. These
include 74 malformed/clock metadata variants and two actual-probe startup tests
with 10000 loops each. All eight upload combinations are refused before target
lookup. Separate config checks pass 10/10. Review sources/tests remained stable.
See `../reviews/P2_motor_native_review.md` and its exact native/config receipts.
The reviewer also inspected both final ELF configurations and confirmed all 38
baseline core/app/existing-locked paths unchanged (14 locked tests plus .gitkeep).
No BLOCKER/MAJOR/MINOR remains. This is separate-context, not cross-model review;
the earlier reused fact-context interim review is supplemental provenance only.

The reviewer independently computed and approved exact replacements for the
five existing inert source hashes. No upload key was added. New staged tests
use the repository's existing CRLF-to-LF canonicalization; the source identity
receipt proves the 21 affected files have no other byte difference. Work files
used for the tests were unchanged. Raw evidence is exempt from normalization.

## Failed drafts and repairs

All observed failures are retained. The initial strict native compile rejected
a fixture indentation warning and production signed/unsigned domain comparison.
The author braced the fixture and the implementer made the domain uint32_t;
no runtime policy changed. A repeated-write draft incorrectly reused admission
after a rejected HIGH; the author restored the contract-required LOW/new writes.
The real-Robot fixture omitted a valid battery and initially started before
release qualification. Its two unsuccessful drafts and subsequent contract
analysis are preserved in native_tests_fixture_analysis.txt; all GO/countdown
assertions were retained.

Malformed EN pin32 exposed a compile-time oversized-shift warning despite
runtime validPad rejection. The coordinator preserved the previous cpp and
added a guarded pinMask helper; validPad still rejects pins outside 0..15.
The fresh reviewer approved this narrow repair. Initial and pre-mask source
snapshots, compiler failures and exploratory subprocess results are retained.
An exploratory run spanning source repairs is not the final regression result.

The probe's first fixture build also copied config.h under a second physical
path while public headers referred to the original, defeating pragma-once file
identity. A single-source symlink in the Linux fixture staging corrected that
harness error; production/probe code did not change. Its full compiler failure
and successful final startup tests are retained. Common doctest main was built
once per run to avoid recompiling the test framework for every metadata variant;
this changes build overhead only, with expectations preserved.

The implementation worker was unavailable for this final narrow repair because
the agent tool reported its thread limit; the coordinator performed it. A fresh
reviewer subsequently became available and reviews the final source separately.

## Actual target compilation

Final source aggregate c35726f4dc0fafc87a08efc97a662c4e65937cd1847e3a7618db596040ef33ec
contains cpp 73e95df12de6ca020fac3df6490bf98dd3623868f577b28a9d8137d04dd0914f.
Both real board-side builds exit 0 on installed CLI1.5.1/core1.0.0:

| Configuration | Program bytes | Compiler memory bytes |
|---|---:|---:|
| Default / MATCH0 / MOTORS_ALLOWED0 | 85052 | 35160 |
| Immediate / MATCH1 / MOTORS_ALLOWED1 | 85588 | 35552 |

These figures describe isolated compile probes, not a complete application or
measured free RAM. The native_target_default_mask/native_target_match_mask
receipts contain exact commands and completion times. Earlier ce4a77a5/da9cd60a
compiles are preserved as superseded source evidence, not final validation.
The existing P2_motor_gate_record.py captured those outputs; only the new
native_* receipts were moved unchanged into P2_motor_native_raw.

Offline target_c35726f4_* receipts preserve all 38 source hashes, three ELF
artifacts per configuration, retained disassembly, sections, relocations and
33 selected native import/export checks. Arduino.h contributes an inherited
RouterBridge initializer; the native user constructor/factory are I/O-free.
This is not a claim that all inherited startup/loop hooks are runtime-qualified.

## Evidence limits

Target builds and offline ELF inspection use the UNO Q Linux compiler only.
No upload, reset, MCU attachment, pin operation or motor run occurs here. Host
MMIO/API substitutes do not prove real electrical behavior or elapsed MCU time.
Physical frequency, EN boot/reset/fault waveforms, reversal/brake behavior,
exclusive peripheral ownership and full fault-path tick WCET remain pending.
F091 inherited Bridge/initializer paths still require runtime integration work.
P0/P1/P2 human gates, PINMAP and EXPLAINED acceptance remain unprovided; no
STAND/RING permission is inferred. The last-known MCU image remains inert QTR
61d7a2d0 and the application remains inert.
