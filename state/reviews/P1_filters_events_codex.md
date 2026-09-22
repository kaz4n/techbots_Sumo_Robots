# Fresh scoped review: filters/stall/DIRECT/events — 2026-09-22

Reviewer: separate fresh-context Codex agent p1_feature_review, read-only; not
cross-model and not the full P1 gate. Coordinator recorded its returned verdict.
Scope:7955c0a through36767f7 and the accompanying current-source documentation.
Loaded AGENTS/safety-auditor role, B5/B11/B12/B15 and accepted D-025/D-028–D-032.

BLOCKER: none. MAJOR: none. MINOR: none open. Verdict: **PASS, scoped review**.

Resolved MINOR at tests/test_opp_filters.cpp:480: four LCG draws biased low-bit
mask sampling to32 of128 masks. Independent read-only reproduction confirmed it.
Author used bits16–22 and128 coverage assertions; independently confirmed all128
masks. Existing behavioral assertions remain. Normal/sanitizer reruns pass.

Reviewer independently ran `wsl -d Ubuntu -- bash tools/test_host.sh`: exit0.
Reviewed final coordinator normal and ASan/UBSan receipts:313 cases,
8,149,851 assertions, zero failures/skips. Finite handling, unsigned-wrap timing,
bounded work/storage, no core I/O and unchanged established locked tests verified.
Scoped tests preserve explicit component-versus-FSM/actuator evidence limits.

Reviewer independently reconstructed and inspected both complete21-file inert
snapshots. Resolved staging paths checked; copied bytes match current originals,
HAL contains only .gitkeep, MOTORS_ALLOWED==0 bench assertions remain and no core
I/O/global execution was introduced. Exact approved source hashes:
- bench/p0_matrix:7b3762a278b1318f93b9418733add5a2248a311d493b71b646b611db266d955a
- bench/p0_timing:fc74b73db18f9ec7f6220a0621d116eb0342948632598fee832edb2061b02033

Approval permits only this source-manifest refresh; preserves existing upload
guards and F-061 Immediate matrix restriction. Tooling rerun follows the refresh.
No board contact, motor authorization, full gate, target compilation or physical
claim. Complete FSM/MotorGate, frame recording/dump and human gates remain pending.
