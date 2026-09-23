# D089 fresh-context software review

Reviewer: separate fresh context of the same model, review-only. Baseline
`4f11a1b131d0ad3179d6b564cee3f29542b02b5f`; final D089 source identity is bound in
`P2_qtr_cal_raw/review/approved_inert_sources.json`, reviewed2026-09-23.
The test author reused an earlier unrelated D087 implementation context and was
instructed not to read D089 implementation bodies. This is not a fully independent
fresh test-author context or a cross-model review.

## Findings

No open BLOCKER, MAJOR or MINOR findings. The following confirmed findings were
repaired and independently reproduced before and after the repair; original
locations below refer to the initial reviewed source.

- MAJOR (resolved): `src/core/fsm_qtr_cal.cpp:45-59` discarded the accumulated source
  era when admitting a distinct frame. After CONTROL absence spans a full
  uint32 wrap, an unseen cached pre-handover frame with forward modular identity
  is accepted as newly acquired, setting line_available and clearing the hold.
  The finite modular age is less than the long accumulated handover age, so the
  comparison at qualification does not prove acquisition after handover.
- MAJOR (resolved, same root cause): `src/hal/qtr_cal.cpp:120-133` admitted a distinct
  cached old frame after a full-wrap WAITING interval and resets source age.
  Its small modular source age can fall inside a new stage capture, contributing
  a sample acquired in the previous clock era.

Reproduction receipts: `P2_qtr_cal_raw/review/source_era_reproducer_v2.txt`
and matching JSON; reviewer-owned `source_era_probe.cpp` compiles against actual
adapter, Robot, Calibration and callback MotorGate implementations. Output:

```text
Robot old distinct pre-handover frame: faults=0 available=1 hold=0 updated=1 age=3000
Owner old distinct frame: phase=2 reason=0 samples=1
```

Implemented bounded repair: ABSENT may remain inhibited indefinitely, but a
present source with retained accumulated source age or CONTROL handover-boundary
age at least half-range cannot prove its era and must reject. Below half-range,
tie each forward start delta to prior accumulated source age before replacing
history. The existing bank, faults, STOP, receipt and token history are preserved.
The D089 contract includes the explicit source-era disposition. The same actual
reproducer now passes (`source_era_fixed_durable.txt`):

```text
Robot old distinct pre-handover frame: faults=256 available=0 hold=1 updated=0 age=4294967295
Owner old distinct frame: phase=4 reason=8 samples=0
```

## Final validation

Static review covered D051/D075/D085/D087/D089, shared raw validator, versioned
adapter, Robot preparation and START/STOP ordering, calibration extrema/atomic
commit/deadline/token policies, bounded formatter and literal display overlay.
No additional confirmed defect. Default no-bank adapter behavior, all existing
locked assertions, the six existing inert sketches, board upload policy and
motor driver source remain byte-identical to the baseline.

The initial isolated full build failed in the still-being-authored new enabled
MotorGate test because REQUIRE used the no-exceptions doctest mode. The compiler
receipt is retained in `P2_qtr_cal_raw/review/build.txt`; this is not a passing
test claim. Two later reviewer invocations lost their isolated `/tmp` artifacts
between WSL processes; neither root nor reviewer performed cleanup or restart.
Those failed invocation receipts are retained. Durable isolated build
`build/qtr_cal_fresh_review` then configured, built and passed without changing
the established tests.

- Reviewer full normal host:2/2 PASS,1254 main cases/24477190 assertions and
  39 enabled MotorGate cases/3843500 assertions; `review/full_host.json` and the
  corresponding text. After the test-only extrema addition, reviewer rebuilt
  and reran focused D089:31 cases/1915 assertions PASS.
- Reviewer-owned source-era reproducer: original Robot and owner failures both
  observed, repaired behavior independently checked as above. Author regressions
  include full-wrap unseen identities and exact half-range adjacent boundaries.
- Inspected root frozen normal and sanitizer receipts after the test-only
  addition:2/2 PASS each,7.06s/28.14s;1255 main cases/24477205 assertions and
 39 enabled cases/3843500 assertions. These were root's runs, not separate
  reviewer full/sanitizer invocations.
- Inspected author scoped tooling:4 distinct methods PASS, including
  CONFIRM2/batch1, CONFIRM3/batch32, batch256, and actual inert setup plus10000
  loops for MATCH/MOTORS0 and1, and the additive18-method config-registry wrapper.
  Final extrema tests pass both nondefault profiles and batch256. Startup tests
  are host substitutes, not target runs.
- Final target source`cc4819aabe25489ef3d8735e81a12ddb708b7bb3f452c56f8104e8cb1b1ca01c`
  compiled successfully:145824B program/72004B compiler globals. Reviewer checked
  all67 target source-file hashes against actual current files,3ELFs,40native
  exports,42AEABI bindings and no missing math binding. Actual setup only stores
  the retained function pointer; loop returns; the new global initializer only
  writes data. Inherited runtime hooks remain outside this qualification.
- Independently staged the exact six existing inert keys in a private workspace
  using the actual staging helper, compared every file against current source
  and shared target source, and issued `review/approved_inert_sources.json`.
  This permits only updating those existing six exact registry hashes. No new
  key or upload is authorized; the new calibration probe remains compile-only.

The added extrema case derives expected values directly from the contract:
for sample count N and sensor i, W=99+20i+N, B=1001-N, and
T=W+floor((B-W)/2)=550+10i. It checks each extremum and the exact exported bank
`{550,560,570,580}`. No production source, target identity or inert hash changed.
The initial approval is preserved as `review/approved_inert_sources_initial.json`;
the current approval carries refreshed test hashes and the test-only addendum.

Raw reviewer commands, outputs, source maps and hashes are under
`state/analysis/P2_qtr_cal_raw/review/`. The strict config-registry extension and
final root normal/sanitizer receipts were inspected; final Git publication remains
root's separate evidence duty.

## Verdict

PASS within the D089 software scope; no open findings. No upload, MCU/pad operation,
physical color/clock/WCET validation, human phase gate or motor permission is
claimed. The actual application scheduler and permitted print transport remain
separate work.
