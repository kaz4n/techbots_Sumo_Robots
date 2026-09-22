# P1 independent front-qualification test author

Date: 2026-09-22, Asia/Dubai. P1 host-only under D-016.

Objective: test the B9.1 NEW-observation centered counter committed in c0b3ad6,
and its public composition with perception, current contact and the governor.
Owned files are `tests/test_front_qualification.cpp` and this report only.

Sources: public fsm.h, opp_fusion.h, governor.h and types.h; B2, B5, B6 and B9;
D-034/D-038; current config defaults. AGENTS and the independent test-author
restrictions were read earlier in this continuous session. No src/core/*.cpp
implementation was read. No existing tests, config, shared build files or state
ledgers were edited. No build or commit was performed by this author.

The 19 new cases cover:

- An independent literal B5 front table across all 256 masks, including ignored
  high bits and side/rear combinations: 160 centered masks and 224 front masks.
  Literal three-observation eligibility is checked before, at and after threshold.
- All 125 triples of the five centered patterns; changing centered patterns does
  not interrupt the streak. Side/rear bits do not displace a current front.
- Every mask after a two-observation streak, all 96 noncentered interruptions
  after qualification, and reset at streak lengths zero through four.
- Stable eligibility over 4,096 fresh centered observations, followed by clearing
  and fresh qualification. This is bounded behavioral evidence for saturation,
  not a proof of internal representation or integer-limit behavior; no private
  state is inspected or modified. An additional generated stream was omitted
  because exhaustive mask/triple boundaries already provide focused coverage.
- Real Fusion debounce before the three confirmed effective observations;
  test-owned freshness gating skips cached timestamps instead of passing stale
  samples to the counter. Irregular elapsed times and timestamp wrap do not
  replace the required count of new observations.
- Fusion observation -> qualifier -> explicitly selected state -> one contact
  commitment -> frontDemand -> Governor. Fresh same-tick impact may latch on
  qualified ATTACK entry; a cue previously committed in TRACK cannot become a
  stale latch. Both close patterns still require twenty confirmed samples.
- Explicit caller reset when leaving normal perception, followed by three new
  observations after OPENER/REFLANK/EDGE_ESCAPE and a fresh contact requirement.
  Phantom suppression and newly stuck bits cannot supply qualification; close
  phantom override must qualify again. Confirmed off-centering clears the
  qualifier and contact together at the debounced boundary.
- Real low-voltage SEARCH_FORWARD and approach caps, centered contact reaching
  full duty after slew, and external inhibition immediately clearing output
  despite valid qualification/contact. Nominal-voltage visual contact is also
  composed through the governor.

Static handoff: 19 cases, no REQUIRE/CHECK_THROWS, no trailing whitespace, and
the removed generated stream's helper was also removed. Compiler and runtime
results remain pending parent verification in the shared host/sanitizer flow.

Limits: the test caller explicitly chooses each state and resets the counter;
these tests do not implement or assert Robot state routing, target-loss routing,
which normal-perception entry tick counts, opener/re-flank transition timing,
or complete edge/STOP arbitration. No MotorGate/EN output, HAL freshness,
hardware behavior, physical contact inference, MCU timing or phase gate is
proved. Eligibility alone does not authorize contact or motors.

Next action: parent reviews and runs the frozen tests, records actual host and
sanitizer evidence, and commits the completed batch.
