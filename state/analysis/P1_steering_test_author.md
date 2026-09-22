# P1 front steering independent test author

Date: 2026-09-22, Asia/Dubai. Contract: `fsm::frontDemand` / `FrontDemand`,
committed by the orchestrator at `d6bdff3`. Active work is P1 host-only under
D-016; P0 hardware acceptance and every human gate remain pending. The local
date matches the first day of PLAN section 3, before code freeze.

Objective: independently encode approved B5/B6/B9/D-036 request behavior and its
composition with the existing governor. Source inputs were AGENTS.md,
`.claude/agents/test-author.md`, BEHAVIOR.md B0/B1/B5/B6/B9/B16, D-036,
public core headers, `src/config.h`, the host test scaffold and phase/resume
documents. No `src/core/*.cpp` implementation was opened. A quick memory-registry
lookup returned no relevant prior project entry.

Owned files only:
- `tests/test_front_steering.cpp`: 17 specification-derived doctest cases.
- `state/analysis/P1_steering_test_author.md`: this report.

Coverage:
- Literal expected duties for all seven TRACK rows and all five eligible ATTACK
  rows, separately for approach and contact. Lone FL15/FR15 requests are the
  approved mirrored `(-0.10, 1.00)` / `(1.00, -0.10)` pairs.
- Invalid zero on absent front, off-center ATTACK, every other named state and
  all unknown state byte values. All 256 masks cover side/rear priority and the
  ignored high bit; both contact inputs are checked.
- Exhaustive mirrored masks and finite bounded requests for every combination
  of 256 state values, 256 mask values and two contact values.
- Actual governor composition at nominal 11.1 V and low 9.0 V: TRACK 0.30 cap,
  ATTACK approach 0.60 cap, centered-contact eligibility, request saturation,
  acceleration slew and immediate contact-cap reduction. Expectations use
  literal outputs rather than a duplicate production calculation.

No scoped specification ambiguity or contradiction found. TRACK centered rows
are intentionally valid while future centered qualification is pending, as the
public contract states. Raw approach requests can exceed 0.60; B6 applies that
cap after voltage compensation. At 9.0 V, contact rows all reach `(1,1)` after
settling; this is the specified individual-wheel cap, not measured steering.

Validation status: authored and statically inspected only. Per delegated scope,
this agent did not build, execute tests, commit, edit existing tests, change
shared files or touch hardware. The orchestrator must compile/run these cases,
retain receipts and send implementation plus tests to the independent reviewer.

Pre-build review correction: the reviewer identified four `REQUIRE(demand.valid)`
uses that the vendored doctest rejects with `DOCTEST_CONFIG_NO_EXCEPTIONS`.
Replaced exactly those four with `CHECK(demand.valid)`, preserving every checked
expression and all subsequent checks. Host configuration and established tests
were unchanged. This is an author-file compatibility correction, not a test-run
result; execution remains with the orchestrator.

Limits: this helper neither counts ATTACK_ENTER_TICKS nor selects transitions,
maintains the D-027 contact latch, issues a target-loss brake to the governor,
enforces edge/STOP/countdown precedence, or writes motor pins. Its tests do not
claim integrated Robot behavior, complete R1/R5 proof, target compilation,
timing-budget compliance, physical steering or a passed phase gate. Governor
requests in these component tests are explicitly wired by the test caller.
