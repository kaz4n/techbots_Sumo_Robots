# P1 gate-review packet — software checks passed / human gate pending

This is the coordinator's current evidence request, not reviewer output or human
approval. It supersedes the historical313-case partial packet. P1 host work is
permitted by D-016 while P0 acceptance remains pending.

Phase: P1. Reviewed software range:2c6e95d..3e46ea4, with subsequent evidence
checkpoint documentation included separately. D-060 interface commits ea4618c/4ae6d45
and clarifications da84b06/99bd3c8 preceded source/test freeze.

Specification: AGENTS R1–R11, P1_core_logic tasks1.1–1.6, BEHAVIOR B0–B16 as
explicitly amended by DECISIONS D-017 through D-061, HARDWARE section8,
P1_robot_contract.md and P1_ambiguous_defend_contract.md. No pin/wiring or physical fact is inferred.

## Claimed software scope

Complete production Robot composition now exists alongside all default P1 core
components, bounded metadata/frame scheduling and actual-duty feedback validation.
Independent new scenarios call the real Robot, including10000 fixed-seed streams,
R1/R5, all16 line masks, six modes, contact/stall/openers and QTR warning episodes.
The app entry is inert and exists only to compile/link P1 core on the target; it
is not a HAL/scheduler implementation. Existing locked tests are unchanged in
this batch; the sole historical amendment is the expressly approved D-039 case.

## Acceptance checklist

- [x] Current normal and ASan/UBSan suites pass:895 cases/13,765,968 assertions,
  no fail/skip; raw receipts indexed in analysis/P1_robot_validation.md.
- [x] Specified P1 table/default behavior and locked invariants have coverage;
  fresh review and runtime close QTR/ambiguity gaps. Optional disabled physical
  features are not claimed implemented; complete hardware validation is later.
- [x] Actual UNO Q app compile-only passes: sourcece90f09d, exit0,
  MATCH0/MOTORS_ALLOWED0,125508B program/61004B globals; no upload/reset/start.
- [x] Fresh full-core safety review PASS with no open BLOCKER/MAJOR/MINOR:
  state/reviews/P1_fresh_gate_codex.md includes actual runtime/target evidence.
  Scoped additional review is P1_robot_codex.md; do not confuse the two contexts.
- [ ] Team member explains complete state diagram; EXPLAINED OK is absent.
- [ ] Human writes GATE P1 PASS; absent and never authored by an agent.

Current source, evidence and remaining checks:
state/analysis/P1_robot_validation.md. Fresh review is same-model Codex, not
cross-model. Test authors derived expectations from public contracts, without
implementation reads. Synthetic application/timing inputs prove host logic only.

Review in REVIEW_GATE.md order: R1–R6 paths, specification and locked history,
bounded work/wrap/finite duties, explainability and evidence provenance. Trace
future actuator responsibility to MotorGate: there is no implemented motor-write
boundary or motor-capable app here. Later HAL tests and complete measured target
WCET remain mandatory and cannot be replaced by this P1 review.

No P0 gate follows from D-016. No P2 HAL work, motor upload/run, release tag or
physical acceptance is authorized by this packet. Human gates remain pending;
no additional hardware connection is requested now.


2026-09-23 D072-D074 software update: LOG_HZ25 fallback adopted explicitly in
D072, with scoped regression/review/target-probe evidence. D073 CSV formatting
and D074 local validation are host-tested offline additions; final993 C++ tests
normal+sanitizer and378controlledtool checks are recorded in their validation
reports. Original target app result above belongs to its historical source, not
the current CSV tree. Physical/EXPLAINED/PINMAP and human gate status unchanged.
See P2_offline_scope_completion_audit.md; no runtime integration or gate inferred.

2026-09-23 D075 update: user explicitly permits P2 software preparation before
physical/human acceptance. MotorGate checked callback boundary1c45f72 now exists
with independent locked tests,1030full+37active host cases and target compile-only
proof; no native UNO Q Port or application integration exists. This supersedes
the historical blanket no-MotorGate statement only. EXPLAINED/GATE records remain
absent; D075 is software scheduling authority, not P1/P0/P2 acceptance.