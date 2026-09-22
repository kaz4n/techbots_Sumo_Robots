# Scoped D-026/D-027 review - 2026-09-22

Reviewer: `p1_remaining_contract_audit`, separate read-only Codex context reused
from the motion/services review. Coordinator records its delivered verdict;
reviewer made no edits. Not cross-model review and not a full phase-gate review.
Scope: contracts 290c13b and implementation/tests c578911, relative to ad764c1.

**PASS. No open BLOCKER, MAJOR or MINOR.**

- opp_fusion.cpp:62: front > side > rear priority and bilateral conflicts match
  B5/D-026. No-history conflicts invent no bearing; valid history is reused.
- opp_fusion.cpp:95: finite world bearing stays in (-180,180], including extreme
  heading and float rounding at the excluded endpoint.
- opp_fusion.cpp:129: front recency uses rising observations; simultaneous ties
  preserve prior side. Zero/wrapping timestamps remain valid.
- opp_fusion.cpp:148: no detections preserve memory. Nonfinite heading invalidates
  world direction while retaining relative validity.
- opp_fusion.cpp:117: impact requires finite, IMU-valid horizontal norm strictly
  above threshold; double intermediates avoid finite-float overflow.
- opp_fusion.cpp:176: separate close-pattern counters saturate and qualify at
  observation 20. Contact exists only in centered ATTACK; ineligible calls clear
  it and re-entry needs a current qualified cue.
- Existing Debouncer/frontView bodies, locked tests, config and upload guards
  unchanged. No heap, I/O, clock read or unbounded work added.

Reviewed all 30 new cases and normal/ASan/UBSan receipts: 212 cases / 6,089,047
assertions pass, zero failures/skips, exit 0. Sanitizer flags present and no
diagnostics. Diff whitespace clean. The subsequent full tooling run passed
48/48, exit 0 (coordinator receipt P1_opp_memory_contact_tools.txt).

Reviewer independently inspected/reconstructed all 17 staged files per sketch
and approved manifest refresh ONLY for these exact byte hashes:

- matrix: a58a11bf03cc03a6e6ca642fb461ed224bf6de026417bd7509f6721232bd1c25
- timing: 8edcdadf19aef9cc96ce0281bc56199321a857279e83a4fb9799cafc87c4b4b5

Further source changes invalidate approval until re-reviewed. No upload, motor
run, hardware acceptance or phase authorization follows from this review.
Phantom/stuck handling, full FSM/target-loss braking, HAL/MotorGate and actual
sample freshness/WCET remain pending. D-028 is policy, not a recorder ring.
