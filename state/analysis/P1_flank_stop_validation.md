# P1 mirrored openers, logical STOP and defensive turn — 2026-09-22

P1 host development under D-016; P0 acceptance and every human gate pending.
Decisions D-033/D-034 define opener exits; D-035 defines logical STOP. New
D-036–D-038 authorize later steering/re-flank work, not measurements. D-039
explicitly authorizes one established locked-case amendment; exact proposal and
initial failed run are preserved in P1_stop_locked_conflict.md and
P1_flank_stop_build_initial.txt (348 cases, one failed case/six assertions, exit8).

Implemented shared SIDESTEP/ARC mirrors, phase-specific target exits, governor
profiles, bounded phase progression; logical StopHold integrated into Controller;
captured defensive turn with distinct700/800ms deadlines. Independent authors
read specs/public headers and avoided implementation.cpp files:35 opener,12 new
locked STOP,23 defend cases. The original locked MODE branch and full-hold checks
remain; approved BOTH branch now tests reset-only STOP instead of obsolete IDLE.

Validation:
- `wsl -d Ubuntu -- bash tools/test_host.sh`: exit0, CTest1/1,
  P1_flank_stop_build.txt.
- Separate reviewer independently ran the same script and host binary: exit0,
  **383 cases / 9,121,864 assertions**, zero fail/skip.
- `wsl -d Ubuntu -- cmake --build build/host-sanitize --parallel 2`, then
  `wsl -d Ubuntu -- build/host-sanitize/sumox26_tests`: exit0 for both,
  same383 cases/9,121,864 assertions, no ASan/UBSan diagnostics. Receipts:
  P1_flank_stop_sanitizer_build.txt and P1_flank_stop_sanitizer.txt.
- Targeted intermediate receipts are explicitly filtered component tests, not
  substitute full-suite passes. Initial failure was a documented specification
  conflict, not an unsuccessful safety-code repair or weakened assertion.
- Fresh separate Codex scoped reviewer: no open finding, exact single approved
  case matches proposal, all other established locked blobs unchanged. Report:
  ../reviews/P1_flank_stop_codex.md. This is not cross-model or a full phase gate.
- Reviewer reconstructed both complete23-file inert snapshots, checked original
  byte matches and inert paths, then approved exact manifest hashes. Tooling
  results recorded separately after that refresh.

All76 B16 defaults unchanged; no new pin or hardware API assumption. Complete
Robot fusion/arbitration, SEARCH/WAIT/escape/re-flank, real MotorGate, target build,
WCET, physical measurements and human gate approvals remain outstanding.

After approved manifest refresh: `wsl -d Ubuntu -- python3 -m unittest discover
-s tests/tooling -v`:48/48 PASS, exit0, P1_flank_stop_tools.txt. Source defaults
and compile-only/upload/strict-SSH guards remain checked by controlled substitutes.
Implementation commits:2071d4f (Flank),6a3dc29 (STOP),4768eb5 (DefendTurn).
